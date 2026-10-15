import json
from pathlib import Path

import pytest

from game_settings_snapshot_comparator.cli import main, markdown
from game_settings_snapshot_comparator.core import compare


def test_nested_redaction_preserves_classifications_and_types(tmp_path: Path) -> None:
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    before.write_text(json.dumps({"nested": {"token": "SECRET_ONE"}, "removed": 12, "same": True}))
    after.write_text(json.dumps({"nested": {"token": "SECRET_TWO"}, "added": None, "same": True}))
    result = compare(before, after, redact_values=True)
    output = json.dumps(result.to_dict()) + markdown(result) + repr(result)
    assert "SECRET" not in output
    assert result.changed[0].key == "nested.token"
    assert result.changed[0].before == "[redacted:string]"
    assert result.added == (("added", "[redacted:null]"),)
    assert result.removed == (("removed", "[redacted:number]"),)
    assert result.unchanged_count == 1
    assert "SECRET_ONE" in markdown(compare(before, after))


@pytest.mark.parametrize(
    "suffix,text",
    [
        (".ini", "[section]\ntoken=SECRET\ntoken=SECRET_AGAIN"),
        (".json", '{"token": SECRET}'),
        (".txt", "token=SECRET\nbroken"),
        (".json", "\\ud800"),
    ],
)
def test_malformed_redacted_cli_hides_source(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], suffix: str, text: str
) -> None:
    path = tmp_path / ("input" + suffix)
    if text == "\\ud800":
        path.write_bytes(bytes([255]))
    else:
        path.write_text(text)
    with pytest.raises(SystemExit) as error:
        main([str(path), str(path), "--redact-values"])
    assert error.value.code == 2
    output = capsys.readouterr()
    assert "SECRET" not in output.out + output.err
    assert "unreadable or malformed" in output.err


def test_all_cli_outputs_are_redacted(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    before, after = tmp_path / "a.cfg", tmp_path / "b.cfg"
    before.write_text("token=SECRET_OLD")
    after.write_text("token=SECRET_NEW")
    target, md = tmp_path / "out.json", tmp_path / "out.md"
    assert (
        main(
            [
                str(before),
                str(after),
                "--redact-values",
                "--json",
                str(target),
                "--markdown",
                str(md),
            ]
        )
        == 1
    )
    assert "SECRET" not in capsys.readouterr().out + target.read_text() + md.read_text()
    assert compare(before, after, redact_values=True).changed


def test_redacted_boolean_types_and_missing_input(tmp_path: Path) -> None:
    before, after = tmp_path / "a.json", tmp_path / "b.json"
    before.write_text('{"flag": true, "values": [1]}')
    after.write_text('{"flag": false, "values": ["secret"]}')
    result = compare(before, after, redact_values=True)
    assert result.changed[0].before == "[redacted:boolean]"
    assert result.changed[1].before == "[redacted:number]"
    assert result.changed[1].after == "[redacted:string]"
    with pytest.raises(ValueError, match="unreadable or malformed"):
        compare(tmp_path / "missing.json", after, redact_values=True)
    with pytest.raises(OSError):
        compare(tmp_path / "missing.json", after)
