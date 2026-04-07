"""
Ingest Module - Extract knowledge from source documents and update wiki.

This is the core module that processes source documents and creates
structured wiki pages.
"""

import os
import sys
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
import click

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.glm_client import GLMClient, GLMClientError
from scripts.page_generator import PageGenerator
from scripts.index_log_manager import IndexManager, LogManager


class IngestEngine:
    """
    Engine for ingesting source documents and updating the wiki.

    This orchestrates:
    1. Reading source documents
    2. Extracting entities and concepts using LLM
    3. Creating wiki pages
    4. Updating index and log
    """

    def __init__(
        self,
        glm_client: GLMClient,
        wiki_root: str = "wiki",
        raw_root: str = "raw",
    ):
        """
        Initialize ingest engine.

        Args:
            glm_client: GLM API client
            wiki_root: Wiki root directory
            raw_root: Raw source documents root directory
        """
        self.client = glm_client
        self.wiki_root = Path(wiki_root)
        self.raw_root = Path(raw_root)

        # Initialize managers
        self.page_generator = PageGenerator(wiki_root=wiki_root)
        self.index_manager = IndexManager(wiki_root=wiki_root)
        self.log_manager = LogManager(wiki_root=wiki_root)

    def ingest_source(
        self,
        source_path: str,
        interactive: bool = False,
    ) -> Dict[str, Any]:
        """
        Ingest a single source document.

        Args:
            source_path: Path to source document
            interactive: Whether to run in interactive mode

        Returns:
            Dictionary with ingestion results
        """
        source_file = Path(source_path)

        if not source_file.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        # Read source
        source_content = source_file.read_text(encoding="utf-8")
        source_hash = hashlib.md5(source_content.encode()).hexdigest()
        source_rel_path = str(source_file.relative_to(self.raw_root.parent))

        click.echo(f"📖 Reading: {source_file.name}")

        # Get existing wiki context
        existing_pages = self.index_manager.get_all_pages()
        existing_context = self._format_existing_context(existing_pages)

        # Extract knowledge using LLM
        click.echo("🤖 Extracting entities and concepts...")
        extracted = self._extract_knowledge(source_content, existing_context)

        if interactive:
            # Show extracted info and get confirmation
            self._show_extracted(extracted)
            if not click.confirm("Continue with ingestion?"):
                click.echo("❌ Ingestion cancelled")
                return {"cancelled": True}

        # Create wiki pages
        click.echo("📝 Creating wiki pages...")
        created_pages = []
        updated_pages = []

        # Create source summary
        source_summary_path = self.page_generator.create_source_summary(
            title=source_file.stem,
            source_path=source_rel_path,
            source_hash=source_hash,
            key_points=extracted.get("key_points", []),
            entities=extracted.get("entities", []),
            concepts=extracted.get("concepts", []),
            decisions=extracted.get("decisions", []),
            confidence=extracted.get("confidence", 0.8),
        )
        created_pages.append(source_summary_path)

        # Create entity pages
        for entity in extracted.get("pages_to_create", []):
            if entity["type"] == "entity":
                page_path = self.page_generator.create_entity_page(
                    name=entity["title"],
                    category=entity.get("category", "service"),
                    overview=entity.get("description", ""),
                    details=entity.get("details", ""),
                    sources=[source_rel_path],
                    tags=entity.get("tags", []),
                    related=[],
                    confidence=entity.get("confidence", 0.8),
                )
                created_pages.append(page_path)

                # Add to index
                self.index_manager.add_page(
                    page_path=page_path,
                    page_type="entity",
                    category=entity.get("category", "service"),
                    title=entity["title"],
                    summary=entity.get("description", ""),
                )

        # Create concept pages
        for concept in extracted.get("pages_to_create", []):
            if concept["type"] == "concept":
                page_path = self.page_generator.create_concept_page(
                    name=concept["title"],
                    category=concept.get("category", "architecture"),
                    definition=concept.get("description", ""),
                    tradeoffs_pros=concept.get("pros", []),
                    tradeoffs_cons=concept.get("cons", []),
                    good_scenarios=concept.get("good_scenarios", []),
                    bad_scenarios=concept.get("bad_scenarios", []),
                    examples=concept.get("examples", ""),
                    sources=[source_rel_path],
                    tags=concept.get("tags", []),
                    related=[],
                    confidence=concept.get("confidence", 0.8),
                )
                created_pages.append(page_path)

                # Add to index
                self.index_manager.add_page(
                    page_path=page_path,
                    page_type="concept",
                    category=concept.get("category", "architecture"),
                    title=concept["title"],
                    summary=concept.get("description", ""),
                )

        # Log the ingestion
        self.log_manager.append_entry(
            operation="ingest",
            details={
                "title": source_file.name,
                "created": len(created_pages),
                "updated": len(updated_pages),
                "entities": extracted.get("entities", []),
                "concepts": extracted.get("concepts", []),
                "files": created_pages + updated_pages,
                "status": "✅ Success",
            }
        )

        # Show results
        click.echo(f"\n✅ Ingestion complete!")
        click.echo(f"   Created: {len(created_pages)} pages")
        click.echo(f"   Updated: {len(updated_pages)} pages")
        click.echo(f"   Entities: {', '.join(extracted.get('entities', []) or ['None'])}")
        click.echo(f"   Concepts: {', '.join(extracted.get('concepts', []) or ['None'])}")

        return {
            "created": len(created_pages),
            "updated": len(updated_pages),
            "pages": created_pages + updated_pages,
            "entities": extracted.get("entities", []),
            "concepts": extracted.get("concepts", []),
        }

    def ingest_batch(
        self,
        source_dir: str,
        interactive: bool = False,
    ) -> Dict[str, Any]:
        """
        Ingest all source documents in a directory.

        Args:
            source_dir: Path to source directory
            interactive: Whether to run in interactive mode

        Returns:
            Dictionary with batch ingestion results
        """
        source_path = Path(source_dir)

        if not source_path.exists() or not source_path.is_dir():
            raise NotADirectoryError(f"Source directory not found: {source_dir}")

        # Find all supported files
        supported_extensions = {".md", ".txt", ".yaml", ".yml", ".json"}
        source_files = [
            f for f in source_path.rglob("*")
            if f.is_file() and f.suffix in supported_extensions
        ]

        if not source_files:
            click.echo(f"⚠️  No supported files found in {source_dir}")
            return {"skipped": True}

        click.echo(f"📦 Found {len(source_files)} files to ingest")

        if interactive:
            if not click.confirm(f"Ingest {len(source_files)} files?"):
                click.echo("❌ Batch ingestion cancelled")
                return {"cancelled": True}

        # Ingest each file
        results = {
            "total": len(source_files),
            "successful": 0,
            "failed": 0,
            "cancelled": 0,
            "files": [],
        }

        for source_file in source_files:
            try:
                result = self.ingest_source(str(source_file), interactive=False)
                if result.get("cancelled"):
                    results["cancelled"] += 1
                else:
                    results["successful"] += 1
                    results["files"].append({
                        "path": str(source_file),
                        "result": result,
                    })
            except Exception as e:
                click.echo(f"❌ Failed to ingest {source_file.name}: {e}")
                results["failed"] += 1

        # Show summary
        click.echo(f"\n📊 Batch ingestion complete!")
        click.echo(f"   Successful: {results['successful']}")
        click.echo(f"   Failed: {results['failed']}")
        click.echo(f"   Cancelled: {results['cancelled']}")

        return results

    def _extract_knowledge(
        self,
        source_content: str,
        existing_context: str,
    ) -> Dict[str, Any]:
        """
        Extract knowledge from source content using LLM.

        Args:
            source_content: Source document content
            existing_context: Existing wiki pages context

        Returns:
            Extracted knowledge dictionary
        """
        # Build prompt
        prompt = f"""You are a knowledge extraction expert for a software development wiki. Analyze the following source document and extract key information.

Source Document:
{source_content}

Existing Wiki Context:
{existing_context}

Extract and return ONLY a valid JSON object with this structure:
{{
  "key_points": ["point 1", "point 2", ...],
  "entities": [
    {{"name": "Entity Name", "type": "service|api|decision|component", "description": "brief description", "category": "service|api|decision|..."}}
  ],
  "concepts": [
    {{"name": "Concept Name", "type": "architecture|pattern|principle", "description": "brief description", "category": "architecture|pattern|..."}}
  ],
  "decisions": [
    {{"title": "Decision Title", "rationale": "why this decision", "date": "YYYY-MM-DD"}}
  ],
  "pages_to_create": [
    {{
      "type": "entity|concept",
      "title": "Page Title",
      "category": "category",
      "description": "Page description",
      "details": "Detailed information",
      "pros": ["pro 1", "pro 2"],
      "cons": ["con 1", "con 2"],
      "good_scenarios": ["scenario 1"],
      "bad_scenarios": ["scenario 2"],
      "examples": "Examples from the project",
      "tags": ["tag1", "tag2"],
      "confidence": 0.8
    }}
  ],
  "confidence": 0.8
}}

Focus on:
1. Extracting named entities (services, APIs, components)
2. Identifying technical concepts (patterns, principles)
3. Capturing decisions with rationale
4. Creating 5-15 wiki pages
5. Assigning appropriate categories and tags

Ensure the response is valid JSON only, no additional text.
"""

        try:
            response = self.client.complete_json(prompt)
            return response
        except GLMClientError as e:
            click.echo(f"⚠️  LLM extraction failed: {e}")
            # Return minimal structure
            return {
                "key_points": ["Failed to extract with LLM"],
                "entities": [],
                "concepts": [],
                "decisions": [],
                "pages_to_create": [],
                "confidence": 0.0,
            }

    def _format_existing_context(self, pages: List[Dict[str, str]]) -> str:
        """
        Format existing wiki pages as context for LLM.

        Args:
            pages: List of existing pages

        Returns:
            Formatted context string
        """
        if not pages:
            return "No existing wiki pages."

        context = "Existing wiki pages:\n"
        for page in pages[:20]:  # Limit to 20 pages
            context += f"- {page['title']}: {page['summary']}\n"

        return context

    def _show_extracted(self, extracted: Dict[str, Any]) -> None:
        """
        Show extracted information to user.

        Args:
            extracted: Extracted knowledge dictionary
        """
        click.echo("\n📋 Extracted Information:")
        click.echo(f"   Key Points: {len(extracted.get('key_points', []))}")
        for point in extracted.get('key_points', [])[:5]:
            click.echo(f"      - {point}")

        click.echo(f"\n   Entities ({len(extracted.get('entities', []))}):")
        for entity in extracted.get('entities', []):
            click.echo(f"      - {entity['name']} ({entity['type']})")

        click.echo(f"\n   Concepts ({len(extracted.get('concepts', []))}):")
        for concept in extracted.get('concepts', []):
            click.echo(f"      - {concept['name']} ({concept['type']})")

        click.echo(f"\n   Pages to Create: {len(extracted.get('pages_to_create', []))}")


