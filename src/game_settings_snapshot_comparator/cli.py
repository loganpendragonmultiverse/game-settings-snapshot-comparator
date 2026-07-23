"""Command-line interface."""

from __future__ import annotations

import argparse
import configparser
import json
from pathlib import Path

from game_settings_snapshot_comparator.core import Comparison, compare


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
    return result


def main(argv: list[str] | None = None) -> int:
    """Run the command."""
    args = parser().parse_args(argv)
    try:
        result = compare(args.before, args.after, ignore=set(args.ignore))
    except (OSError, ValueError, json.JSONDecodeError, configparser.Error) as error:
        parser().error(str(error))
    rendered = markdown(result)
    if args.json_output:
        args.json_output.write_text(json.dumps(result.to_dict(), indent=2) + "\n", encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 1 if result.added or result.removed or result.changed else 0
