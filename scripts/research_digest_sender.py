#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 研究摘要邮件推送
整合 arXiv 论文和 YouTube 访谈视频，发送每周研究摘要
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
from typing import List, Dict, Optional

from arxiv_fetcher import ArxivFetcher, ArxivPaper, filter_recent_papers
from youtube_fetcher import YouTubeFetcher, YouTubeFetcherNoAPI, YouTubeVideo


class ResearchDigestSender:
    """AI 研究摘要邮件发送器"""
    
    def __init__(self):
        self.arxiv_fetcher = ArxivFetcher(max_results=15)
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        
        if self.youtube_api_key:
            self.youtube_fetcher = YouTubeFetcher(api_key=self.youtube_api_key, max_results=5)
        else:
            self.youtube_fetcher = None
            self.youtube_no_api = YouTubeFetcherNoAPI()
        
        # 选择要关注的科技领袖
        self.selected_leaders = ["Elon Musk", "Jensen Huang", "Sam Altman"]
    
    def fetch_arxiv_papers(self) -> Dict[str, List[ArxivPaper]]:
        """获取 arXiv 论文"""
        print("\n" + "=" * 60)
        print("📚 正在获取 arXiv 论文...")
        print("=" * 60)
        
        papers = self.arxiv_fetcher.fetch_all()
        
        # 过滤最近 7 天的论文
        for category in papers:
            papers[category] = filter_recent_papers(papers[category], days=7)
        
        print(f"✅ 获取完成: {len(papers['llm'])} 篇大模型论文, {len(papers['advertising'])} 篇广告领域论文")
        
        return papers
    
    def fetch_youtube_videos(self) -> Dict:
        """获取 YouTube 视频"""
        print("\n" + "=" * 60)
        print("🎬 正在获取 YouTube 视频...")
        print("=" * 60)
        
        if self.youtube_fetcher:
            videos = self.youtube_fetcher.fetch_selected_leaders(self.selected_leaders)
            return {"type": "api", "data": videos}
        else:
            recommendations = self.youtube_no_api.get_recommendations(self.selected_leaders)
            return {"type": "recommendations", "data": recommendations}
    
    def generate_html_content(
        self, 
        papers: Dict[str, List[ArxivPaper]], 
        youtube_data: Dict
    ) -> str:
        """生成 HTML 邮件内容"""
        today = datetime.now().strftime('%Y年%m月%d日')
        
        html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f7fa;
        }}
        .container {{
            background: white;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }}
        .header {{
            text-align: center;
            padding: 30px 0;
            border-bottom: 3px solid #667eea;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #2d3748;
            margin: 0;
            font-size: 32px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .date {{
            color: #718096;
            font-size: 16px;
            margin-top: 10px;
        }}
        .section {{
            margin: 40px 0;
        }}
        .section-header {{
            display: flex;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e2e8f0;
        }}
        .section-icon {{
            font-size: 28px;
            margin-right: 15px;
        }}
        .section-title {{
            font-size: 24px;
            color: #2d3748;
            margin: 0;
        }}
        .section-subtitle {{
            font-size: 14px;
            color: #718096;
            margin-left: auto;
        }}
        .paper-card {{
            background: #f7fafc;
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            border-left: 4px solid #667eea;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .paper-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
        }}
        .paper-card.ad {{
            border-left-color: #48bb78;
        }}
        .paper-title {{
            font-size: 16px;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 8px;
        }}
        .paper-title a {{
            color: #667eea;
            text-decoration: none;
        }}
        .paper-title a:hover {{
            text-decoration: underline;
        }}
        .paper-authors {{
            font-size: 13px;
            color: #718096;
            margin-bottom: 10px;
        }}
        .paper-summary {{
            font-size: 14px;
            color: #4a5568;
            line-height: 1.7;
        }}
        .paper-meta {{
            display: flex;
            gap: 15px;
            margin-top: 12px;
            font-size: 12px;
        }}
        .paper-tag {{
            display: inline-block;
            padding: 3px 10px;
            background: #edf2f7;
            border-radius: 12px;
            color: #4a5568;
        }}
        .paper-link {{
            color: #667eea;
            text-decoration: none;
        }}
        .video-card {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            color: white;
        }}
        .video-title {{
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        .video-title a {{
            color: #ff6b6b;
            text-decoration: none;
        }}
        .video-channel {{
            font-size: 13px;
            color: #a0aec0;
            margin-bottom: 10px;
        }}
        .video-desc {{
            font-size: 14px;
            color: #cbd5e0;
            line-height: 1.6;
        }}
        .channel-card {{
            background: #f7fafc;
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            border-left: 4px solid #e53e3e;
        }}
        .channel-name {{
            font-size: 16px;
            font-weight: 600;
            color: #2d3748;
        }}
        .channel-name a {{
            color: #e53e3e;
            text-decoration: none;
        }}
        .channel-desc {{
            font-size: 14px;
            color: #718096;
            margin-top: 8px;
        }}
        .channel-leaders {{
            font-size: 13px;
            color: #4a5568;
            margin-top: 8px;
        }}
        .search-link {{
            display: inline-block;
            padding: 10px 20px;
            background: #e53e3e;
            color: white;
            border-radius: 25px;
            text-decoration: none;
            margin: 5px;
            font-size: 14px;
        }}
        .search-link:hover {{
            background: #c53030;
        }}
        .leader-section {{
            background: #faf5ff;
            border-radius: 12px;
            padding: 25px;
            margin: 20px 0;
            border-left: 4px solid #9f7aea;
        }}
        .leader-name {{
            font-size: 20px;
            font-weight: 600;
            color: #553c9a;
            margin-bottom: 15px;
        }}
        .footer {{
            margin-top: 50px;
            padding-top: 30px;
            border-top: 2px solid #e2e8f0;
            text-align: center;
            color: #718096;
            font-size: 14px;
        }}
        .footer-links {{
            margin-top: 15px;
        }}
        .footer-links a {{
            color: #667eea;
            text-decoration: none;
            margin: 0 10px;
        }}
        .tips-box {{
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            border-radius: 12px;
            padding: 20px;
            margin: 30px 0;
        }}
        .tips-box h4 {{
            color: #744210;
            margin: 0 0 10px 0;
        }}
        .tips-box p {{
            color: #7b341e;
            margin: 0;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 AI 研究周报</h1>
            <div class="date">{today}</div>
        </div>
        
        <div class="tips-box">
            <h4>📌 本期内容</h4>
            <p>本期包含最新的大模型和广告领域 arXiv 论文，以及科技领袖 (Elon Musk, Jensen Huang, Sam Altman) 的最新访谈视频。</p>
        </div>
        
        <!-- arXiv 论文部分 -->
        <div class="section">
            <div class="section-header">
                <span class="section-icon">📚</span>
                <h2 class="section-title">大模型领域论文</h2>
                <span class="section-subtitle">{len(papers['llm'])} 篇</span>
            </div>
            {self._generate_papers_html(papers['llm'], 'llm')}
        </div>
        
        <div class="section">
            <div class="section-header">
                <span class="section-icon">📊</span>
                <h2 class="section-title">广告领域论文</h2>
                <span class="section-subtitle">{len(papers['advertising'])} 篇</span>
            </div>
            {self._generate_papers_html(papers['advertising'], 'ad')}
        </div>
        
        <!-- YouTube 视频部分 -->
        <div class="section">
            <div class="section-header">
                <span class="section-icon">🎬</span>
                <h2 class="section-title">科技领袖访谈视频</h2>
            </div>
            {self._generate_youtube_html(youtube_data)}
        </div>
        
        <div class="footer">
            <p>📅 {today} | AI 研究周报</p>
            <p>💡 保持学习，保持好奇</p>
            <div class="footer-links">
                <a href="https://arxiv.org/">arXiv</a>
                <a href="https://www.youtube.com/">YouTube</a>
            </div>
        </div>
    </div>
</body>
</html>
'''
        return html
    
    def _generate_papers_html(self, papers: List[ArxivPaper], paper_type: str) -> str:
        """生成论文 HTML"""
        if not papers:
            return '<p style="color: #718096;">本周暂无新论文</p>'
        
        html_parts = []
        card_class = "paper-card" if paper_type == 'llm' else "paper-card ad"
        
        for paper in papers[:10]:  # 限制显示数量
            authors_str = ', '.join(paper.authors[:3])
            if len(paper.authors) > 3:
                authors_str += f' 等 {len(paper.authors)} 位作者'
            
            # 截断摘要
            summary = paper.summary[:300] + '...' if len(paper.summary) > 300 else paper.summary
            
            # 格式化日期
            pub_date = paper.published[:10] if paper.published else ''
            
            html_parts.append(f'''
            <div class="{card_class}">
                <div class="paper-title">
                    <a href="{paper.abs_url}" target="_blank">{paper.title}</a>
                </div>
                <div class="paper-authors">👥 {authors_str}</div>
                <div class="paper-summary">{summary}</div>
                <div class="paper-meta">
                    <span class="paper-tag">📅 {pub_date}</span>
                    <span class="paper-tag">🏷️ {", ".join(paper.categories[:2])}</span>
                    <a href="{paper.pdf_url}" class="paper-link" target="_blank">📄 PDF</a>
                </div>
            </div>
            ''')
        
        return '\n'.join(html_parts)
    
    def _generate_youtube_html(self, youtube_data: Dict) -> str:
        """生成 YouTube HTML"""
        if youtube_data["type"] == "api":
            return self._generate_youtube_api_html(youtube_data["data"])
        else:
            return self._generate_youtube_recommendations_html(youtube_data["data"])
    
    def _generate_youtube_api_html(self, videos_by_leader: Dict[str, List[YouTubeVideo]]) -> str:
        """生成基于 API 数据的 YouTube HTML"""
        html_parts = []
        
        for leader, videos in videos_by_leader.items():
            if not videos:
                continue
            
            html_parts.append(f'''
            <div class="leader-section">
                <div class="leader-name">👤 {leader}</div>
            ''')
            
            for video in videos[:3]:
                desc = video.description[:150] + '...' if len(video.description) > 150 else video.description
                html_parts.append(f'''
                <div class="video-card">
                    <div class="video-title">
                        <a href="{video.watch_url}" target="_blank">🎥 {video.title}</a>
                    </div>
                    <div class="video-channel">📺 {video.channel_title}</div>
                    <div class="video-desc">{desc}</div>
                </div>
                ''')
            
            html_parts.append('</div>')
        
        return '\n'.join(html_parts) if html_parts else '<p style="color: #718096;">本周暂无新视频</p>'
    
    def _generate_youtube_recommendations_html(self, recommendations: Dict) -> str:
        """生成推荐列表 HTML"""
        html_parts = []
        
        # 搜索链接
        html_parts.append('''
        <div style="text-align: center; margin-bottom: 30px;">
            <p style="color: #4a5568; margin-bottom: 15px;">🔍 点击下方按钮搜索最新访谈视频</p>
        ''')
        
        for leader, url in recommendations["search_links"].items():
            html_parts.append(f'<a href="{url}" class="search-link" target="_blank">{leader}</a>')
        
        html_parts.append('</div>')
        
        # 推荐频道
        html_parts.append('''
        <h3 style="color: #2d3748; margin-top: 30px;">📺 推荐科技访谈频道</h3>
        ''')
        
        for name, info in recommendations["channels"].items():
            leaders_str = ', '.join(info.get('leaders', []))
            html_parts.append(f'''
            <div class="channel-card">
                <div class="channel-name">
                    <a href="{info['url']}" target="_blank">{name}</a>
                </div>
                <div class="channel-desc">{info['description']}</div>
                <div class="channel-leaders">🎤 常见嘉宾: {leaders_str}</div>
            </div>
            ''')
        
        return '\n'.join(html_parts)
    
    def send_email(self, to_email: str, subject: str, content: str) -> bool:
        """发送邮件"""
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.qq.com')
        smtp_port = int(os.getenv('SMTP_PORT', '465'))
        from_email = os.getenv('FROM_EMAIL')
        email_password = os.getenv('EMAIL_PASSWORD')
        
        if not from_email or not email_password:
            print("❌ 错误: 未设置邮件配置环境变量 FROM_EMAIL 和 EMAIL_PASSWORD")
            return False
        
        try:
            # 创建邮件
            message = MIMEMultipart('alternative')
            message['From'] = from_email
            message['To'] = to_email
            message['Subject'] = Header(subject, 'utf-8')
            
            # 添加 HTML 内容
            html_part = MIMEText(content, 'html', 'utf-8')
            message.attach(html_part)
            
            # 发送邮件
            print(f"\n正在连接邮件服务器 {smtp_server}:{smtp_port}...")
            
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
    
    def run(self, to_email: Optional[str] = None):
        """运行主流程"""
        print("\n" + "=" * 60)
        print("🔬 AI 研究摘要邮件推送")
        print("=" * 60)
        
        # 获取目标邮箱
        if to_email is None:
            to_email = os.getenv('TO_EMAIL', 'huzhe06@gmail.com')
        
        # 获取 arXiv 论文
        papers = self.fetch_arxiv_papers()
        
        # 获取 YouTube 视频
        youtube_data = self.fetch_youtube_videos()
        
        # 生成邮件内容
        print("\n正在生成邮件内容...")
        html_content = self.generate_html_content(papers, youtube_data)
        
        # 发送邮件
        today = datetime.now().strftime('%m月%d日')
        subject = f"🔬 AI 研究周报 ({today}) - 大模型 & 广告领域论文 + 科技领袖访谈"
        
        success = self.send_email(to_email, subject, html_content)
        
        print("\n" + "=" * 60)
        if success:
            print("✅ 研究摘要发送完成！")
        else:
            print("❌ 研究摘要发送失败，请检查配置")
        print("=" * 60)
        
        return success


if __name__ == "__main__":
    sender = ResearchDigestSender()
    sender.run()
