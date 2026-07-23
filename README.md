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

Version 1.0.0 is feature complete for the supported text formats. Contributions follow [CONTRIBUTING.md](CONTRIBUTING.md), security reports follow [SECURITY.md](SECURITY.md), and the project uses the MIT License.
