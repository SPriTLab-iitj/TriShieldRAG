#!/usr/bin/env bash
# tail_logs.sh — watch RAG-Shield activity live in a terminal during the demo.
mkdir -p logs
echo "Tailing logs/ragshield.log  (Ctrl-C to stop)"
touch logs/ragshield.log
tail -f logs/ragshield.log
