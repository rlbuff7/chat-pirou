#!/usr/bin/env python3
"""pos.py: pós-produção do clipador (onda 2). Tudo que acontece depois que o clipe horizontal existe.

- tipo do corte (humor, falha, hype, susto, historia, geral) por regra grátis sobre o chat;
- gancho no topo (caixa alta, 2 linhas) a partir do que o chat repetiu, com filtro de segurança
  (filtro_gancho.txt) e modelos genéricos por tipo quando não há frase segura. Nunca usa nome de usuário;
- pico de áudio dentro do clipe e vertical curto (~22 s) em volta dele; 1 em cada 4 sai com os 35 s
  inteiros (controle A/B, variante v35);
- layout v2 com margens seguras (pesquisa/retencao-e-ganchos.md, "Mapa do quadro");
- legenda palavra a palavra, palavra falada em amarelo #FFD400 (um evento ASS por palavra);
- <nome>.txt com título, crédito e hashtags prontos para postar;
- layout "facecam" opcional (--layout facecam; facecam.py acha a webcam): rosto ampliado numa faixa em cima e o
  gameplay recortado embaixo. Sem rosto confiável cai no v2 e registra o motivo em clipes/facecam/decisoes.csv.

Uso avulso (testar nos clipes de clipes/_teste sem esperar uma live):
  .venv/bin/python pos.py CLIPE.mp4 --canal lofigirl [--mais "kkkkk x40 | omg x12"] [--msgs 85] [--completo]
                          [--layout facecam]
  .venv/bin/python pos.py --teste
"""
import collections
import csv
import fcntl
import hashlib
import re
import statistics
import struct
import subprocess
import sys
import time
import unicodedata
from pathlib import Path

PASTA = Path(__file__).resolve().parent
FONTES = PASTA / "fontes"
FILTRO = PASTA / "filtro_gancho.txt"

# ---- ajuste aqui ----
MODELO = "small"       # faster-whisper (clip_watcher.py repassa o dele)
IDIOMA = "pt"
VERTICAL_FPS = 30
VERTICAL_S = 22.0      # duração do vertical curto
ANTES_PICO_S = 14.0    # do vertical curto, quanto fica antes do pico de áudio (mais antes que depois)
CONTROLE_A_CADA = 4    # 1 em cada N verticais sai com o clipe inteiro (controle A/B)
JANELA_AUDIO = 0.5     # s de cada janela de RMS
MIN_MSGS_TIPO = 3      # mensagens mínimas de uma categoria para virar o tipo do corte
MAX_PALAVRAS = 4       # palavras por bloco de legenda
PAUSA_BLOCO = 0.7      # pausa entre palavras que quebra o bloco
MASCARA_ATE_S = 7.0    # palavrão forte vira *** nos primeiros segundos do vertical

# ---- layout 1080x1920 (px) ----
W, H = 1080, 1920
VIDEO_Y, VIDEO_H = 576, 608          # vídeo 16:9 em y 576..1184
CAIXA_X0, CAIXA_X1 = 164, 916        # caixa de texto: 164 px das bordas (escapa da coluna de ícones)
CAIXA_W = CAIXA_X1 - CAIXA_X0        # 752
GANCHO_Y, GANCHO_PX, GANCHO_MIN_PX = 330, 84, 64
LEGENDA_Y, LEGENDA_PX = 1244, 64
SELO_Y, SELO_X, SELO_PX = 272, 80, 38

# ---- layout facecam (opt-in): gancho, crédito e legenda ficam onde estão no v2 ----
CAM_Y, CAM_H = 576, 360              # faixa do rosto: y 576..936, logo abaixo do gancho
CAM_W = CAM_H * 16 // 9              # 640: recorte 16:9 nítido, no centro da faixa; as laterais são ele mesmo desfocado
JOGO_Y = CAM_Y + CAM_H               # gameplay recortado de y 936 até 1440 (fim da zona segura); a legenda cai nele
JOGO_H = 1440 - JOGO_Y               # 504
LINHA_COR = "0xFF2E88"               # magenta da marca: fio de 4 px entre a faixa e o jogo
LAYOUTS = ("v2", "facecam")

AMARELO = "&H00D4FF&"   # #FFD400 em BGR
GELO = "&HFAF7F5&"      # #F5F7FA em BGR
TIPOS = ("humor", "falha", "hype", "susto", "historia", "geral")


# ---------- medir texto sem Pillow (lê hmtx/cmap da própria .ttf) ----------

