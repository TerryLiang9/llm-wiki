# LLM Wiki - Implementation Plan

> **创建日期**: 2026-04-07
> **基于**: SPEC.md v1.0.0
> **状态**: Ready for Implementation

---

## 📊 任务概览

| ID | 任务 | 复杂度 | 优先级 | 依赖 |
|----|------|--------|--------|------|
| 1 | 创建项目基础结构 | 低 | P0 | - |
| 2 | 实现 GLM API 客户端 | 中 | P0 | 1 |
| 3 | 实现 Ingest 功能 | 高 | P0 | 2, 4, 5 |
| 4 | 实现 Wiki 页面生成器 | 中 | P0 | 1 |
| 5 | 实现 Index 和 Log 管理 | 中 | P0 | 1 |
| 6 | 实现 Query 功能 | 中 | P1 | 2, 5 |
| 7 | 实现 Lint 健康检查 | 高 | P1 | 2, 5 |
| 8 | 编写单元测试 | 中 | P1 | 2, 3, 4, 5, 6, 7 |
| 9 | 编写集成测试 | 中 | P1 | 3, 6, 7 |
| 10 | 配置 Obsidian 集成 | 低 | P2 | 1 |
| 11 | 编写文档和使用指南 | 低 | P2 | 1, 3, 6, 7 |
| 12 | Git 仓库初始化 | 低 | P0 | 1 |

**总估算**: 12 个任务，约 3-5 个工作日

---

## 🎯 依赖关系图

```
Task 1 (基础结构)
    ├─→ Task 2 (GLM 客户端)
    │       ├─→ Task 3 (Ingest) ──→ Task 8 (单元测试)
    │       ├─→ Task 6 (Query) ───→ Task 9 (集成测试)
    │       └─→ Task 7 (Lint) ────→ Task 8 (单元测试)
    ├─→ Task 4 (页面生成器) ──────→ Task 3 (Ingest)
    ├─→ Task 5 (Index/Log) ───────→ Task 3 (Ingest)
    ├─→ Task 10 (Obsidian 配置)
    ├─→ Task 11 (文档)
    └─→ Task 12 (Git 初始化)
```

---

## 📝 详细任务分解

### Task 1: 创建项目基础结构

**目标**: 建立项目骨架和配置文件

**验收标准**:
- [x] 所有目录存在（raw/, wiki/, scripts/, config/, tests/）
- [x] 每个目录有 README.md 说明用途
- [x] 配置文件就位（config/schema.md, config/glm_config.py）
- [x] .gitignore 配置正确
- [x] Python 虚拟环境配置（requirements.txt, .venv/）

**实现步骤**:
1. 创建目录树
2. 添加 `.gitkeep` 到空目录
3. 创建 `config/schema.md`（wiki 约定）
4. 创建 `config/glm_config.py`（GLM API 配置模板）
5. 创建 `requirements.txt`（依赖列表）
6. 创建 `.gitignore`

**文件清单**:
```
project-wiki/
├── raw/
│   ├── prds/.gitkeep
│   ├── api-specs/.gitkeep
│   ├── meeting-notes/.gitkeep
│   ├── postmortems/.gitkeep
│   └── assets/.gitkeep
├── wiki/
│   ├── entities/.gitkeep
│   ├── concepts/.gitkeep
│   ├── sources/.gitkeep
│   ├── synthesis/.gitkeep
│   ├── index.md
│   └── log.md
├── scripts/
│   └── __init__.py
├── config/
│   ├── schema.md
│   └── glm_config.py
├── tests/
│   ├── fixtures/
│   └── __init__.py
├── requirements.txt
├── .gitignore
└── README.md
```

**边界条件**:
- ✅ 创建空 index.md 和 log.md
- ❌ 不调用任何 API
- ❌ 不创建任何 wiki 内容页面

---

### Task 2: 实现 GLM API 客户端

**目标**: 封装 GLM API 调用，提供统一的接口

