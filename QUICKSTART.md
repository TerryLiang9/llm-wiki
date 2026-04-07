# Quick Start Guide

Get started with LLM Wiki in 5 minutes!

## 🚀 Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure GLM API Key

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API key
# Get your key from: https://open.bigmodel.cn/
```

Edit `.env`:
```
GLM_API_KEY=your-actual-api-key-here
GLM_MODEL=glm-4-flash
```

### 3. Verify Setup

```bash
python -c "from scripts.glm_client import GLMClient; c = GLMClient(); print('✅ GLM client initialized')"
```

If you see "✅ GLM client initialized", you're ready!

---

## 📖 First Ingest

### Create a Test Document

Create `raw/prds/test-feature.md`:

```markdown
# User Authentication Feature

## Overview
Implement JWT-based authentication for user login and registration.

## Technical Approach

### API Endpoints
- POST /api/auth/register - User registration
- POST /api/auth/login - User login
- POST /api/auth/refresh - Token refresh

### Architecture
- Use JWT tokens for stateless authentication
- Store user credentials in PostgreSQL
- Use bcrypt for password hashing

### Design Decisions

**2026-04-07**: Chose JWT over session-based auth
- Better for microservice architecture
- No server-side session state
- Easier to scale

**2026-04-07**: Password hashing with bcrypt
- Proven security track record
- Adaptive work factor
- Built-in salt management

## Related Services
- User Service
- API Gateway
```

### Ingest the Document

```bash
# Ingest with confirmation
python scripts/ingest.py --source raw/prds/test-feature.md --interactive
```

Expected output:
```
📖 Reading: test-feature.md
🤖 Extracting entities and concepts...
📋 Extracted Information:
   Key Points: 5
   Entities (3):
      - User Service (service)
      - API Gateway (service)
      - Authentication API (api)
   Concepts (2):
      - JWT (architecture)
      - Microservice Architecture (architecture)
   Pages to Create: 5

Continue with ingestion? [y/N]: y
📝 Creating wiki pages...
✅ Ingestion complete!
   Created: 5 pages
   Updated: 0 pages
   Entities: User Service, API Gateway, Authentication API
   Concepts: JWT, Microservice Architecture
```

### View the Results

Open `wiki/index.md` to see the updated catalog:
```markdown
## Entities

### Services
- [User Service](wiki/entities/services/user-service.md) - User authentication and management
- [API Gateway](wiki/entities/services/api-gateway.md) - API routing and management

### APIs
- [Authentication API](wiki/entities/apis/authentication-api.md) - User authentication endpoints

## Concepts

### Architecture
- [JWT](wiki/concepts/architecture/jwt.md) - JSON Web Token authentication
- [Microservice Architecture](wiki/concepts/architecture/microservice-architecture.md) - Distributed system architecture
```

---

## 🔍 Query Your Wiki

### Ask a Question

```bash
python scripts/query.py "Why did we choose JWT over sessions?"
```

Expected output:
```
🔍 Searching wiki for: Why did we choose JWT over sessions?
📖 Found 2 relevant pages
🤖 Synthesizing answer...

💡 Answer:
According to the design decision made on 2026-04-07, JWT was chosen over
session-based authentication for several reasons:

1. **Better for microservice architecture**: JWTs are self-contained and
   don't require a centralized session store, making them ideal for
   distributed systems.

2. **No server-side session state**: Eliminates the need for session
   replication across services.

3. **Easier to scale**: Stateless nature allows horizontal scaling
   without session management complexity.

📚 Sources:
   - `wiki/entities/services/user-service.md`:design-decisions
   - `wiki/concepts/architecture/jwt.md`:trade-offs

🔗 Related:
   - wiki/concepts/architecture/microservice-architecture.md
   - wiki/entities/services/api-gateway.md
```

### Search for Topics

```bash
python scripts/query.py --search "authentication"
```

---

## 🧹 Run Health Checks

### Full Health Check

```bash
python scripts/lint.py --full
```

Expected output:
```
🔍 Running full health check...

🔬 Checking for contradictions...
   ✅ No contradictions found

🔍 Finding orphan pages...
   ✅ No orphan pages found

