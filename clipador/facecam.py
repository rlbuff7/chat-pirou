#!/usr/bin/env python3
"""facecam.py: acha a webcam do streamer num clipe e devolve o recorte para o layout vertical "facecam" do pos.py.

Opt-in (`--layout facecam`). O layout v2 continua o padrão e é o plano B de tudo aqui: sem rosto confiável,
`decidir` devolve usar=False com o motivo e o pos.py faz o v2.

Como decide (OpenCV com o Haar cascade que vem dentro do próprio pacote, `cv2.data.haarcascades`; nada é baixado):
- amostra N_QUADROS (6) do clipe e procura rostos em cada um (quadro reduzido para 960 px de largura);
- agrupa os rostos que aparecem no mesmo lugar e com o mesmo tamanho; fica com o que aparece em pelo menos
  METADE dos quadros (rosto que só aparece de vez em quando é cena, não webcam);
- só vale rosto com o centro perto de uma borda do quadro (BORDA_MAX) e pequeno (ROSTO_MAX): webcam é overlay de
  canto/lateral. Rosto grande no meio é outra coisa (foto no jogo, IRL em tela cheia);
- o recorte é 16:9, centrado no rosto, com margem (K_RECORTE vezes a largura do rosto), dentro do quadro.

Cache por canal em clipes/facecam/<canal>.json: o recorte é reaproveitado nos clipes seguintes, só conferindo
em 3 quadros se o rosto continua ali (CONFIANCA_MIN). Confiança caiu = recalcula tudo. "Sem webcam" também vale
no cache, mas só por NEGATIVO_S (o streamer pode trocar de cena).

Uso avulso:  .venv/bin/python facecam.py CLIPE.mp4 [--canal X]   (imprime a decisão)
             .venv/bin/python facecam.py --teste
"""
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# ---- ajuste aqui ----
N_QUADROS = 6            # quadros amostrados na detecção completa
N_QUADROS_CONFERE = 3    # quadros usados para conferir um recorte do cache
LARGURA_DET = 960        # largura do quadro em que o detector roda
ESTAVEL_MIN = 0.5        # fração dos quadros em que o rosto tem de aparecer
BORDA_MAX = 0.25         # centro do rosto a no máximo 25% da borda mais próxima (fração do quadro)
ROSTO_MIN = 0.03          # largura mínima do rosto (fração da largura do quadro): abaixo disso é ícone de HUD, não webcam
ROSTO_MAX = 0.22         # largura máxima: acima disso não é overlay de webcam
K_RECORTE = 3.0          # largura do recorte = K x largura do rosto (cabelo e ombros; mais que isso já pega o jogo em volta de webcams pequenas)
RECORTE_MIN_PX = 240     # recorte menor que isso ampliaria demais (mole): alarga
RECORTE_MAX = 0.5        # recorte de no máximo metade da largura do quadro
CONFIANCA_MIN = 0.6      # conferência do cache: abaixo disso (1 de 3 quadros) invalida
CACHE_VALE_S = 12 * 3600  # recalcula do zero pelo menos a cada 12 h
NEGATIVO_S = 20 * 60      # "sem webcam" no cache vale 20 min
PROPORCAO = 16 / 9
SOBE_CENTRO = 0.10       # sobe o centro do recorte (fração da altura dele): rosto fica um pouco acima do meio

_cascata = None


def _cv2():
    import cv2
    return cv2


def cascata():
    global _cascata
    if _cascata is None:
        cv2 = _cv2()
        c = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml")
        if c.empty():
            raise RuntimeError("haarcascade_frontalface_alt2.xml não abriu")
        _cascata = c
    return _cascata


# ---------- entrada: quadros do clipe ----------

