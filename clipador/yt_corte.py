"""Cortes de lives do YouTube (Davy Jones, Paulinho o Loko, Lipão...), sem baixar a live inteira.

    .venv/bin/python yt_corte.py audio URL NOME                      # só o áudio da live (~300 MB em 7 h)
    .venv/bin/python yt_corte.py reacoes AUDIO [--n 30] [--pular 600]  # picos de reação (grito/risada) + fala em volta
    .venv/bin/python yt_corte.py picos URL [--n 8] [--pular 900]     # trechos mais revistos (heatmap do YouTube)
    .venv/bin/python yt_corte.py picos_chat URL [--n 15] [--palavras sinuca,bug]   # picos de risada no replay do chat
    .venv/bin/python yt_corte.py baixar URL INICIO FIM NOME [--altura 1080]   # só o trecho (HH:MM:SS ou segundos)
    .venv/bin/python yt_corte.py ao_vivo URL 20:44:30 20:47:45 NOME [--atraso 15]   # trecho de live AINDA no ar, pelo horário
    .venv/bin/python yt_corte.py varrer ARQUIVO [--passo 10]        # folha de quadros + picos de áudio, para escolher
    .venv/bin/python yt_corte.py vertical ARQUIVO CANAL CREDITO "LINHA 1" "LINHA 2"   # vertical 1080x1920 do arquivo inteiro

O heatmap tem 100 faixas por vídeo (numa live de 10 h, cada faixa tem ~6 min): ele acha a região,
o `varrer` acha o momento. Os arquivos ficam em clipes/yt/<canal>/.
"""
import json
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
YT = AQUI / "clipes" / "yt"
YTDLP = [str(AQUI / ".venv/bin/yt-dlp"), "--js-runtimes", "node", "--no-warnings"]


def seg(t):
    if isinstance(t, (int, float)):
        return float(t)
    partes = [float(p) for p in str(t).split(":")]
    s = 0.0
    for p in partes:
        s = s * 60 + p
    return s


def hms(s):
    s = int(s)
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"


