#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 数据抓取模块 - 获取 Issues 和 Trending 项目
"""

import urllib.request
import urllib.parse
import json
import re
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional, Dict


@dataclass
class GitHubIssue:
    """GitHub Issue 数据结构"""
    title: str
    url: str
    repo_name: str
    issue_number: int
    comments_count: int
    created_at: str
    author: str
    labels: List[str]
    
    @property
    def unique_id(self) -> str:
        return f"{self.repo_name}#{self.issue_number}"
    
    def to_dict(self) -> dict:
        return {
            "title": f"[{self.repo_name}] {self.title}",
            "url": self.url,
            "description": f"💬 {self.comments_count} comments | by @{self.author}",
            "labels": self.labels
        }


@dataclass
class TrendingRepo:
    """GitHub Trending 仓库数据结构"""
    name: str
    url: str
    description: str
    language: str
    stars: int
    stars_today: int
    forks: int
    
    @property
    def unique_id(self) -> str:
        return self.name
    
    def to_dict(self) -> dict:
        return {
            "title": self.name,
            "url": self.url,
            "description": f"{self.description} | ⭐ {self.stars} (+{self.stars_today} today) | {self.language}"
        }


class GitHubFetcher:
    """GitHub 数据抓取器"""
    
    API_BASE = "https://api.github.com"
    
    # 关注的仓库
    TARGET_REPOS = [
        "ggerganov/llama.cpp",
        "vllm-project/vllm",
        "huggingface/transformers",
    ]
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'DailyReminder-Bot'
        }
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
    
    def _make_request(self, url: str) -> dict:
        """发送 API 请求"""
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            print(f"GitHub API 错误: {e.code}")
            return {}
        except Exception as e:
            print(f"请求失败: {e}")
            return {}
    
    def fetch_issues(self, repo: str, max_results: int = 10, days: int = 7) -> List[GitHubIssue]:
        """
        获取仓库的热门 Issues
        
        Args:
            repo: 仓库名 (owner/repo)
            max_results: 最大返回数量
            days: 获取最近多少天的 issue
        """
        since = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        url = f"{self.API_BASE}/repos/{repo}/issues"
        params = {
            'state': 'open',
            'sort': 'comments',
            'direction': 'desc',
            'per_page': max_results,
            'since': since
        }
        url = f"{url}?{urllib.parse.urlencode(params)}"
        
        data = self._make_request(url)
        if not data:
            return []
        
        issues = []
        for item in data:
            # 跳过 PR (在 issues API 中会包含 PR)
            if 'pull_request' in item:
                continue
            
            issue = GitHubIssue(
                title=item.get('title', ''),
                url=item.get('html_url', ''),
                repo_name=repo.split('/')[-1],
                issue_number=item.get('number', 0),
                comments_count=item.get('comments', 0),
                created_at=item.get('created_at', ''),
                author=item.get('user', {}).get('login', 'unknown'),
                labels=[l.get('name', '') for l in item.get('labels', [])]
            )
            issues.append(issue)
        
        return issues
    
    def fetch_all_issues(self, max_per_repo: int = 5) -> List[GitHubIssue]:
        """获取所有目标仓库的 Issues"""
        all_issues = []
        for repo in self.TARGET_REPOS:
            print(f"  📂 获取 {repo} 的 Issues...")
            issues = self.fetch_issues(repo, max_results=max_per_repo)
            all_issues.extend(issues)
            print(f"     找到 {len(issues)} 条")
        return all_issues
    
    def fetch_trending(self, since: str = 'daily', language: str = '', max_results: int = 10) -> List[TrendingRepo]:
        """
        获取 GitHub Trending 仓库
        
        使用第三方 API (GitHub 官方没有 Trending API)
        """
        # 使用 GitHub Trending RSS 或第三方 API
        # 这里使用一个简单的方法：抓取 GitHub Trending 页面的 RSS
        
        url = f"https://api.gitterapp.com/repositories?since={since}"
        if language:
            url += f"&language={language}"
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'DailyReminder-Bot'})
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"获取 Trending 失败: {e}")
            # 尝试备用方案
            return self._fetch_trending_fallback(since, language, max_results)
        
        repos = []
        for item in data[:max_results]:
            repo = TrendingRepo(
                name=f"{item.get('author', '')}/{item.get('name', '')}",
                url=item.get('url', ''),
                description=item.get('description', '') or '',
                language=item.get('language', '') or 'Unknown',
                stars=item.get('stars', 0),
                stars_today=item.get('currentPeriodStars', 0),
                forks=item.get('forks', 0)
            )
            repos.append(repo)
        
        return repos
    
    def _fetch_trending_fallback(self, since: str, language: str, max_results: int) -> List[TrendingRepo]:
        """备用方案：使用 GitHub Search API 模拟 Trending"""
        # 搜索最近创建且 star 增长快的仓库
        created_after = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        query = f"created:>{created_after} stars:>100"
        if language:
            query += f" language:{language}"
        
        url = f"{self.API_BASE}/search/repositories"
        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': max_results
        }
        url = f"{url}?{urllib.parse.urlencode(params)}"
        
        data = self._make_request(url)
        if not data or 'items' not in data:
            return []
        
        repos = []
        for item in data['items']:
            repo = TrendingRepo(
                name=item.get('full_name', ''),
                url=item.get('html_url', ''),
                description=item.get('description', '') or '',
                language=item.get('language', '') or 'Unknown',
                stars=item.get('stargazers_count', 0),
                stars_today=0,  # Search API 不提供今日 star 数
                forks=item.get('forks_count', 0)
            )
            repos.append(repo)
        
        return repos


# 需要在文件开头导入 os
import os


if __name__ == "__main__":
    fetcher = GitHubFetcher()
    
    print("=== GitHub Issues ===")
    issues = fetcher.fetch_all_issues(max_per_repo=3)
    for issue in issues[:5]:
        print(f"- [{issue.repo_name}] {issue.title} ({issue.comments_count} comments)")
    
    print("\n=== GitHub Trending ===")
    trending = fetcher.fetch_trending(since='daily', max_results=5)
    for repo in trending:
        print(f"- {repo.name}: ⭐ {repo.stars} (+{repo.stars_today})")
