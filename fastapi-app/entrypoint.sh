#!/bin/sh
set -e

python << 'EOF'
import os
import time
import socket

host = "db"
port = 5432

while True:
    try:
        with socket.create_connection((host, port), timeout=1):
            print("Database is ready!")
            break
    except OSError:
        print("Waiting for database...")
        time.sleep(0.5)
EOF

echo "Running migrations..."
uv run alembic upgrade head

echo "Starting FastAPI..."
exec uv run main.py