def info(url):
    cache = YT / "_info"
    cache.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(YTDLP + ["-j", "--skip-download", url], capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        sys.exit(r.stderr[-800:])
    dados = json.loads(r.stdout)
    (cache / f"{dados['id']}.json").write_text(r.stdout, encoding="utf-8")
    return dados


def picos(url, n=8, pular=900):
    d = info(url)
    print(f"{d.get('title')} | {d.get('channel')} | {hms(d.get('duration') or 0)} | {d.get('view_count')} views")
    mapa = d.get("heatmap") or []
    if not mapa:
        print("sem heatmap (vídeo novo demais ou poucas views)")
        return
    faixas = sorted((f for f in mapa if f["start_time"] >= pular), key=lambda f: -f["value"])
    escolhidas = []
    for f in faixas:
        if all(abs(f["start_time"] - e["start_time"]) > 2 * (f["end_time"] - f["start_time"]) for e in escolhidas):
            escolhidas.append(f)
        if len(escolhidas) >= n:
            break
    for i, f in enumerate(escolhidas, 1):
        print(f"{i}. {hms(f['start_time'])} a {hms(f['end_time'])}  força {f['value']:.2f}")


def comentarios(url, n=12, maximo=600):
    """Minutagens citadas nos comentários mais curtidos (o público marca os melhores momentos)."""
    import re
    r = subprocess.run(YTDLP + ["-j", "--skip-download", "--write-comments", "--extractor-args",
                                f"youtube:max_comments={maximo},all,0,0;comment_sort=top", url],
                       capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        sys.exit(r.stderr[-800:])
    d = json.loads(r.stdout)
    dur = d.get("duration") or 10 ** 9
    marcas = []
    for c in d.get("comments") or []:
        texto = c.get("text") or ""
        for m in re.finditer(r"\b(\d{1,2}:\d{2}:\d{2}|\d{1,3}:\d{2})\b", texto):
            s = seg(m.group(1))
            if 60 < s < dur:
                marcas.append((s, (c.get("like_count") or 0) + 1, texto.replace("\n", " ")[:110]))
    grupos = []
    for s, peso, texto in sorted(marcas):
        if grupos and s - grupos[-1]["fim"] <= 90:
            g = grupos[-1]
            g["fim"], g["peso"], g["n"] = s, g["peso"] + peso, g["n"] + 1
            if peso > g["melhor"][0]:
                g["melhor"] = (peso, texto)
        else:
            grupos.append({"ini": s, "fim": s, "peso": peso, "n": 1, "melhor": (peso, texto)})
    print(f"{d.get('title')} | {hms(dur)} | {len(d.get('comments') or [])} comentários, {len(marcas)} minutagens")
    for g in sorted(grupos, key=lambda g: -g["peso"])[:n]:
        print(f"{hms(g['ini'])}-{hms(g['fim'])}  {g['n']} citações, {g['peso']} curtidas | {g['melhor'][1]}")


RISADA = ("kkk", "kaka", "haha", "rsrs", "😂", "🤣")


def picos_chat(url, n=15, palavras="", janela=30, pular=600):
    """Picos de risada no replay do chat de uma live que já acabou (o mesmo sinal do clipador, sem gravar).

    Baixa o chat uma vez (clipes/yt/_chat/<id>.live_chat.json, ~40 MB por hora de live) e lê linha a linha.
    Para cada pico mostra a frase que o chat mais repetiu (bom gancho: "CHAT: ...") e um trecho sugerido,
    que começa 40 s antes porque o chat reage com 10 a 30 s de atraso. `palavras` (vírgula) busca menções."""
    import collections
    import re
    pasta = YT / "_chat"
    pasta.mkdir(parents=True, exist_ok=True)
    m = re.search(r"(?:v=|youtu\.be/|/live/)([\w-]{11})", url)
    vid = m.group(1) if m else subprocess.run(YTDLP + ["--print", "id", url], capture_output=True,
                                               text=True, timeout=180).stdout.strip()
    arq = pasta / f"{vid}.live_chat.json"
    if not arq.exists():
        print("baixando o replay do chat (live de 10 h: ~400 MB, alguns minutos)")
        r = subprocess.run(YTDLP + ["--skip-download", "--write-subs", "--sub-langs", "live_chat",
                                    "-o", str(pasta / "%(id)s"), f"https://www.youtube.com/watch?v={vid}"],
                           capture_output=True, text=True, timeout=3600)
        if not arq.exists():
            sys.exit(f"sem replay do chat: {r.stderr[-400:]}")
    busca = [p.strip().lower() for p in palavras.split(",") if p.strip()]
    total, risos, frases, achados = (collections.Counter(), collections.Counter(),
                                     collections.defaultdict(collections.Counter), [])
    with open(arq, encoding="utf-8") as f:
        for linha in f:
            try:
                acao = json.loads(linha).get("replayChatItemAction", {})
            except json.JSONDecodeError:
                continue
            off = int(acao.get("videoOffsetTimeMsec", 0)) // 1000
            for a in acao.get("actions", []):
                item = a.get("addChatItemAction", {}).get("item", {}).get("liveChatTextMessageRenderer")
                if not item:
                    continue
                runs = item.get("message", {}).get("runs", [])
                texto = "".join(r.get("text") or r.get("emoji", {}).get("emojiId", "") for r in runs).lower()
                b = off // janela * janela
                total[b] += 1
                if any(k in texto for k in RISADA):
                    risos[b] += 1
                limpa = re.sub(r"\s+", " ", re.sub(r"k{2,}|(ka){2,}|(ha){2,}|[^\w\s]", " ", texto)).strip()
                if len(limpa) >= 8:
                    frases[b][limpa] += 1
                if busca and any(p in texto for p in busca):
                    achados.append((off, texto[:90]))
    if not total:
        sys.exit("chat vazio")
    print(f"{vid}: {sum(total.values())} mensagens em {hms(max(total))}; picos de risada (janela {janela} s):")
    escolhidos = []
    for b, q in risos.most_common():
        if b < pular or any(abs(b - e) < 3 * janela for e in escolhidos):
            continue
        escolhidos.append(b)
        frase, rep = (frases[b].most_common(1) or [("", 0)])[0]
        print(f"{len(escolhidos):>2}. {hms(b)}  risos {q:>4} de {total[b]:>4}  trecho {hms(max(0, b - 40))}-{hms(b + janela)}"
              f"  | chat: {frase[:60]!r} x{rep}")
        if len(escolhidos) >= n:
            break
    if busca:
        print(f"menções de {', '.join(busca)}: {len(achados)}")
        for off, t in achados[:40]:
            print(f"  {hms(off)}  {t}")


def audio(url, nome):
    """Só o áudio da live (7 h dão ~300 MB), para achar as reações sem baixar o vídeo."""
    pasta = YT / nome.split("-")[0]
    pasta.mkdir(parents=True, exist_ok=True)
    saida = pasta / f"{nome}.m4a"
    r = subprocess.run(YTDLP + ["-f", "ba[ext=m4a]/ba", "-o", str(saida), "--force-overwrites", url],
                       capture_output=True, text=True, timeout=3600)
    if r.returncode != 0 or not saida.exists():
        sys.exit(r.stderr[-800:])
    print(f"áudio: {saida} ({saida.stat().st_size / 1e6:.0f} MB)")


def _volume_por_segundo(arquivo, sr=8000):
    """RMS de cada segundo e 'cara de risada' (rajadas de 3 a 7 por segundo no envelope), lendo em blocos."""
    import numpy as np
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(arquivo), "-ac", "1", "-ar", str(sr), "-f", "s16le",
                             "-"], stdout=subprocess.PIPE)
    rms, riso = [], []
    passo = 400                                    # envelope em quadros de 50 ms
    while True:
        bloco = proc.stdout.read(sr * 2 * 60)      # 1 min por vez
        if not bloco:
            break
        x = np.frombuffer(bloco, dtype=np.int16).astype(np.float32)
        for i in range(0, len(x) - sr + 1, sr):
            s = x[i:i + sr]
            rms.append(float(np.sqrt(np.mean(s ** 2))))
            env = np.sqrt(np.mean(s[: len(s) // passo * passo].reshape(-1, passo) ** 2, axis=1))
            env = env - env.mean()
            den = float(np.dot(env, env)) or 1.0
            # autocorrelação nos atrasos de 3 a 6 quadros (150-300 ms): o "ha-ha-ha" da risada
            riso.append(max(float(np.dot(env[:-k], env[k:])) / den for k in (3, 4, 5, 6)))
    proc.wait()
    return np.array(rms), np.array(riso)


def reacoes(arquivo, n=30, pular=600, antes=25, depois=15):
    """Os momentos em que o streamer mais reage (grito, risada, explosão de voz), com a fala em volta.
    Base: volume do segundo / mediana dos 5 min em volta. Grava <arquivo>.reacoes.txt."""
    import numpy as np
    arquivo = Path(arquivo)
    rms, riso = _volume_por_segundo(arquivo)
    if len(rms) < 120:
        sys.exit("áudio curto demais")
    k = 150
    base = np.array([np.median(rms[max(0, i - k):i + k]) for i in range(0, len(rms), 10)]).repeat(10)[:len(rms)]
    razao = rms / np.maximum(base, 1.0)
    riso = np.where(razao > 1.3, riso, 0.0)       # silêncio com ruído não é risada
    # 3 s seguidos acima da base contam mais que um estalo isolado
    suave = np.convolve(razao, np.ones(3) / 3, mode="same")
    nota = suave + 1.5 * np.clip(np.convolve(riso, np.ones(3) / 3, mode="same"), 0, None)
    ordem = np.argsort(-nota)
    picos = []
    for i in ordem:
        if i < pular:
            continue
        if all(abs(i - p) > 60 for p in picos):
            picos.append(int(i))
        if len(picos) >= n:
            break
    sys.path.insert(0, str(AQUI))
    import pos  # noqa: E402
    linhas = []
    tmp = Path("/tmp/reacao.wav")
    for p in sorted(picos):
        ini = max(0, p - antes)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ini), "-t", str(antes + depois), "-i", str(arquivo),
                        "-ac", "1", "-ar", "16000", str(tmp)], check=True)
        try:
            fala = " ".join(w[2] for seg in pos.transcrever(tmp) for w in seg)
        except Exception as erro:
            fala = f"(transcrição falhou: {erro})"
        tem_riso = any(t in fala.lower() for t in ("kkk", "haha", "hahaha", "risos", "rsrs"))
        linha = (f"{hms(p)}  volume {suave[p]:.1f}x  risada {riso[p]:.2f}{'  [ri na fala]' if tem_riso else ''}\n"
                 f"   {fala[:400]}")
        print(linha, flush=True)
        linhas.append(linha)
    saida = arquivo.with_suffix(".reacoes.txt")
    saida.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"\nrelatório: {saida}")