**验收标准**:
- [x] 支持 GLM-4-Flash 和 GLM-4-Plus 模型
- [x] 实现 `complete(prompt)` 方法
- [x] 实现 `batch_complete(prompts)` 方法（批量调用）
- [x] 错误处理（超时、限流、API 错误）
- [x] Token 使用统计
- [x] 支持 JSON 模式输出
- [x] 单元测试覆盖率 ≥ 80%

**实现步骤**:
1. 创建 `scripts/glm_client.py`
2. 实现 GLMClient 类
3. 实现 retry 逻辑（指数退避）
4. 实现缓存机制（可选，减少重复调用）
5. 创建 prompt 模板文件
6. 编写单元测试

**接口设计**:
```python
class GLMClient:
    def __init__(self, api_key: str, model: str = "glm-4-flash"):
        ...

    def complete(self, prompt: str, **kwargs) -> str:
        """单次完成"""

    def batch_complete(self, prompts: List[str]) -> List[str]:
        """批量完成（并发）"""

    def complete_json(self, prompt: str) -> dict:
        """返回 JSON 格式"""

    def get_stats(self) -> dict:
        """获取 token 统计"""
```

**Prompt 模板**:
```python
PROMPTS = {
    "ingest": "你是一个软件项目的知识维护者...",
    "query": "你是一个软件项目的知识助手...",
    "lint": "你是一个 wiki 健康检查器...",
}
```

**边界条件**:
- ✅ 自动从环境变量读取 GLM_API_KEY
- ❌ 不硬编码 API Key
- ❓ 超过 3 次失败后需要用户干预

---

### Task 3: 实现 Ingest 功能

**目标**: 从源文档提取知识并更新 wiki

**验收标准**:
- [x] 支持单个文件 ingest
- [x] 支持批量 ingest（目录）
- [x] 支持交互模式（用户确认关键点）
- [x] 创建/更新 10-15 个 wiki 页面
- [x] 自动更新 index.md
- [x] 自动追加到 log.md
- [x] 所有页面有 frontmatter
- [x] 所有断言有源引用

**实现步骤**:
1. 创建 `scripts/ingest.py`
2. 实现源文档解析器（支持 .md, .txt, .yaml, .json）
3. 实现实体提取器（使用 LLM）
4. 实现概念提取器
5. 调用页面生成器（Task 4）
6. 调用 Index/Log 更新器（Task 5）
7. 实现 CLI 参数解析
8. 编写单元测试

**CLI 接口**:
```bash
# 单个文件
python scripts/ingest.py --source raw/prds/feature-x.md

# 批量
python scripts/ingest.py --batch raw/meeting-notes/

# 交互模式
python scripts/ingest.py --interactive

# 指定 GLM 模型
python scripts/ingest.py --model glm-4-plus
```

**工作流程**:
```
1. 读取源文档
2. 调用 LLM 提取关键信息
3. 与用户讨论（交互模式）
4. 创建/更新 wiki 页面
   - entities/*.md
   - concepts/*.md
   - sources/summaries/*.md
5. 更新 index.md
6. 追加到 log.md
7. 输出摘要报告
```

**输出示例**:
```json
{
  "created": 12,
  "updated": 3,
  "pages": [
    "wiki/entities/services/user-service.md",
    "wiki/concepts/architecture/event-driven.md",
    "wiki/sources/summaries/feature-x.md"
  ],
  "entities": ["User Service", "API Gateway"],
  "concepts": ["Event-Driven Architecture", "CQRS"]
}
```

**边界条件**:
- ✅ 保留源文档不变（只读）
- ❓ 创建页面前需要用户确认（交互模式）
- ❌ 不覆盖用户手动编辑的内容（检测冲突）

---

### Task 4: 实现 Wiki 页面生成器

**目标**: 生成符合规范的 wiki 页面

**验收标准**:
- [x] 支持 3 种页面类型（entity, concept, source-summary）
- [x] 所有页面有 frontmatter 元数据
- [x] 自动生成内部链接
- [x] 自动生成源引用
- [x] 支持 YAML frontmatter

**实现步骤**:
1. 创建 `scripts/page_generator.py`
2. 定义 frontmatter schema
3. 实现模板渲染
4. 实现链接生成器
5. 实现源引用格式化
6. 编写单元测试

