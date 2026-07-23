"""Behavior tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from game_settings_snapshot_comparator.cli import main, markdown
from game_settings_snapshot_comparator.core import (
    compare,
    flatten_json,
    load_snapshot,
    parse_key_values,
)


def write(path: Path, text: str) -> Path:
    """Write a snapshot fixture."""
    path.write_text(text, encoding="utf-8")
    return path


def test_json_flattening_preserves_types() -> None:
    assert flatten_json({"video": {"vsync": True}, "modes": ["a"]}) == {
        "modes[0]": '"a"',
        "video.vsync": "true",
    }


def test_compare_json_snapshots(tmp_path: Path) -> None:
    before = write(tmp_path / "before.json", '{"resolution":"1080p","volume":50,"old":true}')
    after = write(tmp_path / "after.json", '{"resolution":"1440p","volume":50,"new":false}')
    result = compare(before, after)
    assert result.changed[0].key == "resolution"
    assert result.added == (("new", "false"),)
    assert result.removed == (("old", "true"),)
    assert result.unchanged_count == 1


def test_ini_sections_are_kept(tmp_path: Path) -> None:
    path = write(tmp_path / "settings.ini", "[Video]\nWidth=1920\n[Audio]\nVolume=80\n")
    assert load_snapshot(path) == {"Video.width": "1920", "Audio.volume": "80"}


def test_key_value_comments_and_equals() -> None:
    assert parse_key_values("# note\nToken=a=b\n") == {"Token": "a=b"}


@pytest.mark.parametrize("text", ["broken", "=empty", "a=1\na=2"])
def test_invalid_key_value_input(text: str) -> None:
    with pytest.raises(ValueError):
        parse_key_values(text)


def test_ignore_exact_key(tmp_path: Path) -> None:
    before = write(tmp_path / "a.cfg", "session=1\nquality=high\n")
    after = write(tmp_path / "b.cfg", "session=2\nquality=high\n")
    assert not compare(before, after, ignore={"SESSION"}).changed


def test_cli_outputs_json_and_markdown(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    before = write(tmp_path / "a.cfg", "quality=low\n")
    after = write(tmp_path / "b.cfg", "quality=high\n")
    output = tmp_path / "result.json"
    assert main([str(before), str(after), "--json", str(output)]) == 1
    assert json.loads(output.read_text(encoding="utf-8"))["changed"][0]["key"] == "quality"
    assert "Changed: 1" in capsys.readouterr().out
    assert "| `quality`" in markdown(compare(before, after))


def test_identical_exit(tmp_path: Path) -> None:
    before = write(tmp_path / "a.cfg", "quality=high\n")
    after = write(tmp_path / "b.cfg", "quality=high\n")
    assert main([str(before), str(after)]) == 0
