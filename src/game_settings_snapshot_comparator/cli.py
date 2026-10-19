"""Command-line interface."""

from __future__ import annotations

import argparse
import configparser
import json
from pathlib import Path

from game_settings_snapshot_comparator.core import Comparison, compare
from game_settings_snapshot_comparator.output import write_reports, write_stdout


def markdown(result: Comparison) -> str:
    """Render a readable comparison."""
    lines = [
        "# Game settings comparison",
        "",
        f"- Added: {len(result.added)}",
        f"- Removed: {len(result.removed)}",
        f"- Changed: {len(result.changed)}",
        f"- Unchanged: {result.unchanged_count}",
        "",
        "## Changed",
        "",
        "| Setting | Before | After |",
        "| --- | --- | --- |",
    ]
    lines.extend(f"| `{item.key}` | `{item.before}` | `{item.after}` |" for item in result.changed)
    for heading, entries in (("Added", result.added), ("Removed", result.removed)):
        lines.extend(["", f"## {heading}", ""])
        lines.extend(f"- `{key}` = `{value}`" for key, value in entries)
    return "\n".join(lines) + "\n"


def parser() -> argparse.ArgumentParser:
    """Build the parser."""
    result = argparse.ArgumentParser(description="Compare local game configuration snapshots.")
    result.add_argument("before", type=Path)
    result.add_argument("after", type=Path)
    result.add_argument("--ignore", action="append", default=[])
    result.add_argument("--json", type=Path, dest="json_output")
    result.add_argument("--markdown", type=Path, dest="markdown_output")
    result.add_argument(
        "--redact-values", action="store_true", help="Omit values; keys and paths remain visible."
    )
    return result


def main(argv: list[str] | None = None) -> int:
    """Run the command."""
    args = parser().parse_args(argv)
    try:
        result = compare(
            args.before, args.after, ignore=set(args.ignore), redact_values=args.redact_values
        )
        rendered = markdown(result)
        reports = []
        if args.json_output:
            reports.append((args.json_output, json.dumps(result.to_dict(), indent=2) + "\n"))
        if args.markdown_output:
            reports.append((args.markdown_output, rendered))
        write_reports([args.before, args.after], reports)
        write_stdout(rendered)
    except (OSError, ValueError, configparser.Error, UnicodeError) as error:
        parser().error(str(error))
    return 1 if result.added or result.removed or result.changed else 0