def sondar(clipe):
    """(largura, altura, duração s) do clipe, ou None."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height:format=duration", "-of", "json", str(clipe)],
                       capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
        return int(d["streams"][0]["width"]), int(d["streams"][0]["height"]), float(d["format"]["duration"])
    except (ValueError, KeyError, IndexError):
        return None


def quadros_cinza(clipe, larg, alt, dur, fracoes):
    """Quadros em cinza, LARGURA_DET de largura, nos instantes dur*fracao. Uma chamada do ffmpeg por quadro
    (busca antes do -i: rápida), em paralelo. Quadro que falhar é pulado."""
    import numpy as np
    dh = max(int(round(LARGURA_DET * alt / larg / 2)) * 2, 2)

    def um(f):
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{dur * f:.2f}", "-i", str(clipe), "-frames:v", "1",
                            "-vf", f"scale={LARGURA_DET}:{dh},format=gray", "-f", "rawvideo", "-"],
                           capture_output=True)
        if len(r.stdout) != LARGURA_DET * dh:
            return None
        return np.frombuffer(r.stdout, dtype=np.uint8).reshape(dh, LARGURA_DET)

    with ThreadPoolExecutor(max_workers=len(fracoes)) as ex:
        return [q for q in ex.map(um, fracoes) if q is not None]


# ---------- detecção ----------

def detectar(gray, min_larg=ROSTO_MIN, max_larg=0.45):
    """Rostos de um quadro cinza: [(cx, cy, w, h)] tudo em fração do quadro (cx, w pela largura; cy, h pela altura)."""
    cv2 = _cv2()
    h, w = gray.shape
    eq = cv2.equalizeHist(gray)
    achados = cascata().detectMultiScale(eq, scaleFactor=1.1, minNeighbors=5,
                                         minSize=(max(int(w * min_larg), 20),) * 2,
                                         maxSize=(int(w * max_larg),) * 2)
    return [((x + fw / 2) / w, (y + fh / 2) / h, fw / w, fh / h) for x, y, fw, fh in achados]


def agrupar(por_quadro, aspecto):
    """Junta rostos do mesmo lugar e tamanho em quadros diferentes.
    `por_quadro`: [[(cx, cy, w, h), ...] por quadro]; `aspecto` = altura/largura do quadro.
    Devolve [{cx, cy, w, h, quadros}] (médias; `quadros` = nº de quadros distintos com o rosto)."""
    grupos = []
    for i, dets in enumerate(por_quadro):
        for cx, cy, w, h in dets:
            for g in grupos:
                if i in g["_idx"]:
                    continue
                folga = 0.6 * max(g["w"], w)
                if abs(g["cx"] - cx) <= folga and abs(g["cy"] - cy) * aspecto <= folga \
                        and 0.6 <= w / g["w"] <= 1.67:
                    n = len(g["_idx"])
                    for k, v in (("cx", cx), ("cy", cy), ("w", w), ("h", h)):
                        g[k] = (g[k] * n + v) / (n + 1)
                    g["_idx"].add(i)
                    break
            else:
                grupos.append({"cx": cx, "cy": cy, "w": w, "h": h, "_idx": {i}})
    for g in grupos:
        g["quadros"] = len(g.pop("_idx"))
    return grupos


def distancia_borda(cx, cy):
    return min(cx, 1 - cx, cy, 1 - cy)


def escolher(grupos, n_quadros):
    """(rosto, confianca, motivo): o grupo que parece webcam, ou (None, confianca do melhor, motivo da recusa)."""
    if not grupos:
        return None, 0.0, f"nenhum rosto em {n_quadros} quadros"
    validos, recusas = [], []
    for g in grupos:
        conf = g["quadros"] / max(n_quadros, 1)
        d = distancia_borda(g["cx"], g["cy"])
        if g["quadros"] < max(2, round(ESTAVEL_MIN * n_quadros)):
            recusas.append((conf, f"rosto instável ({g['quadros']} de {n_quadros} quadros)"))
        elif g["w"] > ROSTO_MAX:
            recusas.append((conf, f"rosto grande demais ({g['w']:.0%} da largura): não é overlay de webcam"))
        elif d > BORDA_MAX:
            recusas.append((conf, f"rosto longe das bordas (a {d:.0%} da mais próxima): não parece webcam"))
        else:
            validos.append((conf * (1 - 0.5 * d / BORDA_MAX), conf, g))
    if validos:
        _, conf, g = max(validos, key=lambda t: t[0])
        return {k: g[k] for k in ("cx", "cy", "w", "h")}, conf, ""
    conf, motivo = max(recusas, key=lambda t: t[0])
    return None, conf, motivo


def recorte_de(rosto, larg, alt):
    """Retângulo 16:9 [x, y, w, h] (frações do quadro) centrado no rosto, com margem, dentro do quadro.
    `larg`/`alt` = pixels do clipe original (para a largura mínima do recorte e a proporção)."""
    cw = min(max(K_RECORTE * rosto["w"] * larg, RECORTE_MIN_PX), RECORTE_MAX * larg)
    ch = cw / PROPORCAO
    if ch > alt:
        ch = alt
        cw = ch * PROPORCAO
    x = rosto["cx"] * larg - cw / 2
    y = rosto["cy"] * alt - ch / 2 - SOBE_CENTRO * ch
    x = min(max(x, 0.0), larg - cw)
    y = min(max(y, 0.0), alt - ch)
    return [round(x / larg, 5), round(y / alt, 5), round(cw / larg, 5), round(ch / alt, 5)]


def conferir(recorte, quadros, rosto_w):
    """Fração dos quadros em que ainda há rosto dentro do recorte (cache)."""
    if not quadros:
        return 0.0
    ok = 0
    for q in quadros:
        h, w = q.shape
        x0, y0 = int(recorte[0] * w), int(recorte[1] * h)
        x1, y1 = int((recorte[0] + recorte[2]) * w) + 1, int((recorte[1] + recorte[3]) * h) + 1
        ok += bool(detectar(q[y0:y1, x0:x1].copy(), min_larg=max(rosto_w * w * 0.6 / max(x1 - x0, 1), 0.05), max_larg=1.0))
    return ok / len(quadros)


# ---------- cache ----------

def _arquivo(pasta, canal):
    return Path(pasta) / (re.sub(r"[^a-z0-9_]", "_", canal.lower()) + ".json")


def ler_cache(pasta, canal):
    try:
        return json.loads(_arquivo(pasta, canal).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def gravar_cache(pasta, canal, dados):
    arq = _arquivo(pasta, canal)
    arq.parent.mkdir(parents=True, exist_ok=True)
    tmp = arq.with_suffix(f".{time.time_ns()}.tmp")
    tmp.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(arq)


# ---------- API ----------

def _sem(motivo, t0, cache="", confianca=0.0):
    return {"usar": False, "recorte": None, "motivo": motivo, "confianca": confianca, "cache": cache,
            "tempo": time.time() - t0}


def decidir(clipe, canal, pasta_cache, agora=None, quadros_fn=None):
    """{usar, recorte [x,y,w,h] em fração do quadro, motivo, confianca, cache, tempo}. Nunca levanta:
    qualquer falha vira usar=False com o motivo (o pos.py cai no layout v2).
    `quadros_fn(fracoes) -> (larg, alt, [quadros cinza])` existe para teste."""
    t0 = time.time()
    agora = agora if agora is not None else t0
    try:
        _cv2()
        import numpy  # noqa: F401
    except ImportError as erro:
        return _sem(f"opencv-python-headless não instalado ({erro})", t0)
    try:
        if quadros_fn is None:
            info = sondar(clipe)
            if not info:
                return _sem("ffprobe não leu o clipe", t0)
            larg, alt, dur = info

            def quadros_fn(fracoes):
                return larg, alt, quadros_cinza(clipe, larg, alt, dur, fracoes)

        cache = ler_cache(pasta_cache, canal)
        invalidado = ""
        if cache and cache.get("ok") and agora - cache.get("quando", 0) < CACHE_VALE_S:
            larg, alt, qs = quadros_fn([0.2, 0.5, 0.8][:N_QUADROS_CONFERE])
            conf = conferir(cache["recorte"], qs, cache["rosto"][2])
            if conf >= CONFIANCA_MIN:
                cache["confianca"] = round(0.5 * cache.get("confianca", conf) + 0.5 * conf, 3)
                cache["usos"] = cache.get("usos", 0) + 1
                gravar_cache(pasta_cache, canal, cache)
                return {"usar": True, "recorte": cache["recorte"], "motivo": "", "confianca": cache["confianca"],
                        "cache": "reaproveitado", "tempo": time.time() - t0}
            invalidado = f"cache invalidado (confiança {conf:.2f} < {CONFIANCA_MIN}); "
        elif cache and cache.get("ok"):
            invalidado = "cache velho; "
        elif cache and not cache.get("ok") and agora - cache.get("quando", 0) < NEGATIVO_S:
            return _sem(cache.get("motivo", "sem webcam") + " (do cache)", t0, "negativo", cache.get("confianca", 0.0))

        fr = [(i + 0.5) / N_QUADROS for i in range(N_QUADROS)]
        larg, alt, qs = quadros_fn(fr)
        if len(qs) < 3:
            return _sem(f"só {len(qs)} quadros legíveis no clipe", t0)
        grupos = agrupar([detectar(q) for q in qs], qs[0].shape[0] / qs[0].shape[1])
        rosto, conf, motivo = escolher(grupos, len(qs))
        if rosto is None:
            gravar_cache(pasta_cache, canal, {"canal": canal, "ok": False, "motivo": motivo, "confianca": round(conf, 3),
                                              "quando": agora})
            return _sem(invalidado + motivo, t0, "novo", conf)
        recorte = recorte_de(rosto, larg, alt)
        gravar_cache(pasta_cache, canal, {"canal": canal, "ok": True, "rosto": [round(rosto[k], 5) for k in ("cx", "cy", "w", "h")],
                                          "recorte": recorte, "confianca": round(conf, 3), "quando": agora, "usos": 1})
        return {"usar": True, "recorte": recorte, "motivo": "", "confianca": round(conf, 3),
                "cache": "renovado" if invalidado else "novo", "tempo": time.time() - t0}
    except Exception as erro:
        return _sem(f"facecam falhou: {type(erro).__name__}: {erro}", t0)


# ---------- testes ----------

def _rosto_sintetico(cv2, np, quadro, cx, cy, larg):
    """Desenha um rosto esquemático (pele, olhos, sobrancelhas, nariz, boca) centrado em (cx, cy) px."""
    a, b = int(larg / 2), int(larg * 0.62)
    cv2.ellipse(quadro, (cx, cy), (a, b), 0, 0, 360, (150, 175, 225), -1)
    for sx in (-1, 1):
        ex = cx + sx * int(a * 0.42)
        cv2.ellipse(quadro, (ex, cy - int(b * 0.18)), (int(a * 0.22), int(a * 0.11)), 0, 0, 360, (240, 240, 240), -1)
        cv2.circle(quadro, (ex, cy - int(b * 0.18)), int(a * 0.1), (30, 30, 30), -1)
        cv2.line(quadro, (ex - int(a * 0.25), cy - int(b * 0.38)), (ex + int(a * 0.25), cy - int(b * 0.38)), (40, 40, 60), max(3, a // 12))
    cv2.line(quadro, (cx, cy - int(b * 0.1)), (cx - int(a * 0.1), cy + int(b * 0.2)), (110, 130, 180), max(2, a // 14))
    cv2.ellipse(quadro, (cx, cy + int(b * 0.5)), (int(a * 0.35), int(a * 0.12)), 0, 0, 180, (50, 50, 140), -1)
    return cv2.GaussianBlur(quadro, (0, 0), max(1.0, a / 40))


def _quadro_sintetico(cv2, np, rosto=None, largura=960, altura=540, centro=False):
    rng = np.random.default_rng(3)
    q = (rng.integers(25, 70, (altura, largura, 3))).astype(np.uint8)
    cv2.rectangle(q, (largura // 3, altura // 3), (largura // 2, altura // 2), (60, 120, 60), -1)   # "cenário"
    if rosto:
        cx, cy, larg = rosto
        q = _rosto_sintetico(cv2, np, q, int(cx * largura), int(cy * altura), int(larg * largura))
    return q


def autoteste():
    # lógica de escolha (não precisa de OpenCV): estabilidade, borda, tamanho, recorte
    grupo = lambda cx, cy, w, n: {"cx": cx, "cy": cy, "w": w, "h": w * 1.7, "quadros": n}   # noqa: E731
    r, conf, m = escolher([grupo(0.10, 0.56, 0.05, 6)], 6)
    assert r and conf == 1.0 and not m, (r, conf, m)
    assert escolher([], 6)[0] is None and "nenhum rosto" in escolher([], 6)[2]
    r, conf, m = escolher([grupo(0.5, 0.5, 0.08, 6)], 6)
    assert r is None and "longe das bordas" in m, m                                   # foto no meio do jogo
    r, conf, m = escolher([grupo(0.1, 0.5, 0.05, 2)], 6)
    assert r is None and "instável" in m, m                                           # aparece de vez em quando
    r, conf, m = escolher([grupo(0.1, 0.5, 0.30, 6)], 6)
    assert r is None and "grande demais" in m, m
    r, _, _ = escolher([grupo(0.5, 0.5, 0.08, 6), grupo(0.9, 0.9, 0.05, 4), grupo(0.12, 0.8, 0.05, 5)], 6)
    assert r and r["cx"] == 0.12, r                                                   # fica com o mais perto da borda/estável
    # recorte: 16:9, dentro do quadro, com o rosto dentro
    for cx, cy, w in [(0.10, 0.56, 0.052), (0.02, 0.03, 0.05), (0.97, 0.97, 0.06), (0.5, 0.5, 0.2), (0.1, 0.5, 0.005)]:
        x, y, rw, rh = recorte_de({"cx": cx, "cy": cy, "w": w, "h": w * 1.7}, 1920, 1080)
        assert 0 <= x and 0 <= y and x + rw <= 1.00001 and y + rh <= 1.00001, (x, y, rw, rh)
        assert abs(rw * 1920 / (rh * 1080) - PROPORCAO) < 0.02, (rw, rh)
        assert rw * 1920 >= RECORTE_MIN_PX - 1 or rw * 1920 >= 0.99 * RECORTE_MAX * 1920
        if 0.05 < cx < 0.9 and 0.1 < cy < 0.9:
            assert x <= cx - w / 2 and cx + w / 2 <= x + rw and y <= cy <= y + rh, "rosto fora do recorte"
    # agrupamento: mesmo lugar em quadros diferentes junta; lugares diferentes não
    gs = agrupar([[(0.1, 0.5, 0.05, 0.09)], [(0.101, 0.502, 0.052, 0.09)], [(0.8, 0.2, 0.05, 0.09)]], 0.5625)
    assert sorted(g["quadros"] for g in gs) == [1, 2], gs
    assert len(agrupar([[(0.1, 0.5, 0.05, 0.09), (0.1, 0.5, 0.05, 0.09)]], 0.5625)) == 2, "2 rostos no mesmo quadro"
    # cache: gravar/ler; negativo vale pouco tempo; sem OpenCV cai no v2 com motivo
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        assert ler_cache(tmp, "x") is None
        gravar_cache(tmp, "Canal-X!", {"ok": True, "quando": 1})
        assert ler_cache(tmp, "canal-x!") == {"ok": True, "quando": 1} and (Path(tmp) / "canal_x_.json").exists()
        try:
            import cv2, numpy as np   # noqa: E401
        except ImportError:
            print("ok (facecam; sem OpenCV: detector e fallback de imagem não testados)")
            return
        # imagem sintética: rosto esquemático no canto inferior esquerdo, estável em todos os quadros
        def faz(rosto, n=6):
            qs = [_quadro_sintetico(cv2, np, rosto) for _ in range(n)]
            return lambda fr: (1920, 1080, [cv2.cvtColor(q, cv2.COLOR_BGR2GRAY) for q in qs[:len(fr)]])
        LR = 0.12                                          # tamanho em que o Haar acha o desenho de forma estável
        achou = decidir("x.mp4", "t1", tmp, quadros_fn=faz((0.12, 0.7, LR)))
        assert achou["usar"], f"o detector não achou o rosto sintético: {achou}"
        x, y, rw, rh = achou["recorte"]
        assert x < 0.2 and 0.45 < y + rh / 2 < 0.8 and achou["cache"] == "novo", achou
        assert (Path(tmp) / "t1.json").exists()
        # segunda chamada usa o cache (3 quadros conferidos)
        d2 = decidir("x.mp4", "t1", tmp, quadros_fn=faz((0.12, 0.7, LR)))
        assert d2["usar"] and d2["cache"] == "reaproveitado" and d2["recorte"] == achou["recorte"], d2
        # confiança cai (o rosto sumiu): invalida e, sem rosto, cai no v2 com o motivo
        d3 = decidir("x.mp4", "t1", tmp, quadros_fn=faz(None))
        assert not d3["usar"] and "invalidado" in d3["motivo"] and d3["recorte"] is None, d3
        # logo depois, o negativo vem do cache (não recalcula)
        d4 = decidir("x.mp4", "t1", tmp, quadros_fn=faz((0.12, 0.7, LR)))
        assert not d4["usar"] and d4["cache"] == "negativo", d4
        # passado o prazo do negativo, recalcula e acha de novo
        d5 = decidir("x.mp4", "t1", tmp, agora=time.time() + NEGATIVO_S + 5, quadros_fn=faz((0.12, 0.7, LR)))
        assert d5["usar"], d5
        # rosto no meio do quadro: não é webcam -> fallback com motivo
        d6 = decidir("x.mp4", "t2", tmp, quadros_fn=faz((0.5, 0.5, LR)))
        assert not d6["usar"] and "longe das bordas" in d6["motivo"], d6
        # sem rosto nenhum
        d7 = decidir("x.mp4", "t3", tmp, quadros_fn=faz(None))
        assert not d7["usar"] and "nenhum rosto" in d7["motivo"], d7
        # quadro que falha: fallback em vez de exceção
        d8 = decidir("x.mp4", "t4", tmp, quadros_fn=lambda fr: 1 / 0)
        assert not d8["usar"] and "facecam falhou" in d8["motivo"], d8
    print("ok (facecam)")


def _cli(args):
    if args == ["--teste"]:
        autoteste()
        return
    if not args or args[0].startswith("-"):
        sys.exit(__doc__)
    canal = args[args.index("--canal") + 1] if "--canal" in args else "teste"
    clipe = Path(args[0])
    d = decidir(clipe, canal, clipe.parent / "facecam")
    print(json.dumps(d, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True)
    _cli(sys.argv[1:])
