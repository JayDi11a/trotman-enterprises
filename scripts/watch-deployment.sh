#!/bin/bash
# Continuously watch deployment status

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Starting deployment dashboard (updates every 30 seconds)"
echo "Press Ctrl+C to exit"
echo ""

while true; do
    "$SCRIPT_DIR/deployment-status.sh"
    sleep 30
done
