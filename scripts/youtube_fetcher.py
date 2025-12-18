#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 视频获取模块
获取 Elon Musk, Jensen Huang 等科技领袖的最新访谈视频
"""

import os
import json
import re
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional, Dict


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
    duration_seconds: Optional[int] = None
    view_count: Optional[str] = None
    
    @property
    def watch_url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}"
    
    @property
    def embed_url(self) -> str:
        return f"https://www.youtube.com/embed/{self.video_id}"


class YouTubeFetcher:
    """YouTube 视频抓取器"""
    
    BASE_URL = "https://www.googleapis.com/youtube/v3"
    
    # 配额成本常量
    QUOTA_COST_SEARCH = 100
    QUOTA_COST_VIDEOS = 1
    
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
        self.total_quota_used = 0
        self.request_count = 0
        self.request_log = []
    
    def _make_request(self, endpoint: str, params: dict) -> dict:
        """发送 API 请求"""
        if not self.api_key:
            raise ValueError("需要设置 YOUTUBE_API_KEY 环境变量")
        
        # 记录配额消耗
        quota_cost = 0
        if 'search' in endpoint:
            quota_cost = self.QUOTA_COST_SEARCH
        elif 'videos' in endpoint:
            quota_cost = self.QUOTA_COST_VIDEOS
            
        self.total_quota_used += quota_cost
        self.request_count += 1
        self.request_log.append({
            'endpoint': endpoint,
            'cost': quota_cost,
            'time': datetime.now().isoformat()
        })
        
        params['key'] = self.api_key
        url = f"{self.BASE_URL}/{endpoint}?{urllib.parse.urlencode(params)}"
        
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"YouTube API 错误: {e.code} - {error_body}")
            raise

    def _parse_duration(self, duration_str: str) -> int:
        """解析 ISO 8601 持续时间格式 (PT1H30M) 为秒数"""
        if not duration_str:
            return 0
            
        pattern = re.compile(r'P(?:(?P<days>\d+)D)?T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?')
        match = pattern.match(duration_str)
        if not match:
            return 0
            
        parts = match.groupdict()
        time_params = {}
        for name, param in parts.items():
            if param:
                time_params[name] = int(param)
                
        return int(timedelta(**time_params).total_seconds())
    
    def get_video_details(self, video_ids: List[str]) -> Dict[str, dict]:
        """获取视频详细信息（时长、观看次数等）"""
        if not video_ids:
            return {}
            
        # 每次最多请求 50 个 ID
        results = {}
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i+50]
            params = {
                'part': 'contentDetails,statistics,snippet',
                'id': ','.join(batch_ids)
            }
            
            data = self._make_request('videos', params)
            for item in data.get('items', []):
                vid = item.get('id')
                results[vid] = item
                
        return results

    def search_videos(self, query: str, days_ago: int = 30, min_duration_minutes: int = 30) -> List[YouTubeVideo]:
        """搜索视频"""
        # 计算日期范围
        published_after = (datetime.now() - timedelta(days=days_ago)).isoformat() + 'Z'
        
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'order': 'date',
            'maxResults': self.max_results * 2,  # 获取更多以备过滤
            'publishedAfter': published_after,
            'relevanceLanguage': 'en',
            'videoDuration': 'long',  # 过滤 > 20分钟的视频
        }
        
        try:
            data = self._make_request('search', params)
            video_snippets = {}
            video_ids = []
            
            for item in data.get('items', []):
                video_id = item.get('id', {}).get('videoId')
                if not video_id:
                    continue
                video_ids.append(video_id)
                video_snippets[video_id] = item.get('snippet', {})
            
            # 获取详细信息以检查具体时长
            video_details = self.get_video_details(video_ids)
            
            final_videos = []
            min_duration_seconds = min_duration_minutes * 60
            
            for vid in video_ids:
                if vid not in video_details:
                    continue
                    
                details = video_details[vid]
                content_details = details.get('contentDetails', {})
                statistics = details.get('statistics', {})
                snippet = video_snippets.get(vid, details.get('snippet', {}))
                
                duration_str = content_details.get('duration', '')
                duration_seconds = self._parse_duration(duration_str)
                
                if duration_seconds < min_duration_seconds:
                    continue
                
                # 获取缩略图 URL
                thumbnails = snippet.get('thumbnails', {})
                thumbnail_url = thumbnails.get('high', thumbnails.get('default', {})).get('url', '')
                
                video = YouTubeVideo(
                    video_id=vid,
                    title=snippet.get('title', ''),
                    description=snippet.get('description', ''),
                    channel_title=snippet.get('channelTitle', ''),
                    published_at=snippet.get('publishedAt', ''),
                    thumbnail_url=thumbnail_url,
                    duration=duration_str,
                    duration_seconds=duration_seconds,
                    view_count=statistics.get('viewCount')
                )
                final_videos.append(video)
                
                if len(final_videos) >= self.max_results:
                    break
            
            return final_videos
            
        except Exception as e:
            print(f"搜索视频时出错: {e}")
            return []
    
    def fetch_leader_videos(self, leader_name: str) -> List[YouTubeVideo]:
        """获取特定科技领袖的视频"""
        keywords = self.TECH_LEADERS.get(leader_name, [f"{leader_name} interview"])
        
        all_videos = []
        seen_ids = set()
        
        for keyword in keywords[:3]:  # 限制查询次数
            videos = self.search_videos(keyword, days_ago=60, min_duration_minutes=30)
            for video in videos:
                if video.video_id not in seen_ids:
                    all_videos.append(video)
                    seen_ids.add(video.video_id)
        
        return all_videos
    
    def fetch_recommended_videos(self, max_results: int = 10) -> List[YouTubeVideo]:
        """获取热门科技视频（模拟主页推荐）"""
        # 使用 Science & Technology (category 28) 的热门视频
        params = {
            'part': 'snippet,contentDetails,statistics',
            'chart': 'mostPopular',
            'regionCode': 'US',
            'videoCategoryId': '28',  # Science & Technology
            'maxResults': max_results * 3, # 多获取一些以便过滤时长
        }
        
        try:
            print(f"正在获取热门科技视频推荐...")
            data = self._make_request('videos', params)
            videos = []
            min_duration_seconds = 30 * 60
            
            for item in data.get('items', []):
                snippet = item.get('snippet', {})
                content_details = item.get('contentDetails', {})
                statistics = item.get('statistics', {})
                video_id = item.get('id')
                
                duration_str = content_details.get('duration', '')
                duration_seconds = self._parse_duration(duration_str)
                
                # 同样应用 30 分钟筛选
                if duration_seconds < min_duration_seconds:
                    continue
                
                thumbnails = snippet.get('thumbnails', {})
                thumbnail_url = thumbnails.get('high', thumbnails.get('default', {})).get('url', '')
                
                video = YouTubeVideo(
                    video_id=video_id,
                    title=snippet.get('title', ''),
                    description=snippet.get('description', ''),
                    channel_title=snippet.get('channelTitle', ''),
                    published_at=snippet.get('publishedAt', ''),
                    thumbnail_url=thumbnail_url,
                    duration=duration_str,
                    duration_seconds=duration_seconds,
                    view_count=statistics.get('viewCount')
                )
                videos.append(video)
                
                if len(videos) >= max_results:
                    break
            
            return videos
            
        except Exception as e:
            print(f"获取推荐视频时出错: {e}")
            return []

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
    
    def print_quota_usage(self):
        """打印配额使用情况"""
        print("\n📊 YouTube API 配额使用统计:")
        print(f"  总请求次数: {self.request_count}")
        print(f"  总配额消耗: {self.total_quota_used} units")
        print("  (每日免费配额通常为 10,000 units)")
        print("\n  请求明细:")
        for log in self.request_log:
            print(f"  - [{log['time']}] {log['endpoint']}: {log['cost']} units")


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
        "Elon Musk": "https://www.youtube.com/results?search_query=elon+musk+interview+2025&sp=CAI%253D",
        "Jensen Huang": "https://www.youtube.com/results?search_query=jensen+huang+interview+2025&sp=CAI%253D",
        "Sam Altman": "https://www.youtube.com/results?search_query=sam+altman+interview+2025&sp=CAI%253D",
        "Satya Nadella": "https://www.youtube.com/results?search_query=satya+nadella+interview+2025&sp=CAI%253D",
        "Sundar Pichai": "https://www.youtube.com/results?search_query=sundar+pichai+interview+2025&sp=CAI%253D",
        "Mark Zuckerberg": "https://www.youtube.com/results?search_query=mark+zuckerberg+interview+2025&sp=CAI%253D",
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
            print(f"\n🎬 {leader} 的视频 (>30min):")
            for video in leader_videos[:3]:
                print(f"  - {video.title}")
                print(f"    时长: {video.duration}")
                print(f"    {video.watch_url}")
        
        # 获取推荐视频
        print("\n🌟 热门科技推荐 (>30min):")
        recs = fetcher.fetch_recommended_videos(max_results=5)
        for video in recs:
            print(f"  - {video.title}")
            print(f"    时长: {video.duration}")
            print(f"    {video.watch_url}")
            
        fetcher.print_quota_usage()
        
    else:
        print("未设置 YOUTUBE_API_KEY，使用推荐列表模式")
        no_api = YouTubeFetcherNoAPI()
        recommendations = no_api.get_recommendations()
        
        print("\n📺 推荐频道:")
        for name, info in recommendations["channels"].items():
            print(f"  - {name}: {info['url']}")
        
        print("\n🔍 搜索链接 (建议手动添加 >20min 过滤):")
        for leader, url in recommendations["search_links"].items():
            print(f"  - {leader}: {url}")
