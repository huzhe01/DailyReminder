#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arXiv 论文抓取模块
获取大模型、广告领域的最新论文
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ArxivPaper:
    """arXiv 论文数据结构"""
    title: str
    authors: List[str]
    summary: str
    arxiv_id: str
    published: str
    updated: str
    pdf_url: str
    abs_url: str
    categories: List[str]


class ArxivFetcher:
    """arXiv 论文抓取器"""
    
    BASE_URL = "http://export.arxiv.org/api/query"
    
    # 大模型相关关键词
    LLM_KEYWORDS = [
        "large language model",
        "LLM",
        "GPT",
        "transformer",
        "BERT",
        "foundation model",
        "instruction tuning",
        "RLHF",
        "reinforcement learning from human feedback",
        "chain of thought",
        "prompt engineering",
        "in-context learning",
        "multimodal",
        "vision language model",
        "language model alignment",
        "neural machine translation",
        "text generation",
    ]
    
    # 广告领域关键词
    AD_KEYWORDS = [
        "computational advertising",
        "click-through rate prediction",
        "CTR prediction",
        "conversion rate prediction",
        "CVR prediction",
        "recommendation system",
        "ad ranking",
        "real-time bidding",
        "RTB",
        "programmatic advertising",
        "user behavior modeling",
        "display advertising",
        "sponsored search",
        "ad auction",
        "ad targeting",
    ]
    
    def __init__(self, max_results: int = 20):
        self.max_results = max_results
    
    def _build_query(self, keywords: List[str], category: str = "cs.CL") -> str:
        """构建 arXiv API 查询字符串"""
        # 将关键词组合成 OR 查询
        keyword_query = " OR ".join([f'ti:"{kw}" OR abs:"{kw}"' for kw in keywords[:5]])
        # 限制分类
        query = f"({keyword_query}) AND cat:{category}"
        return query
    
    def _parse_entry(self, entry: ET.Element, ns: dict) -> ArxivPaper:
        """解析单个论文条目"""
        # 提取 arXiv ID
        arxiv_id = entry.find('atom:id', ns).text.split('/abs/')[-1]
        
        # 提取标题（去除多余空白）
        title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
        
        # 提取作者列表
        authors = [
            author.find('atom:name', ns).text 
            for author in entry.findall('atom:author', ns)
        ]
        
        # 提取摘要
        summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
        
        # 提取时间
        published = entry.find('atom:published', ns).text
        updated = entry.find('atom:updated', ns).text
        
        # 提取链接
        pdf_url = ""
        abs_url = ""
        for link in entry.findall('atom:link', ns):
            if link.get('title') == 'pdf':
                pdf_url = link.get('href')
            elif link.get('type') == 'text/html':
                abs_url = link.get('href')
        
        # 如果没有找到 abs_url，使用默认格式
        if not abs_url:
            abs_url = f"https://arxiv.org/abs/{arxiv_id}"
        if not pdf_url:
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        
        # 提取分类
        categories = [
            cat.get('term') 
            for cat in entry.findall('atom:category', ns)
        ]
        
        return ArxivPaper(
            title=title,
            authors=authors,
            summary=summary,
            arxiv_id=arxiv_id,
            published=published,
            updated=updated,
            pdf_url=pdf_url,
            abs_url=abs_url,
            categories=categories
        )
    
    def fetch_papers(self, keywords: List[str], categories: List[str] = None) -> List[ArxivPaper]:
        """抓取论文"""
        if categories is None:
            categories = ["cs.CL", "cs.LG", "cs.AI", "cs.IR"]
        
        all_papers = []
        seen_ids = set()
        
        for category in categories:
            query = self._build_query(keywords, category)
            
            params = {
                'search_query': query,
                'start': 0,
                'max_results': self.max_results,
                'sortBy': 'submittedDate',
                'sortOrder': 'descending'
            }
            
            url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"
            
            try:
                print(f"正在获取 {category} 分类的论文...")
                with urllib.request.urlopen(url, timeout=30) as response:
                    data = response.read().decode('utf-8')
                
                # 解析 XML
                root = ET.fromstring(data)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                
                for entry in root.findall('atom:entry', ns):
                    paper = self._parse_entry(entry, ns)
                    if paper.arxiv_id not in seen_ids:
                        all_papers.append(paper)
                        seen_ids.add(paper.arxiv_id)
                
            except Exception as e:
                print(f"获取 {category} 分类论文时出错: {e}")
                continue
        
        return all_papers
    
    def fetch_llm_papers(self) -> List[ArxivPaper]:
        """获取大模型相关论文"""
        print("=" * 50)
        print("📚 正在获取大模型领域论文...")
        print("=" * 50)
        return self.fetch_papers(self.LLM_KEYWORDS, ["cs.CL", "cs.LG", "cs.AI"])
    
    def fetch_ad_papers(self) -> List[ArxivPaper]:
        """获取广告领域论文"""
        print("=" * 50)
        print("📊 正在获取广告领域论文...")
        print("=" * 50)
        return self.fetch_papers(self.AD_KEYWORDS, ["cs.IR", "cs.LG", "cs.AI"])
    
    def fetch_all(self) -> dict:
        """获取所有领域论文"""
        return {
            'llm': self.fetch_llm_papers(),
            'advertising': self.fetch_ad_papers()
        }


def filter_recent_papers(papers: List[ArxivPaper], days: int = 7) -> List[ArxivPaper]:
    """过滤最近几天的论文"""
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_papers = []
    
    for paper in papers:
        try:
            # arXiv 日期格式: 2024-01-15T12:00:00Z
            pub_date = datetime.strptime(paper.published[:10], '%Y-%m-%d')
            if pub_date >= cutoff_date:
                recent_papers.append(paper)
        except:
            recent_papers.append(paper)
    
    return recent_papers


if __name__ == "__main__":
    fetcher = ArxivFetcher(max_results=10)
    
    # 测试获取论文
    papers = fetcher.fetch_all()
    
    print(f"\n找到 {len(papers['llm'])} 篇大模型论文")
    print(f"找到 {len(papers['advertising'])} 篇广告领域论文")
    
    # 打印示例
    if papers['llm']:
        print("\n🔬 大模型论文示例:")
        paper = papers['llm'][0]
        print(f"  标题: {paper.title}")
        print(f"  作者: {', '.join(paper.authors[:3])}...")
        print(f"  链接: {paper.abs_url}")
