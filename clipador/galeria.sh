#!/usr/bin/env bash
# Gera clipes/galeria.html (galeria de triagem dos clipes) com o python do .venv desta pasta.
#   ./galeria.sh                  gera uma vez
#   ./galeria.sh --assistir 30    regenera a cada 30 s (deixe a página aberta e dê F5)
#   ./galeria.sh --pasta clipes/_teste   outra pasta de clipes
# Mais opções no topo de galeria.py.
cd "$(dirname "$0")" || exit 1
exec .venv/bin/python galeria.py "$@"
