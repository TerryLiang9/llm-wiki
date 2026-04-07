"""
Lint Module - Health checks for the wiki.

This module checks for contradictions, orphan pages, stale content, etc.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import click
import re
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.glm_client import GLMClient, GLMClientError
from scripts.index_log_manager import IndexManager


class LintEngine:
    """
    Engine for linting the wiki.

    This provides:
    1. Contradiction detection
    2. Orphan page detection
    3. Stale content detection
    4. Reference validation
    """

    def __init__(
        self,
        glm_client: GLMClient,
        wiki_root: str = "wiki",
    ):
        """
        Initialize lint engine.

        Args:
            glm_client: GLM API client
            wiki_root: Wiki root directory
        """
        self.client = glm_client
        self.wiki_root = Path(wiki_root)
        self.index_manager = IndexManager(wiki_root=wiki_root)

    def run_full_check(self) -> Dict[str, Any]:
        """
        Run all health checks.

        Returns:
            Dictionary with check results
        """
        click.echo("🔍 Running full health check...\n")

        results = {
            "timestamp": click.ctx._date.strftime('%Y-%m-%dT%H:%M:%SZ') if hasattr(click.ctx, '_date') else '2026-04-07T00:00:00Z',
            "checks": {},
            "summary": {},
        }

        # Run all checks
        results["checks"]["contradictions"] = self.check_contradictions()
        click.echo("")

        results["checks"]["orphans"] = self.find_orphans()
        click.echo("")

        results["checks"]["stale"] = self.check_stale()
        click.echo("")

        results["checks"]["references"] = self.check_references()

        # Calculate summary
        total_issues = (
            len(results["checks"]["contradictions"]) +
            len(results["checks"]["orphans"]) +
            len(results["checks"]["stale"]) +
            len(results["checks"]["references"])
        )

        critical = len([
            i for check in results["checks"].values()
            for i in check
            if i.get("severity") == "critical"
        ])

        results["summary"] = {
            "total_issues": total_issues,
            "critical": critical,
            "warnings": total_issues - critical,
        }

        # Display summary
        click.echo("\n📊 Summary:")
        click.echo(f"   Total Issues: {results['summary']['total_issues']}")
        click.echo(f"   Critical: {results['summary']['critical']}")
        click.echo(f"   Warnings: {results['summary']['warnings']}")

        return results

    def check_contradictions(self) -> List[Dict[str, Any]]:
        """
        Check for contradictions between pages.

        Returns:
            List of contradiction findings
        """
        click.echo("🔬 Checking for contradictions...")

        contradictions = []

        # Get all pages
        all_pages = list(self.wiki_root.rglob("*.md"))
        all_pages = [p for p in all_pages if p.name not in ["index.md", "log.md"]]

        if len(all_pages) < 2:
            click.echo("   ✅ Not enough pages to check")
            return contradictions

        # Sample a few pages for contradiction checking
        # (Full check would be too expensive)
        sample_pages = all_pages[:5]

        for page in sample_pages:
            try:
                content = page.read_text(encoding="utf-8")
                # Find similar pages
                similar = self._find_similar_pages(page, all_pages)

                if similar:
                    # Use LLM to check for contradictions
                    finding = self._check_page_contradictions(page, similar)
                    if finding:
                        contradictions.extend(finding)
            except Exception as e:
                click.echo(f"   ⚠️  Error checking {page.name}: {e}")

        if contradictions:
            click.echo(f"   ❌ Found {len(contradictions)} potential contradictions")
            for c in contradictions[:3]:
                click.echo(f"      - {c['page']}: {c['issue']}")
        else:
            click.echo("   ✅ No contradictions found")

        return contradictions

    def find_orphans(self) -> List[Dict[str, Any]]:
        """
        Find orphan pages (no inbound links).

        Returns:
            List of orphan pages
        """
        click.echo("🔍 Finding orphan pages...")

        orphans = []
        all_pages = list(self.wiki_root.rglob("*.md"))
        all_pages = [p for p in all_pages if p.name not in ["index.md", "log.md"]]

        # Build link graph
        link_targets = set()
        for page in all_pages:
            try:
                content = page.read_text(encoding="utf-8")
                # Find all markdown links
                links = re.findall(r'\[([^\]]+)\]\((wiki/[^)]+)\)', content)
                for _, target in links:
                    # Extract just the file path
                    target_path = target.split("#")[0]
                    link_targets.add(target_path)
            except Exception:
                pass

        # Find pages with no inbound links
        for page in all_pages:
            rel_path = f"wiki/{page.relative_to(self.wiki_root)}"
            if rel_path not in link_targets:
                # Check if it's linked from index
                if not self._is_linked_in_index(page):
                    orphans.append({
                        "page": str(page.relative_to(self.wiki_root.parent)),
                        "reason": "No inbound links",
                        "severity": "info",
                    })

        if orphans:
            click.echo(f"   ⚠️  Found {len(orphans)} orphan pages")
            for o in orphans[:3]:
                click.echo(f"      - {o['page']}")
        else:
            click.echo("   ✅ No orphan pages found")

        return orphans

    def check_stale(self) -> List[Dict[str, Any]]:
        """
        Check for stale content.

        Returns:
            List of stale findings
        """
        click.echo("🕐 Checking for stale content...")

        stale = []
        all_pages = list(self.wiki_root.rglob("*.md"))
        all_pages = [p for p in all_pages if p.name not in ["index.md", "log.md"]]

        # Check for old pages
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=90)

        for page in all_pages:
            try:
                # Check file modification time
                mtime = datetime.fromtimestamp(page.stat().st_mtime)
                if mtime < cutoff:
                    stale.append({
                        "page": str(page.relative_to(self.wiki_root.parent)),
                        "issue": f"Last updated {mtime.strftime('%Y-%m-%d')}",
                        "suggestion": "Review and update if needed",
                        "severity": "info",
                    })
            except Exception:
                pass

        if stale:
            click.echo(f"   ⚠️  Found {len(stale)} potentially stale pages")
        else:
            click.echo("   ✅ No stale pages found")

        return stale

    def check_references(self) -> List[Dict[str, Any]]:
        """
        Check for broken references.

        Returns:
            List of reference issues
        """
        click.echo("🔗 Checking references...")

        issues = []
        all_pages = list(self.wiki_root.rglob("*.md"))

        for page in all_pages:
            try:
                content = page.read_text(encoding="utf-8")

                # Check source references
                source_refs = re.findall(r'`((raw|wiki)/[^`]+)`', content)
                for ref, _ in source_refs:
                    ref_path = Path(ref)
                    if not ref_path.exists():
                        issues.append({
                            "page": str(page.relative_to(self.wiki_root.parent)),
                            "issue": f"Broken reference: {ref}",
                            "severity": "warning",
                        })

                # Check wiki links
                wiki_links = re.findall(r'\[([^\]]+)\]\((wiki/[^)]+)\)', content)
                for _, target in wiki_links:
                    target_path = Path(target.split("#")[0])
                    if not target_path.exists():
                        issues.append({
                            "page": str(page.relative_to(self.wiki_root.parent)),
                            "issue": f"Broken wiki link: {target}",
                            "severity": "warning",
                        })

            except Exception:
                pass

        if issues:
            click.echo(f"   ⚠️  Found {len(issues)} reference issues")
        else:
            click.echo("   ✅ All references valid")

        return issues

    def _find_similar_pages(self, page: Path, all_pages: List[Path]) -> List[Path]:
        """Find pages similar to the given page."""
        # Simple implementation: pages with similar names
        name = page.stem.lower()
        similar = []

        for other in all_pages:
            if other == page:
                continue
            other_name = other.stem.lower()
            if name in other_name or other_name in name:
                similar.append(other)

        return similar[:3]

    def _check_page_contradictions(
        self,
        page: Path,
        similar_pages: List[Path],
    ) -> List[Dict[str, Any]]:
        """Use LLM to check for contradictions between pages."""
        try:
            content = page.read_text(encoding="utf-8")

            # Build context from similar pages
            similar_context = []
            for similar in similar_pages:
                similar_content = similar.read_text(encoding="utf-8")
                similar_context.append(f"## {similar.stem}\n{similar_content[:1000]}")

            context = "\n\n---\n\n".join(similar_context)

            prompt = f"""Check if the following page contains any contradictions with the provided similar pages.

