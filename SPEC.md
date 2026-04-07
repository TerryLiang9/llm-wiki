# LLM Wiki for Software Development - Project Specification

> **版本**: 1.0.0
> **创建日期**: 2026-04-07
> **状态**: Draft

---

## 📋 项目概述

### 目标
为软件开发项目构建一个基于 LLM 的持久化知识库系统，集成 Obsidian 作为前端界面，使用 GLM（智谱 AI）作为后端 AI 引擎。

### 核心价值主张
- **知识编译而非检索**：LLM 增量构建和维护结构化 wiki，而非每次从原始文档重新生成
- **知识复利**：交叉引用、矛盾标注、综合分析随时间累积
- **零维护负担**：LLM 负责所有繁琐的簿记工作，开发者专注于决策和理解

### 成功标准
1. **功能性**：
   - ✅ 支持从多种源（PRD、API 文档、会议记录、postmortem）自动摄取知识
   - ✅ 查询响应时间 < 3 秒（使用索引）
   - ✅ 知识图谱可视化显示概念关联
   - ✅ 自动检测矛盾和过时内容

2. **可用性**：
   - ✅ 开发者可在 5 分钟内完成初始设置
   - ✅ 每次摄取添加 10-15 个交叉引用的 wiki 页面
   - ✅ Obsidian 图谱视图实时更新

3. **质量**：
   - ✅ 所有断言都有源引用（source provenance）
   - ✅ Git 版本控制支持完整审计追踪
   - ✅ 测试覆盖率 ≥ 80%

---

## 🏗️ 架构设计

### 三层架构

```
┌─────────────────────────────────────────────────────────┐
│                   Layer 3: The Schema                    │
│  ┌────────────────────────────────────────────────────┐  │
│  │  CLAUDE.md / AGENTS.md                             │  │
│  │  - Wiki 结构约定                                    │  │
│  │  - Ingest/Query/Lint 工作流                        │  │
│  │  - 命名规范、页面模板                               │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↕ 配置
┌─────────────────────────────────────────────────────────┐
│                   Layer 2: The Wiki                       │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Obsidian Vault (LLM 完全拥有)                     │  │
│  │  ├── entities/          (实体页面)                 │  │
│  │  ├── concepts/          (概念页面)                 │  │
│  │  ├── sources/           (源摘要)                   │  │
│  │  ├── synthesis/         (综合分析)                 │  │
│  │  ├── index.md           (内容索引)                 │  │
│  │  └── log.md             (变更日志)                 │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↕ 读写
┌─────────────────────────────────────────────────────────┐
│                  Layer 1: Raw Sources                     │
│  ┌────────────────────────────────────────────────────┐  │
│  │  raw/                                              │  │
│  │  ├── prds/              (产品需求文档)             │  │
│  │  ├── api-specs/         (API 规范)                 │  │
│  │  ├── meeting-notes/     (会议记录)                 │  │
│  │  ├── postmortems/       (事故报告)                 │  │
│  │  └── assets/            (图片、图表)               │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↕ 只读
┌─────────────────────────────────────────────────────────┐
│              External: GLM API + Obsidian                 │
│  - GLM-4-Flash / GLM-4-Plus                             │
│  - Obsidian Graph View, Search, Plugins                 │
└─────────────────────────────────────────────────────────┘
```

### 目录结构

```
project-wiki/
├── raw/                          # 不可变源文档
│   ├── prds/
│   ├── api-specs/
│   ├── meeting-notes/
│   ├── postmortems/
│   └── assets/
├── wiki/                         # LLM 生成的 markdown 文件
│   ├── entities/
│   │   ├── services/
│   │   ├── apis/
│   │   └── decisions/
│   ├── concepts/
│   │   ├── architecture/
│   │   └── patterns/
│   ├── sources/
│   │   └── summaries/
│   ├── synthesis/
│   │   ├── timeline.md
│   │   └── roadmap.md
│   ├── index.md
│   └── log.md
├── scripts/                      # CLI 工具
│   ├── ingest.py
│   ├── query.py
│   └── lint.py
├── config/
│   └── schema.md                 # Wiki 约定和模板
├── tests/
│   ├── test_ingest.py
│   ├── test_query.py
│   └── test_lint.py
├── .gitignore
├── SPEC.md
└── README.md
```

---

## 🎮 命令行接口

### 1. Ingest（摄取）

```bash
# 摄取单个源文件
python scripts/ingest.py --source raw/prds/feature-x.md

# 摄取整个目录
python scripts/ingest.py --batch raw/meeting-notes/

# 交互模式（推荐）
python scripts/ingest.py --interactive
```

**工作流程**：
1. LLM 读取源文档
2. 与用户讨论关键要点
3. 创建/更新 wiki 页面（10-15 个）
4. 更新 index.md
5. 追加到 log.md

### 2. Query（查询）

```bash
# 问答模式
python scripts/query.py "API Gateway 的速率限制策略是什么？"

# 搜索模式
python scripts/query.py --search "database migration"

# 生成报告
python scripts/query.py --report --output wiki/reports/quarterly-review.md
```

