# Game Settings Snapshot Comparator

> ⭐ **Gold Star Project**
> I consider this project complete. Fixes, maintenance and good new ideas are still welcome.
> [About Gold Stars](https://www.loganpendragonforge.com/open-source/?gold=1)
>
> Compare local game settings snapshots and review typed changes, with optional value redaction.

Game Settings Snapshot Comparator explains what changed between two local game configuration snapshots. It supports JSON, sectioned INI/CFG, and simple `key=value` text while keeping value types visible and leaving both files untouched.

## Three-minute use

Requires Python 3.10 or newer, with no runtime dependencies.

```sh
python -m pip install "game-settings-snapshot-comparator @ https://github.com/loganpendragonmultiverse/game-settings-snapshot-comparator/releases/download/v1.1.2/game_settings_snapshot_comparator-1.1.2-py3-none-any.whl"
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

## Version 1.1.2 — 2026-10-19

Report destinations must be new, distinct files, separate from every input. Existing files and symlink destinations are refused. Ordinary read, report-write and stdout failures return exit code 2. Inputs and existing reports are preserved. A later write failure can leave a partial new report or an already completed first report; inspect these paths and choose new names when retrying. Reports are not a multi-file or power-loss transaction.

JSON paths retain their existing dotted/indexed display. Literal keys remain supported when unambiguous; a duplicate flattened path, duplicate JSON key, or shared displayed path with different JSON structure is rejected rather than hiding a change. Exact ignored keys are excluded from cross-snapshot path checks. Empty objects and arrays remain visible and use object and array redaction markers when values are redacted. Keys and paths remain visible.

Supported scope: Compare two local JSON, INI/CFG or key-value snapshots, with typed differences and optional value redaction. No external data is fetched and no source file is rewritten.

Authored names, values and titles are escaped in Markdown reports so pipes, backticks, line breaks and HTML text remain report content. JSON values are unchanged.
