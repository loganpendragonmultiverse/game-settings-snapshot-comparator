# Game Settings Snapshot Comparator

Game Settings Snapshot Comparator explains what changed between two local game configuration snapshots. It supports JSON, sectioned INI/CFG, and simple `key=value` text while keeping value types visible and leaving both files untouched.

## Three-minute use

```sh
python -m pip install "game-settings-snapshot-comparator @ https://github.com/loganpendragonmultiverse/game-settings-snapshot-comparator/releases/download/v1.0.0/game_settings_snapshot_comparator-1.0.0-py3-none-any.whl"
game-settings-compare before.ini after.ini --markdown changes.md --json changes.json
```

Use `--ignore sessionToken` repeatedly for exact volatile keys. The exit code is `1` when differences exist, `0` when snapshots match, and `2` for invalid input.

## Privacy and limitations

Processing is local and read-only. Reports may contain usernames, device identifiers, or tokens from supplied files; review them before sharing. The comparator does not understand proprietary binary formats, judge whether a setting is good, or promise that two differently formatted keys represent the same option.

## Development

```sh
python -m pip install -e ".[dev]"
ruff format --check . && ruff check .
mypy src tests
pytest
python -m build
```

The supported text formats remain bounded to JSON, INI/CFG, and key-value snapshots. Contributions follow [CONTRIBUTING.md](CONTRIBUTING.md), security reports follow [SECURITY.md](SECURITY.md), and the project uses the MIT License.

## More open-source projects

This project is part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Browse the catalog for other released tools, source repositories, live demos, and downloads.

## Optional value-redacted reports

Use `game-settings-compare before.json after.json --redact-values --json changes.json --markdown changes.md` to retain setting keys, value types, added/removed/changed classifications, and counts while omitting values. JSON primitive types appear as `[redacted:string]`, `[redacted:number]`, `[redacted:boolean]`, or `[redacted:null]`; INI/CFG and key-value entries are strings. Comparison happens before redaction, so two different secrets still count as changed. Invalid or unreadable redacted inputs produce a generic error without input contents.

Redaction is opt-in; default output continues to include values. **Setting names and input/output paths remain visible** and can themselves contain sensitive information. Redaction does not anonymize names or paths. No files are uploaded or modified.
