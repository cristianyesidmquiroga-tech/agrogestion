#!/bin/sh
set -eu

: "${JWT_SECRET:?JWT_SECRET debe configurarse en Coolify}"
: "${FIELD_ENCRYPTION_KEY:?FIELD_ENCRYPTION_KEY debe configurarse en Coolify}"

python -m alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
