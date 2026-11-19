#!/usr/bin/env bash
# Para os canais (todos, ou só o CANAL dado): manda Ctrl+C (SIGINT) e ESPERA o clip_watcher
# terminar os cortes, legendas e verticais pendentes. Uso: ./parar.sh [CANAL]
cd "$(dirname "$0")" || exit 1
if [ -n "$1" ]; then pids=("logs/$(echo "$1" | tr "[:upper:]" "[:lower:]").pid"); else pids=(logs/*.pid); fi
alvos=()
for f in "${pids[@]}"; do
  [ -f "$f" ] || continue
  c=$(basename "$f" .pid); pid=$(cat "$f")
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    echo "$c: mandando Ctrl+C (pid $pid), esperando terminar os cortes pendentes"
    kill -INT "$pid"; alvos+=("$c:$pid")
  else
    echo "$c: já estava parado"; rm -f "$f"
  fi
done
limite=$((SECONDS + ${ESPERA_MAX:-900}))
for a in "${alvos[@]}"; do
  c=${a%%:*}; pid=${a##*:}
  while kill -0 "$pid" 2>/dev/null; do
    if [ $SECONDS -ge $limite ]; then echo "$c: ainda terminando após ${ESPERA_MAX:-900} s (pid $pid); veja logs/$c.log"; continue 2; fi
    sleep 2
  done
  echo "$c: parado"; rm -f "logs/$c.pid"
done
[ ${#alvos[@]} -eq 0 ] && [ -z "$1" ] && echo "nada rodando"
exit 0