**工作流程**：
1. 搜索 index.md 找到相关页面
2. 读取相关 wiki 页面
3. 合成答案并引用源
4. 可选：将答案写回 wiki

### 3. Lint（健康检查）

```bash
# 运行完整检查
python scripts/lint.py --full

# 只检查矛盾
python scripts/lint.py --check contradictions

# 只检查孤立页面
python scripts/lint.py --check orphans
```

**检查项**：
- ✅ 矛盾检测（新信息 vs 旧断言）
- ✅ 过时内容（被新源取代）
- ✅ 孤立页面（无入链）
- ✅ 缺失交叉引用
- ✅ 引用完整性

---

## 📐 Wiki 页面模板

### 实体页面（entities/services/user-service.md）

```markdown
---
type: entity
category: service
created: 2026-04-07
sources: [raw/api-specs/user-api.yaml, raw/prds/user-auth.md]
tags: [microservice, authentication]
related: [entities/services/auth-service.md, concepts/architecture/service-mesh.md]
---

# User Service

## Overview
[LLM 生成的服务概述]

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST   | /api/users | Create user |
| GET    | /api/users/:id | Get user |

## Dependencies
- **Auth Service**: Token validation
- **Database**: PostgreSQL

## Design Decisions
1. **[2026-04-01]** 使用 JWT 而非 Session（见 concepts/architecture/authentication.md）
2. **[2026-03-15]** 密码哈希使用 Argon2

## Open Questions
- [ ] 是否支持多租户？（待 PRD #42 确认）

## Sources
- `raw/api-specs/user-api.yaml`:55-72
- `raw/prds/user-auth.md`:12-30
```

### 概念页面（concepts/architecture/event-driven.md）

```markdown
---
type: concept
category: architecture
created: 2026-04-07
sources: [raw/meeting-notes/arch-review-2026-04-01.md]
tags: [async, messaging, events]
related: [entities/services/event-bus.md, concepts/patterns/cqrs.md]
---

# Event-Driven Architecture

## Definition
[LLM 生成的定义和解释]

## Trade-offs
| Pros | Cons |
|------|------|
| 松耦合 | 复杂性增加 |
| 可扩展 | 调试困难 |

## When to Use
- ✅ 高并发场景
- ✅ 跨服务通信
- ❌ 简单 CRUD

## Examples in Project
- OrderCreated → PaymentService
- UserDeleted → cleanup all services

## Sources
- `raw/meeting-notes/arch-review-2026-04-01.md`:45-60
```

### 源摘要（sources/summaries/prd-feature-x.md）

```markdown
---
type: source-summary
source: raw/prds/feature-x.md
source_hash: abc123def456
ingested: 2026-04-07
confidence: 0.9
---

# Feature X PRD - Summary

## Key Points
1. **目标**: 提升用户注册转化率 20%
2. **方案**: 简化注册流程，从 5 步减少到 2 步
3. **时间**: Q2 2026 完成

## Entities Mentioned
- entities/services/user-service.md
- entities/apis/registration-api.md
- concepts/design/simplification.md

## Decisions Recorded
- 使用社交媒体 OAuth 登录
- 移除邮箱验证步骤

## Sources
- `raw/prds/feature-x.md`:全文
```

---

## 🔧 GLM 集成

### API 配置

```python
# config/glm_config.py
GLM_CONFIG = {
    "api_key": os.getenv("GLM_API_KEY"),
    "model": "glm-4-flash",  # 或 "glm-4-plus"
    "base_url": "https://open.bigmodel.cn/api/paas/v4/",
    "max_tokens": 8192,
    "temperature": 0.3,  # 低温度保证一致性
}
```

### Prompt 模板

**Ingest Prompt**：
```
你是一个软件项目的知识维护者。阅读以下源文档，并：

1. 提取关键实体（服务、API、决策）
2. 识别核心概念（架构模式、设计原则）
3. 创建/更新 wiki 页面
4. 更新 index.md
5. 追加到 log.md

源文档：{source_content}

现有 wiki 上下文：{existing_context}

请输出：
- 创建/更新的文件列表
- 每个文件的变更说明
- 建议的后续 action
```

**Query Prompt**：
```
你是一个软件项目的知识助手。用户提问：{query}

相关 wiki 页面：
{relevant_pages}

请提供：
1. 直接答案
2. 引用来源
3. 相关链接
4. 后续建议
```

**Lint Prompt**：
```
你是一个 wiki 健康检查器。检查以下 wiki 页面：

{wiki_pages}

检查项：
1. 矛盾：新信息是否与旧断言冲突？
2. 过时：是否有被新源取代的内容？
3. 孤立：哪些页面无入链？
4. 引用：所有源引用是否有效？

输出 JSON 格式的检查报告。
```

---

## 🎨 代码风格约定

### Python

