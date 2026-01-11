#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每周菜品推送脚本（工作日前一天晚上推送）
自动选择1荤1素共2个低油低盐菜品，并提供食材购买链接
"""

import os
import re
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from pathlib import Path
from datetime import datetime, timedelta
from ingredient_links import get_ingredient_link, extract_ingredients


class WeeklyRecipeSender:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent / "cookReminder"
        
        # 荤菜类别（含肉类、海鲜等）
        self.meat_categories = ['炒菜', '蒸菜', '炖菜']
        
        # 素菜类别
        self.veg_categories = ['烫菜', '凉拌', '蒸菜', '炒菜']
        
        # 荤菜关键词
        self.meat_keywords = ['肉', '鸡', '鸭', '鱼', '虾', '牛', '猪', '排骨', '鸡翅', '鸡腿', '河虾']
        
        # 素菜关键词
        self.veg_keywords = ['青菜', '白菜', '西兰花', '豆腐', '菠菜', '莴笋', '胡萝卜', 
                            '茄子', '豆芽', '木耳', '花菜', '娃娃菜', '菜心', '鸡蛋']
    
    def get_all_recipes(self):
        """获取所有菜品文件"""
        recipes = []
        all_categories = list(set(self.meat_categories + self.veg_categories))
        
        for category in all_categories:
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
            
            # 低油：每份用油少于80g，低盐：每份用盐少于15g
            is_low_oil = total_oil < 80 or total_oil == 0
            is_low_salt = total_salt < 15 or total_salt == 0
            
            # 额外检查：包含"清炒"、"清蒸"等关键词
            healthy_keywords = ['清炒', '清蒸', '水煮', '汆烫', '浇汁', '凉拌', '白切', '蒜蓉']
            has_healthy_keyword = any(keyword in content for keyword in healthy_keywords)
            
            return (is_low_oil and is_low_salt) or has_healthy_keyword
            
        except Exception as e:
            print(f"分析菜品 {recipe_path} 时出错: {e}")
            return False
    
    def is_meat_dish(self, recipe):
        """判断是否为荤菜"""
        # 检查菜名是否包含荤菜关键词
        for keyword in self.meat_keywords:
            if keyword in recipe['name']:
                return True
        
        # 检查内容
        try:
            with open(recipe['file'], 'r', encoding='utf-8') as f:
                content = f.read()
                for keyword in self.meat_keywords:
                    if keyword in content:
                        return True
        except:
            pass
        
        return False
    
    def is_veg_dish(self, recipe):
        """判断是否为素菜"""
        # 首先排除荤菜
        if self.is_meat_dish(recipe):
            return False
        
        # 检查是否包含素菜关键词
        for keyword in self.veg_keywords:
            if keyword in recipe['name']:
                return True
        
        # 检查内容
        try:
            with open(recipe['file'], 'r', encoding='utf-8') as f:
                content = f.read()
                # 如果不含肉类关键词，但含有蔬菜关键词，判断为素菜
                has_veg = any(keyword in content for keyword in self.veg_keywords)
                has_meat = any(keyword in content for keyword in self.meat_keywords)
                if has_veg and not has_meat:
                    return True
        except:
            pass
        
        return False
    
    def select_recipes(self):
        """选择1荤1素共2个菜品"""
        all_recipes = self.get_all_recipes()
        
        # 筛选低油低盐菜品
        healthy_recipes = [r for r in all_recipes if self.is_low_oil_salt(r['file'])]
        
        # 分类荤素
        meat_dishes = [r for r in healthy_recipes if self.is_meat_dish(r)]
        veg_dishes = [r for r in healthy_recipes if self.is_veg_dish(r)]
        
        print(f"找到 {len(meat_dishes)} 个健康荤菜")
        print(f"找到 {len(veg_dishes)} 个健康素菜")
        
        if not meat_dishes or not veg_dishes:
            print("未找到足够的荤素搭配菜品")
            return None, None
        
        # 随机选择1荤1素
        meat_recipe = random.choice(meat_dishes)
        veg_recipe = random.choice(veg_dishes)
        
        print(f"选中荤菜: {meat_recipe['category']}/{meat_recipe['name']}")
        print(f"选中素菜: {veg_recipe['category']}/{veg_recipe['name']}")
        
        return meat_recipe, veg_recipe
    
    def read_recipe_content(self, recipe_file):
        """读取菜品内容"""
        try:
            with open(recipe_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            print(f"读取菜品文件失败: {e}")
            return None
    
    def format_email_content(self, meat_recipe, veg_recipe):
        """格式化邮件内容（双菜品+购买链接）"""
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_str = tomorrow.strftime('%Y年%m月%d日')
        weekday_cn = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][tomorrow.weekday()]
        
        meat_content = self.read_recipe_content(meat_recipe['file'])
        veg_content = self.read_recipe_content(veg_recipe['file'])
        
        if not meat_content or not veg_content:
            return None
        
        # 提取食材
        meat_ingredients = extract_ingredients(meat_content)
        veg_ingredients = extract_ingredients(veg_content)
        
        # 生成HTML
        html_content = f'''
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: "Microsoft YaHei", Arial, sans-serif;
                    line-height: 1.8;
                    color: #333;
                    max-width: 900px;
                    margin: 0 auto;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .container {{
                    background: white;
                    border-radius: 12px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    padding: 20px 0;
                    border-bottom: 3px solid #4CAF50;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    color: #2c3e50;
                    margin: 0;
                    font-size: 28px;
                }}
                .date {{
                    color: #7f8c8d;
                    font-size: 16px;
                    margin-top: 10px;
                }}
                .recipe-card {{
                    margin: 30px 0;
                    padding: 25px;
                    background: #f9f9f9;
                    border-radius: 8px;
                    border-left: 5px solid #4CAF50;
                }}
                .recipe-card.meat {{
                    border-left-color: #e74c3c;
                }}
                .recipe-card.veg {{
                    border-left-color: #27ae60;
                }}
                .recipe-title {{
                    display: flex;
                    align-items: center;
                    margin-bottom: 20px;
                }}
                .recipe-tag {{
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 14px;
                    margin-right: 10px;
                    font-weight: bold;
                    color: white;
                }}
                .tag-meat {{
                    background: #e74c3c;
                }}
                .tag-veg {{
                    background: #27ae60;
                }}
                .recipe-name {{
                    font-size: 22px;
                    color: #2c3e50;
                    font-weight: bold;
                }}
                h3 {{
                    color: #34495e;
                    margin-top: 20px;
                    font-size: 18px;
                }}
                ul {{
                    list-style-type: none;
                    padding-left: 0;
                }}
                li {{
                    padding: 8px 0;
                    padding-left: 25px;
                    position: relative;
                }}
                li:before {{
                    content: "▸";
                    position: absolute;
                    left: 0;
                    color: #4CAF50;
                    font-weight: bold;
                }}
                .ingredients-section {{
                    background: white;
                    padding: 25px;
                    border-radius: 8px;
                    margin: 30px 0;
                }}
                .ingredient-item {{
                    display: inline-block;
                    margin: 5px 10px 5px 0;
                    padding: 8px 15px;
                    background: #e8f5e9;
                    border-radius: 20px;
                    font-size: 14px;
                }}
                .ingredient-item a {{
                    color: #2e7d32;
                    text-decoration: none;
                    font-weight: 500;
                }}
                .ingredient-item a:hover {{
                    text-decoration: underline;
                }}
                .buy-section {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 25px;
                    border-radius: 8px;
                    margin: 30px 0;
                    text-align: center;
                }}
                .buy-section h3 {{
                    color: white;
                    margin-top: 0;
                }}
                .buy-button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: white;
                    color: #667eea;
                    border-radius: 25px;
                    text-decoration: none;
                    font-weight: bold;
                    margin: 10px 5px;
                    transition: transform 0.2s;
                }}
                .buy-button:hover {{
                    transform: translateY(-2px);
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #7f8c8d;
                    font-size: 14px;
                    text-align: center;
                }}
                .tips {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🍽️ 明日菜谱推荐</h1>
                    <div class="date">{tomorrow_str} {weekday_cn}</div>
                </div>
                
                <div class="tips">
                    <strong>💡 温馨提示：</strong>低油低盐，健康饮食。今日推荐1荤1素搭配，营养均衡！
                </div>
                
                <!-- 荤菜 -->
                <div class="recipe-card meat">
                    <div class="recipe-title">
                        <span class="recipe-tag tag-meat">荤菜</span>
                        <span class="recipe-name">{meat_recipe['name']}</span>
                    </div>
                    {self._format_recipe_detail(meat_content)}
                </div>
                
                <!-- 素菜 -->
                <div class="recipe-card veg">
                    <div class="recipe-title">
                        <span class="recipe-tag tag-veg">素菜</span>
                        <span class="recipe-name">{veg_recipe['name']}</span>
                    </div>
                    {self._format_recipe_detail(veg_content)}
                </div>
                
                <!-- 购买清单 -->
                <div class="buy-section">
                    <h3>🛒 一键购买所需食材</h3>
                    <p>点击下方按钮，在美团小象超市购买所需食材</p>
                    <a href="https://r.meituan.com/g7YjcD" class="buy-button">📱 打开美团小象超市</a>
                </div>
                
                <div class="ingredients-section">
                    <h3>📝 所需食材清单</h3>
                    <div>
                        {self._format_ingredient_links(meat_ingredients + veg_ingredients)}
                    </div>
                </div>
                
                <div class="footer">
                    <p>📅 {datetime.now().strftime('%Y年%m月%d日')} </p>
                    <p>💚 低油低盐，健康生活从每一餐开始 by 小胡</p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        return html_content
    
    def _format_recipe_detail(self, content):
        """格式化单个菜品的详细内容"""
        lines = content.split('\n')
        html_parts = []
        in_list = False
        
        for line in lines:
            line = line.strip()
            
            # 跳过标题和图片
            if line.startswith('# ') or line.startswith('!['):
                continue
            elif line.startswith('## '):
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False
                html_parts.append(f'<h3>{line[3:]}</h3>')
            elif line.startswith('- '):
                if not in_list:
                    html_parts.append('<ul>')
                    in_list = True
                html_parts.append(f'<li>{line[2:]}</li>')
            elif line:
                if in_list:
                    html_parts.append('</ul>')
                    in_list = False
                html_parts.append(f'<p>{line}</p>')
        
        if in_list:
            html_parts.append('</ul>')
        
        return '\n'.join(html_parts)
    
    def _format_ingredient_links(self, ingredients):
        """格式化食材购买链接"""
        if not ingredients:
            return '<p>暂无食材信息</p>'
        
        # 去重
        ingredients = list(set(ingredients))
        
        html_parts = []
        for ingredient in ingredients:
            link = get_ingredient_link(ingredient)
            html_parts.append(
                f'<span class="ingredient-item">'
                f'<a href="{link}" target="_blank">{ingredient}</a>'
                f'</span>'
            )
        
        return '\n'.join(html_parts)
    
    def send_email(self, subject, content):
        """发送邮件"""
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.qq.com')
        smtp_port = int(os.getenv('SMTP_PORT', '465'))
        from_email = os.getenv('FROM_EMAIL')
        email_password = os.getenv('EMAIL_PASSWORD')
        to_email = os.getenv('TO_EMAIL')
        if not from_email or not email_password:
            print("错误: 未设置邮件配置环境变量 FROM_EMAIL 和 EMAIL_PASSWORD")
            return False
        
        try:
            # 创建邮件
            message = MIMEMultipart('alternative')
            message['From'] = from_email
            message['To'] = to_email
            message['Subject'] = Header(subject, 'utf-8')

            # 添加HTML内容
            html_part = MIMEText(content, 'html', 'utf-8')
            message.attach(html_part)
            
            # 发送邮件
            print(f"正在连接邮件服务器 {smtp_server}:{smtp_port}...")
            
            if smtp_port == 465:
                import ssl
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context)
            else:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
            
            print("正在登录邮箱...")
            server.login(from_email, email_password)
            
            print("正在发送邮件...")
            server.sendmail(from_email, [to_email], message.as_string())
            server.quit()
            
            print(f"✅ 邮件已成功发送到 {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ 发送邮件失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run(self):
        """运行主流程"""
        print("=" * 60)
        print("🍳 明日菜谱推送（1荤1素健康搭配）")
        print("=" * 60)
        
        # 选择菜品
        meat_recipe, veg_recipe = self.select_recipes()
        if not meat_recipe or not veg_recipe:
            return False
        
        # 格式化邮件内容
        content = self.format_email_content(meat_recipe, veg_recipe)
        if not content:
            return False
        
        # 发送邮件
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_str = tomorrow.strftime('%m月%d日')
        weekday_cn = ['周一', '周二', '周三', '周四', '周五'][tomorrow.weekday()] if tomorrow.weekday() < 5 else '周末'
        
        subject = f"🍽️ 明日菜谱 {tomorrow_str} {weekday_cn}：{meat_recipe['name']} + {veg_recipe['name']}"
        
        success = self.send_email(subject, content)
        
        print("=" * 60)
        return success


if __name__ == "__main__":
    sender = WeeklyRecipeSender()
    # 目标邮箱
    sender.run()

