from __future__ import annotations

import json
from pathlib import Path

import pytest

from game_settings_snapshot_comparator.core import compare, flatten_json, load_snapshot


@pytest.mark.parametrize(
    "left,right",
    [
        ({"a.b": 1}, {"a": {"b": 1}}),
        ({"a[0]": 1}, {"a": [1]}),
        ({"$": 1}, 1),
        ({"": 1}, {"$": 1}),
    ],
)
def test_cross_snapshot_path_ambiguity(tmp_path: Path, left: object, right: object) -> None:
    before, after = tmp_path / "a.json", tmp_path / "b.json"
    before.write_text(json.dumps(left))
    after.write_text(json.dumps(right))
    with pytest.raises(ValueError, match="ambiguous flattened JSON path"):
        compare(before, after)
    with pytest.raises(ValueError, match="unreadable or malformed"):
        compare(before, after, redact_values=True)
    assert compare(before, after, ignore=set(flatten_json(left))).unchanged_count == 0


def test_literal_keys_remain_valid_and_local_collision_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "a.json"
    path.write_text('{"a.b":1,"a[0]":2,"":3}')
    assert load_snapshot(path) == {"a.b": "1", "a[0]": "2", "$": "3"}
    assert compare(path, path).unchanged_count == 3
    with pytest.raises(ValueError, match="ambiguous flattened JSON path"):
        flatten_json({"a.b": 1, "a": {"b": 2}})
    path.write_text('{"a":1,"a":2}')
    with pytest.raises(ValueError, match="duplicate JSON key"):
        load_snapshot(path)


def test_empty_container_presence_types_and_redaction(tmp_path: Path) -> None:
    before, after = tmp_path / "a.json", tmp_path / "b.json"
    before.write_text('{"a":{},"b":[],"gone":[],"typed":true}')
    after.write_text('{"a":[],"b":{},"new":{},"typed":1}')
    result = compare(before, after, redact_values=True)
    assert len(result.changed) == 3
    assert result.changed[0].before == "[redacted:object]"
    assert result.changed[0].after == "[redacted:array]"
    assert result.added == (("new", "[redacted:object]"),)
    assert result.removed == (("gone", "[redacted:array]"),)
    assert result.changed[2].before == "[redacted:boolean]"
    assert result.changed[2].after == "[redacted:number]"
    assert flatten_json({}) == {"$": "{}"}
    assert flatten_json([]) == {"$": "[]"}
