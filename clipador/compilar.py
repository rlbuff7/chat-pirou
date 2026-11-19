#!/usr/bin/env python3
"""compilar.py: monta a compilação "melhores momentos" do dia a partir de clipes/picos.csv.

Uso (de dentro da pasta, qualquer python3 serve; só usa ffmpeg/ffprobe do sistema):
  python3 compilar.py                      hoje, os 10 melhores
  python3 compilar.py 2026-11-19 --top 5   outro dia, 5 melhores
  python3 compilar.py --incluir-demo       conta também os cortes forçados do --demo (para testar)

Ranking: mensagens do pico / max(mediana_base, 1), ou seja, quanto o chat explodiu em relação
ao normal daquele canal (um pico de 40 num chat de 5 vale mais que 60 num chat de 30).
Pega os N melhores cujo clipe horizontal ainda existe, junta em ordem cronológica,
1920x1080 60 fps, com uma cartela de 1,5 s ("CORTE n" + canal) antes de cada clipe.

Saída em ../conteudo/compilacoes/:
  <data>-top<N>.mp4   (N = quantos clipes entraram de fato)
  <data>-top<N>.txt   capítulos no formato do YouTube + créditos dos canais
"""
import csv
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

PASTA = Path(__file__).resolve().parent
CLIPES = PASTA / "clipes"
SAIDA = PASTA.parent / "conteudo" / "compilacoes"
FONTE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CARTELA_S = 1.5
LARGURA, ALTURA, FPS = 1920, 1080, 60


def ler_picos(data, incluir_demo):
    """Picos do dia, com pontuação, cujo clipe horizontal existe."""
    picos = []
    arquivo = CLIPES / "picos.csv"
    if not arquivo.exists():
        sys.exit(f"não achei {arquivo}: rode o clip_watcher antes")
    with open(arquivo, newline="", encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            if not linha["quando"].startswith(data):
                continue
            if linha.get("demo") == "1" and not incluir_demo:
                continue
            clipe = CLIPES / linha["clipe"]
            if not clipe.exists():
                continue
            try:
                msgs, base = int(linha["mensagens"]), float(linha["mediana_base"])
            except ValueError:
                continue
            picos.append({"quando": linha["quando"], "canal": linha["canal"], "mensagens": msgs,
                          "base": base, "score": msgs / max(base, 1), "clipe": clipe})
    return picos


def escolher(picos, n):
    """Os n de maior pontuação, devolvidos em ordem cronológica."""
    melhores = sorted(picos, key=lambda p: p["score"], reverse=True)[:n]
    return sorted(melhores, key=lambda p: p["quando"])


def tem_audio(arquivo):
    saida = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
         "-of", "csv=p=0", str(arquivo)], capture_output=True, text=True).stdout
    return bool(saida.strip())


def duracao(arquivo):
    saida = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1",
         str(arquivo)], capture_output=True, text=True).stdout.strip()
    return float(saida)


CODEC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2"]


