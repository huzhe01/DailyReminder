#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 研究摘要邮件推送
整合 arXiv 论文、YouTube、RSS、GitHub、Reddit、HN，发送每日研究摘要
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
from typing import List, Dict, Optional
from openai import OpenAI
import time

from arxiv_fetcher import ArxivFetcher, ArxivPaper, filter_recent_papers
from youtube_fetcher import YouTubeFetcher, YouTubeFetcherNoAPI, YouTubeVideo
from feed_fetcher import FeedFetcher, FeedItem
from github_fetcher import GitHubFetcher, GitHubIssue, TrendingRepo
from reddit_fetcher import RedditFetcher, RedditPost
from hn_fetcher import HNFetcher, HNStory
from deduplicator import Deduplicator
from ai_curator import AICurator

class UsageTracker:
    """资源使用统计追踪器"""
    def __init__(self):
        self.llm_calls = 0
        self.llm_input_tokens = 0
        self.llm_output_tokens = 0
        self.youtube_api_calls = 0
        self.youtube_quota = 0
    
    def log_llm_usage(self, usage):
        """记录 LLM Token 使用"""
        if usage:
            self.llm_calls += 1
            self.llm_input_tokens += getattr(usage, 'prompt_tokens', 0)
            self.llm_output_tokens += getattr(usage, 'completion_tokens', 0)
            
    def log_youtube_usage(self, calls: int, quota: int):
        """记录 YouTube API 使用"""
        self.youtube_api_calls += calls
        self.youtube_quota += quota

