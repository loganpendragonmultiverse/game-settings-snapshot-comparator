"""Create new reports without replacing inputs or existing files."""

from __future__ import annotations

import html
import io
import os
import sys
from pathlib import Path


def write_reports(sources: list[Path], reports: list[tuple[Path, str]]) -> None:
    """Validate every destination before creating any report exclusively."""
    seen: set[Path] = set()
    source_paths = {source.resolve() for source in sources}
    for path, _ in reports:
        if path.is_symlink():
            raise ValueError(f"report destination must not be a symlink: {path}")
        try:
            resolved = path.resolve()
        except RuntimeError as error:
            raise ValueError(f"cannot resolve report destination: {path}") from error
        if resolved in source_paths:
            raise ValueError("report destination must differ from input files")
        if resolved in seen:
            raise ValueError("report destinations must be distinct")
        if path.exists():
            raise FileExistsError(f"report already exists: {path}")
        seen.add(resolved)
    for path, text in reports:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(text)


def write_stdout(text: str) -> None:
    """Report real pipe errors before interpreter shutdown."""
    try:
        descriptor = sys.stdout.fileno()
    except (AttributeError, io.UnsupportedOperation):
        sys.stdout.write(text)
        sys.stdout.flush()
        return
    pending = text.encode(sys.stdout.encoding or "utf-8", sys.stdout.errors or "strict")
    while pending:
        written = os.write(descriptor, pending)
        if written <= 0:
            raise OSError("stdout write made no progress")
        pending = pending[written:]


def literal_text(value: str) -> str:
    """Keep authored text inside its Markdown line, cell or heading."""
    special = "\\`|*_[]!#~\n\r"
    return "".join(f"&#{ord(char)};" if char in special else html.escape(char) for char in value)


def code_text(value: str) -> str:
    """Preserve ordinary code styling and escape structural characters."""
    if any(char in "\x60|\n\r" for char in value):
        return literal_text(value)
    return f"`{value}`"
