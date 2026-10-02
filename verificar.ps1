$ErrorActionPreference = "Stop"
python -m pytest
python -m ruff check .
python -m mypy app
python -m bandit -r app -ll
python -m scripts.exportar_contrato --verificar