🕐 Checking for stale content...
   ✅ No stale pages found

🔗 Checking references...
   ✅ All references valid

📊 Summary:
   Total Issues: 0
   Critical: 0
   Warnings: 0
```

### Check Specific Issues

```bash
# Only check for contradictions
python scripts/lint.py --check contradictions

# Only find orphan pages
python scripts/lint.py --check orphans
```

---

## 📊 Generate Reports

```bash
# Generate a report on authentication
python scripts/query.py --report --output wiki/reports/auth-report.md "Authentication"
```

---

## 🎯 Obsidian Integration

### Open as Vault

1. Open Obsidian
2. Click "Open folder as vault"
3. Select this project directory
4. Enjoy graph visualization!

### Recommended Plugins

Install these plugins for enhanced experience:

- **Graph View**: Visualize connections (built-in)
- **Dataview**: Query wiki metadata
- **Obsidian Git**: Version control integration

### Use Graph View

Press `Ctrl/Cmd + G` to open the graph view and see:
- Entity connections
- Concept relationships
- Source references

---

## 📁 Project Structure

```
llm-wiki/
├── raw/                   # Your source documents
│   └── prds/
│       └── test-feature.md
├── wiki/                  # LLM-generated knowledge base
│   ├── entities/         # Services, APIs, decisions
│   ├── concepts/         # Architecture, patterns
│   ├── sources/          # Source summaries
│   ├── index.md          # Navigation catalog
│   └── log.md            # Change history
└── scripts/              # CLI tools
    ├── ingest.py         # Add knowledge
    ├── query.py          # Search and QA
    └── lint.py           # Health checks
```

---

## 🔄 Typical Workflow

### 1. Add Source Documents
```bash
# Copy documents to raw/ directory
cp my-prd.md raw/prds/
cp meeting-notes.md raw/meeting-notes/
```

### 2. Ingest Knowledge
```bash
# Ingest single document
python scripts/ingest.py --source raw/prds/my-prd.md

# Batch ingest
python scripts/ingest.py --batch raw/meeting-notes/
```

### 3. Query and Explore
```bash
# Ask questions
python scripts/query.py "What's our authentication strategy?"

# Search topics
python scripts/query.py --search "database"
```

### 4. Maintain Health
```bash
# Regular health checks
python scripts/lint.py --full
```

---

## 💡 Tips

### Ingestion Tips
- **Start small**: Ingest one document at a time first
- **Use interactive mode**: Review extracted info before confirming
- **Batch similar docs**: Group related documents for batch ingestion

### Query Tips
- **Be specific**: Detailed questions get better answers
- **Use quotes**: For exact phrases: `"database schema"`
- **Follow links**: Explore related topics suggested in answers

### Lint Tips
- **Run regularly**: Check for contradictions after each ingest
- **Fix orphans**: Link orphan pages to relevant topics
- **Update stale**: Review and update old content periodically

---

## 🐛 Troubleshooting

### GLM API Errors

**Error**: `GLM_API_KEY not found`
**Solution**: Make sure `.env` file exists with valid API key

**Error**: `Rate limit exceeded`
**Solution**: Wait a few minutes and try again, or upgrade to GLM-4-Plus

### Ingestion Issues

**No pages created**: Check that source document has meaningful content
**Extraction failed**: Try with simpler document first
**LLM timeout**: Use `--model glm-4-plus` for better reliability

### Query Issues

**No results found**: Use `--search` mode to find relevant pages
**Vague answers**: Be more specific in your question
**Missing sources**: Run ingest to add more knowledge

---

## 📚 Next Steps

1. **Ingest your documents**: Add PRDs, API docs, meeting notes
2. **Explore in Obsidian**: Open as vault and use graph view
3. **Customize schema**: Edit `config/schema.md` for your needs
4. **Set up automation**: Add to CI/CD pipeline

---

## 🎉 You're Ready!

Your LLM Wiki is now set up and ready to use. Start ingesting documents
and build your knowledge base!

**Repository**: https://github.com/TerryLiang9/llm-wiki
**Issues**: Report bugs at GitHub Issues
**Discussions**: Join the discussion at GitHub Discussions
