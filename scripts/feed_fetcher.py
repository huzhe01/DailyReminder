#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSS/Atom Feed Fetcher for Daily Reminder
Fetches and parses feeds from various AI labs, VCs, and tech news sources.
"""

import feedparser
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time
import socket

# Set timeout for socket operations
socket.setdefaulttimeout(15)

# ==========================================
# 🔧 Feed Configuration (Easily Editable)
# ==========================================
FEEDS_CONFIG = {
    "AI_Labs": [
        {"name": "OpenAI", "url": "https://openai.com/news/rss.xml"},
        {"name": "Anthropic", "url": "https://www.anthropic.com/news/feed"},
        {"name": "Google Research", "url": "http://blog.research.google/feeds/posts/default"},
        {"name": "Google The Keyword", "url": "https://blog.google/rss"},
        {"name": "Meta AI", "url": "https://ai.meta.com/blog/rss.xml"},
        {"name": "Meta Engineering", "url": "https://engineering.fb.com/feed/"},
    ],
    "VC_Trends": [
        {"name": "a16z", "url": "https://a16z.com/feed/"},
        {"name": "Sequoia Capital", "url": "https://www.sequoiacap.com/feed/"},
        {"name": "Y Combinator", "url": "https://blog.ycombinator.com/feed/"},
        {"name": "Benedict Evans", "url": "https://ben-evans.com/benedictevans?format=rss"},
    ],
    "Tech_News": [
        {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
        {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
        {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
        {"name": "Ars Technica", "url": "http://feeds.arstechnica.com/arstechnica/index"},
    ],
    "High_Quality_Filters": [
        {"name": "Hacker News (Top 100+)", "url": "https://hnrss.org/newest?points=100"},
        # TLDR AI doesn't have a direct public RSS for free, skipping or user can add if they find one
    ]
}

@dataclass
class FeedItem:
    """Structure for a single feed item"""
    title: str
    link: str
    summary: str
    published: datetime
    source_name: str
    category: str

    def to_dict(self):
        return {
            "title": self.title,
            "link": self.link,
            "summary": self.summary,
            "published": self.published.strftime("%Y-%m-%d %H:%M"),
            "source_name": self.source_name,
            "category": self.category
        }

class FeedFetcher:
    """Fetcher for RSS monitoring"""

    def __init__(self, days_lookback: int = 1):
        self.days_lookback = days_lookback
        self.cutoff_date = datetime.now() - timedelta(days=days_lookback)

    def parse_date(self, entry) -> datetime:
        """Attempt to parse date from feed entry"""
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            return datetime.fromtimestamp(time.mktime(entry.published_parsed))
        if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            return datetime.fromtimestamp(time.mktime(entry.updated_parsed))
        return datetime.now()  # Fallback

    def fetch_feeds(self, category: str, feed_list: List[Dict]) -> List[FeedItem]:
        """Fetch all feeds for a given category"""
        items = []
        print(f"📡 Fetching {category} feeds...")
        
        for feed_cfg in feed_list:
            name = feed_cfg['name']
            url = feed_cfg['url']
            
            try:
                # print(f"  - Requesting {name}...")
                feed = feedparser.parse(url)
                
                if feed.bozo: # Basic error check
                     # print(f"    ⚠️  Possible parse error for {name}: {feed.bozo_exception}")
                     pass

                count = 0
                for entry in feed.entries:
                    try:
                        pub_date = self.parse_date(entry)
                        
                        # Filter by date
                        if pub_date < self.cutoff_date:
                            continue
                            
                        # Extract summary
                        summary = ""
                        if hasattr(entry, 'summary'):
                            summary = entry.summary
                        elif hasattr(entry, 'description'):
                            summary = entry.description
                        
                        # Clean summary (remove excessive HTML if needed, but keeping simple for now)
                        # Truncate summary for display
                        # summary = summary[:500] + "..." if len(summary) > 500 else summary

                        item = FeedItem(
                            title=entry.title,
                            link=entry.link,
                            summary=summary,
                            published=pub_date,
                            source_name=name,
                            category=category
                        )
                        items.append(item)
                        count += 1
                        
                    except Exception as e:
                        print(f"    Error parsing entry in {name}: {e}")
                        continue
                
                # print(f"    ✅ {name}: Found {count} new items")

            except Exception as e:
                print(f"    ❌ Failed to fetch {name}: {e}")
        
        # Sort items by date (newest first)
        items.sort(key=lambda x: x.published, reverse=True)
        return items

    def fetch_all(self) -> Dict[str, List[FeedItem]]:
        """Fetch all configured categories"""
        all_feeds = {}
        total_items = 0
        
        print(f"\n🌍 Starting Feed Fetch (Lookback: {self.days_lookback} days)")
        
        for category, feeds in FEEDS_CONFIG.items():
            items = self.fetch_feeds(category, feeds)
            all_feeds[category] = items
            total_items += len(items)
            print(f"  👉 {category}: {len(items)} items")
            
        print(f"✨ Total feed items fetched: {total_items}\n")
        return all_feeds

if __name__ == "__main__":
    # Test run
    fetcher = FeedFetcher(days_lookback=2) # Look back 2 days for test
    results = fetcher.fetch_all()
    
    for cat, items in results.items():
        if items:
            print(f"\n=== {cat} ({len(items)}) ===")
            for item in items[:3]:
                print(f"🔹 [{item.source_name}] {item.title} ({item.published})")
                print(f"   {item.link}")
