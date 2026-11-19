#!/usr/bin/env python3
r"""galeria.py: galeria local de triagem dos clipes (um arquivo HTML estático, sem servidor, sem CDN).

Lê o que o clipador já gera e monta clipes/galeria.html com um card por vertical (mais novo primeiro):
vídeo, canal, tipo, variante, horário, mensagens do pico e razão sobre a mediana, gancho, frases mais ditas,
botões de copiar (legenda TikTok/Reels, título Shorts, descrição YouTube), caixas "postado em TikTok / Shorts /
Reels / X" (ficam no localStorage do navegador), link e caminho do horizontal (para a compilação) e o caminho
do vertical no Windows com botão de copiar. Só biblioteca padrão do Python.

Fontes de dados (nada é alterado, só lido):
  clipes/verticais/<canal>/<clipe>_<tipo>_<v22|v35>.mp4 + .txt   (texto do post, feito pelo pos.py)
  clipes/picos.csv       mensagens, mediana_base, mais_ditas, demo, gancho (ligado ao vertical pelo horizontal)
  clipes/verticais.csv   duração e pico de áudio do vertical
  clipes/<canal>-<data>-<hora>.mp4   horizontal do corte (compilação)
Só o .mp4 é obrigatório: sem .txt o card sai sem os botões de copiar; sem CSV sai sem dados do pico.
Vertical sem .txt e sem linha no verticais.csv, modificado há menos de 2 min, é tratado como "ainda sendo
renderizado" e só entra na próxima geração.

Uso (de dentro de clipador/):
  ./galeria.sh                       gera clipes/galeria.html uma vez
  ./galeria.sh --assistir 30         regenera a cada 30 s (deixe a página aberta no navegador e dê F5)
  ./galeria.sh --pasta clipes/_teste usa outra pasta de clipes (teste); o HTML sai dentro dela
  ./galeria.sh --saida ARQ.html      escolhe o arquivo de saída (os caminhos dos vídeos ficam relativos a ele)
  ./galeria.sh --marca "Chat Pirou"  valor inicial do campo Marca (a página também deixa digitar)
  ./galeria.sh --distro Ubuntu       nome da distro para o caminho do Windows (padrão: $WSL_DISTRO_NAME)
  ./galeria.sh --teste               autoteste (arquivos de mentira, em pasta temporária)
  (equivale a .venv/bin/python galeria.py ...)

Abrir no navegador do Windows (o HTML usa caminhos relativos, então abra o arquivo direto da pasta):
  \\wsl.localhost\Ubuntu\home\<usuario>\gta6-cortes\clipador\clipes\galeria.html

Na página:
  - filtros: canal, tipo, esconder postados (alguma rede ou todas), só sem spoiler, esconder demo;
    ordenar por horário (novo ou antigo primeiro) ou pela força do pico (mensagens / mediana, piso 1);
  - as marcações de "postado" e os filtros ficam salvos no navegador (localStorage), por pasta de clipes;
    se o navegador bloquear o localStorage, a página avisa e as marcações valem só até recarregar;
  - campo Marca: ao copiar, troca [MARCA] pelo nome (título) ou pela hashtag (#ChatPirou) nos textos;
  - o texto ainda com [colchetes] (marca, URL do VOD, [revisar spoiler]) aparece como pendência no card;
  - "[revisar spoiler]" (tipo história) ganha borda e selo vermelhos; clipe demo ganha selo e borda amarelos.
"""
import argparse
import csv
import datetime as dt
import html
import json
import os
import re
import sys
import tempfile
import time
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote

try:
    import fcntl
except ImportError:  # Python do Windows: sem trava de arquivo (só lemos, tudo bem)
    fcntl = None

PASTA = Path(__file__).resolve().parent

REDES = (("tiktok", "TikTok"), ("shorts", "Shorts"), ("reels", "Reels"), ("x", "X"))
MARCAS = ("Chat Pirou", "Foi Clipado", "Pico do Hype")     # sugestões do campo Marca (marca/nomes.md)
TIPOS_ROTULO = {"humor": "humor", "falha": "falha", "hype": "hype", "susto": "susto",
                "historia": "história", "geral": "geral"}
DICA_VARIANTE = {"v22": "v22: recorte curto de ~22 s em volta do pico de áudio",
                 "v35": "v35: clipe inteiro de ~35 s (controle do teste A/B)"}
EM_PRODUCAO_S = 120    # vertical sem .txt e sem linha no verticais.csv mais novo que isso: ainda renderizando
CAMPOS_TEXTO = ("titulo", "legenda", "descricao")


# ---------- leitura dos dados ----------

def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


def ler_csv(arquivo):
    """Linhas do CSV como dicts de texto. Arquivo ausente ou ilegível = []. Pega trava compartilhada (os
    clip_watchers escrevem com trava exclusiva), mas lê mesmo se a trava não vier em ~2 s."""
    arquivo = Path(arquivo)
    if not arquivo.is_file():
        return []
    try:
        with open(arquivo, newline="", encoding="utf-8", errors="replace") as f:
            if fcntl:
                for _ in range(40):
                    try:
                        fcntl.flock(f, fcntl.LOCK_SH | fcntl.LOCK_NB)
                        break
                    except OSError:
                        time.sleep(0.05)
            linhas = list(csv.DictReader(f))
    except (OSError, csv.Error):
        return []
    saida = []
    for linha in linhas:
        saida.append({(k or "").strip(): (v or "").strip() for k, v in linha.items()
                      if k is not None and isinstance(v, (str, type(None)))})
    return saida


def numero(txt, tipo=float, padrao=0):
    try:
        return tipo(float(str(txt).replace(",", ".")))
    except (TypeError, ValueError):
        return padrao


RE_NOME = re.compile(r"^(?P<canal>.+)-(?P<data>\d{8})-(?P<hora>\d{6})(?:_(?P<tipo>[a-z]+)_(?P<var>v\d+))?$")


def parse_nome(stem):
    """'gaules-20261118-024943_hype_v22' -> canal, data, hora, tipo, var (tipo e var são None no horizontal)."""
    m = RE_NOME.match(stem)
    return m.groupdict() if m else None


def data_do_nome(nome):
    try:
        return dt.datetime.strptime(nome["data"] + nome["hora"], "%Y%m%d%H%M%S")
    except (TypeError, ValueError, KeyError):
        return None


