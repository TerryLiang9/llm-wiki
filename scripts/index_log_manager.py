"""
Index and Log Manager

This module manages the wiki index (index.md) and change log (log.md).
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import re


class IndexManager:
    """
    Manage the wiki index (index.md).

    The index provides a navigable catalog of all wiki pages.
    """

    def __init__(self, wiki_root: str = "wiki"):
        """
        Initialize index manager.

        Args:
            wiki_root: Root directory for wiki files
        """
        self.wiki_root = Path(wiki_root)
        self.index_path = self.wiki_root / "index.md"
        self.ensure_index()

    def ensure_index(self) -> None:
        """Ensure index.md exists."""
        if not self.index_path.exists():
            self.create_index()

    def create_index(self) -> None:
        """Create a new index.md file."""
        content = """# Wiki Index

Last updated: {date}

## Welcome to LLM Wiki

This index provides a navigation catalog for all wiki pages.

## Quick Links

- [Recent Changes](#recent-changes)
- [Entities](#entities)
- [Concepts](#concepts)
- [Sources](#sources)

## Statistics

- Total Pages: 0
- Total Sources: 0
- Last Update: {date}

---

## Entities

### Services
*No services documented yet*

### APIs
*No APIs documented yet*

### Decisions
*No decisions recorded yet*

---

## Concepts

### Architecture
*No architecture concepts yet*

### Patterns
*No patterns documented yet*

---

## Sources

### Summaries
*No source summaries yet*

---

## Recent Changes

`## [{date}] init | Wiki initialized`

Wiki structure created. Ready for first ingestion.
""".format(date=datetime.now().strftime("%Y-%m-%d"))

        self.index_path.write_text(content, encoding="utf-8")

    def add_page(
        self,
        page_path: str,
        page_type: str,
        category: str,
        title: str,
        summary: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add a page to the index.

        Args:
            page_path: Path to the wiki page
            page_type: Type of page (entity, concept, source-summary)
            category: Category within type
            title: Page title
            summary: One-line summary
            metadata: Additional metadata
        """
        content = self.index_path.read_text(encoding="utf-8")

        # Find the appropriate section
        section_pattern = self._get_section_pattern(page_type, category)

        # Check if section exists
        if section_pattern not in content:
            # Create section
            content = self._add_section(content, page_type, category)

        # Add page entry
        entry = f"- [{title}]({page_path}) - {summary}\n"

        # Insert after section header
        section_regex = re.compile(
            rf'(### {category.title()}\n)(\*No.*yet\*\n)?',
            re.IGNORECASE
        )

        def replace_func(match):
            header = match.group(1)
            existing = match.group(2) or ""
            if existing.startswith("*No"):
                # Replace placeholder
                return header + entry
            else:
                # Append to existing
                return header + existing + entry

        content = section_regex.sub(replace_func, content, count=1)

        # Update timestamp
        content = self._update_timestamp(content)

        # Update statistics
        content = self._update_statistics(content)

        # Write back
        self.index_path.write_text(content, encoding="utf-8")

    def _get_section_pattern(self, page_type: str, category: str) -> str:
        """Get the section pattern for a page type and category."""
        type_section = {
            "entity": "## Entities",
            "concept": "## Concepts",
            "source-summary": "## Sources",
        }.get(page_type, f"## {page_type.title()}")

        return f"{type_section}\n\n### {category.title()}"

    def _add_section(self, content: str, page_type: str, category: str) -> str:
        """Add a new section to the index."""
        type_section = {
            "entity": "## Entities",
            "concept": "## Concepts",
            "source-summary": "## Sources",
        }.get(page_type, f"## {page_type.title()}")

        # Find the main section
        main_section_pattern = rf"## {page_type.title()}"

        # Add subsection
        new_section = f"{type_section}\n\n### {category.title()}\n"

        # Insert before the next main section or end of file
        match = re.search(rf"\n## (?!{page_type.title()})", content)
        if match:
            insert_pos = match.start()
            content = content[:insert_pos] + new_section + content[insert_pos:]
        else:
            # Append to end
            content = content + "\n" + new_section

        return content

    def _update_timestamp(self, content: str) -> str:
        """Update the timestamp in the index."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        content = re.sub(
            r"Last updated: [0-9-]+",
            f"Last updated: {now}",
            content
        )
        return content

    def _update_statistics(self, content: str) -> str:
        """Update statistics in the index."""
        # Count pages
        page_count = len(re.findall(r"- \[.*\]\(wiki/.*\.md\)", content))

        # Count sources (source summaries)
        source_count = len(re.findall(r"\[.*\]\(wiki/sources/summaries/.*\.md\)", content))

        # Update statistics
        stats_pattern = r"## Statistics\n\n- Total Pages: [0-9]+\n- Total Sources: [0-9]+"
        stats_replacement = f"## Statistics\n\n- Total Pages: {page_count}\n- Total Sources: {source_count}"

        content = re.sub(stats_pattern, stats_replacement, content)

        return content

    def search(self, query: str) -> List[Dict[str, str]]:
        """
        Search the index for pages matching the query.

        Args:
            query: Search query

        Returns:
            List of matching pages with metadata
        """
        content = self.index_path.read_text(encoding="utf-8")
        results = []

        # Find all page links
        pattern = r"- \[(.*?)\]\((wiki/.*?\.md)\) - (.*?)(?=\n|$)"
        matches = re.findall(pattern, content, re.MULTILINE)

        query_lower = query.lower()

        for title, path, summary in matches:
            if (query_lower in title.lower() or
                query_lower in summary.lower() or
                query_lower in path.lower()):
                results.append({
                    "title": title,
                    "path": path,
                    "summary": summary.strip(),
                })

        return results

    def get_all_pages(self) -> List[Dict[str, str]]:
        """
        Get all pages from the index.

        Returns:
            List of all pages with metadata
        """
        content = self.index_path.read_text(encoding="utf-8")
        pages = []

        # Find all page links
        pattern = r"- \[(.*?)\]\((wiki/.*?\.md)\) - (.*?)(?=\n|$)"
        matches = re.findall(pattern, content, re.MULTILINE)

        for title, path, summary in matches:
            pages.append({
                "title": title,
                "path": path,
                "summary": summary.strip(),
            })

        return pages


class LogManager:
    """
    Manage the wiki change log (log.md).

    The log maintains a chronological record of all wiki operations.
    """

    def __init__(self, wiki_root: str = "wiki"):
        """
        Initialize log manager.

        Args:
            wiki_root: Root directory for wiki files
        """
        self.wiki_root = Path(wiki_root)
        self.log_path = self.wiki_root / "log.md"
        self.ensure_log()

    def ensure_log(self) -> None:
        """Ensure log.md exists."""
        if not self.log_path.exists():
            self.create_log()

    def create_log(self) -> None:
        """Create a new log.md file."""
        content = """# Wiki Log

This file maintains a chronological record of all wiki operations.

---

## [{datetime.now().strftime("%Y-%m-%d")}] init | Wiki Initialization

**Operation**: Initialize wiki structure

**Details**:
- Created directory structure
- Initialized index.md
- Initialized log.md

**Files Created**:
- wiki/index.md
- wiki/log.md
- raw/ (source directories)
- config/ (configuration files)

**Status**: ✅ Ready for first ingestion

---
"""
        self.log_path.write_text(content, encoding="utf-8")

    def append_entry(
        self,
        operation: str,
        details: Dict[str, Any],
    ) -> None:
        """
        Append an entry to the log.

        Args:
            operation: Operation type (ingest, query, lint, etc.)
            details: Operation details
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        entry = f"\n## [{timestamp}] {operation} | {details.get('title', 'Untitled')}\n\n"

        # Add details
        if "created" in details:
            entry += f"**Created**: {details['created']} pages\n"
        if "updated" in details:
            entry += f"**Updated**: {details['updated']} pages\n"
        if "entities" in details:
            entry += f"**Entities**: {', '.join(details['entities'])}\n"
        if "concepts" in details:
            entry += f"**Concepts**: {', '.join(details['concepts'])}\n"

        # Add files list
        if "files" in details:
            entry += "\n**Files**:\n"
            for file in details["files"]:
                entry += f"- {file}\n"

        # Add status
        if "status" in details:
            entry += f"\n**Status**: {details['status']}\n"

        # Add separator
        entry += "\n---\n"

        # Append to log
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(entry)

    def get_recent_entries(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent log entries.

        Args:
            count: Number of entries to return

        Returns:
            List of recent entries
        """
        content = self.log_path.read_text(encoding="utf-8")

        # Find all entries
        pattern = r"## \[(.*?)\] (.*?) \| (.*?)\n\n(.*?)(?=\n---\n|\n## \[|$)"
        matches = re.findall(pattern, content, re.DOTALL)

        entries = []
        for timestamp, operation, title, body in matches[-count:]:
            entries.append({
                "timestamp": timestamp,
                "operation": operation,
                "title": title,
                "body": body.strip(),
            })

        return list(reversed(entries))

    def get_entries_by_operation(self, operation: str) -> List[Dict[str, Any]]:
        """
        Get log entries filtered by operation type.

        Args:
            operation: Operation type to filter by

        Returns:
            List of matching entries
        """
        content = self.log_path.read_text(encoding="utf-8")

        # Find matching entries
        pattern = rf"## \[(.*?)\] ({operation}) \| (.*?)\n\n(.*?)(?=\n---\n|\n## \[|$)"
        matches = re.findall(pattern, content, re.DOTALL)

        entries = []
        for timestamp, op, title, body in matches:
            entries.append({
                "timestamp": timestamp,
                "operation": op,
                "title": title,
                "body": body.strip(),
            })

        return entries


# Convenience functions
def create_index_manager(wiki_root: str = "wiki") -> IndexManager:
    """Create an index manager."""
    return IndexManager(wiki_root=wiki_root)


def create_log_manager(wiki_root: str = "wiki") -> LogManager:
    """Create a log manager."""
    return LogManager(wiki_root=wiki_root)
