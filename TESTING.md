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
