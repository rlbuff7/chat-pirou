"""Apoio à postagem automática do Chat Pirou (roteiro em plano/postagem-automatica.md).

    .venv/bin/python postagem.py candidatos [--horas 6] [--n 6]   # melhores clipes ainda não postados
    .venv/bin/python postagem.py ver CLIPE                          # 4 quadros + fala do clipe, para conferir
    .venv/bin/python postagem.py refazer CLIPE "LINHA 1" "LINHA 2"  # vertical com gancho escrito à mão
    .venv/bin/python postagem.py preparar VIDEO NN-nome              # comprime para < 9,5 MB e copia para postar
    .venv/bin/python postagem.py registrar NN-nome CLIPE REDE LINK   # anota o post (rede: tiktok, youtube, instagram)
    .venv/bin/python postagem.py proximo                             # próximo número NN
    .venv/bin/python postagem.py hoje                                # quantos posts por rede hoje e o último horário
    .venv/bin/python postagem.py limpar [--executar]                 # apaga os vídeos dos posts que já saíram nas 3 redes

CLIPE é o nome do clipe bruto sem extensão, como aparece no picos.csv (ex.: alanzoka-20261118-161453).
"""
import csv
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CLIPES = AQUI / "clipes"
PICOS = CLIPES / "picos.csv"
VERTICAIS = CLIPES / "verticais"
REFEITOS = CLIPES / "postar"                       # verticais com gancho escrito à mão


def _pasta_windows():
    """Pasta do usuário no Windows vista do WSL. Ordem: variável CHATPIROU_WIN, arquivo local.conf
    (linha WIN=/mnt/c/Users/<voce>, fora do git) ou /mnt/c/Users/<usuário do WSL>."""
    if os.environ.get("CHATPIROU_WIN"):
        return Path(os.environ["CHATPIROU_WIN"])
    conf = AQUI / "local.conf"
    if conf.exists():
        for linha in conf.read_text(encoding="utf-8").splitlines():
            if linha.strip().startswith("WIN="):
                return Path(linha.split("=", 1)[1].strip())
    return Path("/mnt/c/Users") / os.environ.get("USER", "")


WIN = _pasta_windows()
POSTAR = WIN / "Videos" / "chatpirou-postar"       # pasta liberada para a extensão do Chrome subir arquivos
PRONTOS = WIN / "ChatPirou" / "clipes"             # cópia para o dono + .txt dos textos
POSTADOS = PRONTOS / "postados.csv"
FRAMES = POSTAR / "_frames"
LIMITE = 9.5 * 1024 * 1024                         # a extensão aceita até 10 MB por envio
COLUNAS = ["quando", "nome", "clipe", "canal", "rede", "link"]


def win(p):
    return "C:\\" + str(p).removeprefix("/mnt/c/").replace("/", "\\")


