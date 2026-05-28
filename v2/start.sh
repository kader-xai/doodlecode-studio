#!/usr/bin/env bash
#
# DoodleCode Studio v2 launcher.
#
#   ./start.sh         # build the UI once, serve everything from :8001
#   ./start.sh --dev   # Vite hot-reload on :5174 + FastAPI on :8001
#
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
MODE="prod"
if [[ "${1:-}" == "--dev" ]]; then
  MODE="dev"
fi

# ----- Backend setup -----
cd "$ROOT/backend"
if [ ! -d .venv ]; then
  echo "→ creating v2 backend venv (first run)…"
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

# ----- Frontend setup -----
cd "$ROOT/frontend"
if [ ! -d node_modules ]; then
  echo "→ installing v2 frontend deps (first run)…"
  npm install
fi

if [[ "$MODE" == "prod" ]]; then
  echo "→ building frontend…"
  npm run build
fi

# ----- Launch -----
cd "$ROOT/backend"
if [[ "$MODE" == "dev" ]]; then
  (cd "$ROOT/frontend" && npm run dev) &
  VITE_PID=$!
  trap 'kill $VITE_PID 2>/dev/null || true' EXIT
  echo ""
  echo "DoodleCode Studio v2 (dev) is ready:"
  echo "  Vite:    http://localhost:5174"
  echo "  API:     http://localhost:8001"
  echo ""
  exec python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
else
  echo ""
  echo "DoodleCode Studio v2 is ready:"
  echo "  http://localhost:8001"
  echo ""
  exec python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
fi
