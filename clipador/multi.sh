#!/usr/bin/env bash
# Sobe um clip_watcher por canal, em segundo plano (sobrevive ao fechar o terminal).
# Uso: ./multi.sh CANAL1 CANAL2 ... [--demo] [--manter] [--buffer N] [--fator X] [--minimo N] [--layout facecam]
# Log em logs/<canal>.log, PID em logs/<canal>.pid. Não sobe duplicado.
cd "$(dirname "$0")" || exit 1
mkdir -p logs
canais=(); extras=()
while [ $# -gt 0 ]; do
  case "$1" in
    --buffer|--fator|--minimo|--layout) extras+=("$1" "$2"); shift 2 ;;
    -*) extras+=("$1"); shift ;;
    *) canais+=("$(echo "$1" | tr "[:upper:]" "[:lower:]" | sed "s/^#//")"); shift ;;
  esac
done
[ ${#canais[@]} -eq 0 ] && { sed -n "2,4p" "$0" | sed "s/^# \{0,1\}//"; exit 1; }

vivo() { # $1 = arquivo de pid; sucesso se o pid existe e é um clip_watcher
  [ -f "$1" ] || return 1
  local pid; pid=$(cat "$1")
  [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null && tr "\0" " " < "/proc/$pid/cmdline" 2>/dev/null | grep -q clip_watcher
}

for c in "${canais[@]}"; do
  if vivo "logs/$c.pid"; then
    echo "$c: já está rodando (pid $(cat "logs/$c.pid")), não subi de novo"
    continue
  fi
  echo "=== $(date "+%F %T") subindo $c ${extras[*]}" >> "logs/$c.log"
  setsid nohup ./rodar.sh "$c" "${extras[@]}" >> "logs/$c.log" 2>&1 < /dev/null &
  echo $! > "logs/$c.pid"
  sleep 2
  if vivo "logs/$c.pid"; then
    echo "$c: no ar (pid $(cat "logs/$c.pid")), log em logs/$c.log"
  else # setsid pode ter feito fork: acha o processo pelo nome
    pid=$(pgrep -f "clip_watcher.py $c( |$)" | head -1)
    if [ -n "$pid" ]; then echo "$pid" > "logs/$c.pid"; echo "$c: no ar (pid $pid), log em logs/$c.log"
    else echo "$c: NÃO subiu, veja logs/$c.log"; rm -f "logs/$c.pid"; fi
  fi
done
