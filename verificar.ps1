$ErrorActionPreference = "Stop"
python -m pytest
python -m ruff check .
python -m mypy app
python -m bandit -r app -ll