# CLI Interface
@click.command()
@click.option(
    "--source",
    "-s",
    help="Path to source file to ingest",
    type=click.Path(exists=True),
)
@click.option(
    "--batch",
    "-b",
    help="Path to directory for batch ingestion",
    type=click.Path(exists=True, file_okay=False),
)
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="Run in interactive mode",
)
@click.option(
    "--model",
    default="glm-4-flash",
    help="GLM model to use (glm-4-flash or glm-4-plus)",
)
def main(source: Optional[str], batch: Optional[str], interactive: bool, model: str):
    """
    Ingest source documents into the wiki.

    Examples:

        # Ingest a single file
        python scripts/ingest.py --source raw/prds/feature-x.md

        # Batch ingest a directory
        python scripts/ingest.py --batch raw/meeting-notes/

        # Interactive mode
        python scripts/ingest.py --source raw/prds/feature-x.md --interactive
    """
    # Validate options
    if not source and not batch:
        click.echo("❌ Error: Please specify --source or --batch")
        sys.exit(1)

    if source and batch:
        click.echo("❌ Error: Please specify only one of --source or --batch")
        sys.exit(1)

    try:
        # Create GLM client
        client = GLMClient(model=model)

        # Create ingest engine
        engine = IngestEngine(glm_client=client)

        # Run ingestion
        if source:
            result = engine.ingest_source(source, interactive=interactive)
        else:
            result = engine.ingest_batch(batch, interactive=interactive)

        # Exit with appropriate code
        if result.get("cancelled"):
            sys.exit(1)
        elif result.get("failed", 0) > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        click.echo(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
