#!/usr/bin/env python3
"""Liga o clipador sozinho nos candidatos que abrirem live de GTA VI.

Uso: .venv/bin/python auto_lancamento.py [--ate HH:MM] [--max 3] [--intervalo 120] [--qualquer-jogo]

Lê candidatos.txt (um login da Twitch por linha, em ordem de prioridade; # comenta).
A cada intervalo vê quem está ao vivo (streamlink --json). Se a categoria ou o título
for GTA VI, sobe ./multi.sh <canal>, até ter --max canais rodando. Log em logs/auto.log.
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import time
from pathlib import Path

PASTA = Path(__file__).resolve().parent
LOGS = PASTA / "logs"
GTA6 = re.compile(r"grand theft auto vi\b|\bgta ?(6|vi)\b", re.I)


def log(msg):
    linha = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(linha, flush=True)
    with open(LOGS / "auto.log", "a", encoding="utf-8") as f:
        f.write(linha + "\n")


def rodando(canal):
    """Só conta se o PID do arquivo ainda é um clip_watcher (PID pode ser reaproveitado pelo sistema)."""
    try:
        pid = int((LOGS / f"{canal}.pid").read_text().strip())
        cmd = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace")
        return "clip_watcher" in cmd
    except (OSError, ValueError):
        return False


def e_gta6(meta):
    """Vale a categoria da Twitch. O título só conta se a live não tiver categoria
    (18/11: 'Grand Theft Auto V | GTA 6 NADA DEMAIS' ocupou uma vaga por engano)."""
    categoria = (meta.get("category") or "").strip()
    if categoria:
        return bool(GTA6.search(categoria))
    return bool(GTA6.search(meta.get("title") or ""))


def ao_vivo(canal):
    """metadata (category/title) se o canal estiver ao vivo, senão None."""
    try:
        saida = subprocess.run(
            [str(PASTA / ".venv/bin/streamlink"), "--json", f"https://twitch.tv/{canal}"],
            capture_output=True, text=True, timeout=60,
        ).stdout
        dados = json.loads(saida)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return None
    return (dados.get("metadata") or {}) if dados.get("streams") else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ate", default="10:30")
    p.add_argument("--max", type=int, default=3)
    p.add_argument("--intervalo", type=int, default=120)
    p.add_argument("--qualquer-jogo", action="store_true")
    p.add_argument("--lista", default="candidatos.txt", help="arquivo de candidatos (padrão: candidatos.txt)")
    a = p.parse_args()
    LOGS.mkdir(exist_ok=True)

    agora = datetime.datetime.now()
    h, m = map(int, a.ate.split(":"))
    fim = agora.replace(hour=h, minute=m, second=0, microsecond=0)
    if fim <= agora:
        fim += datetime.timedelta(days=1)
    candidatos = []
    for linha in (PASTA / a.lista).read_text(encoding="utf-8").splitlines():
        login = linha.split("#")[0].strip().lower()
        if login and login not in candidatos:
            candidatos.append(login)
    log(f"inicio: {len(candidatos)} candidatos, max {a.max}, procura ate {fim:%d/%m %H:%M}")

    visto = {}  # canal -> último estado logado (evita repetir a mesma linha a cada volta)
    while datetime.datetime.now() < fim:
        ativos = [c for c in candidatos if rodando(c)]
        for canal in candidatos:
            if len(ativos) >= a.max:
                break
            if canal in ativos:
                continue
            meta = ao_vivo(canal)
            if meta is None:
                estado = "offline"
            else:
                texto = f"{meta.get('category') or '?'} | {meta.get('title') or ''}"[:160]
                if a.qualquer_jogo or e_gta6(meta):
                    log(f"ligando {canal}: {texto}")
                    subprocess.run([str(PASTA / "multi.sh"), canal], cwd=PASTA, check=False)
                    ativos.append(canal)
                    continue
                estado = f"ao vivo, mas nao e GTA VI: {texto}"
            if visto.get(canal) != estado:
                visto[canal] = estado
                log(f"{canal}: {estado}")
        log(f"rodando: {', '.join(ativos) or 'nenhum'}")
        time.sleep(a.intervalo)
    log("fim da janela de procura (os canais ligados continuam gravando ate ./parar.sh)")


if __name__ == "__main__":
    main()
