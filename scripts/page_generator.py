"""
Wiki Page Generator

This module generates wiki pages with proper frontmatter and formatting.
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import yaml


class PageGenerator:
    """
    Generate wiki pages with proper frontmatter and formatting.

    Features:
    - Frontmatter generation
    - Template rendering
    - Link generation
    - Source reference formatting
    """

    def __init__(self, wiki_root: str = "wiki"):
        """
        Initialize page generator.

        Args:
            wiki_root: Root directory for wiki files
        """
        self.wiki_root = Path(wiki_root)
        self.ensure_directories()

    def ensure_directories(self) -> None:
        """Ensure all wiki directories exist."""
        directories = [
            self.wiki_root / "entities",
            self.wiki_root / "concepts",
            self.wiki_root / "sources" / "summaries",
            self.wiki_root / "synthesis",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def generate_frontmatter(
        self,
        page_type: str,
        category: str,
        sources: List[str],
        tags: List[str],
        related: List[str],
        confidence: float = 1.0,
        **extra_fields
    ) -> str:
        """
        Generate YAML frontmatter for a wiki page.

        Args:
            page_type: Type of page (entity, concept, source-summary)
            category: Category within type
            sources: List of source file paths
            tags: List of tags
            related: List of related page paths
            confidence: Confidence score (0-1)
            **extra_fields: Additional frontmatter fields

        Returns:
            YAML frontmatter string
        """
        frontmatter = {
            "type": page_type,
            "category": category,
            "created": datetime.now().strftime("%Y-%m-%d"),
            "sources": sources,
            "tags": tags,
            "related": related,
            "confidence": confidence,
            **extra_fields
        }

        return yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)

    def create_entity_page(
        self,
        name: str,
        category: str,
        overview: str,
        details: str,
        sources: List[str],
        tags: List[str],
        related: List[str],
        confidence: float = 1.0,
    ) -> str:
        """
        Create an entity page.

        Args:
            name: Entity name
            category: Entity category (service, api, decision, etc.)
            overview: Brief overview
            details: Detailed information
            sources: Source file paths
            tags: Tags
            related: Related page paths
            confidence: Confidence score

        Returns:
            File path where page was created
        """
        # Generate filename
        filename = self.slugify(name) + ".md"
        filepath = self.wiki_root / "entities" / category / filename

        # Ensure category directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Generate frontmatter
        frontmatter = self.generate_frontmatter(
            page_type="entity",
            category=category,
            sources=sources,
            tags=tags,
            related=related,
            confidence=confidence,
        )

        # Generate related links
        related_links = self.format_related_links(related)

        # Generate source references
        source_references = self.format_source_references(sources)

        # Build page content
        content = f"""---
{frontmatter}---

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

        # Write file
        filepath.write_text(content, encoding="utf-8")

        return str(filepath.relative_to(self.wiki_root.parent))

    def create_concept_page(
        self,
        name: str,
        category: str,
        definition: str,
        tradeoffs_pros: List[str],
        tradeoffs_cons: List[str],
        good_scenarios: List[str],
        bad_scenarios: List[str],
        examples: str,
        sources: List[str],
        tags: List[str],
        related: List[str],
        confidence: float = 1.0,
    ) -> str:
        """
        Create a concept page.

        Args:
            name: Concept name
            category: Concept category (architecture, pattern, etc.)
            definition: Clear definition
            tradeoffs_pros: List of advantages
            tradeoffs_cons: List of disadvantages
            good_scenarios: Good use case scenarios
            bad_scenarios: Bad use case scenarios
            examples: Real examples from project
            sources: Source file paths
            tags: Tags
            related: Related page paths
            confidence: Confidence score

        Returns:
            File path where page was created
        """
        # Generate filename
        filename = self.slugify(name) + ".md"
        filepath = self.wiki_root / "concepts" / category / filename

        # Ensure category directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Generate frontmatter
        frontmatter = self.generate_frontmatter(
            page_type="concept",
            category=category,
            sources=sources,
            tags=tags,
            related=related,
            confidence=confidence,
        )

        # Build trade-offs table
        tradeoffs_table = self.build_tradeoffs_table(tradeoffs_pros, tradeoffs_cons)

        # Format scenarios
        when_to_use = self.format_scenarios(good_scenarios, bad_scenarios)

        # Generate source references
        source_references = self.format_source_references(sources)

        # Build page content
        content = f"""---
{frontmatter}---

# {name}

## Definition
{definition}

## Trade-offs
{tradeoffs_table}

## When to Use
{when_to_use}

## Examples in Project
{examples}

## Sources
{source_references}
"""

        # Write file
        filepath.write_text(content, encoding="utf-8")

        return str(filepath.relative_to(self.wiki_root.parent))

    def create_source_summary(
        self,
        title: str,
        source_path: str,
        source_hash: str,
        key_points: List[str],
        entities: List[str],
        concepts: List[str],
        decisions: List[str],
        confidence: float = 1.0,
    ) -> str:
        """
        Create a source summary page.

        Args:
            title: Source document title
            source_path: Path to source file
            source_hash: Hash of source content
            key_points: List of key points
            entities: List of entity names mentioned
            concepts: List of concept names introduced
            decisions: List of decisions recorded
            confidence: Confidence score

        Returns:
            File path where page was created
        """
        # Generate filename
        filename = self.slugify(title) + ".md"
        filepath = self.wiki_root / "sources" / "summaries" / filename

        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Generate frontmatter
        frontmatter = self.generate_frontmatter(
            page_type="source-summary",
            category="summary",
            sources=[source_path],
            tags=[],
            related=[],
            confidence=confidence,
            source=source_path,
            source_hash=source_hash,
            ingested=datetime.now().strftime("%Y-%m-%d"),
        )

        # Format lists
        key_points_md = self.format_list(key_points)
        entities_md = self.format_entity_links(entities)
        concepts_md = self.format_entity_links(concepts)
        decisions_md = self.format_list(decisions)

        # Build page content
        content = f"""---
{frontmatter}---

# {title} - Summary

## Key Points
{key_points_md}

## Entities Mentioned
{entities_md}

## Concepts Introduced
{concepts_md}

## Decisions Recorded
{decisions_md}

## Sources
- `{source_path}`:full
"""

        # Write file
        filepath.write_text(content, encoding="utf-8")

        return str(filepath.relative_to(self.wiki_root.parent))

    @staticmethod
    def slugify(text: str) -> str:
        """
        Convert text to slug format.

        Args:
            text: Text to slugify

        Returns:
            Slugified text
        """
        # Simple slugification
        slug = text.lower()
        slug = slug.replace(" ", "-")
        slug = slug.replace("_", "-")
        # Remove non-alphanumeric chars (except hyphens)
        slug = "".join(c if c.isalnum() or c == "-" else "" for c in slug)
        # Remove multiple consecutive hyphens
        slug = "-".join(filter(None, slug.split("-")))
        return slug

    @staticmethod
    def format_related_links(related: List[str]) -> str:
        """
        Format related page links.

        Args:
            related: List of related page paths

        Returns:
            Formatted markdown links
        """
        if not related:
            return "*No related pages yet*"

        links = []
        for page in related:
            # Extract filename from path
            filename = Path(page).stem
            # Use proper relative path from wiki root
            rel_path = page if page.startswith("wiki/") else f"wiki/{page}"
            links.append(f"- [{filename}]({rel_path})")

        return "\n".join(links)

    @staticmethod
    def format_source_references(sources: List[str]) -> str:
        """
        Format source file references.

        Args:
            sources: List of source file paths

        Returns:
            Formatted source references
        """
        if not sources:
            return "*No sources specified*"

        refs = []
        for source in sources:
            refs.append(f"- `{source}`:full")

        return "\n".join(refs)

    @staticmethod
    def build_tradeoffs_table(pros: List[str], cons: List[str]) -> str:
        """
        Build a trade-offs table.

        Args:
            pros: List of advantages
            cons: List of disadvantages

        Returns:
            Markdown table
        """
        max_rows = max(len(pros), len(cols))

        table = "| Pros | Cons |\n"
        table += "|------|------|\n"

        for i in range(max_rows):
            pro = pros[i] if i < len(pros) else ""
            con = cons[i] if i < len(cons) else ""
            table += f"| {pro} | {con} |\n"

        return table

    @staticmethod
    def format_scenarios(
        good: List[str],
        bad: List[str],
    ) -> str:
        """
        Format usage scenarios.

        Args:
            good: Good scenarios
            bad: Bad scenarios

        Returns:
            Formatted scenarios
        """
        lines = []

        if good:
            lines.append("### ✅ Good For")
            for scenario in good:
                lines.append(f"- {scenario}")

        if bad:
            lines.append("\n### ❌ Avoid For")
            for scenario in bad:
                lines.append(f"- {scenario}")

        return "\n".join(lines)

    @staticmethod
    def format_list(items: List[str]) -> str:
        """
        Format a list as markdown.

        Args:
            items: List of items

        Returns:
            Formatted list
        """
        if not items:
            return "*None*"

        return "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))

    @staticmethod
    def format_entity_links(entities: List[str]) -> str:
        """
        Format entity names as markdown links.

        Args:
            entities: List of entity names

        Returns:
            Formatted entity links
        """
        if not entities:
            return "*None*"

        links = []
        for entity in entities:
            slug = PageGenerator.slugify(entity)
            links.append(f"- [{entity}](wiki/entities/{slug}.md)")

        return "\n".join(links)


# Convenience functions
def create_generator(wiki_root: str = "wiki") -> PageGenerator:
    """
    Convenience function to create a page generator.

    Args:
        wiki_root: Root directory for wiki files

    Returns:
        PageGenerator instance
    """
    return PageGenerator(wiki_root=wiki_root)
