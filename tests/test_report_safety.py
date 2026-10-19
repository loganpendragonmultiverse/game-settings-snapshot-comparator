from __future__ import annotations

import io
import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest

from game_settings_snapshot_comparator import cli, output
from game_settings_snapshot_comparator.cli import main


def inputs(tmp_path: Path) -> list[Path]:
    paths = [tmp_path / "before.json", tmp_path / "after.json"]
    for index, path in enumerate(paths):
        path.write_text(json.dumps({"quality": index}))
    return paths


def invoke(paths: list[Path], *args: str) -> int:
    return main([*map(str, paths), *args])


@pytest.mark.parametrize("destination", ["source", "existing", "duplicate", "symlink"])
def test_refuse_destinations_before_writing(tmp_path: Path, destination: str) -> None:
    paths = inputs(tmp_path)
    before = [path.read_bytes() for path in paths]
    target = tmp_path / "report.json"
    second = tmp_path / "report.md"
    if destination == "source":
        second = paths[0]
    elif destination == "existing":
        second.write_text("keep")
    elif destination == "duplicate":
        second = target.parent / "." / target.name
    else:
        try:
            second.symlink_to(tmp_path / "missing")
        except OSError:
            pytest.skip("symlink creation unavailable on this platform")
    with pytest.raises(SystemExit) as exc:
        invoke(paths, "--json", str(target), "--markdown", str(second))
    assert exc.value.code == 2
    assert not target.exists()
    assert [path.read_bytes() for path in paths] == before
    if destination == "existing":
        assert second.read_text() == "keep"


def test_missing_parent_and_invalid_encoding_are_errors(tmp_path: Path) -> None:
    paths = inputs(tmp_path)
    with pytest.raises(SystemExit) as exc:
        invoke(paths, "--json", str(tmp_path / "missing" / "report.json"))
    assert exc.value.code == 2
    paths[0].write_bytes(b"\xff")
    with pytest.raises(SystemExit) as exc:
        invoke(paths)
    assert exc.value.code == 2


def test_exclusive_open_preserves_a_racing_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "racing.json"
    original = Path.open

    def racing_open(self: Path, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        if self == target and mode == "x":
            target.write_text("arrived")
        return original(self, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", racing_open)
    with pytest.raises(FileExistsError):
        output.write_reports([], [(target, "replacement")])
    assert target.read_text() == "arrived"


def test_output_io_failure_reaches_cli_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = inputs(tmp_path)

    def failed(*args: object) -> None:
        raise OSError("synthetic output failure")

    monkeypatch.setattr(cli, "write_stdout", failed)
    with pytest.raises(SystemExit) as exc:
        invoke(paths)
    assert exc.value.code == 2


def test_stdout_fallback_and_partial_writes(monkeypatch: pytest.MonkeyPatch) -> None:
    stream = io.StringIO()
    monkeypatch.setattr(sys, "stdout", stream)
    output.write_stdout("abc")
    assert stream.getvalue() == "abc"

    class Descriptor(io.StringIO):
        def fileno(self) -> int:
            return 123

    monkeypatch.setattr(sys, "stdout", Descriptor())
    seen: list[bytes] = []

    def short_write(fd: int, pending: bytes) -> int:
        seen.append(pending[:1])
        return 1

    monkeypatch.setattr(os, "write", short_write)
    output.write_stdout("abc")
    assert b"".join(seen) == b"abc"
    monkeypatch.setattr(os, "write", lambda fd, pending: 0)
    with pytest.raises(OSError, match="no progress"):
        output.write_stdout("x")