```python
# 使用 2 空格缩进
# 使用单引号
# 遵循 PEP 8（但缩进用 2 空格）

def ingest_source(source_path: str, interactive: bool = True) -> dict:
    '''Ingest a source document and update wiki.'''
    # 实现
    pass

# 类型注解必须
# 函数名使用 snake_case
# 常量使用 UPPER_CASE
```

### Markdown

```markdown
# 页面标题

## 二级标题

### 三级标题

- 列表项
- 另一个列表项

| 表头 1 | 表头 2 |
|--------|--------|
| 数据 1 | 数据 2 |

`代码` 或 ```代码块```

[链接文字](path/to/file.md)
```

### Git 提交

```
feat(scope): description

- file1.md: change 1
- file2.md: change 2

Refs #issue
```

---

## 🧪 测试策略

### 测试金字塔

```
       5% E2E
      ┌─────┐
     │      │
     │      │
    │  15%  │ Integration
   │        │
  │          │
 │            │
│    80%      │ Unit
│             │
```

### 单元测试（tests/test_*.py）

```python
def test_extract_entities_from_api_spec():
    source = load_fixture('user-api.yaml')
    entities = extract_entities(source)
    assert len(entities) == 3
    assert entities[0]['name'] == 'User Service'
    assert entities[0]['type'] == 'service'

def test_update_index_adds_new_page():
    index = load_index('wiki/index.md')
    new_page = {'path': 'wiki/entities/test.md', 'summary': 'Test'}
    updated = update_index(index, new_page)
    assert 'wiki/entities/test.md' in updated
```

### 集成测试

```python
def test_ingest_workflow_creates_wiki_pages():
    # 清理测试环境
    setup_test_env()

    # 执行 ingest
    result = ingest_source('raw/test/sample.md')

    # 验证
    assert result['created'] > 0
    assert file_exists('wiki/entities/test-service.md')
    assert file_exists('wiki/sources/summaries/test.md')
    assert index_updated('wiki/index.md')
```

### E2E 测试

```python
def test_full_cycle_query():
    # 1. Ingest
    ingest_source('raw/test/prd.md')

    # 2. Query
    answer = query('What is the authentication strategy?')

    # 3. Verify
    assert 'JWT' in answer
    assert 'raw/test/prd.md' in answer['sources']
```

---

## 🚦 边界定义

### Always Do（自动执行）
- ✅ 所有 wiki 页面必须有 frontmatter 元数据
- ✅ 所有断言必须引用源（`source: path:line`）
- ✅ 每次 ingest 必须更新 index.md 和 log.md
- ✅ Git 提交前必须运行 lint
- ✅ 检测到矛盾时必须标注（`⚠️ CONTRADICTION: ...`）

### Ask First（需要确认）
- ❓ 删除或重命名现有 wiki 页面
- ❓ 修改 schema.md 中的约定
- ❓ 批量 ingest > 10 个文件
- ❓ 覆盖用户手动编辑的内容
- ❓ 发送 API 请求到外部服务（除了 GLM）

### Never Do（禁止操作）
- ❌ 修改 raw/ 目录中的源文档
- ❌ 删除有源引用的 wiki 页面
- ❌ 在未经确认的情况下重构整个 wiki
- ❌ 暴露敏感信息到生成的文本中
- ❌ 自动推送到远程仓库（需要手动确认）

---

## 📊 成功指标

### 开发者体验
- **设置时间**：≤ 5 分钟
- **首次 ingest**：≤ 2 分钟（单个文档）
- **查询响应**：≤ 3 秒（使用索引）
- **学习曲线**：≤ 30 分钟掌握基本命令

### 知识质量
- **覆盖率**：≥ 90% 的源文档被索引
- **引用准确性**：100% 的断言有源引用
- **矛盾检测**：≤ 24 小时内标注新矛盾
- **孤立页面**：≤ 5% 的页面无入链

### 系统性能
- **索引大小**：index.md ≤ 1000 行（100 个源）
- **搜索时间**：≤ 1 秒（grep index.md）
- **LLM 调用**：≤ 10 次/ingest（单个源）
- **存储增长**：≤ 10 MB/月（100 个源/月）

---

## 🔄 后续增强（Phase 2+）

### 潜在功能
- [ ] Obsidian 插件（一键 ingest）
- [ ] 本地向量搜索（QMD 集成）
- [ ] 多模态支持（图片、图表）
- [ ] 团队协作（多用户 wiki）
- [ ] 自动化测试（wiki 驱动的集成测试）

### 集成点
- [ ] CI/CD pipeline（自动 ingest PRD）
- [ ] Slack bot（会议记录 → wiki）
- [ ] GitHub App（PR description → wiki）
- [ ] Jira integration（ticket → wiki）

---

## 📝 变更日志

### v1.0.0 (2026-04-07)
- ✅ 初始规格定义
- ✅ 架构设计
- ✅ 目录结构
- ✅ CLI 接口
- ✅ 页面模板

---

## 🙏 致谢

本设计深受 Andrej Karpathy 的 [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 启发。

---

**状态**: ⏳ 等待用户批准
