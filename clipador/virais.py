"""Coleta para o yt-viral: Shorts de GTA 6 mais vistos da semana e os últimos Shorts de cada canal (mediana).

    .venv/bin/python virais.py [--canais 15] [--por-canal 25]   # grava clipes/virais/coletado.json

Só listas públicas, sem login (yt-dlp sem cookies). Depois:
    python3 ~/.claude/skills/yt-viral/swipe.py clipes/virais/coletado.json --min 2.0   (no Windows)
"""
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "clipes" / "virais"
YTDLP = [str(AQUI / ".venv/bin/yt-dlp"), "--js-runtimes", "node", "--no-warnings", "--flat-playlist", "-J"]
BUSCAS = ["gta 6 alanzoka", "gta 6 cellbit", "gta 6 davy jones", "gta 6 paulinho o loko", "gta 6 lipao",
          "gta 6 cortes", "gta 6 kkkkkk", "gta 6 shorts brasil", "gta 6 flow games", "gta 6 engraçado"]
SEMANA_POR_VIEWS = "CAMSAggD"


SHORTS_SEMANA_POR_VIEWS = "EgQIAxAJ"     # esta semana + tipo Shorts (ordenar por views junto não funciona mais)


def lista(url, n):
    r = subprocess.run(YTDLP + ["--extractor-args", "youtube:lang=pt", "--playlist-end", str(n), url],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print(f"falhou: {url}: {r.stderr[-200:]}", file=sys.stderr)
        return []
    return json.loads(r.stdout).get("entries") or []


def _get(url):
    import urllib.request
    req = urllib.request.Request(url, headers={"Accept-Language": "pt-BR,pt;q=0.9", "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace")


def _views(texto):
    """'72 mil visualizações' / '1,2 mi de visualizações' / '845 visualizações' -> int."""
    import re
    m = re.search(r"([\d.,]+)\s*(mil|mi|bi)?", texto or "")
    if not m:
        return 0
    n = float(m.group(1).replace(".", "").replace(",", "."))
    return int(n * {"mil": 1e3, "mi": 1e6, "bi": 1e9}.get(m.group(2), 1))


def busca_shorts(q):
    """Shorts da busca pública (sem login): id, título, views. O canal vem do oembed."""
    return shorts_da_pagina(f"https://www.youtube.com/results?search_query={quote(q)}&sp={SHORTS_SEMANA_POR_VIEWS}")


def shorts_da_pagina(url):
    """Shorts (id, título, views) de uma página pública: busca ou aba /shorts de um canal (~48 primeiros).
    Lê 'mil'/'mi' certo (o yt-dlp com lang=pt lia '741 mil' como 741)."""
    import re
    html = _get(url)
    m = re.search(r"var ytInitialData = (\{.*?\});</script>", html, re.S)
    if not m:
        return []
    achados = []

    def andar(o):
        if isinstance(o, dict):
            if "shortsLockupViewModel" in o:
                s = o["shortsLockupViewModel"]
                vid = (s.get("onTap", {}).get("innertubeCommand", {}).get("reelWatchEndpoint", {}).get("videoId"))
                meta = s.get("overlayMetadata", {})
                if vid:
                    achados.append({"id": vid, "title": meta.get("primaryText", {}).get("content", ""),
                                    "views": _views(meta.get("secondaryText", {}).get("content", ""))})
                return
            for v in o.values():
                andar(v)
        elif isinstance(o, list):
            for v in o:
                andar(v)
    andar(json.loads(m.group(1)))
    return achados


def canal_de(vid):
    d = json.loads(_get(f"https://www.youtube.com/oembed?url=https://www.youtube.com/shorts/{vid}&format=json"))
    return d.get("author_name"), d.get("author_url")


def main():
    a = sys.argv[1:]
    n_canais = int(a[a.index("--canais") + 1]) if "--canais" in a else 15
    por_canal = int(a[a.index("--por-canal") + 1]) if "--por-canal" in a else 25
    SAIDA.mkdir(parents=True, exist_ok=True)
    if "--so-canais" in a and (SAIDA / "busca.json").exists():
        topo = json.loads((SAIDA / "busca.json").read_text(encoding="utf-8"))
        return medianas(topo, n_canais, por_canal)
    achados = {}
    for q in BUSCAS:
        try:
            for e in busca_shorts(q):
                e["busca"] = q
                achados.setdefault(e["id"], e)
        except Exception as erro:
            print(f"busca falhou ({q}): {erro}", file=sys.stderr)
    topo = sorted(achados.values(), key=lambda v: -v["views"])[:60]
    for v in topo:
        try:
            v["channel"], url_canal = canal_de(v["id"])
            v["channel_id"] = url_canal            # /@handle serve para /shorts
        except Exception:
            v["channel"], v["channel_id"] = "?", None
    topo = [v for v in topo if v.get("channel_id")]
    (SAIDA / "busca.json").write_text(json.dumps(topo, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(topo)} Shorts de GTA 6 nas buscas; os 15 mais vistos:")
    for v in topo[:15]:
        print(f"  {v['views']:>10,}  {v['channel'][:24]:<24} {v['title'][:70]}")
    medianas(topo, n_canais, por_canal)


def medianas(topo, n_canais, por_canal):
    canais = []
    for v in topo:
        if v["channel_id"] not in [c[0] for c in canais]:
            canais.append((v["channel_id"], v["channel"]))
        if len(canais) >= n_canais:
            break
    coletado = []
    for cid, nome in canais:
        try:
            ents = shorts_da_pagina(f"{cid}/shorts")[:por_canal]
        except Exception as erro:
            print(f"  canal {nome} falhou: {erro}", file=sys.stderr)
            ents = []
        for e in ents:
            coletado.append({"channel": nome, "title": e["title"], "views": e["views"],
                             "url": f"https://www.youtube.com/shorts/{e['id']}", "duration": 0})
        print(f"  canal {nome}: {len(ents)} Shorts")
    (SAIDA / "coletado.json").write_text(json.dumps(coletado, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"gravado: {SAIDA / 'coletado.json'} ({len(coletado)} vídeos)")


if __name__ == "__main__":
    main()
