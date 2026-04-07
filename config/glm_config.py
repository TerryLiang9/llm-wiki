"""
GLM API Configuration

This module contains configuration for the GLM (智谱 AI) API client.
"""

import os
from typing import Literal

# GLM API Configuration
GLM_CONFIG = {
    # API Key (from environment variable)
    "api_key": os.getenv("GLM_API_KEY", ""),

    # Model selection
    # Options: "glm-4-flash" (faster, cheaper), "glm-4-plus" (more capable)
    "model": os.getenv("GLM_MODEL", "glm-4-flash"),

    # API Base URL
    "base_url": "https://open.bigmodel.cn/api/paas/v4/",

    # Generation parameters
    "max_tokens": 8192,
    "temperature": 0.3,  # Lower temperature for more consistent output

    # Retry configuration
    "max_retries": 3,
    "retry_delay": 1.0,  # Initial delay in seconds
    "retry_multiplier": 2.0,  # Exponential backoff multiplier

    # Timeout configuration
    "timeout": 60.0,  # Seconds

    # Cache configuration (optional)
    "enable_cache": True,
    "cache_ttl": 3600,  # Cache time-to-live in seconds
}

# Prompt Templates
PROMPTS = {
    "ingest": """你是一个软件项目的知识维护者。阅读以下源文档，并：

1. 提取关键实体（服务、API、决策）
2. 识别核心概念（架构模式、设计原则）
3. 创建/更新 wiki 页面
4. 更新 index.md
5. 追加到 log.md

源文档：
{source_content}

现有 wiki 上下文：
{existing_context}

请输出 JSON 格式：
{{
  "entities": [
    {{"name": "Entity Name", "type": "service|api|decision", "description": "..."}}
  ],
  "concepts": [
    {{"name": "Concept Name", "type": "architecture|pattern", "description": "..."}}
  ],
  "decisions": [
    {{"title": "Decision", "rationale": "...", "date": "YYYY-MM-DD"}}
  ],
  "pages_to_create": [
    {{"path": "wiki/path/to/page.md", "type": "entity|concept", "title": "..."}}
  ]
}}
""",

    "query": """你是一个软件项目的知识助手。用户提问：{query}

相关 wiki 页面：
{relevant_pages}

请提供：
1. 直接答案
2. 引用来源（使用格式：`wiki/path/to/page.md`:line-range）
3. 相关链接
4. 后续建议

输出 JSON 格式：
{{
  "answer": "详细答案...",
  "sources": ["`wiki/path/to/page.md`:45-60"],
  "related": ["wiki/path/to/related.md"],
  "suggestions": ["建议1", "建议2"]
}}
""",

    "lint": """你是一个 wiki 健康检查器。检查以下 wiki 页面：

{wiki_pages}

检查项：
1. 矛盾：新信息是否与旧断言冲突？
2. 过时：是否有被新源取代的内容？
3. 孤立：哪些页面无入链？
4. 引用：所有源引用是否有效？

输出 JSON 格式：
{{
  "contradictions": [
    {{
      "page": "wiki/path/to/page.md",
      "issue": "描述矛盾...",
      "severity": "high|medium|low"
    }}
  ],
  "stale": [
    {{
      "page": "wiki/path/to/page.md",
      "issue": "描述过时内容...",
      "suggestion": "建议..."
    }}
  ],
  "orphans": [
    {{
      "page": "wiki/path/to/page.md",
      "reason": "无入链"
    }}
  ]
}}
""",
}

# Page Templates
ENTITY_TEMPLATE = """---
type: entity
category: {category}
created: {created}
sources: [{sources}]
tags: {tags}
related: {related}
confidence: {confidence}
---

# {name}

## Overview
{overview}

## Details
{details}

## Related
{related_links}

## Sources
{source_references}
"""

CONCEPT_TEMPLATE = """---
type: concept
category: {category}
created: {created}
sources: [{sources}]
tags: {tags}
related: {related}
---

# {name}

## Definition
{definition}

## Trade-offs
| Pros | Cons |
|------|------|
| {pros} | {cons} |

## When to Use
- ✅ {good_scenarios}
- ❌ {bad_scenarios}

## Examples in Project
{examples}

## Sources
{source_references}
"""

SOURCE_SUMMARY_TEMPLATE = """---
type: source-summary
source: {source}
source_hash: {source_hash}
ingested: {ingested}
confidence: {confidence}
---

# {title} - Summary

## Key Points
{key_points}

## Entities Mentioned
{entities}

## Concepts Introduced
{concepts}

## Decisions Recorded
{decisions}

## Sources
- `{source}`:full
"""

# Model Types
ModelType = Literal["glm-4-flash", "glm-4-plus"]


def get_config() -> dict:
    """Get GLM configuration with validation."""
    config = GLM_CONFIG.copy()

    if not config["api_key"]:
        raise ValueError(
            "GLM_API_KEY environment variable not set. "
            "Please set it with: export GLM_API_KEY='your-api-key'"
        )

    return config


def get_prompt(template_name: str, **kwargs) -> str:
    """Get a prompt template with variables filled in."""
    template = PROMPTS.get(template_name)
    if not template:
        raise ValueError(f"Prompt template '{template_name}' not found")

    return template.format(**kwargs)
