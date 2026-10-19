from game_settings_snapshot_comparator.cli import markdown
from game_settings_snapshot_comparator.core import Change, Comparison


def test_authored_text_cannot_change_table_structure() -> None:
    text = "mode|value`\n## Hidden <script>**"
    result = Comparison(
        "before", "after", ((text, text),), ((text, text),), (Change(text, text, text),), 0
    )
    before = result.to_dict()
    rendered = markdown(result)
    assert "\n## Hidden" not in rendered
    assert "<script>" not in rendered
    assert "&#124;" in rendered and "&#96;" in rendered and "&#10;" in rendered
    row = next(line for line in rendered.splitlines() if line.startswith("| mode"))
    assert row.count("|") == 4
    assert result.to_dict() == before
