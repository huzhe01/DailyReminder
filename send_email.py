#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import os

def send_meal_plan():
    """发送健康菜谱到指定邮箱"""
    
    # 读取菜谱内容
    with open('/workspace/健康工作日菜谱.md', 'r', encoding='utf-8') as f:
        meal_plan_content = f.read()
    
    # 邮件配置
    sender = 'noreply@cooklikehoc.com'  # 发件人
    receiver = 'zhuhuiqing13@163.com'   # 收件人
    
    # 创建邮件对象
    message = MIMEMultipart('alternative')
    message['From'] = Header('CookLikeHOC 健康菜谱', 'utf-8')
    message['To'] = Header('用户', 'utf-8')
    message['Subject'] = Header('您的一周健康工作日菜谱（低糖低油低盐）', 'utf-8')
    
    # 邮件正文
    text_content = f"""
您好！

这是根据 CookLikeHOC 菜谱库为您精心定制的一周健康工作日菜谱。

特点：
- 低糖、低油、低盐
- 富含绿叶蔬菜
- 营养均衡
- 烹饪简单

详细内容请查看下方菜谱。

祝您享受健康美味的一周！

---

{meal_plan_content}
"""
    
    # 添加文本内容
    text_part = MIMEText(text_content, 'plain', 'utf-8')
    message.attach(text_part)
    
    # HTML 版本（更美观）
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Microsoft YaHei', Arial, sans-serif;
                line-height: 1.8;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c7a3e;
                border-bottom: 3px solid #2c7a3e;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #4a8f5c;
                margin-top: 30px;
            }}
            h3 {{
                color: #6ba679;
            }}
            .day-section {{
                background-color: #f9fdf9;
                padding: 20px;
                margin: 20px 0;
                border-left: 4px solid #2c7a3e;
                border-radius: 5px;
            }}
            .meal {{
                margin: 15px 0;
            }}
            ul {{
                line-height: 2;
            }}
            .highlight {{
                background-color: #e8f5e9;
                padding: 15px;
                border-radius: 5px;
                margin: 15px 0;
            }}
            .tips {{
                background-color: #fff3e0;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #ff9800;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🥗 一周健康工作日菜谱</h1>
            <div class="highlight">
                <p><strong>定制特点：</strong>低糖 · 低油 · 低盐 · 多绿叶蔬菜 · 营养均衡</p>
                <p><strong>数据来源：</strong>CookLikeHOC 菜谱库</p>
            </div>
            
            {convert_markdown_to_html(meal_plan_content)}
            
            <div class="tips">
                <p><strong>💡 温馨提示：</strong></p>
                <ul>
                    <li>本菜谱已针对健康需求优化，建议按照建议的油盐糖用量烹饪</li>
                    <li>可根据个人喜好微调食材，但需保持低油低盐原则</li>
                    <li>建议配合适量运动，效果更佳</li>
                </ul>
            </div>
            
            <p style="text-align: center; color: #888; margin-top: 30px;">
                祝您享受健康美味的一周！🌿
            </p>
        </div>
    </body>
    </html>
    """
    
    html_part = MIMEText(html_content, 'html', 'utf-8')
    message.attach(html_part)
    
    # 发送邮件
    try:
        # 尝试使用不同的 SMTP 服务器
        smtp_servers = [
            ('localhost', 25),
            ('127.0.0.1', 25),
        ]
        
        sent = False
        for smtp_host, smtp_port in smtp_servers:
            try:
                print(f"尝试连接 SMTP 服务器: {smtp_host}:{smtp_port}")
                server = smtplib.SMTP(smtp_host, smtp_port, timeout=5)
                server.sendmail(sender, [receiver], message.as_string())
                server.quit()
                print(f"✓ 邮件发送成功到: {receiver}")
                sent = True
                break
            except Exception as e:
                print(f"✗ 连接失败: {e}")
                continue
        
        if not sent:
            print("\n⚠ 未能通过 SMTP 发送邮件")
            print("正在生成邮件文件，您可以手动发送...")
            
            # 保存邮件内容到文件
            email_file = '/workspace/菜谱邮件.html'
            with open(email_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✓ 邮件内容已保存到: {email_file}")
            print(f"✓ Markdown 版本: /workspace/健康工作日菜谱.md")
            print(f"\n请将以上文件内容复制并手动发送到: {receiver}")
            
    except Exception as e:
        print(f"发送邮件时出错: {e}")
        print("\n正在生成邮件文件...")
        
        # 保存邮件内容到文件
        email_file = '/workspace/菜谱邮件.html'
        with open(email_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✓ 邮件内容已保存到: {email_file}")
        print(f"✓ Markdown 版本: /workspace/健康工作日菜谱.md")

def convert_markdown_to_html(md_text):
    """简单的 Markdown 到 HTML 转换"""
    import re
    
    html = md_text
    
    # 转换标题
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # 转换粗体
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    
    # 转换列表
    html = re.sub(r'^\- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
    
    # 转换段落
    html = re.sub(r'\n\n', '</p><p>', html)
    html = '<p>' + html + '</p>'
    
    # 转换水平线
    html = re.sub(r'^---$', '<hr/>', html, flags=re.MULTILINE)
    
    return html

if __name__ == '__main__':
    send_meal_plan()