def baixar(url, ini, fim, nome, altura=1080):
    canal = nome.split("-")[0]
    pasta = YT / canal
    pasta.mkdir(parents=True, exist_ok=True)
    saida = pasta / f"{nome}.mp4"
    fmt = f"bv*[height<={altura}][vcodec^=avc1]+ba[ext=m4a]/bv*[height<={altura}]+ba/b[height<={altura}]"
    r = subprocess.run(YTDLP + ["-f", fmt, "--merge-output-format", "mp4", "--download-sections",
                                f"*{hms(seg(ini))}-{hms(seg(fim))}", "-o", str(saida), "--force-overwrites", url],
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0 or not saida.exists():
        sys.exit(r.stderr[-800:])
    if _duracao(saida) < 0.5 * (seg(fim) - seg(ini)):
        # Live que acabou há pouco ("post_live"): o YouTube ainda não montou o vídeo e o
        # --download-sections devolve 1 s. Baixa só os pedaços (~5 s cada) do trecho.
        print("live ainda em processamento: baixando os pedaços do trecho")
        _baixar_pedacos(url, seg(ini), seg(fim), saida, altura)
    print(f"baixado: {saida} ({saida.stat().st_size / 1e6:.1f} MB, {_duracao(saida):.0f} s)")


def _duracao(arquivo):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                        str(arquivo)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def _baixar_pedacos(url, ini, fim, saida, altura):
    import urllib.request
    r = subprocess.run(YTDLP + ["-j", url], capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        sys.exit(r.stderr[-800:])
    d = json.loads(r.stdout)
    fmts = [f for f in d["formats"] if f.get("fragments")]
    video = max((f for f in fmts if f.get("vcodec", "none") != "none" and (f.get("height") or 0) <= altura
                 and str(f.get("vcodec")).startswith("avc1")), key=lambda f: (f.get("height") or 0, f.get("tbr") or 0))
    som = max((f for f in fmts if f.get("vcodec") == "none" and f.get("ext") == "m4a"), key=lambda f: f.get("tbr") or 0)
    n = len(video["fragments"])
    passo = d["duration"] / n
    i0, i1 = max(0, int(ini // passo) - 1), min(n - 1, int(fim // passo) + 1)
    partes = []
    for f, nome in ((video, "v.mp4"), (som, "a.m4a")):
        p = saida.with_name(saida.stem + "." + nome)
        with open(p, "wb") as out:
            for k in range(i0, i1 + 1):
                req = urllib.request.Request(f["fragments"][k]["url"], headers=f.get("http_headers") or {})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    out.write(resp.read())
        partes.append(p)
    desloc = ini - i0 * passo
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(partes[0]), "-i", str(partes[1]), "-ss", f"{desloc:.2f}",
                        "-t", f"{fim - ini:.2f}", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "18", "-c:a", "aac", "-b:a", "160k", str(saida)], capture_output=True, text=True)
    for p in partes:
        p.unlink(missing_ok=True)
    if r.returncode != 0:
        sys.exit(r.stderr[-800:])


def ao_vivo(url, ini, fim, nome, altura=1080, atraso=0.0):
    """Trecho de uma live que AINDA ESTÁ NO AR, pelo horário de parede (HH:MM[:SS] de hoje).

    O --download-sections não corta live em andamento ("cannot be partially downloaded"). O YouTube
    serve a live em pedaços DASH numerados (sq=0, 1, 2...), todos desde o começo. O cabeçalho do pedaço
    traz a hora de parede (X-Walltime-Ms), o tempo da live (X-Head-Time-Sec) e o último sq: daí sai o
    início da live e quantos segundos tem cada pedaço. `atraso` desconta o atraso da live, em segundos.
    """
    import datetime
    import urllib.request
    canal = nome.split("-")[0]
    pasta = YT / canal
    pasta.mkdir(parents=True, exist_ok=True)
    saida = pasta / f"{nome}.mp4"
    r = subprocess.run(YTDLP + ["-j", "--live-from-start", url], capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        sys.exit(r.stderr[-800:])
    fmts = json.loads(r.stdout)["formats"]
    dash = [f for f in fmts if f.get("protocol") == "http_dash_segments_generator"]
    video = max((f for f in dash if f.get("vcodec", "none") != "none" and (f.get("height") or 0) <= altura
                 and str(f.get("vcodec")).startswith("avc1")), key=lambda f: (f.get("height") or 0, f.get("tbr") or 0))
    som = max((f for f in dash if f.get("vcodec") == "none" and f.get("ext") == "m4a"), key=lambda f: f.get("tbr") or 0)

    def pedaco(f, sq):
        u = f["url"] + ("&" if "?" in f["url"] else "?") + f"sq={sq}"
        req = urllib.request.Request(u, headers=f.get("http_headers") or {})
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read(), resp.headers

    _, h = pedaco(som, 0)
    cabeca_seq, cabeca_t = int(h["X-Head-Seqnum"]), float(h["X-Head-Time-Millis"]) / 1000
    passo = cabeca_t / cabeca_seq
    inicio_live = int(h["X-Walltime-Ms"]) / 1000 - cabeca_t
    hoje = datetime.date.today()

    def na_live(t):
        hora = datetime.datetime.combine(hoje, datetime.time.fromisoformat(t))
        return hora.timestamp() - inicio_live - atraso

    t0, t1 = na_live(ini), na_live(fim)
    if t0 < 0 or t1 > cabeca_t or t1 <= t0:
        sys.exit(f"fora da live: {t0:.0f}-{t1:.0f} s (a live tem {cabeca_t:.0f} s)")
    s0, s1 = int(t0 // passo), min(cabeca_seq, int(t1 // passo) + 1)
    print(f"live começou {datetime.datetime.fromtimestamp(inicio_live):%H:%M:%S}; pedaços de {passo:.1f} s; "
          f"sq {s0}-{s1} ({hms(t0)}-{hms(t1)} da live)")
    partes = []
    for f, ext in ((video, "v.mp4"), (som, "a.m4a")):
        p = saida.with_name(saida.stem + "." + ext)
        with open(p, "wb") as out:
            for sq in range(s0, s1 + 1):
                out.write(pedaco(f, sq)[0])
        partes.append(p)
    desloc = t0 - s0 * passo
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(partes[0]), "-i", str(partes[1]), "-ss", f"{desloc:.2f}",
                        "-t", f"{t1 - t0:.2f}", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "18", "-c:a", "aac", "-b:a", "160k", str(saida)], capture_output=True, text=True)
    for p in partes:
        p.unlink(missing_ok=True)
    if r.returncode != 0:
        sys.exit(r.stderr[-800:])
    print(f"baixado: {saida} ({saida.stat().st_size / 1e6:.1f} MB, {_duracao(saida):.0f} s)")


def varrer(arquivo, passo=10):
    arquivo = Path(arquivo)
    folha = arquivo.with_suffix(".folha.jpg")
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(arquivo)], capture_output=True, text=True).stdout.strip())
    n = int(dur // passo) + 1
    colunas = 4
    linhas = (n + colunas - 1) // colunas
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(arquivo), "-vf",
                    f"fps=1/{passo},scale=360:-2,tile={colunas}x{linhas}:padding=4", "-frames:v", "1", str(folha)],
                   check=True)
    print(f"folha: {folha} ({n} quadros, um a cada {passo} s, da esquerda para a direita)")
    # volume por segundo: os 6 segundos mais altos (grito, risada) com 20 s de distância entre eles
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(arquivo), "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
                       capture_output=True, check=True)
    import numpy as np
    pcm = np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32)
    rms = [float(np.sqrt(np.mean(pcm[i:i + 8000] ** 2))) for i in range(0, len(pcm) - 8000, 8000)]
    altos = []
    for i in sorted(range(len(rms)), key=lambda k: -rms[k]):
        if all(abs(i - a) > 20 for a in altos):
            altos.append(i)
        if len(altos) >= 6:
            break
    base = float(np.median(rms)) or 1.0
    print("picos de áudio (s no arquivo):", ", ".join(f"{a} s ({rms[a] / base:.1f}x)" for a in sorted(altos)))


