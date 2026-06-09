#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

BACKEND_PORT=8000
FRONTEND_PORT=5173
RUN_DIR="$ROOT_DIR/.run"
BACKEND_LOG="$RUN_DIR/backend.log"
FRONTEND_LOG="$RUN_DIR/frontend.log"

mkdir -p "$RUN_DIR"

kill_port() {
  local port="$1"
  local pids
  pids="$(lsof -ti "tcp:${port}" || true)"
  if [[ -n "$pids" ]]; then
    kill $pids || true
  fi
}

kill_port "$BACKEND_PORT"
kill_port "$FRONTEND_PORT"

sleep 0.5

: > "$BACKEND_LOG"
: > "$FRONTEND_LOG"

if [[ "${1:-}" == "--sqlite" ]]; then
  echo "Starting backend with sqlite override..."
  (DATABASE_URL="sqlite:///./ats_cv_maker.db" uv run uvicorn backend.src.api.app:app --host 127.0.0.1 --port "$BACKEND_PORT" --reload > "$BACKEND_LOG" 2>&1) &
else
  echo "Starting backend with DATABASE_URL from environment/.env..."
  (uv run uvicorn backend.src.api.app:app --host 127.0.0.1 --port "$BACKEND_PORT" --reload > "$BACKEND_LOG" 2>&1) &
fi
BACKEND_PID=$!

echo "Starting frontend..."
(cd "$ROOT_DIR/frontend" && npm run dev -- --host 127.0.0.1 --port "$FRONTEND_PORT" > "$FRONTEND_LOG" 2>&1) &
FRONTEND_PID=$!

echo ""
echo "Restart complete."
echo "Backend PID:  $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Backend URL:  http://127.0.0.1:${BACKEND_PORT}"
echo "Frontend URL: http://127.0.0.1:${FRONTEND_PORT}"
echo ""
echo "Logs:"
echo "  tail -f $BACKEND_LOG"
echo "  tail -f $FRONTEND_LOG"
