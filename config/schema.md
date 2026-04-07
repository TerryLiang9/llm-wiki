# LLM Wiki Schema

This document defines the conventions and structure for the LLM-maintained wiki.

## Wiki Structure

```
wiki/
├── entities/          # Concrete things (services, APIs, decisions)
├── concepts/          # Abstract ideas (patterns, principles)
├── sources/           # Source document summaries
│   └── summaries/
└── synthesis/         # High-level analysis
    ├── timeline.md
    └── roadmap.md
```

## Page Types

### Entity Pages

**Location**: `wiki/entities/{category}/{name}.md`

**Frontmatter**:
```yaml
---
type: entity
category: service | api | decision | ...
created: YYYY-MM-DD
sources: [raw/path/to/source.md]
tags: [tag1, tag2, ...]
related: [path/to/related.md]
confidence: 0.0-1.0
---

# Entity Name

## Overview
[Brief description]

## Details
[Detailed information]

## Related
- [Related Page](path/to/related.md)

## Sources
- `raw/path/to/source.md`:line-range
```

### Concept Pages

**Location**: `wiki/concepts/{category}/{name}.md`

**Frontmatter**:
```yaml
---
type: concept
category: architecture | pattern | principle | ...
created: YYYY-MM-DD
sources: [raw/path/to/source.md]
tags: [tag1, tag2, ...]
related: [path/to/related.md]
---

# Concept Name

## Definition
[Clear definition]

## Trade-offs
| Pros | Cons |
|------|------|
| ...  | ...  |

## When to Use
- ✅ Good scenarios
- ❌ Bad scenarios

## Examples
[Real examples from the project]

## Sources
- `raw/path/to/source.md`:line-range
```

### Source Summary Pages

**Location**: `wiki/sources/summaries/{source-name}.md`

**Frontmatter**:
```yaml
---
type: source-summary
source: raw/path/to/source.md
source_hash: abc123
ingested: YYYY-MM-DD
confidence: 0.0-1.0
---

# Source Title - Summary

## Key Points
1. Point one
2. Point two

## Entities Mentioned
- [Entity](path/to/entity.md)

## Concepts Introduced
- [Concept](path/to/concept.md)

## Decisions Recorded
- Decision with date

## Sources
- `raw/path/to/source.md`:full
```

## Conventions

### File Naming
- Use `kebab-case` for all file names
- Entity names should be descriptive: `user-service.md`
- Concept names should be abstract: `event-driven-architecture.md`

### Linking
- Use relative paths: `[Page](path/to/page.md)`
- Use `![[Page]]` for Obsidian-style links (optional)
- Always link related pages in frontmatter

### Source References
- Format: `` `raw/path/to/source.md`:`line-range` ``
- Example: `` `raw/prds/feature-x.md`:45-60 ``
- For entire source: `` `raw/prds/feature-x.md`:full ``

### Tags
- Use lowercase tags
- Separate with hyphens for multi-word: `microservice`, `event-driven`
- Common tags: `service`, `api`, `architecture`, `pattern`, `decision`

## Content Guidelines

### What to Include
- ✅ Key decisions and rationale
- ✅ Important trade-offs
- ✅ Relationships between components
- ✅ Source references for all claims
- ✅ Confidence scores for uncertain info

### What to Exclude
- ❌ Duplicate information
- ❌ Implementation details (use code comments)
- ❌ Transient discussions (use commit messages)
- ❌ Personal opinions (mark as such if included)

## Maintenance

### When to Update
- New information contradicts old (add `⚠️ CONTRADICTION:` marker)
- Source document is updated (re-ingest)
- New relationship discovered (add related link)

### When to Delete
- Source is removed from project (mark as `DEPRECATED` first)
- Information is proven wrong (add correction, don't delete)

### Version Control
- All wiki pages are under Git version control
- Each ingest creates a new commit
- Use commit messages: `feat(wiki): ingest Feature X PRD`

## LLM Workflow

### Ingest
1. Read source document
2. Extract entities and concepts
3. Create/update wiki pages
4. Update index.md
5. Append to log.md

### Query
1. Search index.md for relevant pages
2. Load related wiki pages
3. Synthesize answer with citations
4. Optionally write back to wiki

### Lint
1. Check for contradictions (new vs old)
2. Find orphan pages (no inbound links)
3. Validate source references
4. Flag outdated content
5. Generate health report

## Obsidian Integration

### Recommended Plugins
- **Graph View**: Visualize connections
- **Dataview**: Query frontmatter metadata
- **Obsidian Git**: Version control integration
- **Advanced Tables**: Better table editing

### Graph View Configuration
- Enable in `.obsidian/graph.json`
- Use different colors for different page types
- Filter out `sources/summaries` for cleaner graph

### Search
- Use `Ctrl/Cmd + Shift + F` for global search
- Search index.md first for navigation
- Use tag search: `tag:#service`

---

**Last Updated**: 2026-04-07
**Version**: 1.0.0
