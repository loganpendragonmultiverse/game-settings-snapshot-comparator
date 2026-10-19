# Testing

Use Python >=3.10. Create and activate a clean virtual environment, then run:

```sh
python -m pip install -e '.[dev]'
ruff format --check .
ruff check .
mypy src tests
pytest
python -m build
```

The existing 90% coverage floor remains enforced. CI covers Python 3.10 and 3.14 on Linux, Windows, and macOS. Tests use synthetic inputs and preserve the default command-line workflow. No personal data is required.

## 1.1.2 report reliability — 2026-10-19

Preserve source bytes and existing reports. Refuse source aliases, symlinks, duplicate report destinations and files that appear immediately before exclusive creation. Cover ordinary file/encoding/stdout failures and retry at a new path. Run formatting, lint, strict typing, the full coverage suite, builds and dependency audit. Install wheel and source distributions separately outside the source tree; exercise primary workflows and error paths. Independent review and required CI precede merge/release. Publish actual tag-built artifacts with SHA256 checksums after installed acceptance; Gold qualification follows verified publication and catalog reconciliation.
