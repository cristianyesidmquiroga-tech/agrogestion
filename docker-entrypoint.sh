#!/bin/sh
set -e
alembic upgrade head
python -m scripts.seed
python -m scripts.crear_admin
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips="*"
