# LLM Wiki for Software Development
# 软件开发项目的 LLM 知识库

<div align="center">

**A persistent, LLM-maintained knowledge base for software development projects**
**一个为软件开发项目设计的、由 LLM 维护的持久化知识库**

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GLM](https://img.shields.io/badge/GLM-4--Flash%20%7C%204--Plus-green.svg)](https://open.bigmodel.cn/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Active-success.svg)](https://github.com/TerryLiang9/llm-wiki)

</div>

---

## 📖 简介 / Introduction

**English**:

LLM Wiki is a persistent knowledge base system where an LLM (Large Language Model) incrementally builds and maintains a structured, interlinked collection of markdown files. Unlike traditional RAG (Retrieval-Augmented Generation) systems that re-derive knowledge on every query, LLM Wiki compiles knowledge once and keeps it current, allowing the knowledge base to compound and grow richer with every addition.

**中文**：

LLM Wiki 是一个持久化知识库系统，由 LLM（大语言模型）增量构建和维护结构化的、相互链接的 markdown 文件集合。与传统 RAG（检索增强生成）系统每次查询都重新推导知识不同，LLM Wiki 一次性编译知识并保持其更新，使知识库能够随着每次添加而复合增长，变得更加丰富。

### 🌟 核心特性 / Core Features

**English**:
- **🤖 Smart Ingest**: Automatically extract entities, concepts, and decisions from source documents
- **📚 Knowledge Compounding**: Wiki grows richer with every addition, not just retrieval
- **🔍 Source Provenance**: Every claim has traceable references
- **⚠️ Contradiction Detection**: Automatically flag conflicts between old and new information
- **🔗 Obsidian Integration**: Beautiful graph visualization and powerful search
- **📝 Git Version Control**: Complete audit trail of all changes

**中文**:
- **🤖 智能摄取**：自动从源文档中提取实体、概念和决策
- **📚 知识复利**：Wiki 随着每次添加而变得更加丰富，而不仅仅是检索
- **🔍 源引用追踪**：每个断言都有可追溯的引用
- **⚠️ 矛盾检测**：自动标注新旧信息之间的冲突
- **🔗 Obsidian 集成**：美观的图谱可视化和强大的搜索功能
- **📝 Git 版本控制**：所有更改的完整审计追踪

---

## 🏗️ 架构 / Architecture

**English**:

The system uses a three-layer architecture:

1. **Raw Sources**: Your immutable source documents (PRDs, API specs, meeting notes)
2. **The Wiki**: LLM-generated markdown files (entities, concepts, summaries)
3. **The Schema**: Configuration files that tell the LLM how to maintain the wiki

**中文**:

系统采用三层架构：

1. **原始源文档**：不可变的源文档（PRD、API 规范、会议记录）
2. **Wiki**：LLM 生成的 markdown 文件（实体、概念、摘要）
3. **Schema**：配置文件，告诉 LLM 如何维护 wiki

```
┌─────────────────────────────────────────────────────────┐
│                   Layer 3: The Schema                    │
│  ┌────────────────────────────────────────────────────┐  │
│  │  CLAUDE.md / AGENTS.md                             │  │
│  │  - Wiki 结构约定 / Structure conventions            │  │
│  │  - Ingest/Query/Lint 工作流 / Workflows            │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↕ 配置 / Config
┌─────────────────────────────────────────────────────────┐
│                   Layer 2: The Wiki                       │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Obsidian Vault (LLM 完全拥有 / LLM owned)         │  │
│  │  ├── entities/          (实体页面 / Entities)       │  │
│  │  ├── concepts/          (概念页面 / Concepts)       │  │
│  │  ├── sources/           (源摘要 / Summaries)        │  │
│  │  ├── synthesis/         (综合分析 / Analysis)       │  │
│  │  ├── index.md           (内容索引 / Content index)  │  │
│  │  └── log.md             (变更日志 / Change log)     │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↕ 读写 / Read-Write
┌─────────────────────────────────────────────────────────┐
│                  Layer 1: Raw Sources                     │
│  ┌────────────────────────────────────────────────────┐  │
│  │  raw/                                              │  │
│  │  ├── prds/              (产品需求 / PRDs)           │  │
│  │  ├── api-specs/         (API 规范 / API specs)      │  │
│  │  ├── meeting-notes/     (会议记录 / Meeting notes)  │  │
│  │  ├── postmortems/       (事故报告 / Postmortems)    │  │
│  │  └── assets/            (图片、图表 / Assets)       │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↕ 只读 / Read-Only
┌─────────────────────────────────────────────────────────┐
│           External: GLM API + Obsidian                   │
│  - GLM-4-Flash / GLM-4-Plus                             │
│  - Obsidian Graph View, Search, Plugins                 │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始 / Quick Start

### 前置要求 / Prerequisites

**English**:
- Python 3.10 or higher
- GLM API key from [智谱 AI](https://open.bigmodel.cn/) (Get your API key [here](https://open.bigmodel.cn/))
- Obsidian (optional, for visualization)

**中文**:
- Python 3.10 或更高版本
- 来自 [智谱 AI](https://open.bigmodel.cn/) 的 GLM API 密钥（在[这里](https://open.bigmodel.cn/)获取）
- Obsidian（可选，用于可视化）

### 安装步骤 / Installation

```bash
# 1. 克隆仓库 / Clone the repository
git clone https://github.com/TerryLiang9/llm-wiki.git
cd llm-wiki

# 2. 创建虚拟环境 / Create virtual environment
python -m venv .venv

# 激活虚拟环境 / Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 3. 安装依赖 / Install dependencies
pip install -r requirements.txt

# 4. 配置环境变量 / Set up environment variables
cp .env.example .env
# 编辑 .env 并添加你的 GLM_API_KEY
# Edit .env and add your GLM_API_KEY
```

### 第一次使用 / First Usage

**English**:

1. **Create a test document** in `raw/prds/test-authentication.md` (or use the provided example)
2. **Ingest the document**:

```bash
python scripts/ingest.py --source raw/prds/test-authentication.md --interactive
```

3. **Query your wiki**:

```bash
python scripts/query.py "Why did we choose JWT over sessions?"
```

4. **Run health check**:

```bash
python scripts/lint.py --full
```

**中文**：

1. **创建测试文档**，放在 `raw/prds/test-authentication.md`（或使用提供的示例）
2. **摄取文档**：

```bash
python scripts/ingest.py --source raw/prds/test-authentication.md --interactive
```

3. **查询你的 wiki**：

```bash
python scripts/query.py "为什么我们选择 JWT 而不是 sessions？"
```

4. **运行健康检查**：

```bash
python scripts/lint.py --full
```

---

## 📁 项目结构 / Project Structure

```
llm-wiki/
├── raw/                   # 不可变源文档 / Immutable source documents
│   ├── prds/             # 产品需求 / Product requirements
│   ├── api-specs/        # API 规范 / API specifications
│   ├── meeting-notes/    # 会议记录 / Meeting notes
│   ├── postmortems/      # 事故报告 / Incident reports
│   └── assets/           # 图片、图表 / Images, diagrams
├── wiki/                  # LLM 维护的知识库 / LLM-maintained knowledge base
│   ├── entities/         # 服务、API、决策 / Services, APIs, decisions
│   ├── concepts/         # 架构、模式 / Architecture, patterns
│   ├── sources/          # 源摘要 / Source summaries
│   ├── synthesis/        # 高级分析 / High-level analysis
│   ├── index.md          # 内容目录 / Content catalog
│   └── log.md            # 变更历史 / Change history
├── scripts/               # CLI 工具 / CLI tools
│   ├── glm_client.py     # GLM API 客户端 / GLM API client
│   ├── page_generator.py # 页面生成器 / Page generator
│   ├── index_log_manager.py # Index/Log 管理器 / Index/Log manager
│   ├── ingest.py         # 知识摄取 / Knowledge ingestion
│   ├── query.py          # 查询和搜索 / Query and search
│   └── lint.py           # 健康检查 / Health checks
├── config/                # 配置文件 / Configuration files
│   ├── schema.md         # Wiki 约定 / Wiki conventions
│   └── glm_config.py     # GLM 配置 / GLM configuration
├── tests/                 # 测试文件 / Test files
├── SPEC.md                # 项目规格说明 / Project specification
├── PLAN.md                # 实现计划 / Implementation plan
├── QUICKSTART.md          # 快速开始指南 / Quick start guide
└── README.md              # 项目说明 / Project documentation
```

---

## 🎯 使用示例 / Usage Examples

### 1. 摄取文档 / Ingesting Documents

**English**:

Ingest a single document with interactive confirmation:

```bash
python scripts/ingest.py --source raw/prds/user-auth.md --interactive
```

This will:
- Extract entities (User Service, Auth API)
- Identify concepts (JWT, OAuth2, Microservices)
- Create 10-15 cross-linked wiki pages
- Update index.md
- Append to log.md

**中文**：

以交互模式摄取单个文档：

```bash
python scripts/ingest.py --source raw/prds/user-auth.md --interactive
```

这将：
- 提取实体（用户服务、认证 API）
- 识别概念（JWT、OAuth2、微服务）
- 创建 10-15 个交叉链接的 wiki 页面
- 更新 index.md
- 追加到 log.md

**Batch ingestion** / **批量摄取**:

```bash
python scripts/ingest.py --batch raw/meeting-notes/
```

### 2. 查询知识库 / Querying the Wiki

**English**:

Ask natural language questions:

```bash
python scripts/query.py "What is the authentication strategy?"
```

Output example:
```
🔍 Searching wiki for: What is the authentication strategy?
📖 Found 3 relevant pages
🤖 Synthesizing answer...

💡 Answer:
According to the design decision made on 2026-04-07, the authentication
strategy uses JWT tokens for the following reasons:

1. **Better scalability**: No server-side session store required
2. **Microservice-friendly**: Stateless authentication
3. **Mobile app support**: Works well with native mobile apps

📚 Sources:
   - `wiki/entities/services/user-service.md`:design-decisions
   - `wiki/concepts/architecture/jwt.md`:trade-offs

🔗 Related:
   - wiki/concepts/architecture/microservice-architecture.md
   - wiki/entities/services/api-gateway.md
```

**中文**：

用自然语言提问：

```bash
python scripts/query.py "认证策略是什么？"
```

输出示例：
```
🔍 正在搜索：认证策略是什么？
📖 找到 3 个相关页面
🤖 正在合成答案...

💡 答案：
根据 2026-04-07 的设计决策，认证策略使用 JWT 令牌，
原因如下：

1. **更好的可扩展性**：不需要服务器端会话存储
2. **微服务友好**：无状态认证
3. **移动应用支持**：与原生移动应用配合良好

📚 来源：
   - `wiki/entities/services/user-service.md`:design-decisions
   - `wiki/concepts/architecture/jwt.md`:trade-offs

🔗 相关：
   - wiki/concepts/architecture/microservice-architecture.md
   - wiki/entities/services/api-gateway.md
```

**Keyword search** / **关键词搜索**:

```bash
python scripts/query.py --search "database migration"
```

### 3. 健康检查 / Health Checks

**English**:

Run a full health check to detect issues:

```bash
python scripts/lint.py --full
```

Output:
```
🔍 Running full health check...

🔬 Checking for contradictions...
   ✅ No contradictions found

🔍 Finding orphan pages...
   ⚠️  Found 2 orphan pages
      - wiki/entities/deprecated/old-service.md

🕐 Checking for stale content...
   ✅ No stale pages found

🔗 Checking references...
   ✅ All references valid

📊 Summary:
   Total Issues: 2
   Critical: 0
   Warnings: 2
```

**中文**：

运行完整的健康检查以检测问题：

```bash
python scripts/lint.py --full
```

输出：
```
🔍 正在运行完整健康检查...

🔬 检查矛盾...
   ✅ 未发现矛盾

🔍 查找孤立页面...
   ⚠️  发现 2 个孤立页面
      - wiki/entities/deprecated/old-service.md

🕐 检查过期内容...
   ✅ 未发现过期页面

🔗 检查引用...
   ✅ 所有引用有效

📊 总结：
   总问题数: 2
   严重: 0
   警告: 2
```

**Check specific issues** / **检查特定问题**:

```bash
# Only contradictions / 仅检查矛盾
python scripts/lint.py --check contradictions

# Only orphan pages / 仅检查孤立页面
python scripts/lint.py --check orphans

# Only stale content / 仅检查过期内容
python scripts/lint.py --check stale

# Only broken references / 仅检查损坏的引用
python scripts/lint.py --check references
```

---

## 🔧 配置 / Configuration

### GLM API 配置 / GLM API Configuration

**English**:

Edit `.env` file:

```bash
# Your GLM API key from https://open.bigmodel.cn/
GLM_API_KEY=your-actual-api-key-here

# Model selection: glm-4-flash (faster) or glm-4-plus (more capable)
GLM_MODEL=glm-4-flash

# Optional: Custom API base URL
# GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
```

**中文**：

编辑 `.env` 文件：

```bash
# 你的 GLM API 密钥，从 https://open.bigmodel.cn/ 获取
GLM_API_KEY=your-actual-api-key-here

# 模型选择：glm-4-flash（更快）或 glm-4-plus（更强大）
GLM_MODEL=glm-4-flash

# 可选：自定义 API 基础 URL
# GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
```

### Obsidian 配置 / Obsidian Configuration

**English**:

1. Open this project folder as a vault in Obsidian
2. Enable Graph View (Ctrl/Cmd + G) to see connections
3. Install recommended plugins:
   - **Dataview**: Query wiki metadata
   - **Obsidian Git**: Version control integration
   - **Advanced Tables**: Better table editing

**中文**：

1. 在 Obsidian 中将此项目文件夹打开为 vault
2. 启用图谱视图（Ctrl/Cmd + G）查看连接
3. 安装推荐的插件：
   - **Dataview**：查询 wiki 元数据
   - **Obsidian Git**：版本控制集成
   - **Advanced Tables**：更好的表格编辑

---

## 📖 文档 / Documentation

**English**:

- **[Quick Start Guide](QUICKSTART.md)** - Get started in 5 minutes
- **[Schema Reference](config/schema.md)** - Wiki structure and conventions
- **[Project Specification](SPEC.md)** - Detailed project requirements
- **[Implementation Plan](PLAN.md)** - Development roadmap

**中文**：

- **[快速开始指南](QUICKSTART.md)** - 5 分钟内上手
- **[Schema 参考](config/schema.md)** - Wiki 结构和约定
- **[项目规格说明](SPEC.md)** - 详细的项目需求
- **[实现计划](PLAN.md)** - 开发路线图

---

## 🤝 贡献 / Contributing

**English**:

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

**Areas where contributions are especially welcome**:
- Unit tests and integration tests
- Additional LLM provider integrations (OpenAI, Claude, etc.)
- Web UI for easier interaction
- Performance optimizations
- Documentation improvements

**中文**：

欢迎贡献！请随时提交 Pull Request。对于重大更改，请先打开 issue 讨论您想要更改的内容。

**特别欢迎贡献的领域**：
- 单元测试和集成测试
- 额外的 LLM 提供商集成（OpenAI、Claude 等）
- 更易于交互的 Web UI
- 性能优化
- 文档改进

---

## 🐛 常见问题 / FAQ

<details>
<summary><b>English: How do I get a GLM API key?</b></summary>
<br>

**中文: 如何获取 GLM API 密钥？**

1. Visit [https://open.bigmodel.cn/](https://open.bigmodel.cn/)
2. Register an account / 注册账户
3. Go to API Keys section / 进入 API 密钥部分
4. Create a new API key / 创建新的 API 密钥
5. Copy it to your `.env` file / 复制到你的 `.env` 文件

</details>

<details>
<summary><b>English: Can I use other LLM providers?</b></summary>
<br>

**中文: 我可以使用其他 LLM 提供商吗？**

Currently, only GLM (智谱 AI) is supported. However, the code is designed to be easily extensible. Contributions for additional providers are welcome!

目前仅支持 GLM（智谱 AI）。但是代码设计为易于扩展。欢迎贡献对其他提供商的支持！

</details>

<details>
<summary><b>English: How much does it cost to use GLM API?</b></summary>
<br>

**中文: 使用 GLM API 需要多少费用？**

GLM offers both free and paid tiers. Check [https://open.bigmodel.cn/pricing](https://open.bigmodel.cn/pricing) for current pricing. Generally, glm-4-flash is more cost-effective for large-scale usage.

GLM 提供免费和付费 tiers。查看 [https://open.bigmodel.cn/pricing](https://open.bigmodel.cn/pricing) 了解当前定价。通常，glm-4-flash 对于大规模使用更具成本效益。

</details>

<details>
<summary><b>English: How do I back up my wiki?</b></summary>
<br>

**中文: 如何备份我的 wiki？**

Your wiki is just a Git repository! Simply commit and push regularly:

你的 wiki 只是一个 Git 仓库！只需定期提交和推送：

```bash
git add .
git commit -m "Update wiki"
git push
```

You can also use the Obsidian Git plugin for automatic commits.

你也可以使用 Obsidian Git 插件进行自动提交。

</details>

---

## 🗺️ 路线图 / Roadmap

**English**:

- [x] **Phase 1**: Core infrastructure (GLM client, page generator, index/log manager)
- [x] **Phase 2**: Ingest functionality (single and batch)
- [x] **Phase 3**: Query and Lint functionality
- [x] **Phase 4**: Documentation and examples
- [ ] **Phase 5**: Unit and integration tests
- [ ] **Phase 6**: Advanced features (vector search, multi-modal support)
- [ ] **Phase 7**: Web UI

**中文**：

- [x] **阶段 1**：核心基础设施（GLM 客户端、页面生成器、索引/日志管理器）
- [x] **阶段 2**：摄取功能（单个和批量）
- [x] **阶段 3**：查询和健康检查功能
- [x] **阶段 4**：文档和示例
- [ ] **阶段 5**：单元测试和集成测试
- [ ] **阶段 6**：高级功能（向量搜索、多模态支持）
- [ ] **阶段 7**：Web UI

---

## 📝 许可证 / License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢 / Acknowledgments

**English**:

- Inspired by [Andrej Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- Built with [GLM-4](https://open.bigmodel.cn/) by 智谱 AI
- Integrated with [Obsidian](https://obsidian.md/)

**中文**：

- 灵感来自 [Andrej Karpathy 的 LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- 使用智谱 AI 的 [GLM-4](https://open.bigmodel.cn/) 构建
- 与 [Obsidian](https://obsidian.md/) 集成

---

## 📧 联系方式 / Contact

**English**:

- **Repository**: [https://github.com/TerryLiang9/llm-wiki](https://github.com/TerryLiang9/llm-wiki)
- **Issues**: [GitHub Issues](https://github.com/TerryLiang9/llm-wiki/issues)
- **Discussions**: [GitHub Discussions](https://github.com/TerryLiang9/llm-wiki/discussions)

**中文**：

- **仓库地址**：[https://github.com/TerryLiang9/llm-wiki](https://github.com/TerryLiang9/llm-wiki)
- **问题反馈**：[GitHub Issues](https://github.com/TerryLiang9/llm-wiki/issues)
- **讨论交流**：[GitHub Discussions](https://github.com/TerryLiang9/llm-wiki/discussions)

---

<div align="center">

**⭐ If you find this project helpful, please consider giving it a star!**
**⭐ 如果你觉得这个项目有帮助，请考虑给它一个星标！**

**🚧 Status**: Under Active Development / 积极开发中
**📦 Version**: 0.1.0
**📅 Last Updated**: 2026-04-07

Made with ❤️ by Terry Liang

</div>