**Frontmatter Schema**:
```yaml
---
type: entity | concept | source-summary
category: service | architecture | ...
created: 2026-04-07
sources: [raw/prds/feature-x.md]
tags: [microservice, api]
related: [path/to/other.md]
confidence: 0.9
---
```

**模板示例**:
```python
ENTITY_TEMPLATE = """# {name}

## Overview
{overview}

## Details
{details}

## Related
{related_links}

## Sources
{source_references}
"""
```

**边界条件**:
- ✅ 自动生成日期戳
- ✅ 验证 frontmatter 格式
- ❌ 不生成无效链接（检查目标存在）

---

### Task 5: 实现 Index 和 Log 管理

**目标**: 维护 wiki 的导航索引和变更历史

**验收标准**:
- [x] index.md 列出所有页面（分类、摘要、元数据）
- [x] log.md 记录所有操作（时间戳、类型、详情）
- [x] 自动更新
- [x] 支持 grep 搜索
- [x] log.md 可用 unix 工具解析

**实现步骤**:
1. 创建 `scripts/index_manager.py`
2. 创建 `scripts/log_manager.py`
3. 实现 index.md 更新逻辑
4. 实现 log.md 追加逻辑
5. 实现索引查询（grep wrapper）
6. 编写单元测试

**Index 格式**:
```markdown
# Wiki Index

Last updated: 2026-04-07 14:30

## Entities

### Services
- [User Service](entities/services/user-service.md) - 用户认证和管理
- [Order Service](entities/services/order-service.md) - 订单处理

### APIs
- [Registration API](entities/apis/registration-api.md) - 用户注册接口

## Concepts

### Architecture
- [Event-Driven](concepts/architecture/event-driven.md) - 事件驱动架构

### Patterns
- [CQRS](concepts/patterns/cqrs.md) - 命令查询职责分离

## Sources

### Summaries
- [Feature X PRD](sources/summaries/feature-x.md) - 2026-04-07
```

**Log 格式**:
```markdown
## [2026-04-07 14:30] ingest | Feature X PRD

Created: 12 pages
Updated: 3 pages
Entities: User Service, API Gateway
Concepts: Event-Driven, CQRS
Files:
- wiki/entities/services/user-service.md
- wiki/concepts/architecture/event-driven.md
```

**边界条件**:
- ✅ log.md 只追加，不修改
- ✅ index.md 每次重建（保持排序）
- ❌ 不删除 log 条目

---

### Task 6: 实现 Query 功能

**目标**: 从 wiki 查询信息并合成答案

**验收标准**:
- [x] 支持自然语言问答
- [x] 支持关键词搜索
- [x] 支持生成报告
- [x] 答案带引用
- [x] 可选写回 wiki
- [x] 响应时间 ≤ 3 秒

**实现步骤**:
1. 创建 `scripts/query.py`
2. 实现 index.md 搜索（grep）
3. 实现相关页面加载
4. 调用 LLM 合成答案
5. 实现引用格式化
6. 实现报告生成
7. 编写单元测试

**CLI 接口**:
```bash
# 问答
python scripts/query.py "API Gateway 的速率限制策略是什么？"

# 搜索
python scripts/query.py --search "database migration"

# 生成报告
python scripts/query.py --report --output wiki/reports/q2-review.md
```

**输出示例**:
```markdown
## API Gateway 的速率限制策略

根据 `wiki/entities/services/api-gateway.md`，当前策略为：

- **默认限制**: 100 req/min per IP
- **认证用户**: 1000 req/min
- **企业客户**: 自定义

实现基于 Redis + 令牌桶算法（见 `wiki/concepts/architecture/rate-limiting.md`）。

**相关决策**:
- [2026-03-15] 从固定窗口改为令牌桶算法
- [2026-02-01] 添加企业级限流

**来源**:
- wiki/entities/services/api-gateway.md:45-60
- wiki/concepts/architecture/rate-limiting.md:全文
```

