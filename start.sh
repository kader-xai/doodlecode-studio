#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

# --- Backend ---
cd "$ROOT/backend"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
# install ipykernel spec so jupyter_client can find it
python -m ipykernel install --user --name doodlecode --display-name "DoodleCode" >/dev/null 2>&1 || true

uvicorn app.main:app --port 8000 --reload &
BACK_PID=$!

# --- Frontend ---
cd "$ROOT/frontend"
if [ ! -d node_modules ]; then
  npm install
fi
npm run dev &
FRONT_PID=$!

trap "kill $BACK_PID $FRONT_PID 2>/dev/null || true" EXIT INT TERM

echo ""
echo "DoodleCode Studio:"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo ""
wait
