"""
Query Module - Search and query the wiki.

This module provides search and question-answering capabilities.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import click
import subprocess

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.glm_client import GLMClient, GLMClientError
from scripts.index_log_manager import IndexManager


class QueryEngine:
    """
    Engine for querying the wiki.

    This provides:
    1. Keyword search
    2. Natural language questions
    3. Report generation
    """

    def __init__(
        self,
        glm_client: GLMClient,
        wiki_root: str = "wiki",
    ):
        """
        Initialize query engine.

        Args:
            glm_client: GLM API client
            wiki_root: Wiki root directory
        """
        self.client = glm_client
        self.wiki_root = Path(wiki_root)
        self.index_manager = IndexManager(wiki_root=wiki_root)

    def search(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Search the wiki for pages matching the query.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching pages
        """
        results = self.index_manager.search(query)
        return results[:limit]

    def ask(self, question: str, write_back: bool = False) -> Dict[str, Any]:
        """
        Ask a natural language question and get an answer from the wiki.

        Args:
            question: Natural language question
            write_back: Whether to write the answer back to the wiki

        Returns:
            Answer dictionary
        """
        click.echo(f"🔍 Searching wiki for: {question}")

        # Search for relevant pages
        relevant_pages = self.search(question, limit=5)

        if not relevant_pages:
            click.echo("⚠️  No relevant pages found")
            return {"answer": "No relevant information found in the wiki."}

        click.echo(f"📖 Found {len(relevant_pages)} relevant pages")

        # Load page contents
        page_contents = []
        for page in relevant_pages:
            page_path = self.wiki_root.parent / page["path"]
            if page_path.exists():
                content = page_path.read_text(encoding="utf-8")
                # Remove frontmatter
                lines = content.split("\n")
                content_lines = []
                in_frontmatter = False
                for line in lines:
                    if line.strip() == "---":
                        if not in_frontmatter and not content_lines:
                            in_frontmatter = True
                        elif in_frontmatter:
                            in_frontmatter = False
                        continue
                    if not in_frontmatter:
                        content_lines.append(line)
                page_content = "\n".join(content_lines)

                page_contents.append({
                    "path": page["path"],
                    "title": page["title"],
                    "content": page_content[:2000],  # Limit content size
                })

        # Build context for LLM
        context = "\n\n---\n\n".join([
            f"## {p['title']}\n{p['content']}"
            for p in page_contents
        ])

        # Ask LLM to synthesize answer
        click.echo("🤖 Synthesizing answer...")
        answer = self._synthesize_answer(question, context, page_contents)

        # Display answer
        click.echo("\n💡 Answer:")
        click.echo(answer["answer"])

        if answer.get("sources"):
            click.echo("\n📚 Sources:")
            for source in answer["sources"]:
                click.echo(f"   - {source}")

        if answer.get("related"):
            click.echo("\n🔗 Related:")
            for related in answer["related"]:
                click.echo(f"   - {related}")

        # Write back to wiki if requested
        if write_back:
            self._write_back_answer(question, answer)

        return answer

    def generate_report(
        self,
        topic: str,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Generate a comprehensive report on a topic.

        Args:
            topic: Topic to generate report on
            output_path: Optional output file path

        Returns:
            Report content
        """
        click.echo(f"📊 Generating report on: {topic}")

        # Search for relevant pages
        relevant_pages = self.search(topic, limit=20)

        if not relevant_pages:
            return "No relevant information found."

        # Load full page contents
        page_contents = []
        for page in relevant_pages:
            page_path = self.wiki_root.parent / page["path"]
            if page_path.exists():
                content = page_path.read_text(encoding="utf-8")
                page_contents.append({
                    "path": page["path"],
                    "title": page["title"],
                    "content": content,
                })

        # Generate report
        click.echo("🤖 Generating report...")
        report = self._generate_report_content(topic, page_contents)

        # Write to file if specified
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(report, encoding="utf-8")
            click.echo(f"✅ Report written to: {output_path}")

        return report

    def _synthesize_answer(
        self,
        question: str,
        context: str,
        page_contents: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """
        Synthesize an answer using LLM.

        Args:
            question: User's question
            context: Relevant page contents
            page_contents: Page metadata

        Returns:
            Answer dictionary
        """
        prompt = f"""You are a knowledgeable assistant for a software development wiki. Answer the user's question based on the provided wiki pages.

Question: {question}

Relevant Wiki Pages:
{context}

Provide a comprehensive answer with:
1. Direct answer to the question
2. Supporting details from the wiki
3. Source citations (use format: `wiki/path/to/page.md`:section)
4. Related topics to explore
5. Suggestions for further investigation

Return ONLY valid JSON:
{{
  "answer": "Your detailed answer...",
  "sources": ["`wiki/path/to/page.md`:section", ...],
  "related": ["wiki/path/to/related.md", ...],
  "suggestions": ["suggestion 1", "suggestion 2"]
}}

Be specific and cite your sources. If the information is not in the wiki, say so.
"""

        try:
            response = self.client.complete_json(prompt)
            return response
        except GLMClientError as e:
            click.echo(f"⚠️  LLM synthesis failed: {e}")
            return {
                "answer": "Failed to synthesize answer. Please try again.",
                "sources": [],
                "related": [],
                "suggestions": [],
            }

    def _generate_report_content(
        self,
        topic: str,
        page_contents: List[Dict[str, str]],
    ) -> str:
        """
        Generate a report using LLM.

        Args:
            topic: Report topic
            page_contents: Page contents

        Returns:
            Report markdown
        """
        context = "\n\n---\n\n".join([
            f"## {p['title']}\n{p['content']}"
            for p in page_contents[:10]  # Limit pages
        ])

        prompt = f"""You are a technical writer. Generate a comprehensive report on the topic: {topic}

Available wiki pages:
{context}

Generate a well-structured report with:
1. Executive Summary
2. Background/Context
3. Key Findings
4. Detailed Analysis
5. Recommendations
6. Related Topics
7. Sources

Use markdown formatting. Include proper citations to source pages.

Return the report as markdown content only.
"""

        try:
            report = self.client.complete(prompt)
            return report
        except GLMClientError as e:
            click.echo(f"⚠️  Report generation failed: {e}")
            return f"# Report: {topic}\n\nFailed to generate report: {e}"

    def _write_back_answer(self, question: str, answer: Dict[str, Any]) -> None:
        """
        Write an answer back to the wiki as a new page.

        Args:
            question: Original question
            answer: Answer dictionary
        """
        from scripts.page_generator import PageGenerator

        generator = PageGenerator(wiki_root=str(self.wiki_root))

        # Generate filename from question
        filename = generator.slugify(question[:50]) + ".md"
        filepath = self.wiki_root / "synthesis" / filename

        # Build content
        content = f"""---
type: qa
category: synthesis
created: {click.ctx._date.strftime('%Y-%m-%d') if hasattr(click.ctx, '_date') else '2026-04-07'}
tags: [qa, synthesis]
---

# Q: {question}

## Answer
{answer['answer']}

## Sources
{chr(10).join(f"- {s}" for s in answer.get('sources', []))}

## Related
{chr(10).join(f"- {r}" for r in answer.get('related', []))}

## Suggestions
{chr(10).join(f"{i+1}. {s}" for i, s in enumerate(answer.get('suggestions', [])))}
"""

        # Write file
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content, encoding="utf-8")

        click.echo(f"✅ Answer written to: {filepath}")


# CLI Interface
@click.command()
@click.argument("query", required=False)
@click.option(
    "--search",
    "-s",
    is_flag=True,
    help="Search mode (keyword search)",
)
@click.option(
    "--report",
    "-r",
    is_flag=True,
    help="Generate a report",
)
@click.option(
    "--output",
    "-o",
    help="Output file for report",
    type=click.Path(),
)
@click.option(
    "--write-back",
    "-w",
    is_flag=True,
    help="Write answer back to wiki",
)
@click.option(
    "--model",
    default="glm-4-flash",
    help="GLM model to use",
)
def main(query: Optional[str], search: bool, report: bool, output: Optional[str], write_back: bool, model: str):
    """
    Query the wiki.

    Examples:

        # Ask a question
        python scripts/query.py "What is the authentication strategy?"

        # Search for topics
        python scripts/query.py --search "database migration"

        # Generate a report
        python scripts/query.py --report --output wiki/reports/q2-review.md "API Gateway"
    """
    if not query:
        click.echo("❌ Error: Please provide a query or use --search flag")
        sys.exit(1)

    try:
        # Create GLM client
        client = GLMClient(model=model)

        # Create query engine
        engine = QueryEngine(glm_client=client)

        if search:
            # Keyword search
            results = engine.search(query)
            click.echo(f"\n🔍 Search results for: {query}\n")
            if not results:
                click.echo("No results found")
            else:
                for i, result in enumerate(results, 1):
                    click.echo(f"{i}. {result['title']}")
                    click.echo(f"   {result['path']}")
                    click.echo(f"   {result['summary']}")
                    click.echo()

        elif report:
            # Generate report
            report_content = engine.generate_report(query, output_path=output)
            if not output:
                click.echo("\n📊 Report:")
                click.echo(report_content)

        else:
            # Natural language query
            answer = engine.ask(query, write_back=write_back)

        sys.exit(0)

    except Exception as e:
        click.echo(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