**边界条件**:
- ✅ 优先搜索 index.md
- ✅ 限制加载页面数量（≤ 10）
- ❓ 写回 wiki 前需要用户确认

---

### Task 7: 实现 Lint 健康检查

**目标**: 检测 wiki 的健康问题

**验收标准**:
- [x] 检测矛盾（新信息 vs 旧断言）
- [x] 检测过时内容
- [x] 检测孤立页面（无入链）
- [x] 检测缺失引用
- [x] 生成 JSON 报告
- [x] 支持 --check 过滤

**实现步骤**:
1. 创建 `scripts/lint.py`
2. 实现矛盾检测（LLM 辅助）
3. 实现孤立页面检测（图遍历）
4. 实现引用完整性检查
5. 实现报告生成器
6. 编写单元测试

**CLI 接口**:
```bash
# 完整检查
python scripts/lint.py --full

# 只检查矛盾
python scripts/lint.py --check contradictions

# 只检查孤立页面
python scripts/lint.py --check orphans

# 输出 JSON
python scripts/lint.py --output report.json
```

**报告示例**:
```json
{
  "timestamp": "2026-04-07T14:30:00Z",
  "checks": {
    "contradictions": [
      {
        "severity": "high",
        "page": "wiki/entities/services/auth-service.md",
        "issue": "Claims JWT used, but wiki/concepts/architecture/authentication.md says OAuth2",
        "suggestion": "Review auth strategy decision"
      }
    ],
    "orphans": [
      {
        "page": "wiki/entities/deleted/old-service.md",
        "issue": "No inbound links"
      }
    ],
    "stale": [
      {
        "page": "wiki/concepts/deprecated/old-pattern.md",
        "issue": "Last updated 2026-01-01, may be outdated"
      }
    ]
  },
  "summary": {
    "total_issues": 5,
    "critical": 1,
    "warnings": 3,
    "info": 1
  }
}
```

**边界条件**:
- ✅ 只检测，不自动修复
- ❓ 发现严重问题时需要用户确认
- ❌ 不修改任何 wiki 内容

---

### Task 8: 编写单元测试

**目标**: 确保每个模块的正确性

**验收标准**:
- [x] 覆盖率 ≥ 80%
- [x] 所有关键路径有测试
- [x] Mock GLM API 调用
- [x] 测试边界条件

**测试范围**:
```
tests/
├── test_glm_client.py
│   ├── test_complete_success
│   ├── test_complete_retry
│   ├── test_batch_complete
│   └── test_error_handling
├── test_ingest.py
│   ├── test_extract_entities
│   ├── test_create_pages
│   └── test_update_index
├── test_query.py
│   ├── test_search_index
│   ├── test_synthesize_answer
│   └── test_format_citations
├── test_lint.py
│   ├── test_detect_contradictions
│   ├── test_find_orphans
│   └── test_check_references
├── test_page_generator.py
│   ├── test_generate_frontmatter
│   ├── test_create_entity_page
│   └── test_create_concept_page
└── test_index_log_manager.py
    ├── test_update_index
    └── test_append_log
```

**边界条件**:
- ✅ 使用 pytest fixtures
- ✅ Mock 所有外部调用
- ❌ 不调用真实 GLM API

---

### Task 9: 编写集成测试

**目标**: 测试完整工作流

**验收标准**:
- [x] 测试 ingest → query 流程
- [x] 测试 ingest → lint 流程
- [x] 使用测试 fixture
- [x] 清理测试环境

**测试范围**:
```python
def test_full_ingest_query_cycle():
    """完整 ingest → query 流程"""
    # 1. Ingest
    result = ingest_source('tests/fixtures/sample-prd.md')
    assert result['created'] > 0

    # 2. Query
    answer = query('What is the main feature?')
    assert 'user registration' in answer
    assert 'tests/fixtures/sample-prd.md' in answer['sources']

def test_ingest_detects_contradictions():
    """Ingest 后 lint 能检测矛盾"""
    # 1. Inest 第一个版本
    ingest_source('tests/fixtures/v1.md')

    # 2. Ingest 矛盾的第二个版本
    ingest_source('tests/fixtures/v2-contradiction.md')

    # 3. Lint 应该检测到
    report = lint(check='contradictions')
    assert len(report['contradictions']) > 0
```

