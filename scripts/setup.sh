#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
requirements="$repo_root/backend/requirements.txt"
frontend="$repo_root/frontend"
fail() { printf 'Setup cannot continue: %s\n' "$1" >&2; exit 1; }
[[ -f "$requirements" ]] || fail "backend/requirements.txt is not available yet. Builder A needs to provide it."
[[ -f "$frontend/package-lock.json" ]] || fail "frontend/package-lock.json is missing."

python=""
for candidate in python3.11 python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then python="$candidate"; break; fi
done
[[ -n "$python" ]] || fail "Python 3.11 or newer is required. Install it for your user, then rerun setup.sh."
for name in node npm ollama; do command -v "$name" >/dev/null 2>&1 || fail "$name is not installed or is not on PATH."; done
node -e 'const [major, minor] = process.versions.node.split(".").map(Number); if (!((major === 20 && minor >= 19) || (major >= 22 && (major > 22 || minor >= 12)))) process.exit(1)' || fail "Node.js $(node --version) is too old. Install Node.js 20.19+ or 22.12+."

[[ -d "$repo_root/.venv" ]] || "$python" -m venv "$repo_root/.venv"
"$repo_root/.venv/bin/python" -m pip install --upgrade pip
"$repo_root/.venv/bin/python" -m pip install -r "$requirements"
npm --prefix "$frontend" ci
npm --prefix "$frontend" run build
if ! ollama list; then echo 'Ollama is installed but not responding. Start it with: ollama serve' >&2; fi
cat <<'EOF'

Setup complete. No model was downloaded.
The embedding model is still being benchmarked with Builder A. Follow the exact model and prefix instructions they publish before indexing.
Ollama is installed. Start it with: ollama serve
Once Builder A confirms the model, install it explicitly with: ollama pull <confirmed-model-tag>
EOF
