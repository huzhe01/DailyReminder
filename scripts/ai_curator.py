#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 内容筛选模块 - 使用大模型筛选最值得关注的内容
"""

from openai import OpenAI
from typing import List, Dict, Any, Optional
import os


class AICurator:
    """AI 内容筛选器"""
    
    def __init__(self, client: OpenAI = None):
        if client is None:
            api_key = os.environ.get('MODELSCOPE_API_KEY')
            if not api_key:
                raise ValueError("请设置 MODELSCOPE_API_KEY 环境变量")
            self.client = OpenAI(
                base_url='https://api-inference.modelscope.cn/v1/',
                api_key=api_key
            )
        else:
            self.client = client
        
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.calls = 0
    
    def curate(
        self, 
        items: List[Dict[str, Any]], 
        context: str, 
        max_items: int = 4,
        item_format: str = "- {title}"
    ) -> str:
        """
        使用 AI 筛选并总结内容
        
        Args:
            items: 待筛选的内容列表，每个 item 是一个字典
            context: 内容来源描述 (如 "GitHub Issues", "Reddit r/LocalLLaMA")
            max_items: 最多选择的条目数
            item_format: 格式化单个 item 的模板
        
        Returns:
            HTML 格式的筛选结果
        """
        if not items:
            return '<p style="color: #718096;">暂无新内容</p>'
        
        # 构建内容列表
        items_text = "\n".join([
            f"{i+1}. 标题: {item.get('title', 'N/A')}\n   链接: {item.get('url', 'N/A')}\n   描述: {item.get('description', item.get('summary', ''))[:200]}"
            for i, item in enumerate(items[:15])  # 最多处理 15 条
        ])
        
        prompt = f"""你是一位资深 AI 技术编辑。以下是今日"**{context}**"的内容列表：

{items_text}

请完成以下任务：
1. 从中筛选出 {max_items} 条最值得 AI 研究者/工程师关注的内容
2. 为每条内容给出简短的中文点评（1句话，说明为什么值得关注）

输出格式（严格按照此 JSON 格式）：
[
  {{"index": 1, "comment": "一句话点评"}},
  {{"index": 3, "comment": "一句话点评"}},
  ...
]

只返回 JSON 数组，不要其他内容。"""

        try:
            response = self.client.chat.completions.create(
                model="Qwen/Qwen2.5-72B-Instruct",
                messages=[
                    {"role": "system", "content": "你是一位专业的 AI 技术内容筛选专家。只返回 JSON 格式的筛选结果。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # 记录 token 使用
            if response.usage:
                self.total_input_tokens += response.usage.prompt_tokens
                self.total_output_tokens += response.usage.completion_tokens
                self.calls += 1
            
            result_text = response.choices[0].message.content.strip()
            
            # 解析 JSON
            import json
            # 清理可能的 markdown 代码块
            if result_text.startswith("```"):
                result_text = result_text.split("\n", 1)[1].rsplit("```", 1)[0]
            
            selected = json.loads(result_text)
            
            # 生成 HTML
            html_parts = []
            for sel in selected[:max_items]:
                idx = sel.get("index", 1) - 1
                if 0 <= idx < len(items):
                    item = items[idx]
                    comment = sel.get("comment", "")
                    html_parts.append(f'''
                    <div style="padding: 12px; border-left: 3px solid #4299e1; margin: 10px 0; background: #f7fafc;">
                        <div style="font-weight: 600;">
                            <a href="{item.get('url', '#')}" target="_blank" style="color: #2b6cb0; text-decoration: none;">
                                {item.get('title', 'Untitled')}
                            </a>
                        </div>
                        <div style="font-size: 13px; color: #718096; margin-top: 5px;">
                            💡 {comment}
                        </div>
                    </div>
                    ''')
            
            return '\n'.join(html_parts) if html_parts else '<p style="color: #718096;">暂无精选内容</p>'
            
        except Exception as e:
            print(f"❌ AI 筛选失败: {e}")
            # 降级：直接展示前几条
            html_parts = []
            for item in items[:max_items]:
                html_parts.append(f'''
                <div style="padding: 10px; border-left: 3px solid #cbd5e0; margin: 8px 0;">
                    <a href="{item.get('url', '#')}" target="_blank" style="color: #2b6cb0;">
                        {item.get('title', 'Untitled')}
                    </a>
                </div>
                ''')
            return '\n'.join(html_parts)
    
    def get_usage(self) -> Dict[str, int]:
        """获取 token 使用统计"""
        return {
            "calls": self.calls,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens
        }


if __name__ == "__main__":
    # 测试
    curator = AICurator()
    test_items = [
        {"title": "FlashAttention-3 发布", "url": "https://example.com/1", "description": "新版本支持 H200"},
        {"title": "llama.cpp 支持 MoE", "url": "https://example.com/2", "description": "添加了专家混合模型支持"},
        {"title": "Bug fix in tokenizer", "url": "https://example.com/3", "description": "修复了小问题"},
    ]
    result = curator.curate(test_items, "GitHub Issues", max_items=2)
    print(result)