Page to check:
## {page.stem}
{content[:1500]}

Similar pages:
{context}

Look for:
1. Direct factual contradictions
2. Conflicting decisions or approaches
3. Inconsistent information

Return ONLY valid JSON:
{{
  "contradictions": [
    {{
      "page": "{page.relative_to(self.wiki_root.parent)}",
      "issue": "Description of contradiction",
      "severity": "high|medium|low",
      "conflicts_with": "path/to/conflicting/page.md"
    }}
  ]
}}

If no contradictions found, return {{"contradictions": []}}
"""

            response = self.client.complete_json(prompt)
            return response.get("contradictions", [])

        except GLMClientError:
            return []

    def _is_linked_in_index(self, page: Path) -> bool:
        """Check if page is linked from index."""
        index_path = self.wiki_root / "index.md"
        if not index_path.exists():
            return False

        try:
            index_content = index_path.read_text(encoding="utf-8")
            page_name = page.stem
            return page_name in index_content
        except Exception:
            return False


# CLI Interface
@click.command()
@click.option(
    "--full",
    "-f",
    is_flag=True,
    help="Run full health check",
)
@click.option(
    "--check",
    "-c",
    type=click.Choice(["contradictions", "orphans", "stale", "references"]),
    help="Run specific check",
)
@click.option(
    "--output",
    "-o",
    help="Output report to file",
    type=click.Path(),
)
@click.option(
    "--model",
    default="glm-4-flash",
    help="GLM model to use",
)
def main(full: bool, check: Optional[str], output: Optional[str], model: str):
    """
    Run health checks on the wiki.

    Examples:

        # Run full check
        python scripts/lint.py --full

        # Check only for contradictions
        python scripts/lint.py --check contradictions

        # Output JSON report
        python scripts/lint.py --full --output report.json
    """
    if not full and not check:
        click.echo("❌ Error: Please specify --full or --check")
        sys.exit(1)

    try:
        # Create GLM client
        client = GLMClient(model=model)

        # Create lint engine
        engine = LintEngine(glm_client=client)

        # Run checks
        if full:
            results = engine.run_full_check()
            results_data = results
        else:
            if check == "contradictions":
                results_data = {"contradictions": engine.check_contradictions()}
            elif check == "orphans":
                results_data = {"orphans": engine.find_orphans()}
            elif check == "stale":
                results_data = {"stale": engine.check_stale()}
            elif check == "references":
                results_data = {"references": engine.check_references()}

            results = {
                "timestamp": "2026-04-07T00:00:00Z",
                "checks": results_data,
            }

        # Output report
        if output:
            output_path = Path(output)
            output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
            click.echo(f"\n✅ Report written to: {output}")

        # Exit with appropriate code
        total_issues = sum(len(v) for v in results.get("checks", {}).values())
        if total_issues > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        click.echo(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
