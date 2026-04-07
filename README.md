# LLM Wiki for Software Development

A persistent, LLM-maintained knowledge base for software development projects, integrated with Obsidian.

## 🌟 Features

- **Smart Ingest**: Automatically extract entities, concepts, and decisions from source documents
- **Knowledge Compounding**: Wiki grows richer with every addition, not just retrieval
- **Source Provenance**: Every claim has traceable references
- **Contradiction Detection**: Automatically flag conflicts between old and new information
- **Obsidian Integration**: Beautiful graph visualization and powerful search
- **Git Version Control**: Complete audit trail of all changes

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- GLM API key from [智谱 AI](https://open.bigmodel.cn/)
- Obsidian (optional, for visualization)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/llm-wiki.git
cd llm-wiki

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GLM_API_KEY
```

### First Ingest

```bash
# Ingest a single source document
python scripts/ingest.py --source raw/prds/feature-x.md

# Or run in interactive mode
python scripts/ingest.py --interactive
```

### Query Your Wiki

```bash
# Ask a question
python scripts/query.py "What is the authentication strategy?"

# Search for topics
python scripts/query.py --search "database migration"
```

### Health Check

```bash
# Run full health check
python scripts/lint.py --full

# Check only for contradictions
python scripts/lint.py --check contradictions
```

## 📁 Project Structure

```
llm-wiki/
├── raw/                   # Immutable source documents
│   ├── prds/             # Product requirements
│   ├── api-specs/        # API specifications
│   ├── meeting-notes/    # Meeting notes
│   ├── postmortems/      # Incident reports
│   └── assets/           # Images, diagrams
├── wiki/                  # LLM-maintained knowledge base
│   ├── entities/         # Services, APIs, decisions
│   ├── concepts/         # Architecture, patterns
│   ├── sources/          # Source summaries
│   ├── synthesis/        # High-level analysis
│   ├── index.md          # Content catalog
│   └── log.md            # Change history
├── scripts/               # CLI tools
│   ├── ingest.py         # Knowledge ingestion
│   ├── query.py          # Query and search
│   └── lint.py           # Health checks
└── config/                # Configuration
    ├── schema.md         # Wiki conventions
    └── glm_config.py     # GLM API config
```

## 🎯 Usage Examples

### Ingesting a PRD

```bash
python scripts/ingest.py --source raw/prds/user-auth.md
```

This will:
1. Extract entities (User Service, Auth API)
2. Identify concepts (JWT, OAuth2)
3. Create 10-15 cross-linked wiki pages
4. Update index.md
5. Append to log.md

### Querying for Decisions

```bash
python scripts/query.py "Why did we choose JWT over sessions?"
```

Output:
```markdown
According to `wiki/entities/services/auth-service.md`:45-60,
we chose JWT because:
1. Better scalability (no server-side session store)
2. Easier microservice integration
3. Mobile app support

Decision made on 2026-03-15 (see `wiki/log.md`)
```

### Checking for Contradictions

```bash
python scripts/lint.py --check contradictions
```

## 🔧 Configuration

### GLM API

Edit `.env`:
```bash
GLM_API_KEY=your-actual-api-key
GLM_MODEL=glm-4-flash  # or glm-4-plus
```

### Obsidian

1. Open this folder as a vault in Obsidian
2. Enable Graph View to see connections
3. Use Dataview plugin to query metadata
4. Install Obsidian Git for version control

## 📖 Documentation

- [Schema Reference](config/schema.md) - Wiki structure and conventions
- [CLI Reference](docs/cli-reference.md) - Command-line usage
- [Troubleshooting](docs/troubleshooting.md) - Common issues

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](docs/contributing.md)

## 📝 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

Inspired by Andrej Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

---

**Status**: 🚧 Under Active Development
**Version**: 0.1.0
**Last Updated**: 2026-04-07
