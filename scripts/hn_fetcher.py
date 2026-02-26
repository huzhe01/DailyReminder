#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hacker News 数据抓取模块 - 获取热门 AI/LLM 相关帖子
"""

import urllib.request
import json
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class HNStory:
    """Hacker News 帖子数据结构"""
    id: int
    title: str
    url: str
    hn_url: str
    author: str
    score: int
    num_comments: int
    created_at: int
    
    @property
    def unique_id(self) -> str:
        return str(self.id)
    
    @property
    def created_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.created_at)
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "url": self.hn_url,  # 使用 HN 讨论页链接
            "description": f"⬆️ {self.score} | 💬 {self.num_comments} | by {self.author}"
        }


class HNFetcher:
    """Hacker News 数据抓取器"""
    
    API_BASE = "https://hacker-news.firebaseio.com/v0"
    HN_BASE = "https://news.ycombinator.com"
    
    # AI/LLM 相关关键词 (用于过滤)
    AI_KEYWORDS = [
        'llm', 'gpt', 'claude', 'gemini', 'llama', 'mistral',
        'openai', 'anthropic', 'ai', 'ml', 'machine learning',
        'transformer', 'neural', 'deep learning', 'inference',
        'fine-tun', 'rlhf', 'training', 'model', 'embedding',
        'vector', 'rag', 'agent', 'langchain', 'huggingface'
    ]
    
    def __init__(self):
        pass
    
    def _make_request(self, url: str) -> any:
        """发送请求"""
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"HN API 请求失败: {e}")
            return None
    
    def _is_ai_related(self, title: str) -> bool:
        """检查标题是否与 AI/LLM 相关"""
        title_lower = title.lower()
        return any(kw in title_lower for kw in self.AI_KEYWORDS)
    
    def fetch_top_stories(
        self, 
        min_score: int = 50, 
        max_results: int = 15,
        filter_ai: bool = True
    ) -> List[HNStory]:
        """
        获取热门故事
        
        Args:
            min_score: 最低分数
            max_results: 最大返回数量
            filter_ai: 是否只获取 AI 相关内容
        """
        # 获取 top stories IDs
        top_ids = self._make_request(f"{self.API_BASE}/topstories.json")
        if not top_ids:
            return []
        
        stories = []
        checked = 0
        
        for story_id in top_ids:
            if len(stories) >= max_results:
                break
            if checked >= 100:  # 最多检查 100 条
                break
            
            checked += 1
            
            # 获取故事详情
            item = self._make_request(f"{self.API_BASE}/item/{story_id}.json")
            if not item or item.get('type') != 'story':
                continue
            
            score = item.get('score', 0)
            if score < min_score:
                continue
            
            title = item.get('title', '')
            
            # AI 过滤
            if filter_ai and not self._is_ai_related(title):
                continue
            
            story = HNStory(
                id=item.get('id', 0),
                title=title,
                url=item.get('url', ''),
                hn_url=f"{self.HN_BASE}/item?id={item.get('id', 0)}",
                author=item.get('by', 'unknown'),
                score=score,
                num_comments=item.get('descendants', 0),
                created_at=item.get('time', 0)
            )
            stories.append(story)
        
        print(f"🟠 HN: 检查了 {checked} 条，找到 {len(stories)} 条 AI 相关")
        return stories
    
    def fetch_best_stories(self, min_score: int = 100, max_results: int = 10) -> List[HNStory]:
        """获取 best stories (更高质量)"""
        best_ids = self._make_request(f"{self.API_BASE}/beststories.json")
        if not best_ids:
            return []
        
        stories = []
        for story_id in best_ids[:50]:
            if len(stories) >= max_results:
                break
            
            item = self._make_request(f"{self.API_BASE}/item/{story_id}.json")
            if not item or item.get('type') != 'story':
                continue
            
            if item.get('score', 0) < min_score:
                continue
            
            story = HNStory(
                id=item.get('id', 0),
                title=item.get('title', ''),
                url=item.get('url', ''),
                hn_url=f"{self.HN_BASE}/item?id={item.get('id', 0)}",
                author=item.get('by', 'unknown'),
                score=item.get('score', 0),
                num_comments=item.get('descendants', 0),
                created_at=item.get('time', 0)
            )
            stories.append(story)
        
        return stories


if __name__ == "__main__":
    fetcher = HNFetcher()
    
    print("=== Hacker News Top Stories (AI related) ===")
    stories = fetcher.fetch_top_stories(min_score=50, max_results=10, filter_ai=True)
    
    for story in stories:
        print(f"- {story.title[:60]}... (⬆️ {story.score}, 💬 {story.num_comments})")
