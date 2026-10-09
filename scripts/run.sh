#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python="$repo_root/.venv/bin/python"
[[ -x "$python" && -f "$repo_root/backend/app/main.py" && -d "$repo_root/frontend/node_modules" ]] || { echo 'Sift is not set up yet. Run scripts/setup.sh first.' >&2; exit 1; }
port="${SIFT_PORT:-8765}"
if command -v lsof >/dev/null 2>&1 && lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port $port is already in use. Choose another SIFT_PORT; Sift will not stop the owning process." >&2
  exit 1
fi
if command -v lsof >/dev/null 2>&1 && lsof -nP -iTCP:5173 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port 5173 is already in use. Stop the owning app; Sift will not stop it." >&2
  exit 1
fi
npm --prefix "$repo_root/frontend" run dev &
frontend_pid=$!
cleanup() { kill "$frontend_pid" 2>/dev/null || true; }
trap cleanup EXIT INT TERM
open "http://127.0.0.1:5173" >/dev/null 2>&1 || true
echo "Sift UI: http://127.0.0.1:5173 (Vite development server)"
echo 'Backend startup and model activity appear here. Press Ctrl+C to stop.'
cd "$repo_root"
"$python" -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port "$port"
