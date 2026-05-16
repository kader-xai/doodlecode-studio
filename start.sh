#!/usr/bin/env bash
#
# One-command launcher for DoodleCode Studio.
#
#   ./start.sh         # build the UI once, serve everything from :8000
#   ./start.sh --dev   # developer mode: vite hot-reload on :5173 + api :8000
#
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
MODE="prod"
if [[ "${1:-}" == "--dev" ]]; then
  MODE="dev"
fi

# ---------------------------- Backend setup -----------------------------
cd "$ROOT/backend"
if [ ! -d .venv ]; then
  echo "→ creating backend venv (first run)…"
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
python -m ipykernel install --user --name doodlecode --display-name "DoodleCode" \
  >/dev/null 2>&1 || true

# --------------------------- Frontend build -----------------------------
cd "$ROOT/frontend"
if [ ! -d node_modules ]; then
  echo "→ installing frontend dependencies (first run)…"
  npm install
fi

build_needed() {
  [ ! -f "$ROOT/frontend/dist/index.html" ] && return 0
  local newest_src
  newest_src=$(find src package.json vite.config.ts index.html \
    -type f -newer "$ROOT/frontend/dist/index.html" 2>/dev/null | head -1)
  [ -n "$newest_src" ]
}

if [[ "$MODE" == "prod" ]]; then
  if build_needed; then
    echo "→ building frontend (only runs when sources changed)…"
    npm run build
  fi
  cd "$ROOT/backend"
  echo ""
  echo "DoodleCode Studio is ready:"
  echo "  http://localhost:8000"
  echo ""
  exec uvicorn app.main:app --host 127.0.0.1 --port 8000
fi

# ----------------------- Developer mode (--dev) -------------------------
cd "$ROOT/backend"
uvicorn app.main:app --port 8000 --reload &
BACK_PID=$!
cd "$ROOT/frontend"
npm run dev &
FRONT_PID=$!
trap "kill $BACK_PID $FRONT_PID 2>/dev/null || true" EXIT INT TERM
echo ""
echo "DoodleCode Studio (developer mode):"
echo "  Backend:  http://localhost:8000  (API)"
echo "  Frontend: http://localhost:5173  (Vite, hot-reload)"
echo ""
wait