def vertical(arquivo, canal, credito, linha1, linha2=""):
    sys.path.insert(0, str(AQUI))
    import pos  # noqa: E402  (carrega o whisper)
    linhas = [linha1.upper(), linha2.upper()] if linha2 else [linha1.upper()]
    px = pos._caber(linhas)
    if not px:
        sys.exit("gancho não cabe: encurte as linhas")
    ctx = {"canal": canal, "tipo": "geral", "variante": "v35", "layout": "v2", "gancho": linhas, "gancho_px": px,
           "credito": credito}
    r = pos.produzir(Path(arquivo).resolve(), ctx, AQUI / "clipes" / "postar")   # o ffmpeg roda noutra pasta
    if not r:
        sys.exit("vertical falhou")
    print("vertical:", r["vertical"])


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)

    def opc(nome, padrao):
        return type(padrao)(a[a.index(nome) + 1]) if nome in a else padrao

    if a[0] == "picos":
        picos(a[1], opc("--n", 8), opc("--pular", 900))
    elif a[0] == "audio":
        audio(a[1], a[2])
    elif a[0] == "reacoes":
        reacoes(a[1], opc("--n", 30), opc("--pular", 600))
    elif a[0] == "comentarios":
        comentarios(a[1], opc("--n", 12), opc("--max", 600))
    elif a[0] == "picos_chat":
        picos_chat(a[1], opc("--n", 15), opc("--palavras", ""), opc("--janela", 30), opc("--pular", 600))
    elif a[0] == "baixar":
        baixar(a[1], a[2], a[3], a[4], opc("--altura", 1080))
    elif a[0] == "ao_vivo":
        ao_vivo(a[1], a[2], a[3], a[4], opc("--altura", 1080), opc("--atraso", 0.0))
    elif a[0] == "varrer":
        varrer(a[1], opc("--passo", 10))
    elif a[0] == "vertical":
        vertical(a[1], a[2], a[3], a[4], a[5] if len(a) > 5 else "")
    else:
        sys.exit(__doc__)
