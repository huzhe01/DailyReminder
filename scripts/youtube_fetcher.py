#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 视频获取模块
获取 Elon Musk, Jensen Huang 等科技领袖的最新访谈视频
"""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class YouTubeVideo:
    """YouTube 视频数据结构"""
    video_id: str
    title: str
    description: str
    channel_title: str
    published_at: str
    thumbnail_url: str
    duration: Optional[str] = None
    view_count: Optional[int] = None
    
    @property
    def watch_url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}"
    
    @property
    def embed_url(self) -> str:
        return f"https://www.youtube.com/embed/{self.video_id}"


class YouTubeFetcher:
    """YouTube 视频抓取器"""
    
    BASE_URL = "https://www.googleapis.com/youtube/v3"
    
    # 科技领袖搜索关键词
    TECH_LEADERS = {
        "Elon Musk": [
            "Elon Musk interview 2024",
            "Elon Musk talk",
            "Elon Musk podcast",
            "Elon Musk AI",
            "Elon Musk Tesla",
            "Elon Musk SpaceX",
            "Elon Musk xAI",
        ],
        "Jensen Huang": [
            "Jensen Huang interview 2024",
            "Jensen Huang keynote",
            "Jensen Huang NVIDIA",
            "Jensen Huang AI",
            "Jensen Huang talk",
            "Jensen Huang GTC",
        ],
        "Sam Altman": [
            "Sam Altman interview 2024",
            "Sam Altman OpenAI",
            "Sam Altman talk",
            "Sam Altman podcast",
            "Sam Altman AI",
        ],
        "Satya Nadella": [
            "Satya Nadella interview 2024",
            "Satya Nadella Microsoft",
            "Satya Nadella AI",
            "Satya Nadella talk",
        ],
        "Sundar Pichai": [
            "Sundar Pichai interview 2024",
            "Sundar Pichai Google",
            "Sundar Pichai AI",
            "Sundar Pichai Gemini",
        ],
        "Mark Zuckerberg": [
            "Mark Zuckerberg interview 2024",
            "Mark Zuckerberg Meta",
            "Mark Zuckerberg AI",
            "Mark Zuckerberg Llama",
        ],
    }
    
    # 知名科技访谈频道
    TECH_CHANNELS = [
        "Lex Fridman",
        "All-In Podcast",
        "CNBC",
        "Bloomberg Technology",
        "TED",
        "Y Combinator",
    ]
    
    def __init__(self, api_key: Optional[str] = None, max_results: int = 10):
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        self.max_results = max_results
    
    def _make_request(self, endpoint: str, params: dict) -> dict:
        """发送 API 请求"""
        if not self.api_key:
            raise ValueError("需要设置 YOUTUBE_API_KEY 环境变量")
        
        params['key'] = self.api_key
        url = f"{self.BASE_URL}/{endpoint}?{urllib.parse.urlencode(params)}"
        
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"YouTube API 错误: {e.code} - {error_body}")
            raise
    
    def search_videos(self, query: str, days_ago: int = 30) -> List[YouTubeVideo]:
        """搜索视频"""
        # 计算日期范围
        published_after = (datetime.now() - timedelta(days=days_ago)).isoformat() + 'Z'
        
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'order': 'date',
            'maxResults': self.max_results,
            'publishedAfter': published_after,
            'relevanceLanguage': 'en',
            'videoDuration': 'medium',  # 4-20分钟的视频
        }
        
        try:
            data = self._make_request('search', params)
            videos = []
            
            for item in data.get('items', []):
                snippet = item.get('snippet', {})
                video_id = item.get('id', {}).get('videoId')
                
                if not video_id:
                    continue
                
                # 获取缩略图 URL
                thumbnails = snippet.get('thumbnails', {})
                thumbnail_url = thumbnails.get('high', thumbnails.get('default', {})).get('url', '')
                
                video = YouTubeVideo(
                    video_id=video_id,
                    title=snippet.get('title', ''),
                    description=snippet.get('description', ''),
                    channel_title=snippet.get('channelTitle', ''),
                    published_at=snippet.get('publishedAt', ''),
                    thumbnail_url=thumbnail_url,
                )
                videos.append(video)
            
            return videos
            
        except Exception as e:
            print(f"搜索视频时出错: {e}")
            return []
    
    def fetch_leader_videos(self, leader_name: str) -> List[YouTubeVideo]:
        """获取特定科技领袖的视频"""
        keywords = self.TECH_LEADERS.get(leader_name, [f"{leader_name} interview"])
        
        all_videos = []
        seen_ids = set()
        
        for keyword in keywords[:3]:  # 限制查询次数
            videos = self.search_videos(keyword, days_ago=60)
            for video in videos:
                if video.video_id not in seen_ids:
                    all_videos.append(video)
                    seen_ids.add(video.video_id)
        
        return all_videos
    
    def fetch_all_leaders(self) -> dict:
        """获取所有科技领袖的视频"""
        result = {}
        
        for leader_name in self.TECH_LEADERS.keys():
            print(f"正在获取 {leader_name} 的视频...")
            result[leader_name] = self.fetch_leader_videos(leader_name)
            print(f"  找到 {len(result[leader_name])} 个视频")
        
        return result
    
    def fetch_selected_leaders(self, leaders: List[str] = None) -> dict:
        """获取选定科技领袖的视频"""
        if leaders is None:
            leaders = ["Elon Musk", "Jensen Huang", "Sam Altman"]
        
        result = {}
        
        for leader_name in leaders:
            if leader_name in self.TECH_LEADERS:
                print(f"正在获取 {leader_name} 的视频...")
                result[leader_name] = self.fetch_leader_videos(leader_name)
                print(f"  找到 {len(result[leader_name])} 个视频")
        
        return result


class YouTubeFetcherNoAPI:
    """
    无 API 的 YouTube 视频推荐（使用预设列表）
    当没有 API 密钥时使用
    """
    
    # 预设的高质量科技访谈频道和播放列表
    RECOMMENDED_CHANNELS = {
        "Lex Fridman Podcast": {
            "url": "https://www.youtube.com/@lexfridman",
            "description": "深度科技访谈，经常采访 AI 领域专家",
            "leaders": ["Elon Musk", "Sam Altman", "Mark Zuckerberg", "Jensen Huang"],
        },
        "All-In Podcast": {
            "url": "https://www.youtube.com/@alaboringpodcast",
            "description": "科技、商业、政治话题讨论",
            "leaders": ["Elon Musk", "David Sacks", "Chamath Palihapitiya"],
        },
        "Bloomberg Technology": {
            "url": "https://www.youtube.com/@BloombergTechnology",
            "description": "科技新闻和CEO访谈",
            "leaders": ["Jensen Huang", "Satya Nadella", "Sundar Pichai"],
        },
        "NVIDIA": {
            "url": "https://www.youtube.com/@NVIDIA",
            "description": "NVIDIA 官方频道，Jensen Huang 主题演讲",
            "leaders": ["Jensen Huang"],
        },
        "TED": {
            "url": "https://www.youtube.com/@TED",
            "description": "TED 演讲",
            "leaders": ["Various Tech Leaders"],
        },
        "Y Combinator": {
            "url": "https://www.youtube.com/@ycombinator",
            "description": "创业和科技访谈",
            "leaders": ["Sam Altman", "Various Founders"],
        },
    }
    
    # 推荐的搜索链接
    SEARCH_LINKS = {
        "Elon Musk": "https://www.youtube.com/results?search_query=elon+musk+interview+2024&sp=CAI%253D",
        "Jensen Huang": "https://www.youtube.com/results?search_query=jensen+huang+interview+2024&sp=CAI%253D",
        "Sam Altman": "https://www.youtube.com/results?search_query=sam+altman+interview+2024&sp=CAI%253D",
        "Satya Nadella": "https://www.youtube.com/results?search_query=satya+nadella+interview+2024&sp=CAI%253D",
        "Sundar Pichai": "https://www.youtube.com/results?search_query=sundar+pichai+interview+2024&sp=CAI%253D",
        "Mark Zuckerberg": "https://www.youtube.com/results?search_query=mark+zuckerberg+interview+2024&sp=CAI%253D",
    }
    
    def get_recommendations(self, leaders: List[str] = None) -> dict:
        """获取推荐内容"""
        if leaders is None:
            leaders = ["Elon Musk", "Jensen Huang", "Sam Altman"]
        
        return {
            "channels": self.RECOMMENDED_CHANNELS,
            "search_links": {k: v for k, v in self.SEARCH_LINKS.items() if k in leaders},
            "leaders": leaders,
        }


def get_youtube_fetcher(api_key: Optional[str] = None) -> YouTubeFetcher:
    """获取 YouTube 抓取器实例"""
    key = api_key or os.getenv('YOUTUBE_API_KEY')
    if key:
        return YouTubeFetcher(api_key=key)
    else:
        print("⚠️ 未设置 YOUTUBE_API_KEY，将使用推荐列表模式")
        return None


if __name__ == "__main__":
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if api_key:
        fetcher = YouTubeFetcher(api_key=api_key, max_results=5)
        videos = fetcher.fetch_selected_leaders(["Elon Musk", "Jensen Huang"])
        
        for leader, leader_videos in videos.items():
            print(f"\n🎬 {leader} 的视频:")
            for video in leader_videos[:3]:
                print(f"  - {video.title}")
                print(f"    {video.watch_url}")
    else:
        print("未设置 YOUTUBE_API_KEY，使用推荐列表模式")
        no_api = YouTubeFetcherNoAPI()
        recommendations = no_api.get_recommendations()
        
        print("\n📺 推荐频道:")
        for name, info in recommendations["channels"].items():
            print(f"  - {name}: {info['url']}")
        
        print("\n🔍 搜索链接:")
        for leader, url in recommendations["search_links"].items():
            print(f"  - {leader}: {url}")