class Fonte:
    """Largura de texto em px, sem kerning: suficiente para decidir quebra de linha e tamanho."""

    def __init__(self, caminho):
        d = Path(caminho).read_bytes()
        n = struct.unpack(">H", d[4:6])[0]
        tab = {}
        for i in range(n):
            tag, _, off, tam = struct.unpack(">4sIII", d[12 + 16 * i:28 + 16 * i])
            tab[tag] = (off, tam)
        self.d = d
        self.upem = struct.unpack(">H", d[tab[b"head"][0] + 18:tab[b"head"][0] + 20])[0]
        self.nh = struct.unpack(">H", d[tab[b"hhea"][0] + 34:tab[b"hhea"][0] + 36])[0]
        self.hmtx = tab[b"hmtx"][0]
        self.cmap = self._achar_cmap(tab[b"cmap"][0])
        self._cache = {}

    def _achar_cmap(self, base):
        d = self.d
        n = struct.unpack(">H", d[base + 2:base + 4])[0]
        melhor = None
        for i in range(n):
            plat, enc, off = struct.unpack(">HHI", d[base + 4 + 8 * i:base + 12 + 8 * i])
            if struct.unpack(">H", d[base + off:base + off + 2])[0] == 4 and (plat, enc) in ((3, 1), (0, 3), (0, 4)):
                melhor = base + off
        if melhor is None:
            raise ValueError("fonte sem cmap formato 4")
        return melhor

    def _glifo(self, cp):
        d, t = self.d, self.cmap
        seg2 = struct.unpack(">H", d[t + 6:t + 8])[0]
        fins, inis = t + 14, t + 16 + seg2
        deltas, ranges = inis + seg2, inis + 2 * seg2
        for s in range(seg2 // 2):
            fim = struct.unpack(">H", d[fins + 2 * s:fins + 2 * s + 2])[0]
            if cp > fim:
                continue
            ini = struct.unpack(">H", d[inis + 2 * s:inis + 2 * s + 2])[0]
            if cp < ini:
                return 0
            delta = struct.unpack(">h", d[deltas + 2 * s:deltas + 2 * s + 2])[0]
            ro = struct.unpack(">H", d[ranges + 2 * s:ranges + 2 * s + 2])[0]
            if ro == 0:
                return (cp + delta) & 0xFFFF
            pos = ranges + 2 * s + ro + 2 * (cp - ini)
            g = struct.unpack(">H", d[pos:pos + 2])[0]
            return (g + delta) & 0xFFFF if g else 0
        return 0

    def _avanco(self, ch):
        if ch not in self._cache:
            g = self._glifo(ord(ch))
            g = min(g, self.nh - 1)
            self._cache[ch] = struct.unpack(">H", self.d[self.hmtx + 4 * g:self.hmtx + 4 * g + 2])[0]
        return self._cache[ch]

    def largura(self, texto, px):
        return sum(self._avanco(c) for c in texto) * px / self.upem


_fontes = {}


def fonte(nome):
    if nome not in _fontes:
        _fontes[nome] = Fonte(FONTES / nome)
    return _fontes[nome]


def anton():
    return fonte("Anton-Regular.ttf")


def montserrat():
    return fonte("Montserrat-ExtraBold.ttf")


# ---------- filtro de segurança ----------

def _colapsa(txt):
    return re.sub(r"(.)\1+", r"\1", txt)


def normalizar(txt):
    """minúsculas, sem acento, leet -> letra, runs repetidos viram uma letra só."""
    txt = unicodedata.normalize("NFKD", txt.lower())
    txt = "".join(c for c in txt if not unicodedata.combining(c))
    txt = txt.translate(str.maketrans("013457@$", "oieastas"))
    return _colapsa(re.sub(r"[^a-z0-9\s]", " ", txt))


_bloqueio = None


def carregar_bloqueio(arquivo=FILTRO):
    """(palavras/frases inteiras, pedaços, fortes): termos já normalizados."""
    palavras, pedacos, fortes = set(), set(), set()
    try:
        linhas = Path(arquivo).read_text(encoding="utf-8").splitlines()
    except OSError:
        linhas = []
    for linha in linhas:
        t = linha.strip()
        if not t or t.startswith("#"):
            continue
        forte = t.startswith("!")
        t = t.lstrip("!")
        if t.startswith("*"):
            n = normalizar(t[1:]).replace(" ", "")
            if n:
                pedacos.add(n)
            continue
        n = " ".join(normalizar(t).split())
        if n:
            palavras.add(n)
            if forte:
                fortes.add(n)
    return palavras, pedacos, fortes


def bloqueio():
    global _bloqueio
    if _bloqueio is None:
        _bloqueio = carregar_bloqueio()
    return _bloqueio


def tem_bloqueado(txt, lista=None):
    palavras, pedacos, _ = lista or bloqueio()
    n = " ".join(normalizar(txt).split())
    if not n:
        return False
    cheio = f" {n} "
    if any(f" {p} " in cheio for p in palavras):
        return True
    junto = n.replace(" ", "")
    return any(p in junto for p in pedacos)


def mascarar_forte(palavra, lista=None):
    """'caralho' -> 'c***' se estiver na lista forte; senão a própria palavra."""
    _, _, fortes = lista or bloqueio()
    n = " ".join(normalizar(palavra).split())
    return palavra[:1] + "***" if n and n in fortes else palavra


EMOTES = ("kappa", "pogchamp", "lulw", "omegalul", "kekw", "kekl", "4head", "pepe", "peepo", "monka", "sadge",
          "copium", "ezclap", "widepeepo", "cmonbruh", "residentsleeper", "biblethump", "wutface", "gaules",
          "trihard", "jebaited", "notlikethis", "sourpls", "catjam", "pausechamp", "omegaw")
RISO_EMOJI = "\U0001F602\U0001F923\U0001F480\U0001F639"


def frase_segura(txt):
    """Só deixa passar texto curto, legível e sem nada que identifique alguém ou renda problema."""
    t = txt.strip()
    if not t or len(t) > 30:
        return False
    baixo = t.lower()
    if re.search(r"https?:|www\.|://|\.(com|tv|br|net|gg|ly|me|io)\b|bit\.ly|t\.co", baixo):
        return False
    if "@" in t or t[0] in "!/#$&":                      # menção ou comando de bot
        return False
    if re.search(r"\d{5,}", t) or sum(c.isdigit() for c in t) > 4:
        return False
    if re.search(r"[^a-zA-ZÀ-ÿ0-9\s?!.,'\-]", t):       # emoji solto, símbolo, código estranho
        return False
    tokens = re.findall(r"[a-zA-ZÀ-ÿ0-9']+", baixo)
    if not tokens or len(tokens) > 4:
        return False
    for tok in tokens:
        if len(tok) > 14 or (re.search(r"\d", tok) and re.search(r"[a-z]", tok)):
            return False                                  # emote-código, nick com número, palavra colada
        if tok.startswith(EMOTES) or not re.search(r"[aeiouáéíóúâêôãõ]|^(f+|k+|rs+|gg|wtf|pqp|mds)$", tok):
            return False
    return not tem_bloqueado(t)


# ---------- tipo do corte e gancho ----------

RISO = re.compile(r"^(k{3,}|(?:ha){2,}h?|(?:he){2,}h?|(?:rs){2,}|(?:ks){2,}|kek\w*|lul\w*|omegalul|lol+|lmao+|lmfao+|ja{2,}|j(?:aj)+a?)$")
FALHA = re.compile(r"^(f+|rip|no{3,}|nao{2,}|ihh+|ixi+|morreu|morri|morreeu|perdeu|ferrou|f[eê]rrou)$")
HYPE = re.compile(r"^(pog\w*|omg|caraca\w*|hype|vamo+s?|gg|gol+|insano|brabo|monstro|lenda|wow|uau|mds|pqp|eita)$")
SUSTO = re.compile(r"^(susto\w*|assust\w*|a{3,}h*|ah{3,}|credo|socorro|medo|jumpscare|cag(?:ou|uei)\w*|gritou)$")
HISTORIA = re.compile(r"^(spoilers?|spoil\w*|cutscenes?|cinem[aá]tica|hist[oó]ria|trama|enredo|ending|plot|final|finalzinho)$")
CATEGORIAS = (("historia", HISTORIA), ("susto", SUSTO), ("falha", FALHA), ("humor", RISO), ("hype", HYPE))


def _tokens(msg):
    msg = unicodedata.normalize("NFKC", msg.lower())
    if any(e in msg for e in RISO_EMOJI):
        msg = msg + " kkkkk"
    return re.findall(r"[a-zà-ÿ0-9]+", msg)


def categorias_da_mensagem(msg):
    """Categorias que a mensagem aciona (por token inteiro; 'f' só em mensagem curta)."""
    toks = _tokens(msg)
    achou = set()
    for nome, rx in CATEGORIAS:
        for tok in toks:
            if rx.match(tok) and not (nome == "falha" and tok.startswith("f") and len(toks) > 3 and len(set(tok)) == 1):
                achou.add(nome)
                break
    if re.search(r"!{3,}", msg):
        achou.add("hype")
    return achou


def classificar_chat(textos):
    """(tipo, contagens). Humor, falha, hype, susto, historia ou geral; só conta o que o chat disse."""
    cont = collections.Counter()
    for msg in textos:
        for c in categorias_da_mensagem(msg):
            cont[c] += 1
    total = max(len(textos), 1)
    # história precisa de pouco (é a que mais pede revisão: 2 msgs e 5%); as demais, de 3 msgs e 10% da janela
    elegiveis = {c: n for c, n in cont.items()
                 if n >= (2 if c == "historia" else MIN_MSGS_TIPO) and n >= (0.05 if c == "historia" else 0.10) * total}
    if not elegiveis:
        return "geral", cont
    if "historia" in elegiveis:
        return "historia", cont
    ordem = [c for c, _ in CATEGORIAS]
    return max(elegiveis, key=lambda c: (elegiveis[c], -ordem.index(c))), cont


# Modelos do gancho: "linha 1|linha 2"; linha 2 (amarela) leva a frase do chat.
# {k}=frase segura mais repetida, {n}=quantas vezes, {m}=mensagens na janela de 10 s.
MODELOS_FRASE = {
    "humor": ["O CHAT NÃO SEGUROU|{k} x{n}", "ATÉ O CHAT RIU|{k} x{n}", "O CHAT PIROU DE RIR|{k} x{n}"],
    "falha": ["F NO CHAT|{k} x{n}", "DEU RUIM?|NO CHAT: {k} x{n}", "O CHAT DEU F|{k} x{n}"],
    "hype": ["O CHAT PIROU|{k} x{n}", "CLIMA DE HYPE|{k} x{n}", "O CHAT ENLOUQUECEU|{k} x{n}"],
    "susto": ["O CHAT SE ASSUSTOU|{k} x{n}", "QUE SUSTO!|NO CHAT: {k} x{n}", "O CHAT GRITOU|{k} x{n}"],
}
# Sem frase segura: genérico por tipo (só números do próprio log). História nunca mostra frase do chat (spoiler).
MODELOS_GENERICOS = {
    "humor": ["O CHAT NÃO SEGUROU|{m} MSGS EM 10 s", "ATÉ O CHAT RIU|{m} MSGS EM 10 s"],
    "falha": ["DEU RUIM?|{m} MSGS EM 10 s", "O CHAT DEU F|{m} MSGS EM 10 s"],
    "hype": ["O CHAT PIROU|{m} MSGS EM 10 s", "CLIMA DE HYPE|{m} MSGS EM 10 s"],
    "susto": ["O CHAT SE ASSUSTOU|{m} MSGS EM 10 s", "QUE SUSTO!|{m} MSGS EM 10 s"],
    "historia": ["O CHAT REAGIU|{m} MSGS EM 10 s", "CLIMA DE HISTÓRIA|{m} MSGS EM 10 s"],
    "geral": ["O CHAT EXPLODIU|{m} MSGS EM 10 s", "OLHA O CHAT|{m} MSGS EM 10 s"],
}
GANCHO_SEM_CHAT = "MOMENTO CLIPADO|AO VIVO NA TWITCH"   # chat quase parado (ex.: --demo): sem número inventado
MIN_MSGS_NUMERO = 5


def _frase_do_tipo(tipo, textos):
    """(texto exibido, n): a frase segura mais repetida da categoria. Risada vira 'KKKKK' padronizado."""
    if tipo == "humor":
        n = sum(1 for m in textos if "humor" in categorias_da_mensagem(m))
        return ("KKKKK", n) if n >= MIN_MSGS_TIPO else (None, 0)
    achadas = collections.Counter()
    for msg in textos:
        if tipo in categorias_da_mensagem(msg):
            limpo = re.sub(r"\s+", " ", msg.strip().lower())
            limpo = re.sub(r"(.)\1{3,}", r"\1\1\1", limpo)          # "caraaaaaaaaaaaaa" -> "caraaa"
            if frase_segura(limpo):
                achadas[limpo] += 1
    for frase, n in achadas.most_common():
        if n >= MIN_MSGS_TIPO:
            return frase.upper(), n
    return None, 0


def _caber(linhas):
    """Maior fonte do gancho (84 a 64 px, de 4 em 4) em que todas as linhas cabem na caixa, ou None."""
    a = anton()
    px = GANCHO_PX
    while px >= GANCHO_MIN_PX:
        if all(a.largura(l, px) <= CAIXA_W - 12 for l in linhas):
            return px
        px -= 4
    return None


def gerar_gancho(tipo, textos, mensagens, canal=""):
    """(linhas, px). Nunca usa nome de usuário (o chat entra só como texto); sempre cabe na caixa."""
    if mensagens < MIN_MSGS_NUMERO:                  # chat quase parado (demo): não inventa número nem reação
        modelos = [GANCHO_SEM_CHAT]
    else:
        modelos = []
        frase, n = (None, 0) if tipo in ("historia", "geral") else _frase_do_tipo(tipo, textos)
        semente = int(hashlib.md5(f"{canal}{len(textos)}{mensagens}".encode()).hexdigest(), 16)
        if frase:
            lista = MODELOS_FRASE[tipo]
            modelos.append(lista[semente % len(lista)].format(k=frase, n=n, m=mensagens))
        lista = MODELOS_GENERICOS[tipo]
        modelos.append(lista[semente % len(lista)].format(m=mensagens))
        modelos.append(MODELOS_GENERICOS["geral"][0].format(m=mensagens))
    for modelo in modelos:
        linhas = modelo.split("|")
        if len(linhas) <= 2 and (px := _caber(linhas)):
            return linhas, px
    return ["OLHA O CHAT"], GANCHO_PX


def analisar_chat(canal, mensagens, textos):
    """Tudo que o pico já sabe sobre o chat: tipo, contagens por categoria e gancho."""
    tipo, cont = classificar_chat(textos)
    linhas, px = gerar_gancho(tipo, textos, mensagens, canal)
    return {"tipo": tipo, "contagens": dict(cont), "gancho": linhas, "gancho_px": px, "mensagens": mensagens}


# ---------- áudio: pico e janela do vertical ----------

def pico_de_pcm(x, sr=16000, de=18.0, ate=34.0, janela=JANELA_AUDIO):
    """Instante (s) do trecho mais alto (RMS por janela de 0,5 s) entre `de` e `ate`; None se não houver
    pico claro (silêncio ou tudo no mesmo volume)."""
    import numpy as np
    passo = int(sr * janela)
    n = len(x) // passo
    if n == 0:
        return None
    rms = np.sqrt((x[:n * passo].astype(np.float32).reshape(n, passo) ** 2).mean(axis=1))
    i0, i1 = max(int(de / janela), 0), min(n, int(ate / janela))
    if i1 - i0 < 2:
        return None
    trecho = rms[i0:i1]
    topo = float(trecho.max())
    if topo < 0.004 or topo < 1.4 * max(float(np.median(rms)), 1e-6):
        return None
    return (i0 + int(trecho.argmax())) * janela


def ler_pcm(clipe, sr=16000):
    import numpy as np
    bruto = subprocess.run(["ffmpeg", "-v", "error", "-i", str(clipe), "-vn", "-ac", "1", "-ar", str(sr),
                            "-f", "s16le", "-"], capture_output=True, timeout=120).stdout
    return np.frombuffer(bruto, dtype=np.int16).astype(np.float32) / 32768.0


def volume_e_riso(x, sr=8000):
    """Para cada segundo de PCM int16 (float32 na escala do int16): RMS e 'cara de risada'
    (autocorrelação do envelope de 50 ms nos atrasos de 150-300 ms, o "ha-ha-ha")."""
    import numpy as np
    rms, riso = [], []
    passo = sr // 20
    for i in range(0, len(x) - sr + 1, sr):
        s = x[i:i + sr]
        rms.append(float(np.sqrt(np.mean(s ** 2))))
        env = np.sqrt(np.mean(s[: len(s) // passo * passo].reshape(-1, passo) ** 2, axis=1))
        env = env - env.mean()
        den = float(np.dot(env, env)) or 1.0
        riso.append(max(float(np.dot(env[:-k], env[k:])) / den for k in (3, 4, 5, 6)))
    return rms, riso


def volume_por_segundo(arquivo, sr=8000, timeout=60):
    """RMS e riso de cada segundo de um arquivo curto (um segmento do buffer, por exemplo)."""
    import numpy as np
    bruto = subprocess.run(["ffmpeg", "-v", "error", "-i", str(arquivo), "-vn", "-ac", "1", "-ar", str(sr),
                            "-f", "s16le", "-"], capture_output=True, timeout=timeout).stdout
    return volume_e_riso(np.frombuffer(bruto, dtype=np.int16).astype(np.float32), sr)


def duracao_de(clipe):
    saida = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                            "default=nw=1:nk=1", str(clipe)], capture_output=True, text=True, timeout=60).stdout.strip()
    try:
        return float(saida)
    except ValueError:
        return 0.0


def janela_do_vertical(dur, t_pico, alvo=VERTICAL_S, antes=ANTES_PICO_S):
    """(ini, fim) em s do clipe: `antes` s antes do pico e o resto depois, sem passar de 0 nem de `dur`.
    Clipe curto (<= alvo) vai inteiro."""
    if dur <= alvo + 0.5:
        return 0.0, dur
    ini = max(t_pico - antes, 0.0)
    fim = ini + alvo
    if fim > dur:
        fim = dur
        ini = max(fim - alvo, 0.0)
    return ini, fim


def variante_do_numero(numero):
    """v35 (controle) para cada N-ésimo clipe; v22 nos outros. `numero` = linha do picos.csv (1, 2, ...)."""
    return "v35" if numero % CONTROLE_A_CADA == 0 else "v22"


# ---------- legenda: palavras -> blocos -> ASS ----------

_whisper = None


def transcrever(clipe):
    """Segmentos de palavras [(ini, fim, texto)] do clipe inteiro."""
    global _whisper
    from faster_whisper import WhisperModel
    if _whisper is None:
        print(f"carregando o modelo de legenda '{MODELO}' (na primeira vez ele é baixado)")
        _whisper = WhisperModel(MODELO, device="cpu", compute_type="int8")
    segmentos, _ = _whisper.transcribe(str(clipe), language=IDIOMA, vad_filter=True, word_timestamps=True)
    saida = []
    for seg in segmentos:
        palavras = [(p.start, p.end, p.word.strip()) for p in (seg.words or []) if p.word.strip()]
        if palavras:
            saida.append(palavras)
    return saida


def blocos_srt(segmentos):
    """Como antes: até 4 palavras por bloco dentro de cada segmento."""
    blocos = []
    for palavras in segmentos:
        for i in range(0, len(palavras), 4):
            g = palavras[i:i + 4]
            blocos.append((g[0][0], g[-1][1], " ".join(p[2] for p in g)))
    return blocos


def tempo_srt(s):
    ms = int(round(s * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    seg, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{seg:02d},{ms:03d}"


def tempo_ass(s):
    cs = int(round(max(s, 0) * 100))
    h, cs = divmod(cs, 360_000)
    m, cs = divmod(cs, 6000)
    seg, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{seg:02d}.{cs:02d}"


def escrever_srt(blocos, destino):
    linhas = []
    for i, (ini, fim, texto) in enumerate(blocos, 1):
        linhas += [str(i), f"{tempo_srt(ini)} --> {tempo_srt(fim)}", texto, ""]
    destino.write_text("\n".join(linhas), encoding="utf-8")


def limpo(x):
    return x.replace("\\", "").replace("{", "").replace("}", "")


def quebrar_linhas(palavras, largura_max, px, fonte_=None):
    """Quebra uma lista de textos em linhas que cabem em largura_max (guloso). [[i, ...], ...]"""
    f = fonte_ or montserrat()
    linhas, atual = [], []
    for i, p in enumerate(palavras):
        tentativa = " ".join(palavras[j] for j in atual + [i])
        if atual and f.largura(tentativa, px) > largura_max:
            linhas.append(atual)
            atual = [i]
        else:
            atual.append(i)
    if atual:
        linhas.append(atual)
    return linhas


def montar_blocos(palavras, largura_max=CAIXA_W - 12, px=LEGENDA_PX):
    """palavras [(ini, fim, texto)] (caixa alta) -> blocos de até 4 palavras, no máximo 2 linhas na caixa,
    quebrados também em pausa longa. Cada bloco: lista de palavras."""
    blocos, atual = [], []
    for p in palavras:
        if atual:
            pausa = p[0] - atual[-1][1]
            textos = [q[2] for q in atual] + [p[2]]
            if len(atual) >= MAX_PALAVRAS or pausa > PAUSA_BLOCO or len(quebrar_linhas(textos, largura_max, px)) > 2:
                blocos.append(atual)
                atual = []
        atual.append(p)
    if atual:
        blocos.append(atual)
    return blocos


ASS_CAB = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Gancho,Anton,{GANCHO_PX},&H00FAF7F5,&H000000FF,&H00120B0B,&H80000000,0,0,0,0,100,100,0,0,1,8,2,8,{CAIXA_X0},{CAIXA_X0},{GANCHO_Y},1
Style: Legenda,Montserrat ExtraBold,{LEGENDA_PX},&H00FAF7F5,&H000000FF,&H00120B0B,&H80000000,0,0,0,0,100,100,0,0,1,7,2,8,{CAIXA_X0},{CAIXA_X0},{LEGENDA_Y},1
Style: Selo,Montserrat ExtraBold,{SELO_PX},&H00FAF7F5,&H000000FF,&H00120B0B,&H80000000,0,0,0,0,100,100,0,0,1,4,0,7,{SELO_X},{SELO_X},{SELO_Y},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def gancho_ass(linhas, px):
    """Linha 1 em gelo; a seguinte (a frase do chat) em amarelo. \\q2 = sem quebra automática."""
    corpo = limpo(linhas[0]) + "".join("\\N{\\c" + AMARELO + "}" + limpo(l) for l in linhas[1:])
    fs = f"\\fs{px}" if px != GANCHO_PX else ""
    return "{\\q2" + fs + "\\fad(120,0)\\t(0,160,\\fscx106\\fscy106)\\t(160,320,\\fscx100\\fscy100)}" + corpo


def escrever_ass(palavras, gancho, px, canal, dur, destino, mascarar=True, credito=None):
    """.ass do vertical: selo/crédito, gancho (clipe inteiro) e legenda palavra a palavra.
    `palavras` já relativas ao início do vertical (s). `credito` troca o selo (ex.: youtube.com/@Gameplayrj)."""
    saida = [ASS_CAB]
    saida.append(f"Dialogue: 2,{tempo_ass(0)},{tempo_ass(dur)},Selo,,0,0,0,,"
                 f"{{\\q2\\alpha&H4D&}}{limpo(credito or f'twitch.tv/{canal}')}\n")
    saida.append(f"Dialogue: 1,{tempo_ass(0)},{tempo_ass(dur)},Gancho,,0,0,0,,{gancho_ass(gancho, px)}\n")
    lista = bloqueio()
    pal = []
    for ini, fim, texto in palavras:
        t = limpo(texto).upper()
        pal.append((ini, fim, mascarar_forte(t, lista) if mascarar and ini < MASCARA_ATE_S else t))
    eventos = []
    for bloco in montar_blocos(pal):
        textos = [p[2] for p in bloco]
        linhas = quebrar_linhas(textos, CAIXA_W - 12, LEGENDA_PX)
        for k, (ini, fim, _) in enumerate(bloco):
            fim_ev = bloco[k + 1][0] if k + 1 < len(bloco) else fim
            fim_ev = max(fim_ev, ini + 0.12)
            partes = []
            for numero_linha, idxs in enumerate(linhas):
                partes.append(" ".join(("{\\c" + AMARELO + "}" if j == k else "{\\c" + GELO + "}") + textos[j]
                                       for j in idxs))
            eventos.append([ini, fim_ev, "{\\q2}" + "\\N".join(partes)])
    # Nunca duas legendas ao mesmo tempo: o libass empilha eventos sobrepostos e a legenda "pisca" dobrada
    # (o mínimo de 0,12 s e o fim de palavra do whisper passavam do início da palavra seguinte).
    for ev, prox in zip(eventos, eventos[1:]):
        ev[1] = min(ev[1], prox[0])
    for ini, fim_ev, texto in eventos:
        if tempo_ass(fim_ev) > tempo_ass(ini):      # palavra que ficou sem tempo só perde o destaque
            saida.append(f"Dialogue: 0,{tempo_ass(ini)},{tempo_ass(fim_ev)},Legenda,,0,0,0,,{texto}\n")
    destino.write_text("".join(saida), encoding="utf-8")


def palavras_no_recorte(segmentos, ini, fim):
    """Palavras do clipe inteiro -> palavras do recorte [ini, fim], tempos relativos ao recorte."""
    saida = []
    for seg in segmentos:
        for a, b, t in seg:
            if b <= ini or a >= fim:
                continue
            saida.append((max(a - ini, 0.0), min(b - ini, fim - ini), t))
    return saida


# ---------- vertical v2 ----------

def _esc_filtro(caminho):
    return str(caminho).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace(",", "\\,")


def filtro_facecam(recorte, ass):
    """Layout facecam. `recorte` = [x, y, w, h] da webcam em fração do quadro (facecam.decidir).
    Faixa y 576..936: a webcam ampliada (640x360, nítida) sobre ela mesma desfocada; jogo de y 936..1440 recortado
    do centro, cobrindo a largura toda; fio magenta entre os dois; fundo desfocado como no v2 (sobra em volta)."""
    x, y, w, h = recorte

    def par(dim, frac):   # fração do quadro -> px pares (crop de largura/altura ímpar quebra o yuv420p)
        return f"trunc({dim}*{frac:.5f}/2)*2"
    return (f"[0:v]fps={VERTICAL_FPS},split=3[a][b][c];"
            "[a]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,boxblur=6:1,"
            f"scale={W}:{H},eq=brightness=-0.10[fundo];"
            f"[b]crop={par('iw', w)}:{par('ih', h)}:{par('iw', x)}:{par('ih', y)},split=2[cam1][cam2];"
            f"[cam1]scale={CAM_W}:{CAM_H}:flags=lanczos[cam];"
            f"[cam2]scale=270:{CAM_H // 4}:force_original_aspect_ratio=increase,crop=270:{CAM_H // 4},"
            f"boxblur=4:1,scale={W}:{CAM_H},eq=brightness=-0.15[faixa];"
            f"[c]scale={W}:{JOGO_H}:force_original_aspect_ratio=increase,crop={W}:{JOGO_H}[jogo];"
            f"[fundo][faixa]overlay=0:{CAM_Y}[v1];[v1][cam]overlay=(W-w)/2:{CAM_Y}[v2];"
            f"[v2][jogo]overlay=0:{JOGO_Y},drawbox=x=0:y={JOGO_Y - 2}:w={W}:h=4:color={LINHA_COR}:t=fill,setsar=1,"
            f"ass={ass.name}:fontsdir={_esc_filtro(FONTES)}[v]")


def fazer_vertical(clipe, ass, saida, ini, dur, recorte=None):
    """1080x1920: fundo desfocado e escurecido 10% + vídeo 16:9 inteiro em y 576..1184 + gancho/crédito/legenda.
    Com `recorte` (webcam achada), o layout facecam no lugar (filtro_facecam).
    O recorte de tempo (-ss/-t antes do -i) é exato porque há reencode."""
    filtro = filtro_facecam(recorte, ass) if recorte else (
              f"[0:v]fps={VERTICAL_FPS},split=2[a][b];"
              "[a]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,boxblur=6:1,"
              f"scale={W}:{H},eq=brightness=-0.10[fundo];"
              f"[b]scale={W}:{VIDEO_H}:force_original_aspect_ratio=decrease[frente];"
              f"[fundo][frente]overlay=(W-w)/2:{VIDEO_Y}+({VIDEO_H}-h)/2,setsar=1,"
              f"ass={ass.name}:fontsdir={_esc_filtro(FONTES)}[v]")
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-ss", f"{ini:.2f}", "-t", f"{dur:.2f}", "-i", str(clipe),
         "-filter_complex", filtro, "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
         str(saida)], cwd=str(ass.parent), capture_output=True, text=True, timeout=600)
    if r.returncode != 0 and r.stderr:
        print(f"ffmpeg (vertical): {r.stderr.strip()[-400:]}")
    return saida.exists() and saida.stat().st_size > 0


# ---------- legenda de post ----------

HASHTAGS = {
    "humor": "#GTA6 #fail #zoeira #cortesdelive #gamebr",
    "falha": "#GTA6 #fail #gamerfail #cortesdelive #gamebr",
    "hype": "#GTA6 #GTA6Brasil #cortesdelive #cortesgta #gamebr",
    "susto": "#GTA6 #GTA6Brasil #cortesdelive #gamebr",
    "historia": "#GTA6 #spoiler #cortesdelive #gamebr",
    "geral": "#GTA6 #GTA6Brasil #cortesdelive #gamebr",
}
MARCA = "Chat Pirou"     # marca escolhida em 18/11 (vai no título)
MARCA_TAG = "ChatPirou"  # hashtag da marca, sem o #


def texto_post(canal, tipo, gancho, variante, stem):
    uma = " - ".join(l.strip() for l in gancho)
    corrido = ": ".join(l.strip() for l in gancho)
    frase = corrido[:1] + corrido[1:].lower() if corrido else ""
    revisar = tipo == "historia"
    linhas = []
    if revisar:
        linhas += ["[revisar spoiler] cena de história: confira o clipe antes de postar. Pelas regras da marca,",
                   "vermelho (história) não vai ao ar na primeira semana (19 a 25/11) e o final nunca. Se for postar,",
                   "troque o aviso abaixo por 'SPOILER DE HISTÓRIA' e tire o gancho se ele entregar algo.", ""]
    linhas += [f"Arquivo: {stem}  |  tipo: {tipo}  |  variante: {variante}", "",
               "== TÍTULO (YouTube Shorts, até 100 caracteres) ==",
               f"{uma} | {MARCA}"[:100], "",
               "== LEGENDA (TikTok e Reels) ==",
               f"🎥 Live: {canal} | https://twitch.tv/{canal}",
               frase]
    if revisar:
        linhas.append("⚠️ SPOILER DE HISTÓRIA [revisar spoiler]")
    linhas += ["Segue pra ver o próximo 👇", f"{HASHTAGS[tipo]} #{MARCA_TAG}", "",
               "== DESCRIÇÃO (YouTube) ==",
               f"🎥 Live: {canal} | https://twitch.tv/{canal}",
               "Vídeo original: [URL da live ou do VOD] ([minuto:segundo])", "",
               f"{frase}.", "Se inscreve pra ver o próximo corte.", "",
               "Canal de fãs, sem vínculo com a Rockstar Games nem com a Take-Two Interactive.",
               f"Hashtags da descrição: #GTA6 #{MARCA_TAG} #cortesdelive", "",
               "(As hashtags e o gancho assumem que a live é de GTA 6: confira o jogo antes de postar.)"]
    return "\n".join(linhas) + "\n"


# ---------- registro (picos.csv com trava) ----------

COLUNAS_PICOS = ["quando", "canal", "gravacao", "gravado_s", "relogio_s", "mensagens", "mediana_base",
                 "inicio_corte_s", "clipe", "mais_ditas", "demo", "tipo", "variante", "gancho"]
COLUNAS_VERTICAIS = ["quando", "canal", "clipe", "vertical", "tipo", "variante", "t_pico_audio_s", "ini_s",
                     "dur_s", "gancho", "pos_producao_s"]


def anexar_csv(arquivo, colunas, linha_fn):
    """Acrescenta uma linha com trava de arquivo (vários clip_watchers escrevem no mesmo CSV).
    `linha_fn(numero)` recebe o nº da linha de dados (1, 2, ...) e devolve a lista de valores.
    Cabeçalho antigo (sem as colunas novas) é migrado preenchendo as novas com vazio. Devolve o número."""
    arquivo = Path(arquivo)
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    with open(arquivo, "a+", newline="", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.seek(0)
            linhas = list(csv.reader(f))
            if not linhas:
                csv.writer(f).writerow(colunas)
                numero = 1
            else:
                if linhas[0] != colunas and set(linhas[0]) <= set(colunas):   # migra o cabeçalho antigo
                    novas = [colunas] + [[dict(zip(linhas[0], l)).get(c, "") for c in colunas] for l in linhas[1:]]
                    f.seek(0)
                    f.truncate()
                    csv.writer(f).writerows(novas)
                numero = sum(1 for l in linhas[1:] if l) + 1
            csv.writer(f).writerow(linha_fn(numero))
            f.flush()
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    return numero


# ---------- layout facecam: decisão e registro ----------

COLUNAS_FACECAM = ["quando", "canal", "clipe", "layout", "motivo", "confianca", "cache", "recorte", "tempo_s"]


def escolher_facecam(clipe, canal, pasta_cache):
    """(recorte ou None, segundos gastos, nota). None = fica no v2; a nota diz por quê.
    Cada decisão vai para <pasta_cache>/decisoes.csv (clipes/facecam/decisoes.csv)."""
    import facecam
    d = facecam.decidir(clipe, canal, pasta_cache)
    nota = (f"facecam: webcam achada (confiança {d['confianca']:.2f}, cache {d['cache']})" if d["usar"]
            else f"facecam: sem webcam confiável, ficou no layout v2: {d['motivo']}")
    print(f"{nota} [{d['tempo']:.1f} s]")
    try:
        anexar_csv(Path(pasta_cache) / "decisoes.csv", COLUNAS_FACECAM, lambda n: [
            time.strftime("%Y-%m-%d %H:%M:%S"), canal, clipe.name, "facecam" if d["usar"] else "v2 (fallback)",
            d["motivo"], f"{d['confianca']:.2f}", d["cache"], " ".join(f"{v:.3f}" for v in d["recorte"] or []),
            f"{d['tempo']:.1f}"])
    except OSError as erro:
        print(f"decisoes.csv não gravou: {erro}")
    return d["recorte"] if d["usar"] else None, d["tempo"], nota


# ---------- orquestração ----------

def produzir(clipe, ctx, pasta_verticais, antes=20, janela=10, depois=5):
    """Legenda .srt, vertical v2 e .txt de um clipe. `ctx` vem de analisar_chat + canal + variante.
    Devolve dict com o resultado (vertical, tempos) ou None se o vertical falhar."""
    t0 = time.time()
    canal, tipo = ctx["canal"], ctx["tipo"]
    variante = ctx.get("variante", "v22")
    segmentos = []
    try:
        segmentos = transcrever(clipe)
        escrever_srt(blocos_srt(segmentos), clipe.with_suffix(".srt"))
        print(f"legenda pronta: {clipe.with_suffix('.srt').name} ({time.time() - t0:.0f} s)")
    except Exception as erro:  # sem legenda ainda dá para postar o vertical
        print(f"legenda falhou em {clipe.name}: {erro}")
    t1 = time.time()
    dur_clipe = duracao_de(clipe)
    t_pico = None
    try:
        t_pico = pico_de_pcm(ler_pcm(clipe), de=max(antes - 2, 0), ate=antes + janela + depois - 1)
    except Exception as erro:
        print(f"pico de áudio falhou em {clipe.name}: {erro}")
    t_ref = t_pico if t_pico is not None else antes + janela - 2     # sem pico claro: 28 s no clipe de 35
    ini, fim = (0.0, dur_clipe) if variante == "v35" else janela_do_vertical(dur_clipe, t_ref)
    dur = fim - ini
    pasta = pasta_verticais / canal
    pasta.mkdir(parents=True, exist_ok=True)
    layout = ctx.get("layout", "v2")
    recorte, t_fc, nota_fc = None, 0.0, ""
    if layout == "facecam":     # opt-in: sem rosto confiável, segue no v2 e anota o motivo
        recorte, t_fc, nota_fc = escolher_facecam(clipe, canal, pasta_verticais.parent / "facecam")
    stem = f"{clipe.stem}_{tipo}_{variante}" + ("_fc" if recorte else "")
    ass, saida, txt = pasta / f"{stem}.ass", pasta / f"{stem}.mp4", pasta / f"{stem}.txt"
    escrever_ass(palavras_no_recorte(segmentos, ini, fim), ctx["gancho"], ctx["gancho_px"], canal, dur, ass,
                 credito=ctx.get("credito"))
    ok = fazer_vertical(clipe, ass, saida, ini, dur, recorte)
    seg_total = time.time() - t0
    if not ok:
        print(f"vertical falhou: {clipe.name}")
        return None
    txt.write_text(texto_post(canal, tipo, ctx["gancho"], variante, stem), encoding="utf-8")
    anexar_csv(pasta_verticais.parent / "verticais.csv", COLUNAS_VERTICAIS, lambda n: [
        time.strftime("%Y-%m-%d %H:%M:%S"), canal, clipe.name, saida.name, tipo, variante,
        "" if t_pico is None else f"{t_pico:.1f}", f"{ini:.1f}", f"{dur:.1f}", " / ".join(ctx["gancho"]),
        f"{seg_total:.1f}"])
    print(f"vertical pronto: {saida} ({variante}, {dur:.0f} s, pico de áudio "
          f"{'sem pico claro' if t_pico is None else f'{t_pico:.1f} s'}; vertical {time.time() - t1:.0f} s, "
          f"pós-produção {seg_total:.0f} s)")
    return {"vertical": saida, "txt": txt, "ass": ass, "t_pico": t_pico, "ini": ini, "dur": dur, "tempo": seg_total,
            "layout": "facecam" if recorte else "v2", "facecam_s": t_fc, "facecam_nota": nota_fc}


# ---------- testes ----------

def autoteste():
    import numpy as np
    # filtro de segurança
    ruins = ["olha https://x.com/abc", "vai @fulano", "ligue 11999998888", "!comandos", "caralho velho",
             "PORRAAAA", "p0rr4", "vai tomar no cu", "Kappa", "pepehands", "gaules1", "a" * 20,
             "visite meusite.com.br", "kill yourself", "VIADO", "sorteio pix", "um dois tres quatro cinco",
             "\U0001F602\U0001F602", "ç@"]
    for r in ruins:
        assert not frase_segura(r), f"deveria bloquear: {r!r}"
    for b in ["omg", "meu deus", "caraca", "kkkkk", "f", "que isso", "gg"]:
        assert frase_segura(b), f"deveria liberar: {b!r}"
    assert tem_bloqueado("puuuuuta") and tem_bloqueado("fdp") and not tem_bloqueado("computador")
    assert not tem_bloqueado("escutar") and not tem_bloqueado("classe")           # 'cu' e 'ass' só como palavra
    assert mascarar_forte("caralho") == "c***" and mascarar_forte("carro") == "carro"
    # tipo do corte
    assert classificar_chat(["kkkkk", "kkkk", "LUL", "kkkkkkk", "oi", "pog"] + ["kkk"] * 4)[0] == "humor"
    assert classificar_chat(["F", "f", "rip", "ff", "nooooo", "f"] + ["x"] * 4)[0] == "falha"
    assert classificar_chat(["pog", "POGGERS", "omg", "caraca", "!!!!"] + ["x"] * 3)[0] == "hype"
    assert classificar_chat(["spoiler", "cutscene", "kkkk", "kkkk", "kkkk", "kkkk"])[0] == "historia"
    assert classificar_chat(["que susto", "AAAAAAA", "ahhhh", "credo", "oi", "oi", "oi", "oi", "oi", "oi"])[0] == "susto"
    assert classificar_chat(["oi", "gaules", "salve", "boa noite"])[0] == "geral"
    assert classificar_chat([])[0] == "geral"
    assert classificar_chat(["f"] + ["voltei de f"] * 0 + ["x"] * 30)[0] == "geral"
    # gancho: cabe, no máximo 2 linhas, sem nome de usuário, usa genérico quando a frase é insegura
    ctx = analisar_chat("canal", 85, ["kkkkk"] * 30 + ["omg"] * 5)
    assert ctx["tipo"] == "humor" and ctx["gancho"][1] == "KKKKK x30", ctx
    assert len(ctx["gancho"]) <= 2 and _caber(ctx["gancho"]) is not None
    ctx = analisar_chat("canal", 60, ["vai @fulano"] * 8 + ["https://t.co/x"] * 8 + ["pog"] * 4)
    assert ctx["tipo"] == "hype" and not any("@" in l or "HTTP" in l for l in ctx["gancho"]), ctx
    ctx = analisar_chat("canal", 60, ["caralho"] * 12)            # só palavrão: nenhuma categoria, genérico
    assert ctx["gancho"][-1] == "60 MSGS EM 10 s" and "CARALHO" not in " ".join(ctx["gancho"]), ctx
    ctx = analisar_chat("canal", 60, ["f"] * 9 + ["porra"] * 3)
    assert ctx["tipo"] == "falha" and ctx["gancho"][-1].endswith("x9") and "PORRA" not in " ".join(ctx["gancho"]), ctx
    ctx = analisar_chat("canal", 70, ["spoiler"] * 10)
    assert ctx["tipo"] == "historia" and "SPOILER" not in " ".join(ctx["gancho"]), ctx
    ctx = analisar_chat("canal", 0, [])
    assert ctx["gancho"] == GANCHO_SEM_CHAT.split("|"), ctx
    for tipo, lista in {**MODELOS_FRASE, **MODELOS_GENERICOS}.items():
        for m in lista:
            linhas = m.format(k="KKKKK", n=99, m=999).split("|")
            assert len(linhas) <= 2 and _caber(linhas) is not None, f"modelo não cabe: {m}"
    assert anton().largura("MMMMMMMMMMMMMMMMMMMMMMMM", 84) > CAIXA_W, "medida de fonte suspeita"
    assert 0 < montserrat().largura("A", 64) < 64
    # tempos
    assert tempo_srt(3723.456) == "01:02:03,456", tempo_srt(3723.456)
    assert tempo_ass(3723.456) == "1:02:03.46", tempo_ass(3723.456)
    assert janela_do_vertical(35, 28) == (13.0, 35.0)                   # 28 s + 8 passaria do fim: recua o início
    ini, fim = janela_do_vertical(35, 24)
    assert (ini, fim) == (10.0, 32.0), (ini, fim)                       # 14 s antes, 8 depois
    ini, fim = janela_do_vertical(35, 33.5)
    assert fim == 35 and abs((fim - ini) - VERTICAL_S) < 1e-6 and ini >= 0, (ini, fim)   # não passa do fim
    ini, fim = janela_do_vertical(35, 3)
    assert ini == 0.0 and abs(fim - VERTICAL_S) < 1e-6, (ini, fim)       # não passa do começo
    assert janela_do_vertical(15, 10) == (0.0, 15)                       # clipe curto vai inteiro
    assert [variante_do_numero(n) for n in range(1, 9)] == ["v22", "v22", "v22", "v35"] * 2
    # áudio sintético: ruído de fundo + estouro entre 24 e 25,5 s
    rng = np.random.default_rng(1)
    x = rng.normal(0, 0.01, 16000 * 35).astype(np.float32)
    x[16000 * 24:int(16000 * 25.5)] += rng.normal(0, 0.3, int(16000 * 1.5)).astype(np.float32)
    t = pico_de_pcm(x)
    assert t is not None and 24.0 <= t <= 25.0, t
    assert pico_de_pcm(np.zeros(16000 * 35, dtype=np.float32)) is None, "silêncio não tem pico"
    assert pico_de_pcm(rng.normal(0, 0.1, 16000 * 35).astype(np.float32)) is None, "volume parelho não tem pico"
    y = x.copy()
    y[16000 * 5:16000 * 6] += rng.normal(0, 0.6, 16000).astype(np.float32)       # barulho fora da faixa de busca
    assert 24.0 <= pico_de_pcm(y) <= 25.0, "a busca fica entre 18 e 34 s"
    # blocos de legenda: no máximo 4 palavras, 2 linhas, quebra em pausa; palavras fora do recorte somem
    pal = [(i * 0.3, i * 0.3 + 0.25, w) for i, w in enumerate("ISSO É UMA COISA MUITO LOUCA DEMAIS".split())]
    bl = montar_blocos(pal)
    assert all(len(b) <= MAX_PALAVRAS for b in bl) and sum(len(b) for b in bl) == len(pal), bl
    assert len(montar_blocos([(0, 0.2, "A"), (2.0, 2.2, "B")])) == 2, "pausa longa quebra o bloco"
    seg = [[(1.0, 1.4, "oi"), (10.0, 10.5, "tchau"), (30.0, 30.4, "fim")]]
    assert palavras_no_recorte(seg, 8.0, 20.0) == [(2.0, 2.5, "tchau")]
    # .txt de post
    t = texto_post("canal", "historia", ["O CHAT REAGIU", "60 MSGS EM 10 s"], "v22", "x")
    assert "[revisar spoiler]" in t and "twitch.tv/canal" in t and "#spoiler" in t
    assert "[revisar spoiler]" not in texto_post("canal", "humor", ["A", "B"], "v35", "x")
    # picos.csv: cabeçalho antigo é migrado, numeração segue a contagem de linhas
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        arq = Path(tmp) / "picos.csv"
        antigas = COLUNAS_PICOS[:11]
        arq.write_text(",".join(antigas) + "\n" + ",".join(f"v{i}" for i in range(11)) + "\n", encoding="utf-8")
        n = anexar_csv(arq, COLUNAS_PICOS, lambda k: [f"n{k}"] * len(COLUNAS_PICOS))
        linhas = list(csv.DictReader(open(arq, newline="", encoding="utf-8")))
        assert n == 2 and len(linhas) == 2 and linhas[0]["tipo"] == "" and linhas[0]["demo"] == "v10", (n, linhas)
        assert anexar_csv(arq, COLUNAS_PICOS, lambda k: [""] * len(COLUNAS_PICOS)) == 3
        novo = Path(tmp) / "novo.csv"
        assert anexar_csv(novo, COLUNAS_PICOS, lambda k: [k] * len(COLUNAS_PICOS)) == 1
        assert novo.read_text(encoding="utf-8").count("quando,canal") == 1
    # layout facecam: o grafo do ffmpeg roda e dá 1080x1920 (vídeo sintético 1920x1080); sem webcam cai no v2
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        sint = tmp / "sint.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=1920x1080:rate=30:duration=1",
                        "-f", "lavfi", "-i", "anullsrc=r=16000:cl=mono", "-t", "1", "-c:v", "libx264", "-preset", "ultrafast",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", str(sint)], check=True)
        ass = tmp / "a.ass"
        escrever_ass([(0.1, 0.5, "TESTE")], ["GANCHO", "LINHA 2"], GANCHO_PX, "canal", 1.0, ass)
        for recorte, nome in (([0.0, 0.45, 0.21, 0.21], "fc"), ([0.79, 0.02, 0.2, 0.2], "fc2"), (None, "v2")):
            saida = tmp / f"{nome}.mp4"
            assert fazer_vertical(sint, ass, saida, 0.0, 1.0, recorte), f"ffmpeg falhou no layout {nome}"
            dim = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                  "-of", "csv=p=0", str(saida)], capture_output=True, text=True).stdout.strip()
            assert dim == "1080,1920", (nome, dim)
        assert CAM_Y + CAM_H == JOGO_Y and JOGO_Y + JOGO_H == 1440 and CAM_Y >= GANCHO_Y + 200, "faixas do facecam fora da zona segura"
        # escolher_facecam: clipe ilegível -> None (fica no v2), motivo registrado em decisoes.csv
        rec, t_fc, nota = escolher_facecam(tmp / "nao_existe.mp4", "canal", tmp / "facecam")
        assert rec is None and "layout v2" in nota, nota
        linhas = list(csv.DictReader(open(tmp / "facecam" / "decisoes.csv", newline="", encoding="utf-8")))
        assert len(linhas) == 1 and linhas[0]["layout"] == "v2 (fallback)" and linhas[0]["motivo"], linhas
    import facecam
    facecam.autoteste()
    print("ok (pos)")


def _cli(args):
    if args == ["--teste"]:
        autoteste()
        return
    if not args or args[0].startswith("-"):
        sys.exit(__doc__)
    clipe, canal, mais, msgs, completo, layout, i = Path(args[0]).resolve(), "teste", "", 80, False, "v2", 1
    while i < len(args):
        if args[i] == "--canal":
            canal, i = args[i + 1].lower(), i + 1
        elif args[i] == "--mais":
            mais, i = args[i + 1], i + 1
        elif args[i] == "--msgs":
            msgs, i = int(args[i + 1]), i + 1
        elif args[i] == "--completo":
            completo = True
        elif args[i] == "--layout" and i + 1 < len(args) and args[i + 1] in LAYOUTS:
            layout, i = args[i + 1], i + 1
        else:
            sys.exit(__doc__)
        i += 1
    textos = []
    for parte in mais.split(" | "):
        m = re.match(r"^(.*) x(\d+)$", parte.strip())
        if m:
            textos += [m.group(1)] * int(m.group(2))
    ctx = analisar_chat(canal, msgs, textos)
    ctx.update(canal=canal, variante="v35" if completo else "v22", layout=layout)
    print(f"tipo {ctx['tipo']} | gancho {' / '.join(ctx['gancho'])} ({ctx['gancho_px']} px)")
    produzir(clipe, ctx, clipe.parent / "verticais")


if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True)
    _cli(sys.argv[1:])
