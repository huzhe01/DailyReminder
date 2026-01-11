#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日菜品推送脚本
自动选择低油低盐的菜品并发送到指定邮箱
"""

import os
import re
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from pathlib import Path
from datetime import datetime
import json


class RecipeSender:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent / "cookReminder"
        self.low_oil_categories = ['蒸菜', '烫菜', '汤', '凉拌', '早餐']
        self.prefer_dishes = []  # 优先推荐的清淡菜品
        
    def get_all_recipes(self):
        """获取所有菜品文件"""
        recipes = []
        categories = ['蒸菜', '烫菜', '汤', '炒菜', '凉拌', '早餐', '主食']
        
        for category in categories:
            category_path = self.base_dir / category
            if category_path.exists():
                for recipe_file in category_path.glob('*.md'):
                    if recipe_file.name != 'README.md':
                        recipes.append({
                            'file': recipe_file,
                            'category': category,
                            'name': recipe_file.stem
                        })
        
        return recipes
    
    def is_low_oil_salt(self, recipe_path):
        """判断是否为低油低盐菜品"""
        try:
            with open(recipe_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查油的用量（克数）
            oil_pattern = r'(\d+)g?\s*[大豆油|油|食用油|花生油]'
            oil_matches = re.findall(oil_pattern, content)
            
            # 检查盐的用量（克数）
            salt_pattern = r'(\d+)g?\s*盐'
            salt_matches = re.findall(salt_pattern, content)
            
            # 计算油盐用量
            total_oil = sum([int(m) for m in oil_matches]) if oil_matches else 0
            total_salt = sum([int(m) for m in salt_matches]) if salt_matches else 0
            
            # 低油：每份用油少于50g，低盐：每份用盐少于10g
            # 或者没有明确标注油盐的（可能是清蒸、水煮类）
            is_low_oil = total_oil < 50 or total_oil == 0
            is_low_salt = total_salt < 10 or total_salt == 0
            
            # 额外检查：包含"清炒"、"清蒸"、"水煮"等关键词
            healthy_keywords = ['清炒', '清蒸', '水煮', '汆烫', '浇汁', '凉拌', '白切']
            has_healthy_keyword = any(keyword in content for keyword in healthy_keywords)
            
            return (is_low_oil and is_low_salt) or has_healthy_keyword
            
        except Exception as e:
            print(f"分析菜品 {recipe_path} 时出错: {e}")
            return False
    
    def select_recipe(self):
        """选择一个低油低盐的菜品"""
        all_recipes = self.get_all_recipes()
        
        # 筛选低油低盐菜品
        healthy_recipes = []
        for recipe in all_recipes:
            if self.is_low_oil_salt(recipe['file']):
                healthy_recipes.append(recipe)
        
        if not healthy_recipes:
            print("未找到符合条件的低油低盐菜品")
            return None
        
        # 随机选择一个
        selected = random.choice(healthy_recipes)
        print(f"选中菜品: {selected['category']}/{selected['name']}")
        
        return selected
    
    def read_recipe_content(self, recipe_file):
        """读取菜品内容"""
        try:
            with open(recipe_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            print(f"读取菜品文件失败: {e}")
            return None
    
    def format_email_content(self, recipe):
        """格式化邮件内容"""
        content = self.read_recipe_content(recipe['file'])
        if not content:
            return None
        
        # 转换markdown为HTML
        html_content = self.markdown_to_html(content, recipe)
        
        return html_content
    
    def markdown_to_html(self, markdown_content, recipe):
        """将Markdown转换为HTML邮件格式"""
        # 简单的markdown转HTML
        lines = markdown_content.split('\n')
        html_lines = []
        
        html_lines.append(f'''
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: "Microsoft YaHei", Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #34495e;
                    margin-top: 25px;
                }}
                ul {{
                    list-style-type: none;
                    padding-left: 0;
                }}
                li {{
                    padding: 5px 0;
                    padding-left: 20px;
                }}
                li:before {{
                    content: "▸ ";
                    color: #3498db;
                    font-weight: bold;
                }}
                .category {{
                    display: inline-block;
                    background: #3498db;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-size: 14px;
                    margin-bottom: 15px;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #7f8c8d;
                    font-size: 14px;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="category">{recipe['category']}</div>
        ''')
        
        in_list = False
        for line in lines:
            line = line.strip()
            
            # 标题
            if line.startswith('# '):
                html_lines.append(f'<h1>{line[2:]}</h1>')
            elif line.startswith('## '):
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(f'<h2>{line[3:]}</h2>')
            # 列表项
            elif line.startswith('- '):
                if not in_list:
                    html_lines.append('<ul>')
                    in_list = True
                html_lines.append(f'<li>{line[2:]}</li>')
            # 图片（跳过，邮件中不易显示本地图片）
            elif line.startswith('!['):
                continue
            # 普通段落
            elif line:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(f'<p>{line}</p>')
        
        if in_list:
            html_lines.append('</ul>')
        
        # 添加页脚
        today = datetime.now().strftime('%Y年%m月%d日')
        html_lines.append(f'''
            <div class="footer">
                <p>📅 {today} | 像老乡鸡那样做饭</p>
                <p>💡 低油低盐，健康生活从每一餐开始 From Zhe Hu</p>
            </div>
        </body>
        </html>
        ''')
        
        return '\n'.join(html_lines)
    
    def send_email(self, to_email, subject, content):
        """发送邮件"""
        # 从环境变量读取邮件配置
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.qq.com')
        smtp_port = int(os.getenv('SMTP_PORT', '465'))  # 默认使用SSL端口465
        from_email = os.getenv('FROM_EMAIL')
        email_password = os.getenv('EMAIL_PASSWORD')
        
        if not from_email or not email_password:
            print("错误: 未设置邮件配置环境变量 FROM_EMAIL 和 EMAIL_PASSWORD")
            return False
        
        try:
            # 创建邮件
            message = MIMEMultipart('alternative')
            # QQ邮箱要求From字段必须是纯邮箱地址，不能包含显示名称
            message['From'] = from_email
            message['To'] = to_email
            message['Subject'] = Header(subject, 'utf-8')
            
            # 添加HTML内容
            html_part = MIMEText(content, 'html', 'utf-8')
            message.attach(html_part)
            
            # 发送邮件 - 根据端口选择连接方式
            print(f"正在连接邮件服务器 {smtp_server}:{smtp_port}...")
            print(f"发件邮箱: {from_email}")
            print(f"授权码长度: {len(email_password)} 字符")
            
            if smtp_port == 465:
                # 使用SSL连接（推荐用于QQ邮箱）
                import ssl
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context)
            else:
                # 使用TLS连接（端口587）
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
            
            # 开启调试模式
            server.set_debuglevel(1)
            
            print("正在登录邮箱...")
            print(f"尝试登录: {from_email}")
            server.login(from_email, email_password)
            print("✓ 登录成功！")
            
            print("正在发送邮件...")
            server.sendmail(from_email, [to_email], message.as_string())
            print("✓ 邮件发送成功！")
            
            server.quit()
            
            print(f"✅ 邮件已成功发送到 {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ 发送邮件失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run(self, to_email):
        """运行主流程"""
        print("=" * 50)
        print("🍳 每日健康菜品推送")
        print("=" * 50)
        
        # 选择菜品
        recipe = self.select_recipe()
        if not recipe:
            return False
        
        # 格式化邮件内容
        content = self.format_email_content(recipe)
        if not content:
            return False
        
        # 发送邮件
        today = datetime.now().strftime('%Y年%m月%d日')
        subject = f"🍽️ 今日推荐菜品：{recipe['name']} ({today})"
        
        success = self.send_email(to_email, subject, content)
        
        print("=" * 50)
        return success


if __name__ == "__main__":
    sender = RecipeSender()
    # 目标邮箱
    target_email = "huzhe06@gmail.com"
    sender.run(target_email)

