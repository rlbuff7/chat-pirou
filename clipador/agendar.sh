#!/usr/bin/env bash
# Espera até INICIO, roda o auto_lancamento.py até ATE e mantém esta sessão do WSL viva até MANTER
# (o WSL desliga quando nenhum terminal está conectado, e isso mataria a gravação).
# Uso: ./agendar.sh [INICIO=07:40] [ATE=10:30] [MANTER=12:00]
cd "$(dirname "$0")" || exit 1
mkdir -p logs
inicio="${1:-07:40}"; ate="${2:-10:30}"; manter="${3:-12:00}"
alvo=$(date -d "$inicio" +%s)
[ "$alvo" -le "$(date +%s)" ] && alvo=$(date -d "tomorrow $inicio" +%s)
echo "$(date '+%F %T') agendado: procura de $inicio ate $ate; WSL acordado ate $manter" | tee -a logs/auto.log
sleep $(( alvo - $(date +%s) ))
.venv/bin/python auto_lancamento.py --ate "$ate"
fim=$(date -d "$manter" +%s)
[ "$fim" -le "$(date +%s)" ] && fim=$(date -d "tomorrow $manter" +%s)
while [ "$(date +%s)" -lt "$fim" ]; do sleep 60; done
echo "$(date '+%F %T') agendar.sh terminou (canais ligados continuam ate ./parar.sh)" | tee -a logs/auto.log