def rodar(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg falhou:\n{r.stderr[-1500:]}")


def normalizar(clipe, destino):
    """Mesmo tamanho, fps e áudio para todos, para o concat final poder só copiar."""
    filtro = (f"scale={LARGURA}:{ALTURA}:force_original_aspect_ratio=decrease,"
              f"pad={LARGURA}:{ALTURA}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS}")
    if tem_audio(clipe):
        rodar(["ffmpeg", "-v", "error", "-y", "-i", str(clipe), "-vf", filtro, *CODEC, str(destino)])
    else:  # sem áudio: põe silêncio para o concat não quebrar
        rodar(["ffmpeg", "-v", "error", "-y", "-i", str(clipe), "-f", "lavfi", "-i",
               "anullsrc=r=48000:cl=stereo", "-shortest", "-vf", filtro, *CODEC, str(destino)])


def limpo(texto):
    """Só o que o drawtext aceita sem escape."""
    return re.sub(r"[^\w \-|#]", "", texto)


def cartela(numero, pico, destino):
    titulo = f"CORTE {numero}"
    sub = f"{limpo(pico['canal'])}  |  {pico['mensagens']} msgs no chat"
    texto = (f"drawtext=fontfile={FONTE}:text='{titulo}':fontsize=150:fontcolor=white:"
             f"x=(w-text_w)/2:y=(h/2)-150,"
             f"drawtext=fontfile={FONTE}:text='{sub}':fontsize=60:fontcolor=0xd0d0d0:"
             f"x=(w-text_w)/2:y=(h/2)+50,format=yuv420p")
    rodar(["ffmpeg", "-v", "error", "-y",
           "-f", "lavfi", "-i", f"color=c=0x14141c:s={LARGURA}x{ALTURA}:r={FPS}",
           "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", str(CARTELA_S),
           "-vf", texto, *CODEC, str(destino)])


def marca(segundos):
    s = int(round(segundos))
    h, resto = divmod(s, 3600)
    m, seg = divmod(resto, 60)
    return f"{h}:{m:02d}:{seg:02d}" if h else f"{m:02d}:{seg:02d}"


def main(data, n, incluir_demo):
    for prog in ("ffmpeg", "ffprobe"):
        if not shutil.which(prog):
            sys.exit(f"{prog} não encontrado")
    if not Path(FONTE).exists():
        sys.exit(f"fonte não encontrada: {FONTE}")
    picos = ler_picos(data, incluir_demo)
    if not picos:
        sys.exit(f"nenhum pico com clipe em {data} (use --incluir-demo para contar os cortes de teste)")
    escolhidos = escolher(picos, n)
    SAIDA.mkdir(parents=True, exist_ok=True)
    base = SAIDA / f"{data}-top{len(escolhidos)}"
    print(f"{len(picos)} picos com clipe em {data}; montando os {len(escolhidos)} melhores")
    inicio = time.time()
    capitulos, partes, cursor = [], [], 0.0
    with tempfile.TemporaryDirectory(prefix="compilar-") as tmp:
        tmp = Path(tmp)
        for i, pico in enumerate(escolhidos, 1):
            c, v = tmp / f"c{i:02d}.mp4", tmp / f"v{i:02d}.mp4"
            cartela(i, pico, c)
            normalizar(pico["clipe"], v)
            partes += [c, v]
            capitulos.append((cursor, f"Corte {i} - {pico['canal']} ({pico['mensagens']} msgs no chat)"))
            cursor += duracao(c) + duracao(v)
            print(f"  corte {i}: {pico['clipe'].name} score {pico['score']:.1f}")
        lista = tmp / "lista.txt"
        lista.write_text("".join(f"file '{p}'\n" for p in partes), encoding="utf-8")
        rodar(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
               "-c", "copy", "-movflags", "+faststart", str(base.with_suffix(".mp4"))])
    canais = sorted({p["canal"] for p in escolhidos})
    texto = ["Capítulos", ""]
    texto += [f"{marca(t)} {titulo}" for t, titulo in capitulos]
    texto += ["", "Créditos", "Cortes de transmissões ao vivo da Twitch dos canais:"]
    texto += [f"- {c}: https://twitch.tv/{c}" for c in canais]
    base.with_suffix(".txt").write_text("\n".join(texto) + "\n", encoding="utf-8")
    print(f"pronto em {time.time() - inicio:.0f} s ({cursor:.0f} s de vídeo): {base.with_suffix('.mp4')}")
    print(f"capítulos e créditos: {base.with_suffix('.txt')}")


if __name__ == "__main__":
    args, data, n, demo, i = sys.argv[1:], time.strftime("%Y-%m-%d"), 10, False, 0
    while i < len(args):
        if args[i] == "--top" and i + 1 < len(args) and args[i + 1].isdigit():
            n, i = int(args[i + 1]), i + 1
        elif args[i] == "--incluir-demo":
            demo = True
        elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", args[i]):
            data = args[i]
        else:
            sys.exit(__doc__)
        i += 1
    main(data, max(n, 1), demo)
