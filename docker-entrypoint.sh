#!/bin/sh
set -e

node /app/build/main.js --host 127.0.0.1 --port 4416 &

python3 - <<'PY'
import socket
import sys
import time

for _ in range(100):
    try:
        with socket.create_connection(("127.0.0.1", 4416), timeout=1):
            sys.exit(0)
    except OSError:
        time.sleep(0.2)

sys.exit("POT provider did not start on port 4416")
PY

exec gunicorn --bind "0.0.0.0:${PORT:-10000}" --workers 1 --threads 4 --timeout 180 app:app
