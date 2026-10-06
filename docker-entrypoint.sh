#!/bin/sh
set -eu

: "${JWT_SECRET:?JWT_SECRET debe configurarse en Coolify}"
: "${FIELD_ENCRYPTION_KEY:?FIELD_ENCRYPTION_KEY debe configurarse en Coolify}"

alembic upgrade head
python -m scripts.seed
python -m scripts.crear_admin
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips="*"