def ler_picos():
    with open(PICOS, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ler_postados():
    if not POSTADOS.exists():
        return []
    with open(POSTADOS, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def vertical_de(stem):
    achados = sorted(VERTICAIS.glob(f"*/{stem}_*.mp4"))
    return achados[0] if achados else None


def duracao(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def fala(stem):
    srt = CLIPES / f"{stem}.srt"
    if not srt.exists():
        return "(sem legenda)"
    linhas = [l.strip() for l in srt.read_text(encoding="utf-8").splitlines()]
    return " ".join(l for l in linhas if l and not l.isdigit() and "-->" not in l)


def candidatos(horas=6.0, n=6):
    postados = {p["clipe"] for p in ler_postados()}
    limite = datetime.now() - timedelta(hours=horas)
    lista = []
    for p in ler_picos():
        stem = p["clipe"].removesuffix(".mp4")
        quando = datetime.strptime(p["quando"], "%Y-%m-%d %H:%M:%S")
        if stem in postados or p.get("demo", "0") != "0" or quando < limite:
            continue
        v = vertical_de(stem)
        if not v:
            continue
        base = max(float(p["mediana_base"] or 1), 1.0)
        msgs = int(float(p["mensagens"]))
        lista.append({"stem": stem, "canal": p["canal"], "quando": p["quando"][11:16], "msgs": msgs,
                      "forca": msgs / base, "tipo": p["tipo"], "gancho": p["gancho"], "chat": p["mais_ditas"],
                      "vertical": v, "mb": v.stat().st_size / 1e6})
    lista.sort(key=lambda c: (c["tipo"] == "historia", -c["forca"]))
    for c in lista[:n]:
        aviso = "  [HISTÓRIA: NÃO POSTAR NA 1ª SEMANA]" if c["tipo"] == "historia" else ""
        print(f"{c['stem']}  {c['canal']}  {c['quando']}  {c['msgs']} msgs  força {c['forca']:.1f}x  "
              f"{c['tipo']}  {c['mb']:.1f} MB{aviso}")
        print(f"   gancho atual: {c['gancho']}")
        print(f"   chat: {c['chat'][:160]}")
        print(f"   fala: {fala(c['stem'])[:220]}")
        print()
    if not lista:
        print(f"nenhum clipe novo nas últimas {horas:g} h")


def ver(stem):
    v = vertical_de(stem)
    if not v:
        sys.exit(f"vertical de {stem} não encontrado")
    FRAMES.mkdir(parents=True, exist_ok=True)
    dur = duracao(v)
    for i, frac in enumerate((0.05, 0.35, 0.65, 0.9), 1):
        saida = FRAMES / f"{stem}-{i}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{dur * frac:.2f}", "-i", str(v), "-frames:v", "1",
                        "-vf", "scale=432:-2", str(saida)], check=True)
        print(win(saida))
    print(f"vertical: {v} ({dur:.0f} s, {v.stat().st_size / 1e6:.1f} MB)")
    print("fala:", fala(stem))


def refazer(stem, linha1, linha2, variante=None):
    sys.path.insert(0, str(AQUI))
    import pos  # noqa: E402  (carrega o whisper: ~1 GB de RAM por ~30 s)
    pico = next((p for p in ler_picos() if p["clipe"].removesuffix(".mp4") == stem), None)
    if not pico:
        sys.exit(f"{stem} não está no picos.csv")
    linhas = [linha1.upper(), linha2.upper()] if linha2 else [linha1.upper()]
    px = pos._caber(linhas)
    if not px:
        sys.exit("gancho não cabe: encurte as linhas")
    ctx = {"canal": pico["canal"], "tipo": pico["tipo"], "variante": variante or pico["variante"] or "v22",
           "layout": "v2", "gancho": linhas, "gancho_px": px}
    r = pos.produzir(CLIPES / f"{stem}.mp4", ctx, REFEITOS)
    if not r:
        sys.exit("vertical falhou")
    print("vertical refeito:", r["vertical"])


def preparar(video, nome):
    video = Path(video)
    POSTAR.mkdir(parents=True, exist_ok=True)
    saida = POSTAR / f"{nome}.mp4"
    if video.stat().st_size <= LIMITE:
        shutil.copy2(video, saida)
    else:
        dur = duracao(video)
        alvo = 9.0 * 8 * 1024 * 1024 / dur          # bits por segundo para caber em ~9 MB
        kbps = int((alvo - 128_000) / 1000)
        for tentativa in range(3):
            log = f"/tmp/postagem-2pass-{nome}"
            base = ["ffmpeg", "-v", "error", "-y", "-i", str(video), "-c:v", "libx264", "-preset", "medium",
                    "-b:v", f"{kbps}k", "-pix_fmt", "yuv420p", "-passlogfile", log]
            subprocess.run(base + ["-pass", "1", "-an", "-f", "mp4", "/dev/null"], check=True)
            subprocess.run(base + ["-pass", "2", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
                                   str(saida)], check=True)
            if saida.stat().st_size <= LIMITE:
                break
            kbps = int(kbps * 0.85)
        else:
            sys.exit(f"não coube em 9,5 MB: {saida.stat().st_size / 1e6:.1f} MB")
    PRONTOS.mkdir(parents=True, exist_ok=True)
    shutil.copy2(saida, PRONTOS / saida.name)
    print(f"pronto para subir: {win(saida)} ({saida.stat().st_size / 1e6:.1f} MB)")


def registrar(nome, stem, rede, link):
    canal = stem.split("-")[0]
    novo = not POSTADOS.exists()
    with open(POSTADOS, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if novo:
            w.writerow(COLUNAS)
        w.writerow([time.strftime("%Y-%m-%d %H:%M"), nome, stem, canal, rede, link])
    print(f"registrado: {nome} {rede}")


def proximo():
    # conta pelo .txt: o .mp4 dos já postados vai para a Lixeira (limpar)
    numeros = [int(p.name[:2]) for p in PRONTOS.glob("[0-9][0-9]-*.txt")]
    print(f"{max(numeros, default=0) + 1:02d}")


def arquivos_do_post(nome, stem):
    """Vídeos de um post já publicado: (no WSL, apagar de vez) e (no Windows, mandar para a Lixeira).
    Fica: o .txt dos textos, o postados.csv, o picos.csv e os .reacoes.txt."""
    wsl = [p for p in (CLIPES / f"{stem}.mp4", CLIPES / f"{stem}.srt") if p.exists()]
    for pasta in (VERTICAIS, REFEITOS, CLIPES / "estreia"):
        wsl += list(pasta.rglob(f"{stem}_*"))
    if stem.endswith("-corte"):                     # corte de live do YouTube (yt_corte.py)
        base = stem.removesuffix("-corte")
        for p in (CLIPES / "yt").rglob(f"{base}*"):
            if p.stem.split(".")[0] in (base, stem) or p.name.startswith(f"{base}-"):
                if not p.name.endswith(".reacoes.txt") and p.suffix != ".m4a":
                    wsl.append(p)
    wsl += list(FRAMES.glob(f"{stem}-*.jpg"))
    windows = [p for p in (POSTAR / f"{nome}.mp4", PRONTOS / f"{nome}.mp4") if p.exists()]
    return sorted(set(wsl)), windows


def limpar(executar=False):
    """Apaga os vídeos dos posts que já saíram nas 3 redes (pedido do dono em 19/11: 'o que já foi postado vá
    apagando'). Sem --executar só lista."""
    redes = {}
    for p in ler_postados():
        redes.setdefault((p["nome"], p["clipe"]), set()).add(p["rede"])
    total = 0
    for (nome, stem), feitas in redes.items():
        if not {"tiktok", "youtube", "instagram"} <= feitas:
            continue
        wsl, windows = arquivos_do_post(nome, stem)
        if not wsl and not windows:
            continue
        tam = sum(p.stat().st_size for p in wsl + windows)
        total += tam
        print(f"{nome}: {len(wsl)} no WSL + {len(windows)} no Windows ({tam / 1e6:.0f} MB)")
        if executar:
            for p in wsl:
                p.unlink(missing_ok=True)
            for p in windows:
                comando = ("Add-Type -AssemblyName Microsoft.VisualBasic; [Microsoft.VisualBasic.FileIO.FileSystem]::"
                           f"DeleteFile('{win(p)}', 'OnlyErrorDialogs', 'SendToRecycleBin')")
                subprocess.run(["powershell.exe", "-NoProfile", "-Command", comando], capture_output=True)
                if p.exists():
                    print(f"  não foi para a Lixeira: {win(p)}")
    print(f"{'apagado' if executar else 'a apagar (rode com --executar)'}: {total / 1e6:.0f} MB")


def hoje():
    dia = time.strftime("%Y-%m-%d")
    por_rede = {}
    for p in ler_postados():
        if p["quando"].startswith(dia):
            por_rede.setdefault(p["rede"], []).append(p["quando"][11:])
    for rede in ("tiktok", "youtube", "instagram"):
        horas = por_rede.get(rede, [])
        print(f"{rede}: {len(horas)} hoje" + (f", último às {horas[-1]}" if horas else ""))


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    cmd, resto = args[0], args[1:]
    if cmd == "candidatos":
        horas = float(resto[resto.index("--horas") + 1]) if "--horas" in resto else 6.0
        n = int(resto[resto.index("--n") + 1]) if "--n" in resto else 6
        candidatos(horas, n)
    elif cmd == "ver":
        ver(resto[0])
    elif cmd == "refazer":
        refazer(resto[0], resto[1], resto[2] if len(resto) > 2 else "")
    elif cmd == "preparar":
        preparar(resto[0], resto[1])
    elif cmd == "registrar":
        registrar(*resto[:4])
    elif cmd == "proximo":
        proximo()
    elif cmd == "hoje":
        hoje()
    elif cmd == "limpar":
        limpar("--executar" in resto)
    else:
        sys.exit(__doc__)
