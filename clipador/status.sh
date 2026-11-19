#!/usr/bin/env bash
# Resumo de cada canal: vivo?, desde quando, picos/clipes/verticais, último pico, buffer, disco.
cd "$(dirname "$0")" || exit 1
for f in logs/*.pid; do
  [ -f "$f" ] || continue
  c=$(basename "$f" .pid); pid=$(cat "$f")
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    est="VIVO desde $(ps -o lstart= -p "$pid" | sed "s/  */ /g") (pid $pid, cpu $(ps -o %cpu= -p "$pid" | tr -d " ")%)"
  else est="PARADO"; fi
  picos=0; ultimo="nenhum"
  if [ -f clipes/picos.csv ]; then
    picos=$(awk -F, -v c="$c" "NR>1 && \$2==c" clipes/picos.csv | wc -l)
    ultimo=$(awk -F, -v c="$c" "NR>1 && \$2==c {u=\$1\" (\"\$6\" msgs, base \"\$7\")\"} END{print u==\"\"?\"nenhum\":u}" clipes/picos.csv)
  fi
  clipes=$(ls clipes/"$c"-*.mp4 2>/dev/null | wc -l)
  vert=$(ls clipes/verticais/"$c"/*.mp4 2>/dev/null | wc -l)
  nseg=$(find gravacoes/"$c" -name "seg_*.ts" 2>/dev/null | wc -l)
  buf=$(du -sh gravacoes/"$c" 2>/dev/null | cut -f1)
  echo "$c: $est"
  echo "   picos $picos | clipes $clipes | verticais $vert | último pico: $ultimo"
  echo "   buffer: ${nseg} segmentos, ${buf:-0}"
  tail -n 1 logs/"$c".log 2>/dev/null | sed "s/^/   log: /"
done
ls logs/*.pid >/dev/null 2>&1 || echo "nenhum canal registrado (use ./multi.sh CANAL ...)"
echo "C: $(df -h /mnt/c | awk "NR==2{print \$4\" livres de \"\$2\" (\"\$5\" usado)\"}")"
