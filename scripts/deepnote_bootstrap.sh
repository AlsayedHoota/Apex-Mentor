#!/usr/bin/env bash
set -e

REPO_URL="https://github.com/AlsayedHoota/Apex-Mentor.git"
PROJECT_DIR="Apex-Mentor"
PORT="${APEX_PORT:-8000}"
HOST="${APEX_HOST:-0.0.0.0}"

printf "\n== Apex Mentor Deepnote bootstrap ==\n"

if ! command -v git >/dev/null 2>&1; then
  echo "git is required but was not found."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but was not found."
  exit 1
fi

if [ ! -d "$PROJECT_DIR" ]; then
  echo "Cloning Apex Mentor..."
  git clone "$REPO_URL" "$PROJECT_DIR"
else
  echo "Apex Mentor folder already exists. Pulling latest changes..."
  cd "$PROJECT_DIR"
  git pull --ff-only || true
  cd ..
fi

cd "$PROJECT_DIR"

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f ".env" ]; then
  echo "Creating .env..."
  cp .env.example .env
fi

python - <<'PY'
from pathlib import Path
import secrets

path = Path('.env')
text = path.read_text() if path.exists() else ''
if 'change-this-token-before-exposing' in text:
    token = secrets.token_urlsafe(48)
    text = text.replace('change-this-token-before-exposing', token)
    path.write_text(text)
    print('\nGenerated private APEX_AUTH_TOKEN in .env')
    print('Save this token somewhere safe:')
    print(token)
else:
    print('\n.env already has a custom APEX_AUTH_TOKEN')
PY

mkdir -p data

printf "\nStarting Apex Mentor on http://%s:%s\n" "$HOST" "$PORT"
printf "API docs path: /docs\n"
printf "\nTo expose it with Cloudflare Tunnel in another Deepnote terminal, run:\n"
printf "cloudflared tunnel --url http://127.0.0.1:%s\n\n" "$PORT"

uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
