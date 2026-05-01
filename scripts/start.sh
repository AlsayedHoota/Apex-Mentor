#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but was not found."
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv .venv
fi

source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f ".env" ]; then
  echo "Creating .env from .env.example..."
  cp .env.example .env
fi

mkdir -p data

HOST=$(python - <<'PY'
from app.config import get_settings
print(get_settings().host)
PY
)

PORT=$(python - <<'PY'
from app.config import get_settings
print(get_settings().port)
PY
)

echo "Starting Apex Mentor at http://${HOST}:${PORT}"
echo "API docs: http://${HOST}:${PORT}/docs"
echo "Stop with Ctrl+C"

uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