**边界条件**:
- ✅ 使用临时目录
- ✅ 每个测试独立
- ❌ 不影响真实 wiki

---

### Task 10: 配置 Obsidian 集成

**目标**: 优化 Obsidian 作为 wiki 前端

**验收标准**:
- [x] Obsidian vault 配置就绪
- [x] Graph View 显示正确
- [x] 搜索快捷键配置
- [x] 推荐插件列表

**配置步骤**:
1. 创建 `.obsidian/` 目录
2. 配置 `graph.json`
3. 配置快捷键
4. 创建插件推荐列表

**配置文件**:
```json
// .obsidian/graph.json
{
  "backgroundColors": [
    "#e4e4e4",
    "#7aa5d2",
    "#4c8cb5",
    "#23527c",
    "#172d4f"
  ]
}
```

**推荐插件**:
- Dataview（查询 frontmatter）
- Obsidian Git（版本控制集成）
- Advanced Tables（表格编辑）

**边界条件**:
- ✅ 只创建配置文件
- ❌ 不安装插件（用户手动选择）

---

### Task 11: 编写文档和使用指南

**目标**: 提供清晰的使用说明

**验收标准**:
- [x] README.md 快速开始
- [x] CLI 命令参考
- [x] 故障排查指南
- [x] 贡献指南

**文档结构**:
```
README.md - 快速开始
docs/
├── cli-reference.md - CLI 命令
├── schema.md - Wiki 约定
├── troubleshooting.md - 故障排查
└── contributing.md - 贡献指南
```

**边界条件**:
- ✅ 包含示例
- ✅ 包含常见问题

---

### Task 12: Git 仓库初始化

**目标**: 设置版本控制

**验收标准**:
- [x] .gitignore 配置正确
- [x] 初始提交创建
- [x] 分支策略文档

**.gitignore**:
```
# GLM API Key
.env
glm_config.json

# Python
__pycache__/
*.pyc
.venv/

# Obsidian
.obsidian/workspace

# 测试
.pytest_cache/
.coverage

# IDE
.vscode/
.idea/
```

**边界条件**:
- ✅ 忽略敏感信息
- ✅ 提交所有配置和代码

---

## 🚀 执行顺序

### 迭代 1: 核心基础设施（P0）
1. Task 1: 创建项目基础结构
2. Task 12: Git 仓库初始化
3. Task 2: 实现 GLM API 客户端
4. Task 4: 实现 Wiki 页面生成器
5. Task 5: 实现 Index 和 Log 管理

### 迭代 2: Ingest 功能（P0）
6. Task 3: 实现 Ingest 功能
7. Task 8: 编写单元测试（ingest 模块）

### 迭代 3: Query 和 Lint（P1）
8. Task 6: 实现 Query 功能
9. Task 7: 实现 Lint 健康检查
10. Task 8: 编写单元测试（query 和 lint 模块）
11. Task 9: 编写集成测试

### 迭代 4: 完善和文档（P2）
12. Task 10: 配置 Obsidian 集成
13. Task 11: 编写文档和使用指南

---

## 📈 进度追踪

- [ ] 迭代 1: 核心基础设施 (0/5)
- [ ] 迭代 2: Ingest 功能 (0/2)
- [ ] 迭代 3: Query 和 Lint (0/4)
- [ ] 迭代 4: 完善和文档 (0/2)

**总进度**: 0/12 (0%)

---

## 🎯 成功标准

- [ ] 所有 P0 任务完成
- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 集成测试全部通过
- [ ] 文档完整
- [ ] 可在 5 分钟内完成设置
- [ ] Ingest 单个文档 ≤ 2 分钟
- [ ] Query 响应时间 ≤ 3 秒

---

## 🔄 下一步

确认此计划后，将进入 **Phase 3: Build**，按迭代顺序实现功能。

**预计时间**: 3-5 个工作日