class ResearchDigestSender:
    """AI 研究摘要邮件发送器"""
    
    def __init__(self):
        self.arxiv_fetcher = ArxivFetcher(max_results=15)
        self.feed_fetcher = FeedFetcher(days_lookback=2)
        self.github_fetcher = GitHubFetcher()
        self.reddit_fetcher = RedditFetcher()
        self.hn_fetcher = HNFetcher()
        self.deduplicator = Deduplicator()
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.usage_tracker = UsageTracker()
        
        # Initialize OpenAI client for paper summarization
        api_key = os.getenv('MODELSCOPE_API_KEY')
        if not api_key:
            raise ValueError("请设置 MODELSCOPE_API_KEY 环境变量")
        self.client = OpenAI(
            base_url='https://api-inference.modelscope.cn/v1/',
            api_key=api_key
        )
        
        # AI Curator (shares the same client)
        self.ai_curator = AICurator(client=self.client)
        
        if self.youtube_api_key:
            self.youtube_fetcher = YouTubeFetcher(api_key=self.youtube_api_key, max_results=5)
        else:
            self.youtube_fetcher = None
            self.youtube_no_api = YouTubeFetcherNoAPI()
        
        # 选择要关注的科技领袖
        self.selected_leaders = ["Elon Musk", "Jensen Huang", "Sam Altman"]
    
    def summarize_paper(self, title: str, abstract: str) -> str:
        """使用 AI 翻译并总结论文"""
        try:
            response = self.client.chat.completions.create(
                model="Qwen/Qwen3-32B",
                messages=[
                    {"role": "system", "content": "你是一个专业的AI研究助手。请将给定的论文摘要翻译成中文，并用一句话总结这篇论文的核心贡献。格式要求：先给出中文摘要，换行后给出'核心贡献：'。"},
                    {"role": "user", "content": f"Title: {title}\nAbstract: {abstract}"}
                ],
                extra_body={"enable_thinking": False}
            )
            self.usage_tracker.log_llm_usage(response.usage)
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ AI 摘要生成失败: {e}")
            return abstract

    def generate_daily_briefing(self, papers: Dict, feeds: Dict, videos: Dict) -> str:
        """生成每日 AI 简报"""
        print("\n🤖 正在生成每日 AI 简报...")
        
        # 准备输入数据 provided to LLM
        context = "请根据以下今天收集到的信息，为我撰写一份简短的'每日 AI 简报' (Daily Briefing)。\n\n"
        
        # Top 3 LLM Papers
        context += "【热门大模型论文】\n"
        for p in papers.get('llm', [])[:3]:
            context += f"- {p.title}\n"
            
        # Top News
        context += "\n【重要科技新闻】\n"
        news_items = feeds.get('Tech_News', [])[:3] + feeds.get('AI_Labs', [])[:3]
        for item in news_items:
            context += f"- {item.title} ({item.source_name})\n"
            
        # Top Videos
        context += "\n【最新访谈】\n"
        video_data = videos.get('data', {})
        if videos['type'] == 'api':
            for leader, vids in video_data.items():
                if vids:
                    context += f"- {leader}: {vids[0].title}\n"
        
        context += "\n要求：用中文撰写，语气专业且引人入胜。分为三个简短段落：1. 学术突破 (基于论文); 2. 行业动态 (基于新闻); 3. 值得关注 (综合)。总字数控制在 400 字以内。"

        try:
            response = self.client.chat.completions.create(
                model="Qwen/Qwen3-32B",
                messages=[
                    {"role": "system", "content": "你是一位资深的科技主编，擅长从海量信息中提炼关键洞察。"},
                    {"role": "user", "content": context}
                ],
                extra_body={"enable_thinking": False}
            )
            self.usage_tracker.log_llm_usage(response.usage)
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ 简报生成失败: {e}")
            return "无法生成今日简报，请直接阅读下方详细内容。"

    def fetch_arxiv_papers(self) -> Dict[str, List[ArxivPaper]]:
        """获取 arXiv 论文"""
        print("\n" + "=" * 60)
        print("📚 正在获取 arXiv 论文...")
        print("=" * 60)
        
        papers = self.arxiv_fetcher.fetch_all()
        
        # 过滤最近 7 天的论文
        for category in papers:
            papers[category] = filter_recent_papers(papers[category], days=7)
            
            # AI 摘要生成 (只处理前5篇以节省资源和时间)
            if papers[category]:
                print(f"\n🤖 正在生成 {category} 类别的 AI 摘要...")
                for i, paper in enumerate(papers[category][:5]):
                    print(f"  [{i+1}/{min(len(papers[category]), 5)}] 处理: {paper.title[:30]}...")
                    paper.summary = self.summarize_paper(paper.title, paper.summary)
        
        print(f"✅ 获取完成: {len(papers['llm'])} 篇大模型论文, {len(papers['advertising'])} 篇广告领域论文")
        return papers
    
    def fetch_feeds(self) -> Dict[str, List[FeedItem]]:
        """获取 RSS 订阅"""
        print("\n" + "=" * 60)
        print("rss 正在获取 RSS 订阅...")
        print("=" * 60)
        return self.feed_fetcher.fetch_all()

    def fetch_youtube_videos(self) -> Dict:
        """获取 YouTube 视频"""
        print("\n" + "=" * 60)
        print("🎬 正在获取 YouTube 视频...")
        print("=" * 60)
        
        if self.youtube_fetcher:
            videos = self.youtube_fetcher.fetch_selected_leaders(self.selected_leaders)
            # Log usage
            self.usage_tracker.log_youtube_usage(
                self.youtube_fetcher.request_count,
                self.youtube_fetcher.total_quota_used
            )
            return {"type": "api", "data": videos}
        else:
            recommendations = self.youtube_no_api.get_recommendations(self.selected_leaders)
            return {"type": "recommendations", "data": recommendations}
    
    def fetch_github_data(self) -> Dict:
        """获取 GitHub Issues 和 Trending"""
        print("\n" + "=" * 60)
        print("🐙 正在获取 GitHub 数据...")
        print("=" * 60)
        
        issues = self.github_fetcher.fetch_all_issues(max_per_repo=5)
        issues = self.deduplicator.filter_new('github_issue', issues, lambda x: x.unique_id)
        
        trending = self.github_fetcher.fetch_trending(since='daily', max_results=10)
        trending = self.deduplicator.filter_new('github_trending', trending, lambda x: x.unique_id)
        
        return {"issues": issues, "trending": trending}
    
    def fetch_reddit_data(self) -> List[RedditPost]:
        """获取 Reddit 帖子"""
        print("\n" + "=" * 60)
        print("🔴 正在获取 Reddit 数据...")
        print("=" * 60)
        
        posts = self.reddit_fetcher.fetch_all(max_per_subreddit=15)
        posts = self.deduplicator.filter_new('reddit', posts, lambda x: x.unique_id)
        return posts
    
    def fetch_hn_data(self) -> List[HNStory]:
        """获取 Hacker News 数据"""
        print("\n" + "=" * 60)
        print("🟠 正在获取 Hacker News 数据...")
        print("=" * 60)
        
        stories = self.hn_fetcher.fetch_top_stories(min_score=50, max_results=15, filter_ai=True)
        stories = self.deduplicator.filter_new('hn', stories, lambda x: x.unique_id)
        return stories
    
    def generate_html_content(
        self, 
        briefing: str,
        papers: Dict[str, List[ArxivPaper]], 
        feeds: Dict[str, List[FeedItem]],
        youtube_data: Dict,
        github_data: Dict = None,
        reddit_posts: List = None,
        hn_stories: List = None
    ) -> str:
        """生成 HTML 邮件内容"""
        today = datetime.now().strftime('%Y年%m月%d日')
        
        # Render markdown briefing to simple HTML paragraphs
        briefing_html = "".join([f"<p>{line}</p>" for line in briefing.split('\n') if line.strip()])
        
        # Stats HTML
        stats_html = f'''
        <div class="stats-box">
            <h4 style="margin:0 0 10px 0; color:#4a5568;">⚙️ 系统运行统计</h4>
            <div style="display:flex; justify-content:space-between; font-size:12px; color:#718096;">
                <div>
                    <strong>🤖 AI 模型 (Qwen-72B)</strong><br>
                    调用次数: {self.usage_tracker.llm_calls}<br>
                    Input Tokens: {self.usage_tracker.llm_input_tokens}<br>
                    Output Tokens: {self.usage_tracker.llm_output_tokens}
                </div>
                <div>
                    <strong>🎬 YouTube API</strong><br>
                    API 调用: {self.usage_tracker.youtube_api_calls}<br>
                    Quota 消耗: {self.usage_tracker.youtube_quota} units
                </div>
            </div>
        </div>
        '''

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
        .briefing-box {{
            background: linear-gradient(135deg, #e6fffa 0%, #b2f5ea 100%);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 40px;
            border-left: 5px solid #38b2ac;
        }}
        .briefing-title {{
            font-size: 20px;
            font-weight: bold;
            color: #234e52;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
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
        /* Paper Cards */
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
        .paper-card.ad {{ border-left-color: #48bb78; }}
        .paper-title {{ font-size: 16px; font-weight: 600; margin-bottom: 8px; }}
        .paper-title a {{ color: #2d3748; text-decoration: none; }}
        .paper-title a:hover {{ color: #667eea; }}
        .paper-authors {{ font-size: 13px; color: #718096; margin-bottom: 10px; }}
        .paper-summary {{ font-size: 14px; color: #4a5568; line-height: 1.7; }}
        .paper-meta {{ display: flex; gap: 15px; margin-top: 12px; font-size: 12px; }}
        .paper-tag {{ display: inline-block; padding: 3px 10px; background: #edf2f7; border-radius: 12px; color: #4a5568; }}
        
        /* Feed Cards */
        .feed-list {{ list-style: none; padding: 0; }}
        .feed-item {{
            padding: 15px;
            border-bottom: 1px solid #edf2f7;
            display: flex;
            flex-direction: column;
        }}
        .feed-item:last-child {{ border-bottom: none; }}
        .feed-source {{ 
            font-size: 12px; 
            text-transform: uppercase; 
            color: #718096; 
            font-weight: bold;
            margin-bottom: 4px;
        }}
        .feed-title {{ font-size: 16px; font-weight: 600; margin-bottom: 5px; }}
        .feed-title a {{ color: #2b6cb0; text-decoration: none; }}
        .feed-title a:hover {{ text-decoration: underline; }}
        .feed-date {{ font-size: 12px; color: #a0aec0; }}

        .video-card {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            color: white;
        }}
        .video-title a {{ color: #ff6b6b; text-decoration: none; }}
        
        .footer {{
            margin-top: 50px;
            padding-top: 30px;
            border-top: 2px solid #e2e8f0;
            text-align: center;
            color: #718096;
            font-size: 14px;
        }}
        .stats-box {{
            background: #f1f5f9;
            border-radius: 8px;
            padding: 15px;
            margin-top: 30px;
            border: 1px solid #e2e8f0;
            text-align: left;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 AI 研究周报</h1>
            <div class="date">{today}</div>
        </div>
        
        <!-- AI Daily Briefing -->
        <div class="briefing-box">
            <div class="briefing-title">☕️ 今日 AI 简报</div>
            <div style="color: #2c7a7b; font-size: 15px; line-height: 1.8;">
                {briefing_html}
            </div>
        </div>
        
        <!-- arXiv Papers -->
        <div class="section">
            <div class="section-header">
                <span class="section-icon">📚</span>
                <h2 class="section-title">核心论文 (ArXiv)</h2>
            </div>
            <h3 style="color: #4a5568; margin-top:20px;">🔥 大模型前沿</h3>
            {self._generate_papers_html(papers['llm'], 'llm')}
            
            <h3 style="color: #4a5568; margin-top:30px;">📊 广告与推荐算法</h3>
            {self._generate_papers_html(papers['advertising'], 'ad')}
        </div>
        
        <!-- RSS Feeds -->
        <div class="section">
            <div class="section-header">
                <span class="section-icon">📡</span>
                <h2 class="section-title">业界动态</h2>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 40px;">
                <div>
                    <h3 style="border-bottom: 2px solid #ed8936; padding-bottom: 10px; color: #c05621;">🏢 AI Labs 更新</h3>
                    {self._generate_feeds_html(feeds.get('AI_Labs', []))}
                </div>
                <div>
                    <h3 style="border-bottom: 2px solid #48bb78; padding-bottom: 10px; color: #2f855a;">💰 顶级风投观点</h3>
                    {self._generate_feeds_html(feeds.get('VC_Trends', []))}
                </div>
            </div>
            
            <div style="margin-top: 40px;">
                 <h3 style="border-bottom: 2px solid #4299e1; padding-bottom: 10px; color: #2b6cb0;">📰 科技新闻精选</h3>
                 {self._generate_feeds_html(feeds.get('Tech_News', []) + feeds.get('High_Quality_Filters', []))}
            </div>
        </div>
        
        <!-- YouTube Videos -->
        <div class="section">
            <div class="section-header">
                <span class="section-icon">🎬</span>
                <h2 class="section-title">科技领袖访谈</h2>
            </div>
            {self._generate_youtube_html(youtube_data)}
        </div>
        
        <!-- New Sources: GitHub, Reddit, HN -->
        {self._generate_community_section(github_data, reddit_posts, hn_stories)}
        
        {stats_html}
        
        <div class="footer">
            <p>📅 {today} | Daily Info System</p>
            <p>💡 Stay Hungry, Stay Foolish</p>
        </div>
    </div>
</body>
</html>
'''
        return html
    
    def _generate_papers_html(self, papers: List[ArxivPaper], paper_type: str) -> str:
        """生成论文 HTML"""
        if not papers:
            return '<p style="color: #718096; font-style: italic;">今日无更新</p>'
        
        html_parts = []
        card_class = "paper-card" if paper_type == 'llm' else "paper-card ad"
        
        for paper in papers[:6]:  # Limit per section
            authors_str = ', '.join(paper.authors[:3])
            summary = paper.summary
            
            html_parts.append(f'''
            <div class="{card_class}">
                <div class="paper-title">
                    <a href="{paper.abs_url}" target="_blank">{paper.title}</a>
                </div>
                <div class="paper-authors">👥 {authors_str}</div>
                <div class="paper-summary">{summary}</div>
                <div class="paper-meta">
                    <span class="paper-tag">📅 {paper.published[:10]}</span>
                    <a href="{paper.pdf_url}" class="paper-link" target="_blank">📄 PDF</a>
                </div>
            </div>
            ''')
        return '\n'.join(html_parts)

    def _generate_feeds_html(self, items: List[FeedItem]) -> str:
        """生成 Feed 列表 HTML"""
        if not items:
            return '<p style="color: #cbd5e0;">暂无动态</p>'
        
        html = '<div class="feed-list">'
        for item in items[:8]: # Limit items per list
            html += f'''
            <div class="feed-item">
                <div class="feed-source">{item.source_name}</div>
                <div class="feed-title"><a href="{item.link}" target="_blank">{item.title}</a></div>
                <div class="feed-date">{item.published.strftime('%m-%d')}</div>
            </div>
            '''
        html += '</div>'
        return html

    def _generate_youtube_html(self, youtube_data: Dict) -> str:
        """生成 YouTube HTML (Simplified for brevity)"""
        if youtube_data["type"] == "api":
            return self._generate_youtube_api_html(youtube_data["data"])
        else:
            return self._generate_youtube_recommendations_html(youtube_data["data"])

    def _generate_youtube_api_html(self, videos_by_leader: Dict[str, List[YouTubeVideo]]) -> str:
        html_parts = []
        for leader, videos in videos_by_leader.items():
            if not videos: continue
            html_parts.append(f'<h4 style="margin: 20px 0 10px 0; color: #553c9a;">👤 {leader}</h4>')
            for video in videos[:2]:
                html_parts.append(f'''
                <div class="video-card">
                    <div class="video-title"><a href="{video.watch_url}" target="_blank">🎥 {video.title}</a></div>
                    <div style="font-size: 12px; color: #a0aec0; margin-top:5px;">{video.description[:100]}...</div>
                </div>
                ''')
        return '\n'.join(html_parts) if html_parts else '<p>暂无新视频</p>'

    def _generate_youtube_recommendations_html(self, recommendations: Dict) -> str:
        # Reusing the logic but simplified
        html = '<p>点击下方链接搜索最新视频：</p><div style="display:flex; gap:10px; flex-wrap:wrap;">'
        for leader, url in recommendations["search_links"].items():
            html += f'<a href="{url}" style="padding:5px 15px; background:#e53e3e; color:white; border-radius:15px; text-decoration:none;">{leader}</a>'
        html += '</div>'
        return html
    
    def _generate_community_section(self, github_data: Dict, reddit_posts: List, hn_stories: List) -> str:
        """生成开源社区版块 HTML (使用 AI 筛选)"""
        if not github_data and not reddit_posts and not hn_stories:
            return ''
        
        sections = []
        
        # GitHub Issues
        if github_data and github_data.get('issues'):
            print("  🤖 AI 筛选 GitHub Issues...")
            issues_dicts = [i.to_dict() for i in github_data['issues']]
            issues_html = self.ai_curator.curate(issues_dicts, "GitHub 热门 Issues (llama.cpp/vllm/transformers)", max_items=3)
            sections.append(f'''
            <div style="margin-bottom: 30px;">
                <h3 style="border-bottom: 2px solid #6366f1; padding-bottom: 10px; color: #4338ca;">🐙 开源社区动态</h3>
                {issues_html}
            </div>
            ''')
        
        # GitHub Trending
        if github_data and github_data.get('trending'):
            print("  🤖 AI 筛选 GitHub Trending...")
            trending_dicts = [t.to_dict() for t in github_data['trending']]
            trending_html = self.ai_curator.curate(trending_dicts, "GitHub 每日趋势项目", max_items=3)
            sections.append(f'''
            <div style="margin-bottom: 30px;">
                <h3 style="border-bottom: 2px solid #f59e0b; padding-bottom: 10px; color: #d97706;">🔥 GitHub 趋势项目</h3>
                {trending_html}
            </div>
            ''')
        
        # Reddit
        if reddit_posts:
            print("  🤖 AI 筛选 Reddit 帖子...")
            reddit_dicts = [p.to_dict() for p in reddit_posts]
            reddit_html = self.ai_curator.curate(reddit_dicts, "Reddit r/LocalLLaMA 热议", max_items=3)
            sections.append(f'''
            <div style="margin-bottom: 30px;">
                <h3 style="border-bottom: 2px solid #ef4444; padding-bottom: 10px; color: #dc2626;">🔴 Reddit 热议</h3>
                {reddit_html}
            </div>
            ''')
        
        # Hacker News
        if hn_stories:
            print("  🤖 AI 筛选 Hacker News...")
            hn_dicts = [s.to_dict() for s in hn_stories]
            hn_html = self.ai_curator.curate(hn_dicts, "Hacker News AI 相关热帖", max_items=3)
            sections.append(f'''
            <div style="margin-bottom: 30px;">
                <h3 style="border-bottom: 2px solid #f97316; padding-bottom: 10px; color: #ea580c;">🟠 Hacker News 精选</h3>
                {hn_html}
            </div>
            ''')
        
        # Merge AI curator usage into main tracker
        curator_usage = self.ai_curator.get_usage()
        self.usage_tracker.llm_calls += curator_usage['calls']
        self.usage_tracker.llm_input_tokens += curator_usage['input_tokens']
        self.usage_tracker.llm_output_tokens += curator_usage['output_tokens']
        
        if sections:
            return f'''
            <div class="section">
                <div class="section-header">
                    <span class="section-icon">🌐</span>
                    <h2 class="section-title">社区精选 (AI Curated)</h2>
                </div>
                {''.join(sections)}
            </div>
            '''
        return ''

    def send_email(self, to_email: str, subject: str, content: str, cc_emails: List[str] = []) -> bool:
        """发送邮件 (支持 CC)"""
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.qq.com')
        smtp_port = int(os.getenv('SMTP_PORT', '465'))
        from_email = os.getenv('FROM_EMAIL')
        email_password = os.getenv('EMAIL_PASSWORD')
        
        if not from_email or not email_password:
            print("❌ 错误: 未设置邮件配置环境变量")
            return False
        
        try:
            message = MIMEMultipart('alternative')
            message['From'] = from_email
            message['To'] = to_email
            message['Subject'] = Header(subject, 'utf-8')
            
            if cc_emails:
                message['Cc'] = ', '.join(cc_emails)
            
            message.attach(MIMEText(content, 'html', 'utf-8'))
            
            print(f"\n📧 正在连接邮件服务器...")
            if smtp_port == 465:
                import ssl
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context)
            else:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
            
            server.login(from_email, email_password)
            
            # Recipients = To + Cc
            recipients = [to_email] + cc_emails
            
            print(f"🚀 正在发送邮件给: {recipients}...")
            server.sendmail(from_email, recipients, message.as_string())
            server.quit()
            
            print(f"✅ 邮件发送成功！")
            return True
            
        except Exception as e:
            print(f"❌ 发送邮件失败: {e}")
            return False
    

    def save_report_to_file(self, html_content: str):
        """保存日报到本地 archives 文件夹"""
        try:
            # 确保目录存在
            archive_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'archives')
            if not os.path.exists(archive_dir):
                os.makedirs(archive_dir)
            
            # 生成文件名
            date_str = datetime.now().strftime('%Y-%m-%d')
            filename = f"daily_report_{date_str}.html"
            filepath = os.path.join(archive_dir, filename)
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            print(f"✅ 日报已保存到: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ 保存日报文件失败: {e}")
            return None

    def run(self, to_email: Optional[str] = None):
        """运行主流程"""
        print("\n" + "=" * 60)
        print("🚀 启动 AI 研究与资讯抓取任务")
        print("=" * 60)
        
        if to_email is None:
            to_email = os.getenv('TO_EMAIL', 'huzhe06@gmail.com')
        
        # 定义抄送人
        cc_list = ['zhuhuiqing13@163.com']
        extra_cc = os.getenv('CC_EMAIL')
        if extra_cc:
            cc_list.extend([email.strip() for email in extra_cc.split(',')])

        # 1. Fetch all data sources
        papers = self.fetch_arxiv_papers()
        feeds = self.fetch_feeds()
        youtube_data = self.fetch_youtube_videos()
        github_data = self.fetch_github_data()
        reddit_posts = self.fetch_reddit_data()
        hn_stories = self.fetch_hn_data()
        
        # 2. Generate Briefing
        briefing = self.generate_daily_briefing(papers, feeds, youtube_data)
        
        # 3. Generate Email Content
        print("\n🎨 正在生成 HTML 邮件...")
        html_content = self.generate_html_content(
            briefing, papers, feeds, youtube_data,
            github_data=github_data,
            reddit_posts=reddit_posts,
            hn_stories=hn_stories
        )
        
        # 3.1 Save report and deduplication state
        self.save_report_to_file(html_content)
        self.deduplicator.save()
        
        # 4. Send Email
        today = datetime.now().strftime('%m月%d日')
        subject = f"日报 | AI 每日简报 & 研究动态 ({today})"
        
        success = self.send_email(to_email, subject, html_content, cc_emails=cc_list)
        return success


if __name__ == "__main__":
    sender = ResearchDigestSender()
    sender.run()

