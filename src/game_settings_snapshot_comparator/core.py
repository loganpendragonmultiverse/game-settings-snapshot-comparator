"""Configuration parsing and comparison."""

from __future__ import annotations

import configparser
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Change:
    """One changed setting."""

    key: str
    before: str
    after: str


@dataclass(frozen=True)
class Comparison:
    """Deterministic comparison result."""

    before: str
    after: str
    added: tuple[tuple[str, str], ...]
    removed: tuple[tuple[str, str], ...]
    changed: tuple[Change, ...]
    unchanged_count: int

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-ready representation."""
        return asdict(self)


def value_text(value: object) -> str:
    """Render a JSON value without losing its type."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def flatten_json(value: object, prefix: str = "") -> dict[str, str]:
    """Flatten nested JSON objects and arrays into dotted keys."""
    if isinstance(value, dict):
        result: dict[str, str] = {}
        for key in sorted(value):
            child = f"{prefix}.{key}" if prefix else str(key)
            result.update(flatten_json(value[key], child))
        return result
    if isinstance(value, list):
        result = {}
        for index, item in enumerate(value):
            child = f"{prefix}[{index}]"
            result.update(flatten_json(item, child))
        return result
    return {prefix or "$": value_text(value)}


def parse_ini(text: str) -> dict[str, str]:
    """Parse INI while retaining section names."""
    parser = configparser.ConfigParser(interpolation=None)
    parser.read_string(text)
    result: dict[str, str] = {}
    for section in parser.sections():
        for key, value in parser.items(section):
            result[f"{section}.{key}"] = value
    return result


def parse_key_values(text: str) -> dict[str, str]:
    """Parse simple key=value snapshots."""
    result: dict[str, str] = {}
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", ";", "//")):
            continue
        if "=" not in stripped:
            raise ValueError(f"line {number} does not contain '='")
        key, value = stripped.split("=", 1)
        normalized = key.strip()
        if not normalized:
            raise ValueError(f"line {number} has an empty key")
        if normalized in result:
            raise ValueError(f"duplicate key on line {number}: {normalized}")
        result[normalized] = value.strip()
    return result


def load_snapshot(path: Path) -> dict[str, str]:
    """Load a JSON, INI, or simple key=value snapshot."""
    text = path.read_text(encoding="utf-8-sig")
    suffix = path.suffix.casefold()
    if suffix == ".json":
        return flatten_json(json.loads(text))
    if suffix in {".ini", ".cfg"} and any(
        line.lstrip().startswith("[") for line in text.splitlines()
    ):
        return parse_ini(text)
    return parse_key_values(text)


def compare(
    before_path: Path,
    after_path: Path,
    *,
    ignore: set[str] | None = None,
    redact_values: bool = False,
) -> Comparison:
    """Compare two snapshots, optionally excluding exact dotted keys."""
    excluded = {key.casefold() for key in (ignore or set())}
    try:
        return _compare(before_path, after_path, excluded, redact_values)
    except (OSError, UnicodeError, ValueError, configparser.Error):
        if redact_values:
            raise ValueError(
                "Cannot compare snapshots: input is unreadable or malformed."
            ) from None
        raise


def _compare(
    before_path: Path, after_path: Path, excluded: set[str], redact_values: bool
) -> Comparison:
    before = {
        key: value
        for key, value in load_snapshot(before_path).items()
        if key.casefold() not in excluded
    }
    after = {
        key: value
        for key, value in load_snapshot(after_path).items()
        if key.casefold() not in excluded
    }
    added = tuple((key, after[key]) for key in sorted(after.keys() - before.keys()))
    removed = tuple((key, before[key]) for key in sorted(before.keys() - after.keys()))
    shared = before.keys() & after.keys()
    changed = tuple(
        Change(key, before[key], after[key]) for key in sorted(shared) if before[key] != after[key]
    )
    unchanged = sum(before[key] == after[key] for key in shared)

    if redact_values:

        def marker(value: str, path: Path) -> str:
            kind = "string"
            if path.suffix.casefold() == ".json":
                parsed = json.loads(value)
                if parsed is None:
                    kind = "null"
                elif isinstance(parsed, bool):
                    kind = "boolean"
                elif isinstance(parsed, (int, float)):
                    kind = "number"
            return f"[redacted:{kind}]"

        added = tuple((key, marker(value, after_path)) for key, value in added)
        removed = tuple((key, marker(value, before_path)) for key, value in removed)
        changed = tuple(
            Change(item.key, marker(item.before, before_path), marker(item.after, after_path))
            for item in changed
        )
    return Comparison(str(before_path), str(after_path), added, removed, changed, unchanged)