def data_do_csv(txt):
    try:
        return dt.datetime.strptime(txt, "%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        return None


RE_SECAO = re.compile(r"^==\s*(.+?)\s*==$")


def parse_txt(texto):
    """Quebra o .txt do post (pos.texto_post) em título, legenda e descrição.
    Devolve dict: titulo, legenda, descricao (texto pronto), nota (aviso do topo, ex. [revisar spoiler]),
    avisos (parágrafos finais entre parênteses: são avisos internos, não fazem parte da descrição),
    revisar (True se aparece [revisar spoiler])."""
    cab, secoes, ordem, atual = [], {}, [], None
    for linha in texto.splitlines():
        m = RE_SECAO.match(linha.strip())
        if m:
            rot = sem_acento(m.group(1))
            atual = ("titulo" if "titulo" in rot else "legenda" if "legenda" in rot
                     else "descricao" if "descricao" in rot else rot)
            secoes.setdefault(atual, [])
            ordem.append(atual)
            continue
        (cab if atual is None else secoes[atual]).append(linha)
    corpo = {k: "\n".join(v).strip() for k, v in secoes.items()}
    avisos = []
    if ordem:
        ultimo = ordem[-1]
        paragrafos = re.split(r"\n\s*\n", corpo[ultimo])
        while len(paragrafos) > 1 and paragrafos[-1].strip().startswith("(") and paragrafos[-1].strip().endswith(")"):
            avisos.append(paragrafos.pop().strip())
        corpo[ultimo] = "\n\n".join(paragrafos).strip()
    nota = []
    for l in cab:
        if l.strip().startswith("Arquivo:"):
            break
        if l.strip():
            nota.append(l.strip())
    return {"titulo": corpo.get("titulo", ""), "legenda": corpo.get("legenda", ""),
            "descricao": corpo.get("descricao", ""), "nota": " ".join(nota), "avisos": list(reversed(avisos)),
            "revisar": "[revisar spoiler]" in texto.lower()}


def caminho_windows(caminho, distro="Ubuntu"):
    """Caminho do arquivo como o Windows enxerga: \\\\wsl.localhost\\<distro>\\home\\... (ou C:\\... em /mnt/c)."""
    s = str(Path(caminho).resolve())
    if re.match(r"^[A-Za-z]:[\\/]", s) or s.startswith("\\\\"):
        return s.replace("/", "\\")
    m = re.match(r"^/mnt/([A-Za-z])(?:/(.*))?$", s)
    if m:
        return m.group(1).upper() + ":\\" + (m.group(2) or "").replace("/", "\\")
    return "\\\\wsl.localhost\\" + distro + s.replace("/", "\\")


def url_relativa(arquivo, base):
    """Caminho relativo (com / e escapado) de `arquivo` a partir da pasta `base`, para usar em src/href."""
    return quote(Path(os.path.relpath(arquivo, base)).as_posix(), safe="/")


def achar_verticais(pasta):
    raiz = pasta / "verticais"
    if not raiz.is_dir():
        return []
    return sorted(p for p in raiz.rglob("*.mp4") if p.is_file() and not p.name.startswith("."))


def coletar(pasta, destino, distro="Ubuntu"):
    """(clipes, picos_sem_vertical): um dict por vertical, mais novo primeiro."""
    pasta = Path(pasta).resolve()
    base_html = Path(destino).resolve().parent
    picos = {r["clipe"]: r for r in ler_csv(pasta / "picos.csv") if r.get("clipe")}
    verts = {r["vertical"]: r for r in ler_csv(pasta / "verticais.csv") if r.get("vertical")}
    agora = time.time()
    usados, clipes = set(), []
    for mp4 in achar_verticais(pasta):
        try:
            st = mp4.stat()
        except OSError:
            continue
        txt_arq = mp4.with_suffix(".txt")
        vrow = verts.get(mp4.name, {})
        if st.st_size == 0 or (not txt_arq.is_file() and not vrow and agora - st.st_mtime < EM_PRODUCAO_S):
            continue    # vazio ou ainda renderizando
        nome = parse_nome(mp4.stem)
        pai = mp4.parent.name if mp4.parent.name != "verticais" else ""
        canal = (nome and nome["canal"]) or vrow.get("canal") or pai or "?"
        h_nome = f"{nome['canal']}-{nome['data']}-{nome['hora']}.mp4" if nome else vrow.get("clipe", "")
        prow = picos.get(h_nome, {})
        if h_nome:
            usados.add(h_nome)
        tipo = (nome and nome["tipo"]) or vrow.get("tipo") or prow.get("tipo") or "geral"
        variante = (nome and nome["var"]) or vrow.get("variante") or prow.get("variante") or ""
        quando = data_do_csv(prow.get("quando")) or (data_do_nome(nome) if nome else None) \
            or dt.datetime.fromtimestamp(st.st_mtime)
        msgs, base = numero(prow.get("mensagens"), int), numero(prow.get("mediana_base"), float)
        gancho = [p.strip() for p in (prow.get("gancho") or vrow.get("gancho") or "").split(" / ") if p.strip()]
        mais = [p.strip() for p in prow.get("mais_ditas", "").split(" | ") if p.strip()]
        texto_post = ""
        if txt_arq.is_file():
            try:
                texto_post = txt_arq.read_text(encoding="utf-8", errors="replace")
            except OSError:
                texto_post = ""
        post = parse_txt(texto_post) if texto_post else None
        h_arq = (pasta / h_nome) if h_nome else None
        h_existe = bool(h_arq and h_arq.is_file())
        h_srt = h_arq.with_suffix(".srt") if h_arq else None
        clipes.append({
            "id": mp4.relative_to(pasta).as_posix(), "nome": mp4.name, "src": url_relativa(mp4, base_html),
            "canal": canal, "tipo": tipo, "variante": variante,
            "quando": quando, "ts": time.mktime(quando.timetuple()), "mtime": st.st_mtime,
            "msgs": msgs, "base": base, "forca": (msgs / max(base, 1.0)) if msgs > 0 else 0.0,
            "tem_picos": bool(prow), "demo": prow.get("demo", "").lower() in ("1", "true", "sim"),
            "gancho": gancho, "mais": mais, "dur": numero(vrow.get("dur_s"), float, None) if vrow else None,
            "pico_audio": numero(vrow.get("t_pico_audio_s"), float, None) if vrow.get("t_pico_audio_s") else None,
            "post": post, "texto_bruto": texto_post,
            "revisar": tipo == "historia" or bool(post and post["revisar"]),
            "win_v": caminho_windows(mp4, distro),
            "h_nome": h_nome, "h_existe": h_existe, "h_src": url_relativa(h_arq, base_html) if h_existe else "",
            "h_win": caminho_windows(h_arq, distro) if h_arq else "",
            "h_srt": url_relativa(h_srt, base_html) if h_srt and h_srt.is_file() and h_srt.stat().st_size else "",
        })
    clipes.sort(key=lambda c: (-c["ts"], -c["mtime"], c["id"]))
    for i, c in enumerate(clipes):
        c["i"] = i
    return clipes, sum(1 for h in picos if h not in usados)


# ---------- HTML ----------

def br(x, casas=1):
    return f"{x:.{casas}f}".replace(".", ",")


def card_html(c):
    e = html.escape
    i = c["i"]
    tipo_rot = TIPOS_ROTULO.get(c["tipo"], c["tipo"])
    classes = ["card", "tipo-" + (re.sub(r"[^a-z0-9]", "", c["tipo"]) or "x")]
    if c["revisar"]:
        classes.append("spoiler")
    if c["demo"]:
        classes.append("demo")
    selos = [f'<span class="selo neutro">{e(tipo_rot)}</span>']
    if c["variante"]:
        selos.append(f'<span class="selo neutro" title="{e(DICA_VARIANTE.get(c["variante"], c["variante"]))}">'
                     f'{e(c["variante"])}</span>')
    if c["revisar"]:
        selos.append('<span class="selo spoiler">Revisar spoiler</span>')
    else:
        selos.append('<span class="selo seguro" title="Pelo tipo do corte; confira o clipe antes de postar">'
                     'Sem spoiler</span>')
    if c["demo"]:
        selos.append('<span class="selo demo" title="Corte forçado de demonstração, não é um pico real">Demo</span>')

    if c["msgs"] > 0:
        pico = (f'<span class="selo pico" title="mensagens no pico / mediana da base (piso 1, como no detector)">'
                f'Pico ×{br(c["forca"])}</span> '
                f'{c["msgs"]} msgs no pico · mediana {br(c["base"], 0 if c["base"] == int(c["base"]) else 1)}')
    elif c["demo"]:
        pico = '<span class="suave">Sem pico de chat (corte de demonstração).</span>'
    elif not c["tem_picos"]:
        pico = '<span class="suave">Sem dados de pico (este clipe não está no picos.csv).</span>'
    else:
        pico = '<span class="suave">Pico sem mensagens registradas.</span>'

    meta = [f'<time datetime="{c["quando"].strftime("%Y-%m-%dT%H:%M:%S")}">{c["quando"].strftime("%d/%m %H:%M:%S")}</time>'
            f' <span class="ago" data-ts="{int(c["ts"] * 1000)}"></span>']
    if c["dur"]:
        meta.append(f'{br(c["dur"], 0)} s')
    if c["pico_audio"] is not None:
        meta.append(f'pico de áudio em {br(c["pico_audio"])} s')

    gancho = ""
    if c["gancho"]:
        gancho = '<p class="gancho">' + "".join(f"<span>{e(l)}</span>" for l in c["gancho"]) + "</p>"
    chips = ""
    if c["mais"]:
        chips = ('<ul class="chips" aria-label="Frases mais ditas no chat">'
                 + "".join(f"<li>{e(m)}</li>" for m in c["mais"]) + "</ul>")
    post = c["post"]
    aviso = ""
    if post and post["nota"]:
        aviso += f'<p class="aviso">{e(post["nota"])}</p>'
    for a in (post["avisos"] if post else []):
        aviso += f'<p class="aviso leve">{e(a)}</p>'
    if c["revisar"] and not (post and post["nota"]):
        aviso += '<p class="aviso">[revisar spoiler] cena de história: confira o clipe antes de postar.</p>'

    botoes = []
    for chave, rotulo, prim in (("legenda", "Copiar legenda TikTok/Reels", True),
                                ("titulo", "Copiar título Shorts", False),
                                ("descricao", "Copiar descrição YouTube", False)):
        ok = bool(post and post[chave])
        classe = "btn prim" if prim else "btn"
        extra = "" if ok else ' disabled title="Sem texto: falta o .txt deste clipe"'
        botoes.append(f'<button type="button" class="{classe}" data-copiar="{chave}"{extra}>{rotulo}</button>')

    quem = f'{c["canal"]} {c["quando"].strftime("%H:%M:%S")} {tipo_rot}'
    redes = "".join(f'<label class="chk mini"><input type="checkbox" data-rede="{r}"> {n}</label>' for r, n in REDES)

    caminhos = (f'<div class="cam"><span class="rot">Vertical</span><code data-cam="v">{e(c["win_v"])}</code>'
                '<button type="button" class="btn mini" data-caminho="v">Copiar caminho</button></div>')
    if c["h_existe"]:
        srt = f' · <a href="{c["h_srt"]}" target="_blank" rel="noopener">legenda .srt</a>' if c["h_srt"] else ""
        caminhos += (f'<div class="cam"><span class="rot">Horizontal (compilação)</span>'
                     f'<span><a href="{c["h_src"]}" target="_blank" rel="noopener">abrir {e(c["h_nome"])}</a>{srt}</span>'
                     f'<code data-cam="h">{e(c["h_win"])}</code>'
                     '<button type="button" class="btn mini" data-caminho="h">Copiar caminho</button></div>')
    else:
        faltou = ": " + e(c["h_nome"]) if c["h_nome"] else ""
        caminhos += ('<div class="cam"><span class="rot">Horizontal (compilação)</span>'
                     f'<span class="suave">não encontrado{faltou}</span></div>')

    bruto = ""
    if c["texto_bruto"]:
        bruto = ('<details class="texto"><summary>Ver texto do post</summary>'
                 f'<pre>{e(c["texto_bruto"])}</pre></details>')

    return (
        f'<article class="{" ".join(classes)}" aria-labelledby="t{i}" data-id="{e(c["id"])}" data-i="{i}" '
        f'data-canal="{e(c["canal"])}" data-tipo="{e(c["tipo"])}" data-spoiler="{int(c["revisar"])}" '
        f'data-demo="{int(c["demo"])}" data-ts="{int(c["ts"] * 1000)}" data-forca="{c["forca"]:.3f}" '
        f'data-msgs="{c["msgs"]}">\n'
        f'<div class="midia"><video controls preload="metadata" playsinline src="{c["src"]}#t=0.1" '
        f'aria-label="Vertical de {e(c["canal"])}, {e(tipo_rot)}, {c["quando"].strftime("%H:%M:%S")}"></video></div>\n'
        '<div class="corpo">\n'
        f'<div class="cab"><h2 id="t{i}">{e(c["canal"])}</h2><div class="selos">{"".join(selos)}</div></div>\n'
        f'{gancho}\n'
        f'<p class="meta">{" · ".join(meta)}</p>\n'
        f'<p class="pico-l">{pico}</p>\n'
        f'{chips}\n{aviso}\n'
        '<p class="pend" hidden></p>\n'
        f'<div class="acoes">{"".join(botoes)}</div>\n'
        f'<div class="redes" role="group" aria-labelledby="g{i}"><span class="rot" id="g{i}">Postado em'
        f'<span class="sr">: {e(quem)}</span></span>{redes}</div>\n'
        f'<div class="caminhos">{caminhos}</div>\n'
        f'{bruto}\n'
        '</div>\n</article>')


def json_seguro(obj):
    s = json.dumps(obj, ensure_ascii=False)
    for a, b in (("<", "\\u003c"), (">", "\\u003e"), ("&", "\\u0026"), ("\u2028", "\\u2028"), ("\u2029", "\\u2029")):
        s = s.replace(a, b)
    return s


def pagina(clipes, sem_vertical, pasta, destino, marca="", assistir=None):
    e = html.escape
    canais = sorted({c["canal"] for c in clipes})
    tipos = sorted({c["tipo"] for c in clipes})
    cfg = {"clipes": {c["id"]: {k: (c["post"][k] if c["post"] else "") for k in CAMPOS_TEXTO} for c in clipes},
           "redes": [list(r) for r in REDES], "ns": re.sub(r"[^A-Za-z0-9_.-]", "_", Path(pasta).name),
           "marca_padrao": marca}
    opcoes_canal = "".join(f'<option value="{e(c)}">{e(c)}</option>' for c in canais)
    opcoes_tipo = "".join(f'<option value="{e(t)}">{e(TIPOS_ROTULO.get(t, t))}</option>' for t in tipos)
    agora = time.strftime("%d/%m/%Y %H:%M:%S")
    atualiza = (f"A página é regenerada a cada {assistir:g} s (modo --assistir): dê F5 para ver os novos clipes. "
                if assistir else "Para ver clipes novos, rode ./galeria.sh de novo e dê F5. ")
    sub = f"{len(clipes)} verticais em {len(canais)} canais · gerada em {agora}."
    if sem_vertical:
        sub += f" {sem_vertical} picos ainda sem vertical (em produção ou falhou)."
    if clipes:
        cartoes = "\n".join(card_html(c) for c in clipes)
        vazio_total = ""
    else:
        cartoes = ""
        vazio_total = (f'<p class="vazio">Nenhum vertical ainda em <code>{e(str(Path(pasta) / "verticais"))}</code>. '
                       'O clipador gera os verticais em clipes/verticais/&lt;canal&gt;/ depois de cada pico; '
                       'deixe <code>./galeria.sh --assistir 30</code> rodando e atualize a página (F5).</p>')
    valores = {"CSS": CSS, "JS": JS, "SUB": e(sub), "ATUALIZA": e(atualiza), "CANAIS": opcoes_canal,
               "TIPOS": opcoes_tipo, "MARCAS": "".join(f'<option value="{e(m)}"></option>' for m in MARCAS),
               "CARTOES": cartoes, "VAZIO_TOTAL": vazio_total, "DADOS": json_seguro(cfg)}
    # uma passada só: texto vindo do chat nunca é tratado como marcador do molde
    return re.sub(r"__([A-Z_]+)__", lambda m: valores.get(m.group(1), m.group(0)), MOLDE)


MOLDE = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark">
<title>Galeria de clipes GTA 6</title>
<style>
__CSS__
</style>
</head>
<body>
<a class="pular" href="#lista">Pular para os clipes</a>
<header class="titulo">
<h1>Galeria de <span>clipes</span></h1>
<p class="sub">__SUB__</p>
<p class="sub">__ATUALIZA__As marcações de postado ficam só neste navegador.</p>
<p class="aviso-storage" id="aviso-storage" hidden>O navegador bloqueou o armazenamento local: as marcações e os filtros valem só até recarregar a página.</p>
<noscript><p class="aviso-storage">Esta página precisa de JavaScript para filtros, marcações e botões de copiar.</p></noscript>
</header>
<div class="barra">
<div class="contador" id="contador" role="status" aria-label="Contagem de postagens"></div>
<form class="filtros" id="filtros" aria-label="Filtros e ordenação">
<div class="campo"><label for="f-canal">Canal</label><select id="f-canal"><option value="">Todos</option>__CANAIS__</select></div>
<div class="campo"><label for="f-tipo">Tipo</label><select id="f-tipo"><option value="">Todos</option>__TIPOS__</select></div>
<div class="campo"><label for="f-ordem">Ordenar por</label><select id="f-ordem"><option value="recente">Horário (mais novo primeiro)</option><option value="antigo">Horário (mais antigo primeiro)</option><option value="forca">Força do pico (maior primeiro)</option></select></div>
<label class="chk" for="f-postados"><input type="checkbox" id="f-postados"> Esconder postados</label>
<div class="campo"><label for="f-modo">Postado = marcado em</label><select id="f-modo"><option value="alguma">alguma rede</option><option value="todas">todas as redes</option></select></div>
<label class="chk" for="f-spoiler"><input type="checkbox" id="f-spoiler"> Só sem spoiler</label>
<label class="chk" for="f-demo"><input type="checkbox" id="f-demo"> Esconder demo</label>
<div class="campo"><label for="marca">Marca (troca [MARCA] ao copiar)</label><input type="text" id="marca" list="marcas" autocomplete="off" placeholder="ex.: Chat Pirou"><datalist id="marcas">__MARCAS__</datalist></div>
<button type="button" class="btn" id="f-limpar">Limpar filtros</button>
<p class="status" id="status" role="status"></p>
</form>
</div>
<main id="lista" tabindex="-1">
__VAZIO_TOTAL__
<div class="grade" id="grade">
__CARTOES__
</div>
<p class="vazio" id="vazio" hidden>Nenhum clipe com esses filtros. Use "Limpar filtros" para ver tudo.</p>
</main>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<script type="application/json" id="dados">__DADOS__</script>
<script>
__JS__
</script>
</body>
</html>
"""

CSS = r"""
:root{--carvao:#0B0B12;--grafite:#1A1A24;--grafite2:#242433;--borda:#34344A;--ctl:#7A7A96;--gelo:#F5F7FA;
--suave:#B9BECB;--amarelo:#FFD400;--magenta:#FF2E88;--ciano:#19E3FF;--vermelho:#FF3B30;--verde:#22D47B;
--display:Anton,Impact,"Arial Narrow Bold","Arial Narrow",sans-serif;color-scheme:dark}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--carvao);color:var(--gelo);font:16px/1.45 Inter,"Segoe UI",system-ui,-apple-system,Roboto,Arial,sans-serif}
[hidden]{display:none!important}
a{color:var(--ciano)}
code{font:12px/1.4 ui-monospace,SFMono-Regular,Consolas,"Liberation Mono",monospace;overflow-wrap:anywhere;color:var(--suave)}
:focus-visible{outline:3px solid var(--amarelo);outline-offset:2px}
.sr{position:absolute;width:1px;height:1px;margin:-1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.pular{position:absolute;left:8px;top:-60px;background:var(--amarelo);color:var(--carvao);padding:8px 14px;border-radius:8px;font-weight:700;z-index:30}
.pular:focus{top:8px}
.titulo{max-width:1500px;margin:0 auto;padding:16px 16px 4px}
h1{margin:0;font:400 clamp(1.7rem,4.5vw,2.4rem)/1.05 var(--display);letter-spacing:.02em;text-transform:uppercase}
h1 span{color:var(--amarelo)}
.sub{margin:.35rem 0 0;color:var(--suave);font-size:.9rem}
.aviso-storage{margin:.6rem 0 0;padding:8px 12px;border-left:4px solid var(--amarelo);background:rgba(255,212,0,.1);border-radius:6px;font-size:.9rem}
.barra{background:rgba(11,11,18,.97);border-bottom:1px solid var(--borda);border-top:1px solid var(--borda);margin-top:12px}
.contador{max-width:1500px;margin:0 auto;padding:10px 16px 0;display:flex;flex-wrap:wrap;gap:8px}
.pill{display:inline-flex;gap:6px;align-items:baseline;padding:3px 10px;border:1px solid var(--ctl);border-radius:999px;background:var(--grafite);font-size:.85rem}
.pill b{color:var(--amarelo)}
.filtros{max-width:1500px;margin:0 auto;padding:10px 16px 12px;display:flex;flex-wrap:wrap;gap:10px 14px;align-items:flex-end}
.campo{display:flex;flex-direction:column;gap:4px;font-size:.8rem;color:var(--suave)}
select,input[type=text],button{font:inherit;color:inherit}
select,input[type=text]{background:var(--grafite);color:var(--gelo);border:1px solid var(--ctl);border-radius:8px;padding:8px 10px;min-height:40px;max-width:100%}
input[type=text]{width:13rem}
input[type=checkbox]{width:20px;height:20px;margin:0;accent-color:var(--amarelo);flex:none}
.chk{display:inline-flex;align-items:center;gap:8px;min-height:40px;padding:0 12px;border:1px solid var(--ctl);border-radius:8px;background:var(--grafite);cursor:pointer;user-select:none}
.chk.mini{min-height:36px;padding:0 10px;font-size:.9rem}
.chk:hover{border-color:var(--gelo)}
.status{margin:0;align-self:center;color:var(--suave);font-size:.85rem}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:40px;padding:8px 14px;border-radius:8px;border:1px solid var(--ctl);background:var(--grafite2);color:var(--gelo);font-weight:600;cursor:pointer;text-align:center;line-height:1.2}
.btn:hover{border-color:var(--gelo)}
.btn.prim{background:var(--amarelo);border-color:var(--amarelo);color:var(--carvao)}
.btn.ok,.btn.ok:hover{background:var(--verde);border-color:var(--verde);color:var(--carvao)}
.btn:disabled{opacity:.45;cursor:not-allowed}
.btn.mini{min-height:32px;padding:4px 10px;font-size:.8rem}
main{outline:none}
.grade{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,580px),1fr));gap:16px;max-width:1500px;margin:0 auto;padding:16px}
.vazio{max-width:1500px;margin:24px auto;padding:0 16px;color:var(--suave)}
.card{display:grid;grid-template-columns:minmax(150px,210px) minmax(0,1fr);gap:14px;background:var(--grafite);border:1px solid var(--borda);border-radius:12px;padding:12px;align-content:start}
.card.demo{border:2px dashed var(--amarelo)}
.card.spoiler{border:2px solid var(--vermelho);box-shadow:0 0 0 3px rgba(255,59,48,.18)}
.card.postado-parcial{border-left:6px solid var(--verde)}
.card.postado-todas{opacity:.72}
.card.vai-sumir{opacity:.45}
.midia video{display:block;width:100%;aspect-ratio:9/16;background:#000;border-radius:8px;object-fit:contain}
.corpo{display:flex;flex-direction:column;gap:8px;min-width:0}
.corpo>p{margin:0}
.cab{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center}
h2{margin:0;font:400 1.5rem/1.1 var(--display);letter-spacing:.03em;text-transform:uppercase;overflow-wrap:anywhere}
.selos{display:flex;flex-wrap:wrap;gap:6px}
.selo{display:inline-block;padding:2px 9px;border-radius:999px;font-size:.72rem;font-weight:800;letter-spacing:.04em;text-transform:uppercase;line-height:1.5}
.selo.neutro{border:1px solid var(--ctl);color:var(--gelo)}
.selo.spoiler{background:var(--vermelho);color:var(--carvao)}
.selo.seguro{background:var(--verde);color:var(--carvao)}
.selo.pico{background:var(--magenta);color:var(--carvao)}
.selo.demo{background:var(--amarelo);color:var(--carvao)}
.gancho{display:flex;flex-direction:column;font:400 1.3rem/1.15 var(--display);text-transform:uppercase;letter-spacing:.02em}
.gancho span:nth-child(2){color:var(--amarelo)}
.meta,.pico-l{font-size:.9rem}
.meta,.suave{color:var(--suave)}
.ago{color:var(--suave)}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin:0;padding:0;list-style:none}
.chips li{padding:2px 9px;border-radius:6px;background:var(--grafite2);border:1px solid var(--borda);font-size:.8rem;overflow-wrap:anywhere}
.aviso{padding:8px 10px;border-left:4px solid var(--vermelho);background:rgba(255,59,48,.13);border-radius:6px;font-size:.85rem}
.aviso.leve{border-left-color:var(--ctl);background:var(--grafite2);color:var(--suave)}
.pend{font-size:.82rem;color:var(--amarelo)}
.acoes{display:flex;flex-wrap:wrap;gap:8px}
.redes{display:flex;flex-wrap:wrap;gap:6px 8px;align-items:center}
.redes .rot{font-size:.8rem;color:var(--suave);padding-right:4px}
.caminhos{display:flex;flex-direction:column;gap:8px;font-size:.85rem}
.cam{display:flex;flex-wrap:wrap;gap:4px 10px;align-items:center}
.cam .rot{font-weight:700;min-width:9.5rem}
.texto summary{cursor:pointer;color:var(--ciano);font-size:.85rem}
.texto pre{margin:8px 0 0;padding:10px;background:var(--carvao);border:1px solid var(--borda);border-radius:8px;white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.5 ui-monospace,Consolas,monospace;user-select:all}
.toast{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);max-width:min(92vw,560px);background:var(--gelo);color:var(--carvao);padding:10px 16px;border-radius:10px;font-weight:600;font-size:.9rem;box-shadow:0 6px 24px rgba(0,0,0,.5);opacity:0;pointer-events:none;z-index:40}
.toast.on{opacity:1}
@media (prefers-reduced-motion:no-preference){.toast{transition:opacity .15s}.btn,.chk{transition:background-color .12s,border-color .12s}}
@media (min-width:900px) and (min-height:820px){.barra{position:sticky;top:0;z-index:20}}
@media (max-width:620px){.card{grid-template-columns:1fr}.midia{max-width:300px;width:100%;margin:0 auto}.grade{padding:12px 16px}input[type=text]{width:100%}.campo{flex:1 1 140px}}
@media (forced-colors:active){.selo,.btn,.chk{border:1px solid ButtonText}}
"""

JS = r"""
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var cfg;
  try { cfg = JSON.parse(document.getElementById('dados').textContent); }
  catch (e) { cfg = { clipes: {}, redes: [], ns: 'x', marca_padrao: '' }; }
  var REDES = cfg.redes;
  var NS = 'gta6galeria:' + cfg.ns + ':';
  var K_POST = NS + 'postados', K_FILT = NS + 'filtros', K_MARCA = 'gta6galeria:marca';
  var ROTULOS = { titulo: 'título Shorts', legenda: 'legenda TikTok/Reels', descricao: 'descrição YouTube' };
  var RE_PEND = /\[[^\]\n]{1,60}\]/g;

  var grade = $('#grade');
  var cards = Array.prototype.slice.call(grade.querySelectorAll('.card'));

  /* ---- armazenamento: localStorage pode falhar (janela privada, dados bloqueados...) ---- */
  var storageRuim = false;
  function avisarStorage() { var el = $('#aviso-storage'); if (el) { el.hidden = !storageRuim; } }
  function lerLS(k) {
    try { return window.localStorage.getItem(k); } catch (e) { storageRuim = true; return null; }
  }
  function gravarLS(k, v) {
    try { window.localStorage.setItem(k, v); } catch (e) { storageRuim = true; }
    avisarStorage();
  }
  function lerJSON(k, padrao) {
    var s = lerLS(k);
    if (!s) { return padrao; }
    try { var o = JSON.parse(s); return (o && typeof o === 'object') ? o : padrao; } catch (e) { return padrao; }
  }

  /* ---- marcações de postado ---- */
  var postados = lerJSON(K_POST, {});
  function marcado(id, rede) { var p = postados[id]; return !!(p && p[rede]); }
  function nMarcas(id) {
    var p = postados[id], n = 0;
    if (p) { REDES.forEach(function (r) { if (p[r[0]]) { n++; } }); }
    return n;
  }
  function postadoConta(id, modo) { var n = nMarcas(id); return modo === 'todas' ? n === REDES.length : n > 0; }
  function definir(id, rede, valor) {
    var p = postados[id] || (postados[id] = {});
    if (valor) { p[rede] = true; } else { delete p[rede]; }
    if (!nMarcas(id)) { delete postados[id]; }
    gravarLS(K_POST, JSON.stringify(postados));
  }
  function pintar(card) {
    var n = nMarcas(card.getAttribute('data-id'));
    card.classList.toggle('postado-parcial', n > 0 && n < REDES.length);
    card.classList.toggle('postado-todas', n > 0 && n === REDES.length);
  }
  function contar() {
    var por = {}, sem = 0, html = '';
    REDES.forEach(function (r) { por[r[0]] = 0; });
    cards.forEach(function (c) {
      var id = c.getAttribute('data-id');
      if (!nMarcas(id)) { sem++; }
      REDES.forEach(function (r) { if (marcado(id, r[0])) { por[r[0]]++; } });
    });
    REDES.forEach(function (r) { html += '<span class="pill"><b>' + r[1] + '</b> ' + por[r[0]] + '/' + cards.length + '</span>'; });
    html += '<span class="pill"><b>' + sem + '</b> sem nenhuma postagem</span>';
    $('#contador').innerHTML = html;
  }

  /* ---- filtros e ordem ---- */
  var PADRAO = { canal: '', tipo: '', ordem: 'recente', postados: false, modo: 'alguma', spoiler: false, demo: false };
  var ctl = {
    canal: $('#f-canal'), tipo: $('#f-tipo'), ordem: $('#f-ordem'), postados: $('#f-postados'),
    modo: $('#f-modo'), spoiler: $('#f-spoiler'), demo: $('#f-demo')
  };
  function lerFiltros() {
    return {
      canal: ctl.canal.value, tipo: ctl.tipo.value, ordem: ctl.ordem.value || 'recente',
      postados: ctl.postados.checked, modo: ctl.modo.value || 'alguma',
      spoiler: ctl.spoiler.checked, demo: ctl.demo.checked
    };
  }
  function definirSelect(sel, valor, padrao) {
    sel.value = valor;
    if (sel.selectedIndex < 0) { sel.value = padrao; }
  }
  function escreverFiltros(f) {
    definirSelect(ctl.canal, f.canal, '');
    definirSelect(ctl.tipo, f.tipo, '');
    definirSelect(ctl.ordem, f.ordem, 'recente');
    definirSelect(ctl.modo, f.modo, 'alguma');
    ctl.postados.checked = !!f.postados;
    ctl.spoiler.checked = !!f.spoiler;
    ctl.demo.checked = !!f.demo;
  }
  function num(c, k) { return Number(c.getAttribute('data-' + k)) || 0; }
  var ordemAtual = 'recente';
  var COMPARADORES = {
    recente: function (a, b) { return num(b, 'ts') - num(a, 'ts') || num(a, 'i') - num(b, 'i'); },
    antigo: function (a, b) { return num(a, 'ts') - num(b, 'ts') || num(b, 'i') - num(a, 'i'); },
    forca: function (a, b) {
      return num(b, 'forca') - num(a, 'forca') || num(b, 'msgs') - num(a, 'msgs') ||
        num(b, 'ts') - num(a, 'ts') || num(a, 'i') - num(b, 'i');
    }
  };
  function reordenar(ordem) {
    cards.sort(COMPARADORES[ordem] || COMPARADORES.recente);
    var frag = document.createDocumentFragment();
    cards.forEach(function (c) { frag.appendChild(c); });
    grade.appendChild(frag);
    ordemAtual = ordem;
  }
  function pausar(card) {
    var v = card.querySelector('video');
    if (v && !v.paused) { v.pause(); }
  }
  function aplicar() {
    var f = lerFiltros(), visiveis = 0;
    if (f.ordem !== ordemAtual) { reordenar(f.ordem); }
    cards.forEach(function (c) {
      var ok = (!f.canal || c.getAttribute('data-canal') === f.canal) &&
        (!f.tipo || c.getAttribute('data-tipo') === f.tipo) &&
        !(f.spoiler && c.getAttribute('data-spoiler') === '1') &&
        !(f.demo && c.getAttribute('data-demo') === '1') &&
        !(f.postados && postadoConta(c.getAttribute('data-id'), f.modo));
      c.classList.remove('vai-sumir');
      if (!ok) { pausar(c); }
      c.hidden = !ok;
      if (ok) { visiveis++; }
    });
    $('#status').textContent = visiveis + ' de ' + cards.length + ' clipes';
    $('#vazio').hidden = visiveis > 0 || cards.length === 0;
    gravarLS(K_FILT, JSON.stringify(f));
  }

  /* ---- marca e pendências ---- */
  var marcaEl = $('#marca');
  function marcaNome() { return (marcaEl.value || '').trim(); }
  function marcaTag(nome) { return nome.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^A-Za-z0-9_]/g, ''); }
  function montar(id, qual) {
    var t = cfg.clipes[id], s = t ? (t[qual] || '') : '', nome = marcaNome(), tag = marcaTag(nome);
    if (nome && tag) {
      s = s.replace(/#?\[MARCA\]/g, function () { return qual === 'titulo' ? nome : '#' + tag; });
    }
    return s;
  }
  function pendencias(texto) {
    var vistos = {}, lista = [];
    (texto.match(RE_PEND) || []).forEach(function (p) { if (!vistos[p]) { vistos[p] = 1; lista.push(p); } });
    return lista;
  }
  function atualizarPend() {
    cards.forEach(function (c) {
      var el = c.querySelector('.pend');
      if (!el) { return; }
      var id = c.getAttribute('data-id');
      var lista = pendencias(['titulo', 'legenda', 'descricao'].map(function (q) { return montar(id, q); }).join('\n'));
      el.textContent = lista.length ? 'Ainda no texto, trocar antes de postar: ' + lista.join(' · ') : '';
      el.hidden = !lista.length;
    });
  }

  /* ---- copiar ---- */
  var toastT = null;
  function toast(msg, longo) {
    var el = $('#toast');
    el.textContent = msg;
    el.classList.add('on');
    clearTimeout(toastT);
    toastT = setTimeout(function () { el.classList.remove('on'); }, longo ? 6000 : 2600);
  }
  function copiarSelecao(texto) {
    var ta = document.createElement('textarea'), ok = false;
    ta.value = texto;
    ta.setAttribute('readonly', '');
    ta.setAttribute('aria-hidden', 'true');
    ta.style.cssText = 'position:fixed;top:0;left:0;width:1px;height:1px;opacity:0';
    document.body.appendChild(ta);
    try { ta.focus(); ta.select(); ta.setSelectionRange(0, texto.length); ok = document.execCommand('copy'); }
    catch (e) { ok = false; }
    document.body.removeChild(ta);
    return ok;
  }
  function copiarTexto(texto) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        return navigator.clipboard.writeText(texto).then(function () { return true; },
          function () { return copiarSelecao(texto); });
      } catch (e) { /* cai no plano B */ }
    }
    return Promise.resolve(copiarSelecao(texto));
  }
  function feedback(btn) {
    if (!btn.getAttribute('data-rot')) { btn.setAttribute('data-rot', btn.textContent); }
    btn.textContent = 'Copiado \u2713';
    btn.classList.add('ok');
    clearTimeout(btn._t);
    btn._t = setTimeout(function () { btn.textContent = btn.getAttribute('data-rot'); btn.classList.remove('ok'); }, 1600);
  }
  function copiar(texto, btn, nome, qual, card) {
    copiarTexto(texto).then(function (ok) {
      try { btn.focus(); } catch (e) { /* sem foco, tudo bem */ }
      if (!ok) {
        toast('Não consegui copiar. Abra "Ver texto do post" e selecione o texto à mão.', true);
        var d = card && card.querySelector('details');
        if (d) { d.open = true; }
        return;
      }
      feedback(btn);
      var avisos = [], p = pendencias(texto);
      if (p.length) { avisos.push('ainda tem ' + p.join(' ')); }
      if (qual === 'titulo' && texto.length > 100) { avisos.push('título com ' + texto.length + ' caracteres, o Shorts aceita 100'); }
      toast('Copiado: ' + nome + (avisos.length ? ' (atenção: ' + avisos.join('; ') + ')' : ''), avisos.length > 0);
    });
  }

  /* ---- eventos ---- */
  $('#filtros').addEventListener('submit', function (ev) { ev.preventDefault(); });
  $('#filtros').addEventListener('change', aplicar);
  $('#f-limpar').addEventListener('click', function () { escreverFiltros(PADRAO); aplicar(); });
  marcaEl.addEventListener('input', function () { gravarLS(K_MARCA, marcaEl.value); atualizarPend(); });

  grade.addEventListener('click', function (ev) {
    var b = ev.target && ev.target.closest ? ev.target.closest('button') : null;
    if (!b || !grade.contains(b)) { return; }
    var card = b.closest('.card');
    if (!card) { return; }
    var qual = b.getAttribute('data-copiar'), cam = b.getAttribute('data-caminho');
    if (qual) {
      var texto = montar(card.getAttribute('data-id'), qual);
      if (!texto) { toast('Sem texto para copiar: falta o .txt deste clipe.'); return; }
      copiar(texto, b, ROTULOS[qual] || qual, qual, card);
    } else if (cam) {
      var code = card.querySelector('code[data-cam="' + cam + '"]');
      if (code) { copiar(code.textContent, b, 'caminho', 'caminho', card); }
    }
  });
  grade.addEventListener('change', function (ev) {
    var cb = ev.target, rede = cb && cb.getAttribute ? cb.getAttribute('data-rede') : null;
    if (!rede) { return; }
    var card = cb.closest('.card'), f = lerFiltros();
    definir(card.getAttribute('data-id'), rede, cb.checked);
    pintar(card);
    contar();
    card.classList.toggle('vai-sumir', f.postados && postadoConta(card.getAttribute('data-id'), f.modo));
  });
  grade.addEventListener('play', function (ev) {   /* um vídeo por vez */
    cards.forEach(function (c) {
      var v = c.querySelector('video');
      if (v && v !== ev.target && !v.paused) { v.pause(); }
    });
  }, true);

  /* ---- "há X min" ---- */
  function haQuanto(ms) {
    var m = Math.round((Date.now() - ms) / 60000), h;
    if (m < 1) { return 'agora'; }
    if (m < 60) { return 'há ' + m + ' min'; }
    h = Math.floor(m / 60);
    return h < 24 ? 'há ' + h + ' h ' + (m % 60) + ' min' : 'há ' + Math.floor(h / 24) + ' d';
  }
  function atualizarAgo() {
    Array.prototype.forEach.call(grade.querySelectorAll('.ago'), function (el) {
      el.textContent = '(' + haQuanto(Number(el.getAttribute('data-ts'))) + ')';
    });
  }

  /* ---- início ---- */
  cards.forEach(function (c) {
    var id = c.getAttribute('data-id');
    REDES.forEach(function (r) {
      var cb = c.querySelector('input[data-rede="' + r[0] + '"]');
      if (cb) { cb.checked = marcado(id, r[0]); }
    });
    pintar(c);
  });
  var m0 = lerLS(K_MARCA);
  marcaEl.value = m0 !== null ? m0 : (cfg.marca_padrao || '');
  escreverFiltros(Object.assign({}, PADRAO, lerJSON(K_FILT, {})));
  aplicar();
  contar();
  atualizarPend();
  atualizarAgo();
  avisarStorage();
  setInterval(atualizarAgo, 30000);
})();
"""


# ---------- geração ----------

def escrever_atomico(destino, texto):
    """Grava em arquivo temporário e troca: quem der F5 no meio nunca pega a página pela metade."""
    destino = Path(destino)
    tmp = destino.with_name("." + destino.name + ".tmp")
    tmp.write_text(texto, encoding="utf-8", newline="\n")
    os.replace(tmp, destino)


def gerar(pasta, saida=None, distro="Ubuntu", marca="", assistir=None):
    pasta = Path(pasta).resolve()
    if not pasta.is_dir():
        raise SystemExit(f"pasta de clipes não encontrada: {pasta}")
    destino = Path(saida).resolve() if saida else pasta / "galeria.html"
    clipes, sem_vertical = coletar(pasta, destino, distro)
    escrever_atomico(destino, pagina(clipes, sem_vertical, pasta, destino, marca, assistir))
    return destino, clipes, sem_vertical


def assistir_loop(args):
    ultimo = None
    print(f"galeria: regenerando a cada {args.assistir:g} s (Ctrl+C para parar)", flush=True)
    while True:
        try:
            destino, clipes, sem_vertical = gerar(args.pasta, args.saida, args.distro, args.marca, args.assistir)
            estado = (len(clipes), sem_vertical)
            if estado != ultimo:
                print(f"[{time.strftime('%H:%M:%S')}] {destino}: {len(clipes)} verticais "
                      f"({sem_vertical} picos sem vertical)", flush=True)
                ultimo = estado
        except Exception as erro:   # CSV pela metade, disco cheio... tenta de novo no próximo ciclo
            print(f"[{time.strftime('%H:%M:%S')}] erro ao gerar a galeria: {erro}", flush=True)
        time.sleep(args.assistir)


# ---------- autoteste ----------

class _Valida(HTMLParser):
    """Confere que as tags fecham direito e que ids são únicos."""
    VAZIAS = {"meta", "link", "input", "br", "hr", "img", "source", "area", "base", "col", "embed", "param",
              "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pilha, self.erros, self.ids, self.srcs, self.fors = [], [], set(), [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            if a["id"] in self.ids:
                self.erros.append(f"id repetido: {a['id']}")
            self.ids.add(a["id"])
        if tag in ("video", "a") and (a.get("src") or a.get("href")):
            self.srcs.append(a.get("src") or a.get("href"))
        if tag == "label" and a.get("for"):
            self.fors.append(a["for"])
        if tag not in self.VAZIAS:
            self.pilha.append(tag)

    def handle_endtag(self, tag):
        if tag in self.VAZIAS:
            return
        if not self.pilha or self.pilha[-1] != tag:
            self.erros.append(f"</{tag}> fora de lugar (aberto: {self.pilha[-3:]})")
            if tag in self.pilha:
                while self.pilha and self.pilha.pop() != tag:
                    pass
        else:
            self.pilha.pop()


def valida_html(texto, base=None):
    """Lista de problemas do HTML: tags mal fechadas, ids repetidos, label sem alvo, src/href relativo que não existe."""
    v = _Valida()
    v.feed(texto)
    v.close()
    erros = list(v.erros) + ([f"tags abertas no fim: {v.pilha}"] if v.pilha else [])
    erros += [f"label for={f} sem alvo" for f in v.fors if f not in v.ids]
    if base:
        for s in v.srcs:
            if s.startswith(("#", "http:", "https:", "data:")):
                continue
            if not (Path(base) / unquote(s.split("#")[0])).exists():
                erros.append(f"arquivo não existe: {s}")
    return erros


def autoteste():
    # texto do post
    amostra = ("[revisar spoiler] cena de história: confira.\nSegunda linha do aviso.\n\n"
               "Arquivo: gaules-20261118-024943_historia_v35  |  tipo: historia  |  variante: v35\n\n"
               "== TÍTULO (YouTube Shorts, até 100 caracteres) ==\nCLIMA | [MARCA]\n\n"
               "== LEGENDA (TikTok e Reels) ==\n🎥 Live: gaules\nTexto\n#GTA6 #[MARCA]\n\n"
               "== DESCRIÇÃO (YouTube) ==\nLinha 1\n\nHashtags: #GTA6 [MARCA]\n\n(Aviso interno do clipador.)\n")
    p = parse_txt(amostra)
    assert p["titulo"] == "CLIMA | [MARCA]", p["titulo"]
    assert p["legenda"].startswith("🎥 Live: gaules") and p["legenda"].endswith("#[MARCA]"), p["legenda"]
    assert p["descricao"].endswith("#GTA6 [MARCA]"), p["descricao"]
    assert p["avisos"] == ["(Aviso interno do clipador.)"] and p["revisar"], p
    assert p["nota"].startswith("[revisar spoiler] cena") and "Segunda linha" in p["nota"], p["nota"]
    assert parse_txt("sem seções")["titulo"] == ""
    # nomes
    assert parse_nome("gaules-20261118-024943_hype_v22") == {
        "canal": "gaules", "data": "20261118", "hora": "024943", "tipo": "hype", "var": "v22"}
    n = parse_nome("loud_coringa2-20261118-024943")
    assert n["canal"] == "loud_coringa2" and n["tipo"] is None, n
    assert parse_nome("qualquer.mp4") is None
    # caminho do Windows
    assert caminho_windows("/home/x/a b/y.mp4", "Ubuntu").startswith("\\\\wsl.localhost\\Ubuntu\\home\\x\\a b\\y.mp4")
    assert caminho_windows("/mnt/c/Users/Z/f.mp4") == "C:\\Users\\Z\\f.mp4"
    assert numero("7,5") == 7.5 and numero("") == 0 and numero("x", float, None) is None
    # pasta falsa de ponta a ponta
    with tempfile.TemporaryDirectory() as tmp:
        raiz = Path(tmp) / "clipes"
        (raiz / "verticais" / "gaules").mkdir(parents=True)
        (raiz / "verticais" / "lofi girl").mkdir()
        agora = time.time()
        antigo = agora - 3600

        def faz(caminho, conteudo=b"x", idade=antigo):
            caminho.write_bytes(conteudo)
            os.utime(caminho, (idade, idade))

        faz(raiz / "gaules-20261118-024943.mp4")
        faz(raiz / "gaules-20261118-024943.srt")
        v1 = raiz / "verticais" / "gaules" / "gaules-20261118-024943_historia_v35.mp4"
        faz(v1)
        faz(v1.with_suffix(".txt"), amostra.encode("utf-8"))
        v2 = raiz / "verticais" / "gaules" / "gaules-20261118-031500_hype_v22.mp4"
        faz(v2)
        faz(raiz / "verticais" / "lofi girl" / "lofi-20261118-030000.mp4")          # legado: sem .txt, antigo
        faz(raiz / "verticais" / "gaules" / "gaules-20261118-040000_humor_v22.mp4", idade=agora)   # renderizando
        faz(raiz / "verticais" / "gaules" / "vazio-20261118-050000_humor_v22.mp4", b"")           # vazio
        (raiz / "picos.csv").write_text(
            "quando,canal,gravacao,gravado_s,relogio_s,mensagens,mediana_base,inicio_corte_s,clipe,mais_ditas,demo\n"
            "2026-11-18 02:49:43,gaules,g/1,1,1,70,10.0,0,gaules-20261118-024943.mp4,\"kkk x40 | a, \"\"b\"\" x3\",0\n"
            "2026-11-18 03:15:00,gaules,g/2,1,1,0,0,0,gaules-20261118-031500.mp4,,1\n"
            "2026-11-18 03:20:00,gaules,g/3,1,1,5,1,0,gaules-20261118-032000.mp4,,0\n", encoding="utf-8")
        (raiz / "verticais.csv").write_text(
            "quando,canal,clipe,vertical,tipo,variante,t_pico_audio_s,ini_s,dur_s,gancho,pos_producao_s\n"
            "2026-11-18 03:16:00,gaules,gaules-20261118-031500.mp4,gaules-20261118-031500_hype_v22.mp4,hype,v22,"
            "21.5,7.5,22.0,A / B,19\n", encoding="utf-8")
        destino, clipes, sem_vertical = gerar(raiz, distro="Ubuntu", marca="Chat Pirou")
        nomes = [c["nome"] for c in clipes]
        assert nomes == ["gaules-20261118-031500_hype_v22.mp4", "lofi-20261118-030000.mp4",
                         "gaules-20261118-024943_historia_v35.mp4"], nomes
        assert sem_vertical == 1, sem_vertical
        h = {c["nome"]: c for c in clipes}
        c1 = h["gaules-20261118-024943_historia_v35.mp4"]
        assert c1["revisar"] and c1["msgs"] == 70 and abs(c1["forca"] - 7.0) < 1e-9 and c1["h_existe"] and c1["h_srt"]
        assert c1["mais"] == ["kkk x40", 'a, "b" x3'], c1["mais"]
        c2 = h["gaules-20261118-031500_hype_v22.mp4"]
        assert c2["demo"] and c2["gancho"] == ["A", "B"] and c2["dur"] == 22.0 and c2["pico_audio"] == 21.5
        c3 = h["lofi-20261118-030000.mp4"]
        assert c3["canal"] == "lofi" and c3["post"] is None and not c3["h_existe"]
        texto = destino.read_text(encoding="utf-8")
        erros = valida_html(texto, destino.parent)
        assert not erros, erros
        assert "<video controls preload=\"metadata\"" in texto and "lofi%20girl/lofi-20261118" in texto
        assert "Revisar spoiler" in texto and 'class="selo demo"' in texto
        cfg = json.loads(re.search(r'<script type="application/json" id="dados">(.*?)</script>', texto, re.S).group(1))
        assert cfg["clipes"][c1["id"]]["titulo"] == "CLIMA | [MARCA]" and cfg["marca_padrao"] == "Chat Pirou"
        # pasta sem verticais gera página válida e vazia
        vazia = Path(tmp) / "vazia"
        vazia.mkdir()
        d2, c, _ = gerar(vazia)
        assert not c and not valida_html(d2.read_text(encoding="utf-8")), valida_html(d2.read_text(encoding="utf-8"))
    print("autoteste da galeria: ok")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Galeria local de triagem dos clipes (gera clipes/galeria.html).")
    ap.add_argument("--pasta", default=str(PASTA / "clipes"), help="pasta de clipes (padrão: clipes/)")
    ap.add_argument("--saida", help="arquivo HTML de saída (padrão: <pasta>/galeria.html)")
    ap.add_argument("--assistir", type=float, metavar="N", help="regenera a cada N segundos (mínimo 2)")
    ap.add_argument("--distro", default=os.environ.get("WSL_DISTRO_NAME") or "Ubuntu",
                    help="distro do WSL no caminho do Windows (padrão: $WSL_DISTRO_NAME ou Ubuntu)")
    ap.add_argument("--marca", default="", help="valor inicial do campo Marca (ex.: 'Chat Pirou')")
    ap.add_argument("--teste", action="store_true", help="autoteste")
    args = ap.parse_args(argv)
    if args.teste:
        autoteste()
        return 0
    if args.assistir is not None:
        args.assistir = max(args.assistir, 2.0)
        try:
            assistir_loop(args)
        except KeyboardInterrupt:
            print("\ngaleria: parado.", flush=True)
        return 0
    destino, clipes, sem_vertical = gerar(args.pasta, args.saida, args.distro, args.marca)
    print(f"galeria pronta: {destino} ({len(clipes)} verticais, {sem_vertical} picos sem vertical)")
    print("Windows: " + caminho_windows(destino, args.distro))
    return 0


if __name__ == "__main__":
    sys.exit(main())
