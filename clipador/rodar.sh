#!/usr/bin/env bash
# Roda o clip-watcher com o python do .venv desta pasta.
cd "$(dirname "$0")" || exit 1
exec .venv/bin/python clip_watcher.py "$@"
