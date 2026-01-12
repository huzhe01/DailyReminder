#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reddit 数据抓取模块 - 获取 r/LocalLLaMA 等子版块的热门帖子
"""

import urllib.request
import json
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RedditPost:
    """Reddit 帖子数据结构"""
    title: str
    url: str
    reddit_url: str
    subreddit: str
    author: str
    score: int
    num_comments: int
    created_utc: float
    selftext: str
    
    @property
    def unique_id(self) -> str:
        # 从 reddit_url 提取 post id
        parts = self.reddit_url.rstrip('/').split('/')
        for i, p in enumerate(parts):
            if p == 'comments' and i + 1 < len(parts):
                return parts[i + 1]
        return self.reddit_url
    
    @property
    def created_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.created_utc)
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "url": self.reddit_url,
            "description": f"⬆️ {self.score} | 💬 {self.num_comments} | by u/{self.author}"
        }


class RedditFetcher:
    """Reddit 数据抓取器"""
    
    BASE_URL = "https://www.reddit.com"
    
    # 目标子版块
    TARGET_SUBREDDITS = [
        "LocalLLaMA",
    ]
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'DailyReminder-Bot/1.0 (AI Research Digest)'
        }
    
    def _make_request(self, url: str) -> dict:
        """发送请求"""
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            print(f"Reddit API 错误: {e.code}")
            return {}
        except Exception as e:
            print(f"请求失败: {e}")
            return {}
    
    def fetch_subreddit(
        self, 
        subreddit: str, 
        sort: str = 'hot', 
        limit: int = 15,
        min_score: int = 10
    ) -> List[RedditPost]:
        """
        获取子版块帖子
        
        Args:
            subreddit: 子版块名称 (不含 r/)
            sort: 排序方式 (hot, new, top, rising)
            limit: 获取数量
            min_score: 最低分数过滤
        """
        url = f"{self.BASE_URL}/r/{subreddit}/{sort}.json?limit={limit}"
        
        data = self._make_request(url)
        if not data or 'data' not in data:
            return []
        
        posts = []
        for child in data['data'].get('children', []):
            item = child.get('data', {})
            
            # 跳过置顶帖和低分帖
            if item.get('stickied', False):
                continue
            if item.get('score', 0) < min_score:
                continue
            
            # 获取链接（如果是 self post，用 reddit 链接）
            post_url = item.get('url', '')
            if item.get('is_self', False):
                post_url = f"{self.BASE_URL}{item.get('permalink', '')}"
            
            post = RedditPost(
                title=item.get('title', ''),
                url=post_url,
                reddit_url=f"{self.BASE_URL}{item.get('permalink', '')}",
                subreddit=subreddit,
                author=item.get('author', 'unknown'),
                score=item.get('score', 0),
                num_comments=item.get('num_comments', 0),
                created_utc=item.get('created_utc', 0),
                selftext=item.get('selftext', '')[:500]  # 限制长度
            )
            posts.append(post)
        
        return posts
    
    def fetch_all(self, max_per_subreddit: int = 10) -> List[RedditPost]:
        """获取所有目标子版块的帖子"""
        all_posts = []
        for subreddit in self.TARGET_SUBREDDITS:
            print(f"  🔴 获取 r/{subreddit}...")
            posts = self.fetch_subreddit(subreddit, limit=max_per_subreddit)
            all_posts.extend(posts)
            print(f"     找到 {len(posts)} 条")
        return all_posts


if __name__ == "__main__":
    fetcher = RedditFetcher()
    posts = fetcher.fetch_all(max_per_subreddit=5)
    
    print("\n=== Reddit Posts ===")
    for post in posts[:5]:
        print(f"- [{post.subreddit}] {post.title[:60]}... (⬆️ {post.score}, 💬 {post.num_comments})")
