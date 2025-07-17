#!/bin/bash

echo "[OpenAlgo] Starting up..."

mkdir -p db logs
chmod -R 777 db logs 2>/dev/null || echo "⚠️  Skipping chmod (volume may be mounted)"

# Run gunicorn using full path inside virtualenv
# Use FLASK_PORT environment variable, default to 5000 if not set
FLASK_PORT=${FLASK_PORT:-5000}
exec /app/.venv/bin/gunicorn --bind=0.0.0.0:$FLASK_PORT \
                              --worker-class=eventlet \
                              --workers=1 \
                              --log-level=info \
                              app:app
