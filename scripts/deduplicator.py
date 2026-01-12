#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
去重模块 - 跟踪已展示过的内容，避免重复推送
"""

import os
import json
from datetime import datetime
from typing import Set, Dict


class Deduplicator:
    """内容去重器"""
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            # 默认存储在 archives/seen_items.json
            base_dir = os.path.dirname(os.path.dirname(__file__))
            self.storage_path = os.path.join(base_dir, 'archives', 'seen_items.json')
        else:
            self.storage_path = storage_path
        
        self.seen_items: Dict[str, Set[str]] = {}
        self.load()
    
    def load(self):
        """从文件加载已见内容"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # JSON 不支持 Set，转换回来
                    self.seen_items = {k: set(v) for k, v in data.items()}
                print(f"📂 已加载 {sum(len(v) for v in self.seen_items.values())} 条历史记录")
            except Exception as e:
                print(f"⚠️ 加载去重记录失败: {e}")
                self.seen_items = {}
        else:
            self.seen_items = {}
            print("📂 初始化新的去重记录")
    
    def save(self):
        """保存已见内容到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            # Set 转换为 List 以便 JSON 序列化
            data = {k: list(v) for k, v in self.seen_items.items()}
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 已保存 {sum(len(v) for v in self.seen_items.values())} 条去重记录")
        except Exception as e:
            print(f"❌ 保存去重记录失败: {e}")
    
    def is_seen(self, content_type: str, unique_id: str) -> bool:
        """检查内容是否已展示过"""
        if content_type not in self.seen_items:
            return False
        return unique_id in self.seen_items[content_type]
    
    def mark_seen(self, content_type: str, unique_id: str):
        """标记内容为已展示"""
        if content_type not in self.seen_items:
            self.seen_items[content_type] = set()
        self.seen_items[content_type].add(unique_id)
    
    def filter_new(self, content_type: str, items: list, id_getter) -> list:
        """
        过滤出新内容并标记为已见
        
        Args:
            content_type: 内容类型 (arxiv, youtube, feed, github_issue, etc.)
            items: 待过滤的内容列表
            id_getter: 从单个 item 获取唯一 ID 的函数
        
        Returns:
            仅包含新内容的列表
        """
        new_items = []
        for item in items:
            unique_id = id_getter(item)
            if not self.is_seen(content_type, unique_id):
                new_items.append(item)
                self.mark_seen(content_type, unique_id)
        
        filtered_count = len(items) - len(new_items)
        if filtered_count > 0:
            print(f"  🔄 {content_type}: 过滤掉 {filtered_count} 条重复内容，保留 {len(new_items)} 条新内容")
        
        return new_items
    
    def get_stats(self) -> Dict[str, int]:
        """获取各类型的已见数量统计"""
        return {k: len(v) for k, v in self.seen_items.items()}


if __name__ == "__main__":
    # 测试
    dedup = Deduplicator()
    print("Stats:", dedup.get_stats())
