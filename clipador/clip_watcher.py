#!/usr/bin/env python3
"""clip-watcher: acompanha uma live da Twitch, conta o chat e corta cada pico.

Base: projeto do @patrickndf (Conecta Ads). Mudanças desta versão:
- BUFFER ROTATIVO em vez de gravar a live inteira: streamlink -> ffmpeg grava
  segmentos de 10 s em gravacoes/<canal>/<sessao>/seg_NNNNNN.ts e apaga os que
  passam de BUFFER_S (600 s) e não são usados por nenhum corte pendente. Gasta
  ~0,5 GB por canal em vez de ~3 GB por hora (o disco C: é pequeno);
- guarda de disco: se o C: (/mnt/c, é onde mora o disco virtual do WSL) ficar
  com menos de 12 GB livres, para de gravar e avisa bem alto. Nunca apaga nada
  fora de gravacoes/;
- o ponto do corte vem da régua de tempo dos próprios segmentos (lista.csv do
  ffmpeg), não do relógio. O streamlink pula os anúncios (a flag antiga
  --twitch-disable-ads foi desativada na versão 8; o filtro agora é padrão) e a
  gravação fica mais curta que o relógio; no original, cada intervalo comercial
  desalinhava os cortes seguintes. O relógio só entra como último recurso
  (e fica registrado no log);
- se a live cair ou acabar, volta a esperar e grava num buffer novo;
- legenda em português com faster-whisper (modelo carregado uma vez só);
- pós-produção da onda 2 (pos.py): tipo do corte pelo chat, gancho no topo, vertical 1080x1920 de ~22 s
  ancorado no pico de áudio (1 em 4 com os 35 s inteiros, controle A/B), legenda palavra a palavra em
  amarelo, crédito twitch.tv/<canal> e um .txt de post pronto, tudo em clipes/verticais/<canal>/;
- clipes/picos.csv registra cada pico (horário, mensagens, frases mais ditas, tipo, variante, gancho)
  para calibrar e para montar as compilações do dia (compilar.py); clipes/verticais.csv registra o
  recorte de cada vertical (pico de áudio, início, duração, tempo de pós-produção).

Uso (de dentro da pasta):
  ./rodar.sh CANAL                 acompanha e corta até Ctrl+C
  ./rodar.sh CANAL --demo          força um corte depois de ~90 s gravados (teste)
  ./rodar.sh CANAL --manter        não apaga os segmentos (só se sobrar disco)
  ./rodar.sh CANAL --buffer 120    buffer de 120 s em vez de 600 (mínimo 60)
  ./rodar.sh CANAL --fator 4 --minimo 5   calibra a regra de pico sem editar o arquivo
  ./rodar.sh CANAL --layout facecam  vertical com a webcam do streamer ampliada em cima (padrão: v2; sem webcam
                                   confiável cai no v2 sozinho; ver pos.py e facecam.py)
  ./rodar.sh --teste               autoteste das regras
Vários canais de uma vez: ./multi.sh CANAL1 CANAL2 ...  (ver LEIAME.md)
"""
import collections
import csv
import fcntl
import queue
import random
import re
import shutil
import signal
import socket
import statistics
import subprocess
import sys
import threading
import time
from pathlib import Path

import pos

# ---- ajuste aqui (um valor por vez, numa live de teste) ----
JANELA = 10        # segundos de cada contagem do chat
HISTORICO = 30     # janelas usadas como base (5 minutos)
FATOR = 3.0        # pico = FATOR vezes a mediana da base (4 se corta demais, 2 se corta de menos)
MINIMO = 10        # mensagens mínimas na janela; canal pequeno pede 4 ou 5
ANTES = 20         # segundos antes da janela do pico: o chat reage depois do lance
DEPOIS = 5         # segundos depois da janela: pega a reação do streamer
DESCANSO = 60      # segundos sem marcar outro pico
# áudio (19/11, ideia do chopify): o volume do streamer também marca pico, somado ao chat
A_FATOR = 3.0      # áudio forte = volume médio da janela >= A_FATOR x a mediana dos últimos 5 min
A_PISO = 300.0     # mediana mínima do volume (RMS int16): silêncio na base não infla a razão
A_SO_AUDIO = 4.0   # sem chat (live do YouTube sem chat lido): só o áudio, e mais exigente
PESO_AUDIO, PESO_CHAT = 0.6, 0.4   # pico misto: PESO_AUDIO*áudio/A_FATOR + PESO_CHAT*chat/FATOR >= 1
A_MIN_MISTO = 1.8  # no pico misto o áudio precisa estar pelo menos 1,8x a base
CREDITO_YT = {"gameplayrj": "Gameplayrj", "paulinholokooficial": "PaulinhoLOKOoficial", "lipaogamer": "LipaoGamer"}
MODELO = "small"   # faster-whisper: tiny, base, small, medium (maior = melhor e mais lento)
IDIOMA = "pt"
# layout, tamanho do vertical, controle A/B, fontes e lista de bloqueio do gancho: topo do pos.py
DEMO_APOS = 90    # --demo: força um corte quando a gravação passar disso
LAYOUT = "v2"      # --layout facecam troca o vertical (opt-in); v2 é o padrão
BUFFER_S = 600     # segundos de gravação mantidos em disco por canal
SEGMENTO = 10      # duração de cada segmento do buffer
DISCO_MIN_GB = 12  # abaixo disso no C: para de gravar
DISCO_RETOMA_GB = 14   # depois de parar por disco, só volta com folga acima disso
DISCO_REF = Path("/mnt/c")  # o vhdx do WSL vive no C:; é ele que enche
BATIDA = 60        # a cada quantos segundos checa o disco e imprime o resumo
TRAVADO_S = 300    # sem segmento novo por tanto tempo = gravação travada, reinicia
                   # (o streamlink 8 filtra anúncios: um intervalo comercial de até ~3 min não pode contar como travado)

PASTA = Path(__file__).resolve().parent
GRAVACOES = PASTA / "gravacoes"
CLIPES = PASTA / "clipes"
VERTICAIS = CLIPES / "verticais"
LOG_PICOS = CLIPES / "picos.csv"


def eh_pico(contagem, base):
    """Pico: janela bem acima da mediana recente e com volume mínimo."""
    if len(base) < 6 or contagem < MINIMO:
        return False
    return contagem >= FATOR * max(statistics.median(base), 1)


def eh_pico_misto(razao_audio, razao_chat, tem_chat):
    """Pico pelo áudio. Com chat: soma ponderada áudio + chat (o chat sozinho continua no eh_pico).
    Sem chat (YouTube): só o áudio, com A_SO_AUDIO."""
    if razao_audio is None:
        return False
    if not tem_chat:
        return razao_audio >= A_SO_AUDIO
    if razao_audio < A_MIN_MISTO:
        return False
    return PESO_AUDIO * razao_audio / A_FATOR + PESO_CHAT * razao_chat / FATOR >= 1.0


def fonte_do_canal(canal):
    """'yt-gameplayrj' -> ('youtube', URL da live, crédito); qualquer outro -> Twitch."""
    if canal.startswith("yt-"):
        handle = CREDITO_YT.get(canal[3:], canal[3:])
        return "youtube", f"https://www.youtube.com/@{handle}/live", f"youtube.com/@{handle}"
    return "twitch", f"https://twitch.tv/{canal}", f"twitch.tv/{canal}"


def programa(nome):
    """Prefere o executável do mesmo .venv do python que está rodando."""
    local = Path(sys.executable).parent / nome
    return str(local) if local.exists() else shutil.which(nome)


# ---------- disco ----------

def livre_gb():
    """GB livres no C: (o que o vhdx do WSL consome ao crescer)."""
    alvo = DISCO_REF if DISCO_REF.exists() else PASTA
    try:
        return shutil.disk_usage(alvo).free / 1e9
    except OSError as erro:  # /mnt/c pode soluçar; não derruba o canal (a próxima batida tenta de novo)
        print(f"aviso: não consegui ler o espaço livre do C: ({erro}); seguindo")
        return float("inf")


def aviso_disco(livre, minimo):
    barra = "!" * 70
    print(f"\n{barra}\n!!  DISCO C: QUASE CHEIO: {livre:.1f} GB livres (mínimo {minimo} GB).\n"
          f"!!  A GRAVAÇÃO ESTÁ PARADA. Libere espaço no C: (nada é apagado fora de gravacoes/).\n"
          f"{barra}\n")


def aguardar_disco(minimo):
    """Bloqueia (avisando a cada batida) até o C: ter pelo menos `minimo` GB livres."""
    while (livre := livre_gb()) < minimo:
        aviso_disco(livre, minimo)
        time.sleep(BATIDA)


# ---------- buffer rotativo ----------

class Sessao:
    """Uma gravação: streamlink -> ffmpeg segmentando em gravacoes/<canal>/<sessao>/."""

    def __init__(self, canal, streamlink, url=None):
        url = url or f"https://twitch.tv/{canal}"
        self.nome = time.strftime("%Y%m%d-%H%M%S")
        self.pasta = GRAVACOES / canal / self.nome
        self.pasta.mkdir(parents=True, exist_ok=True)
        self.lista = self.pasta / "lista.csv"
        self.apagados = set()
        self.t0 = time.time()
        self._chave, self._segs, self._mtime = None, [], 0.0
        # --retry-streams: fica esperando e começa a escrever quando a live abrir
        # setpriv --pdeathsig: se este python morrer (kill, OOM), o kernel manda SIGTERM ao streamlink/ffmpeg,
        # em vez de deixá-los gravando órfãos sem limpeza do buffer nem guarda de disco
        morrer_junto = ["setpriv", "--pdeathsig", "TERM", "--"] if shutil.which("setpriv") else []
        self.sl = subprocess.Popen(
            morrer_junto + [streamlink, "-O", "--loglevel", "warning", "--retry-streams", "15",
                            url, "best"],
            stdout=subprocess.PIPE)
        self.ff = subprocess.Popen(
            morrer_junto + ["ffmpeg", "-v", "error", "-y", "-i", "pipe:0", "-c", "copy", "-f", "segment",
             "-segment_time", str(SEGMENTO), "-segment_format", "mpegts", "-reset_timestamps", "0",
             "-segment_list", str(self.lista), "-segment_list_type", "csv",
             "-segment_list_flags", "+live", str(self.pasta / "seg_%06d.ts")],
            stdin=self.sl.stdout)
        self.sl.stdout.close()  # só o ffmpeg lê o pipe: o EOF chega quando o streamlink sair

    def vivo(self):
        return self.ff.poll() is None

    def segmentos(self):
        """[(nome, inicio, fim)] na régua de tempo do ffmpeg, só os já fechados."""
        try:
            st = self.lista.stat()
        except OSError:
            return []
        chave = (st.st_mtime_ns, st.st_size)
        if chave != self._chave:
            segs = []
            try:
                linhas = self.lista.read_text(encoding="utf-8").splitlines()
            except OSError:
                return self._segs
            for linha in linhas:
                partes = linha.split(",")
                try:
                    segs.append((partes[0], float(partes[1]), float(partes[2])))
                except (IndexError, ValueError):
                    continue  # linha ainda sendo escrita
            self._chave, self._segs, self._mtime = chave, segs, st.st_mtime
        return self._segs

    def ultimo_listado(self):
        """Instante (relógio) em que a lista mudou pela última vez, ou None."""
        return self._mtime if self.segmentos() else None

    def agora(self):
        """(posição gravada em s, fonte). Fim do último segmento fechado + o que já
        correu do segmento aberto; sem nenhum segmento ainda, cai no relógio."""
        segs = self.segmentos()
        if segs:
            extra = min(max(time.time() - self._mtime, 0.0), 2 * SEGMENTO)
            return segs[-1][2] + extra, "gravado"
        return time.time() - self.t0, "relogio"

    def existentes(self):
        return [s for s in self.segmentos() if s[0] not in self.apagados and (self.pasta / s[0]).exists()]

    def tamanho_mb(self):
        total = 0
        for arq in self.pasta.glob("seg_*.ts"):
            try:
                total += arq.stat().st_size
            except OSError:
                pass
        return total / 1e6

    def encerrar(self):
        """Fecha o streamlink; o ffmpeg vê o fim do pipe e fecha o último segmento sozinho."""
        for proc, espera in ((self.sl, 10), (self.ff, 30)):
            if proc.poll() is None and proc is self.sl:
                proc.terminate()
            try:
                proc.wait(timeout=espera)
            except subprocess.TimeoutExpired:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()


class Protecao:
    """Faixas de tempo que cortes pendentes ainda vão ler: a limpeza não as apaga."""

    def __init__(self):
        self.trava = threading.Lock()
        self.faixas = {}
        self.n = 0

    def pedir(self, sessao, ini, fim):
        with self.trava:
            self.n += 1
            self.faixas[self.n] = (sessao, ini, fim)
            return self.n

    def liberar(self, ident):
        with self.trava:
            self.faixas.pop(ident, None)

    def usa(self, sessao, seg_ini, seg_fim):
        with self.trava:
            return any(s is sessao and seg_ini < f and seg_fim > i for s, i, f in self.faixas.values())

    def sessao_em_uso(self, sessao):
        with self.trava:
            return any(s is sessao for s, _, _ in self.faixas.values())


def limpar(sessao, protecao, agora):
    """Apaga segmentos mais velhos que BUFFER_S, menos os que um corte pendente usa."""
    limite = agora - BUFFER_S
    for nome, ini, fim in sessao.segmentos():
        if fim >= limite:
            break
        if nome in sessao.apagados or protecao.usa(sessao, ini, fim):
            continue
        try:
            (sessao.pasta / nome).unlink()
        except FileNotFoundError:
            pass
        except OSError as erro:
            print(f"não consegui apagar {nome}: {erro}")
            continue
        sessao.apagados.add(nome)


def apagar_sessao(sessao):
    """Sessão encerrada e sem corte pendente: tira a pasta toda (só dentro de gravacoes/)."""
    pasta = sessao.pasta.resolve()
    if GRAVACOES.resolve() in pasta.parents:
        shutil.rmtree(pasta, ignore_errors=True)


# ---------- chat ----------

class Chat:
    """Chat da Twitch por IRC anônimo (nick justinfan): sem conta, sem token, só leitura."""

    def __init__(self, canal):
        self.canal = canal
        self.trava = threading.Lock()
        self.contagem = 0
        self.recentes = collections.deque(maxlen=3000)  # (instante, texto)
        threading.Thread(target=self._ler, daemon=True).start()

    def _ler(self):
        while True:
            try:
                with socket.create_connection(("irc.chat.twitch.tv", 6667), timeout=360) as s:
                    nick = f"justinfan{random.randint(10000, 99999)}"
                    s.sendall(f"NICK {nick}\r\nJOIN #{self.canal}\r\n".encode())
                    resto = b""
                    while True:
                        dados = s.recv(4096)
                        if not dados:
                            break
                        *linhas, resto = (resto + dados).split(b"\r\n")
                        for linha in linhas:
                            if linha.startswith(b"PING"):
                                s.sendall(b"PONG :tmi.twitch.tv\r\n")
                            elif b" PRIVMSG #" in linha:
                                partes = linha.split(b" :", 1)
                                texto = partes[1].decode("utf-8", "replace").strip() if len(partes) == 2 else ""
                                with self.trava:
                                    self.contagem += 1
                                    self.recentes.append((time.time(), texto))
            except OSError as erro:
                print(f"chat caiu ({erro}), reconectando em 5 s")
            time.sleep(5)

    def fechar_janela(self):
        with self.trava:
            n, self.contagem = self.contagem, 0
        return n

    def textos(self, segundos):
        """Mensagens (só o texto, minúsculo; nunca o nome de quem mandou) dos últimos `segundos`."""
        limite = time.time() - segundos
        with self.trava:
            return [t.lower()[:120] for instante, t in self.recentes if instante >= limite and t]

    def mais_ditas(self, segundos, quantas=8, textos=None):
        """[(frase, vezes)] das mais repetidas; vale o mesmo recorte de `textos` se for passado."""
        textos = self.textos(segundos) if textos is None else textos
        return [(t[:30], n) for t, n in collections.Counter(textos).most_common(quantas)]


class ChatYT(Chat):
    """Chat de uma live do YouTube, lido pelo próprio yt-dlp (legenda 'live_chat', sem login).
    Mesma interface do Chat da Twitch. Se não der para ler, a contagem fica 0 e o pico vem só do áudio."""

    def __init__(self, canal, url):
        self.url = url
        self.pasta = GRAVACOES / "_chat"
        self.pasta.mkdir(parents=True, exist_ok=True)
        self.lendo = False                       # True enquanto chega mensagem
        super().__init__(canal)

    @staticmethod
    def textos_da_acao(obj):
        """Textos das mensagens dentro de uma linha do live_chat.json (qualquer aninhamento)."""
        achados = []

        def andar(o):
            if isinstance(o, dict):
                r = o.get("liveChatTextMessageRenderer")
                if isinstance(r, dict):
                    runs = (r.get("message") or {}).get("runs") or []
                    achados.append("".join(x.get("text") or (x.get("emoji") or {}).get("shortcuts", [""])[0]
                                           for x in runs if isinstance(x, dict)))
                    return
                for v in o.values():
                    andar(v)
            elif isinstance(o, list):
                for v in o:
                    andar(v)
        andar(obj)
        return achados

    def _ler(self):
        import json
        ytdlp = programa("yt-dlp")
        base = self.pasta / self.canal
        while True:
            for velho in self.pasta.glob(f"{self.canal}.live_chat.json*"):
                velho.unlink(missing_ok=True)
            proc = subprocess.Popen([ytdlp, "--js-runtimes", "node", "--no-warnings", "--skip-download",
                                     "--write-subs", "--sub-langs", "live_chat", "-o", str(base), self.url],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            lido, resto = 0, b""
            nomes = [self.pasta / f"{self.canal}.live_chat.json.part", self.pasta / f"{self.canal}.live_chat.json"]
            while proc.poll() is None:
                time.sleep(1)
                # o yt-dlp escreve uma ação por linha no .part (os .part-FragN são temporários, outro formato)
                arq = next((n for n in nomes if n.exists()), None)
                if arq is None:
                    continue
                try:
                    with open(arq, "rb") as f:
                        f.seek(lido)
                        novo = f.read()
                except OSError:
                    continue
                lido += len(novo)
                *linhas, resto = (resto + novo).split(b"\n")
                agora = time.time()
                for linha in linhas:
                    # ao ligar vem o histórico recente de uma vez: só conta mensagem do último minuto
                    marca = re.search(rb'"timestampUsec": ?"(\d+)"', linha)
                    if marca and agora - int(marca.group(1)) / 1e6 > 60:
                        continue
                    try:
                        textos = self.textos_da_acao(json.loads(linha))
                    except ValueError:
                        continue
                    with self.trava:
                        for t in textos:
                            self.contagem += 1
                            self.recentes.append((agora, t.strip()))
                    self.lendo = self.lendo or bool(textos)
            self.lendo = False
            time.sleep(60)                       # live fora do ar ou chat fechado: tenta de novo


class Audio:
    """Volume (RMS) e 'cara de risada' de cada segundo gravado, lidos dos segmentos já fechados."""

    def __init__(self):
        self.lidos, self.rms, self.riso = set(), {}, {}

    def atualizar(self, sessao):
        for nome, ini, _fim in sessao.existentes():
            if nome in self.lidos:
                continue
            self.lidos.add(nome)
            try:
                rms, riso = pos.volume_por_segundo(sessao.pasta / nome)
            except Exception as erro:  # segmento ruim não derruba o canal
                print(f"aviso: não li o áudio de {nome} ({type(erro).__name__})")
                continue
            for i, (a, b) in enumerate(zip(rms, riso)):
                self.rms[int(ini) + i] = a
                self.riso[int(ini) + i] = b
        if len(self.rms) > 2 * BUFFER_S:          # guarda só o que a base usa
            corte = max(self.rms) - BUFFER_S
            for t in [t for t in self.rms if t < corte]:
                self.rms.pop(t, None)
                self.riso.pop(t, None)

    def fim(self):
        """Último segundo com áudio lido (+1), ou None."""
        return max(self.rms) + 1 if self.rms else None

    def razao(self, ate, janela=JANELA):
        """(volume médio de [ate-janela, ate) / mediana dos 5 min antes, maior riso da janela) ou (None, 0)."""
        vals = [self.rms[t] for t in range(int(ate - janela), int(ate)) if t in self.rms]
        base = [v for t, v in self.rms.items() if ate - 300 <= t < ate - janela]
        if len(vals) < janela // 2 or len(base) < 60:
            return None, 0.0
        riso = max((self.riso.get(t, 0.0) for t in range(int(ate - janela), int(ate))), default=0.0)
        return statistics.mean(vals) / max(statistics.median(base), A_PISO), riso


# ---------- pós-produção ----------

def pos_producao(fila):
    """Uma fila só: legenda, vertical e texto de post de um clipe por vez, para não travar a máquina."""
    pos.MODELO, pos.IDIOMA = MODELO, IDIOMA
    while (item := fila.get()) is not None:
        clipe, ctx = item
        try:
            pos.produzir(clipe, ctx, VERTICAIS, antes=ANTES, janela=JANELA, depois=DEPOIS)
        except Exception as erro:  # um clipe com problema não derruba a fila
            print(f"pós-produção falhou em {clipe.name}: {type(erro).__name__}: {erro}")


# ---------- corte ----------

def cortar(sessao, inicio, fim, saida):
    """Junta os segmentos que cobrem [inicio, fim] e corta, tudo na régua da lista.csv."""
    segs = [s for s in sessao.existentes() if s[2] > inicio and s[1] < fim]
    if not segs:
        print(f"nenhum segmento cobre {inicio:.0f}-{fim:.0f} s (já apagados?)")
        return False
    relativo = max(inicio - segs[0][1], 0.0)          # a partir do começo do 1º segmento
    duracao = min(fim, segs[-1][2]) - inicio
    entrada = "concat:" + "|".join(str(sessao.pasta / s[0]) for s in segs)
    try:
        r = subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-ss", f"{relativo:.2f}", "-i", entrada,
             "-t", f"{duracao:.2f}", "-c", "copy", "-avoid_negative_ts", "make_zero",
             "-movflags", "+faststart", str(saida)],
            check=False, timeout=120,
        )
    except subprocess.TimeoutExpired:
        print(f"corte travou (> 120 s) e foi abortado: {saida.name}")
        return False
    return r.returncode == 0 and saida.exists() and saida.stat().st_size > 0


def agendar_corte(sessao, inicio, fim, saida, protecao, fila, ctx):
    """Espera existir segmento fechado até `fim` (o trecho de DEPOIS) e corta."""
    ident = protecao.pedir(sessao, inicio, fim)  # protege os segmentos já, antes da thread

    def trabalho():
        try:
            limite = time.time() + 3 * SEGMENTO + 60
            while sessao.vivo() and time.time() < limite:
                segs = sessao.segmentos()
                if segs and segs[-1][2] >= fim:
                    break
                time.sleep(1)
            t0 = time.time()
            if cortar(sessao, inicio, fim, saida):
                print(f"clipe pronto: {saida} (corte {time.time() - t0:.1f} s, "
                      f"{saida.stat().st_size / 1e6:.1f} MB)")
                fila.put((saida, ctx))
            else:
                print(f"corte falhou: {saida}")
        finally:
            protecao.liberar(ident)

    t = threading.Thread(target=trabalho)
    t.start()
    return t


# ---------- principal ----------

def main(canal, demo=False, manter=False):
    for pasta in (GRAVACOES / canal, CLIPES, VERTICAIS):
        pasta.mkdir(parents=True, exist_ok=True)
    trava = open(GRAVACOES / f"{canal}.lock", "w")
    try:
        fcntl.flock(trava, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        sys.exit(f"já existe um clip_watcher rodando para {canal}")
    streamlink = programa("streamlink")
    if not streamlink:
        sys.exit("streamlink não encontrado: rode pelo ./rodar.sh")
    if not manter:  # sobras de uma execução anterior que caiu (a trava garante que não são de outro processo)
        for velho in (GRAVACOES / canal).iterdir():
            if velho.is_dir():
                shutil.rmtree(velho, ignore_errors=True)
                print(f"buffer antigo removido: {velho.name}")

    origem, url, credito = fonte_do_canal(canal)
    print(f"buffer de {BUFFER_S} s em {GRAVACOES / canal}"
          + (" (--manter: nada será apagado)" if manter else "")
          + f" | C: com {livre_gb():.1f} GB livres (para de gravar abaixo de {DISCO_MIN_GB} GB)"
          + f" | fonte {origem}: {url}")
    chat = ChatYT(canal, url) if origem == "youtube" else Chat(canal)
    fila = queue.Queue()
    fila_pos = threading.Thread(target=pos_producao, args=(fila,))
    fila_pos.start()
    protecao = Protecao()
    cortes, sessoes, sessao = [], [], None
    minimo_disco = DISCO_MIN_GB

    def faxina():
        """Limpa o buffer das sessões; sessão encerrada e sem corte pendente some inteira."""
        for s in list(sessoes):
            if s.vivo():
                limpar(s, protecao, s.agora()[0])
            elif not protecao.sessao_em_uso(s):
                if not manter:
                    apagar_sessao(s)
                sessoes.remove(s)

    try:
        while True:
            aguardar_disco(minimo_disco)
            minimo_disco = DISCO_MIN_GB
            sessao = Sessao(canal, streamlink, url)
            sessoes.append(sessao)
            audio = Audio()
            print(f"esperando a live de {canal} (Ctrl+C para parar)")
            while sessao.vivo() and not any(sessao.pasta.glob("seg_*.ts")):
                time.sleep(1)
            if not sessao.vivo() and not sessao.segmentos():
                print("o streamlink/ffmpeg saiu antes de gravar; tentando de novo em 15 s")
                sessao.encerrar()
                faxina()
                time.sleep(15)
                continue
            chat.fechar_janela()  # descarta o que chegou antes de gravar
            print(f"gravando em {sessao.pasta.relative_to(PASTA)}")

            base, ultimo, forcado = [], -DESCANSO, False
            janelas_chat = collections.deque(maxlen=HISTORICO)   # (posição gravada no fim da janela, msgs)
            audio_ate = None                                       # fim da última janela de áudio avaliada
            proxima = time.time() + JANELA
            prox_batida = time.time() + BATIDA
            motivo_parada = None
            while sessao.vivo():
                time.sleep(max(0.0, proxima - time.time()))
                proxima += JANELA
                contagem = chat.fechar_janela()
                agora, fonte = sessao.agora()
                relogio = time.time() - sessao.t0
                if fonte == "relogio":
                    print(f"aviso: nenhum segmento listado ainda, usando o relógio ({relogio:.0f} s) como posição")
                janelas_chat.append((agora, contagem))
                mediana = statistics.median(base) if base else 0
                forcar = demo and not forcado and agora >= DEMO_APOS
                ponto, motivo = None, ""
                if forcar or eh_pico(contagem, base):
                    ponto = agora
                else:
                    # áudio: avalia cada janela de 10 s assim que o segmento dela fecha (chega ~10 s atrasado)
                    try:
                        audio.atualizar(sessao)
                    except OSError as erro:
                        print(f"aviso: leitura do áudio falhou ({erro})")
                    fim_audio = audio.fim()
                    if fim_audio is not None and (audio_ate is None or fim_audio - audio_ate >= JANELA):
                        audio_ate = fim_audio
                        razao_a, riso = audio.razao(fim_audio)
                        # o chat reage depois do lance: maior janela de chat entre o lance e 15 s depois
                        perto = [n for t, n in janelas_chat if fim_audio - 5 <= t <= fim_audio + 15]
                        msgs = max(perto, default=0)
                        razao_c = msgs / max(mediana, 1)
                        tem_chat = origem == "twitch" or getattr(chat, "lendo", False)
                        if eh_pico_misto(razao_a, razao_c, tem_chat):
                            ponto = fim_audio
                            motivo = f"[áudio {razao_a:.1f}x, riso {riso:.2f}, chat {razao_c:.1f}x]"
                if ponto is not None and ponto - ultimo > DESCANSO:
                    agora = ponto
                    forcado = forcado or forcar
                    ultimo = agora
                    inicio = max(agora - JANELA - ANTES, 0.0)
                    fim = agora + DEPOIS
                    saida = CLIPES / f"{canal}-{time.strftime('%Y%m%d-%H%M%S')}.mp4"
                    textos = chat.textos(JANELA + 15 if motivo else JANELA + 5)
                    mais = [f"{t} x{n}" for t, n in chat.mais_ditas(JANELA + 5, textos=textos)]
                    if motivo:
                        mais = [motivo] + mais
                    ctx = pos.analisar_chat(canal, contagem, textos)
                    ctx["canal"] = canal
                    ctx["layout"] = LAYOUT
                    ctx["credito"] = credito
                    print(f"pico{' (demo)' if forcar else ''}{' pelo áudio' if motivo else ''}: {contagem} msgs em "
                          f"{JANELA} s (base {mediana:.0f}) | gravado {agora:.0f} s ({fonte}), relógio {relogio:.0f} s | "
                          f"tipo {ctx['tipo']} | gancho: {' / '.join(ctx['gancho'])} | {' | '.join(mais[:3])}")

                    def linha(numero, ctx=ctx, agora=agora, relogio=relogio, contagem=contagem, mediana=mediana,
                              inicio=inicio, saida=saida, mais=mais, forcar=forcar):
                        ctx["variante"] = pos.variante_do_numero(numero)
                        return [time.strftime("%Y-%m-%d %H:%M:%S"), canal, f"{canal}/{sessao.nome}",
                                f"{agora:.1f}", f"{relogio:.1f}", contagem, mediana, f"{inicio:.1f}", saida.name,
                                " | ".join(mais), int(forcar), ctx["tipo"], ctx["variante"],
                                " / ".join(ctx["gancho"])]
                    try:
                        pos.anexar_csv(LOG_PICOS, pos.COLUNAS_PICOS, linha)
                    except Exception as erro:  # log do pico falhar não pode derrubar o canal
                        print(f"aviso: não gravei o pico no picos.csv ({type(erro).__name__}: {erro})")
                    cortes.append(agendar_corte(sessao, inicio, fim, saida, protecao, fila, ctx))
                    cortes = [t for t in cortes if t.is_alive()]
                base = (base + [contagem])[-HISTORICO:]
                try:
                    faxina()
                except OSError as erro:  # apagar segmento falhar não pode derrubar o canal
                    print(f"aviso: faxina do buffer falhou ({erro}); tento de novo na próxima janela")

                ultima = sessao.ultimo_listado()
                if ultima is not None and time.time() - ultima > TRAVADO_S:
                    print(f"gravação travada há {time.time() - ultima:.0f} s sem segmento novo: reiniciando")
                    break
                if time.time() >= prox_batida:
                    prox_batida = time.time() + BATIDA
                    livre = livre_gb()
                    if livre < DISCO_MIN_GB:
                        aviso_disco(livre, DISCO_MIN_GB)
                        motivo_parada = "disco"
                        break
                    print(f"[{canal}] gravado {agora:.0f} s | relógio {relogio:.0f} s "
                          f"(deriva {relogio - agora:+.0f} s) | buffer {len(sessao.existentes())} seg "
                          f"{sessao.tamanho_mb():.0f} MB | C: {livre:.1f} GB livres | chat {contagem}/{JANELA} s")
            sessao.encerrar()
            if motivo_parada == "disco":
                print("gravação parada por falta de disco; volta quando o C: passar de "
                      f"{DISCO_RETOMA_GB} GB livres")
                minimo_disco = DISCO_RETOMA_GB
            else:
                print(f"a gravação parou (live acabou ou caiu). Voltando a esperar {canal}.")
            faxina()
    except KeyboardInterrupt:
        print("\nparando: terminando os cortes e verticais que faltam...")
    finally:
        if sessao is not None:
            sessao.encerrar()
        for t in cortes:
            t.join()
        fila.put(None)
        fila_pos.join()
        faxina()
        if not manter:  # nada mais usa o buffer
            for s in sessoes:
                apagar_sessao(s)
    print("fim")


def autoteste():
    assert not eh_pico(50, [5] * 3), "base curta não marca"
    assert not eh_pico(9, [1] * 10), "abaixo do mínimo não marca"
    assert not eh_pico(20, [10] * 10), "2x a mediana não é pico"
    assert eh_pico(40, [10] * 10), "4x a mediana é pico"
    assert eh_pico(12, [0] * 10), "chat parado que acorda é pico"
    # áudio + chat (19/11)
    assert not eh_pico_misto(None, 5, True), "sem áudio lido não marca"
    assert eh_pico_misto(4.0, 1.5, True), "grito (4x) com chat animado (1,5x) é pico"
    assert not eh_pico_misto(3.0, 1.0, True), "áudio 3x com chat normal não basta"
    assert eh_pico_misto(5.0, 0.5, True), "grito muito forte basta mesmo com chat parado"
    assert not eh_pico_misto(1.5, 6.0, True), "áudio baixo não vira pico misto (o chat sozinho já tem regra)"
    assert eh_pico_misto(4.5, 0, False) and not eh_pico_misto(3.5, 0, False), "sem chat: só áudio >= A_SO_AUDIO"
    assert fonte_do_canal("yt-gameplayrj") == ("youtube", "https://www.youtube.com/@Gameplayrj/live",
                                               "youtube.com/@Gameplayrj")
    assert fonte_do_canal("cellbit") == ("twitch", "https://twitch.tv/cellbit", "twitch.tv/cellbit")
    acao = {"replayChatItemAction": {"actions": [{"addChatItemAction": {"item": {"liveChatTextMessageRenderer": {
        "message": {"runs": [{"text": "KKKK "}, {"emoji": {"shortcuts": [":face-with-tears-of-joy:"]}}]}}}}}]}}
    assert ChatYT.textos_da_acao(acao) == ["KKKK :face-with-tears-of-joy:"]
    import numpy as np
    tom = (3000 * np.sin(np.arange(16000) * 2 * np.pi * 440 / 8000)).astype(np.float32)
    rms, riso = pos.volume_e_riso(tom)
    assert len(rms) == 2 and 2000 < rms[0] < 2200, rms
    a = Audio()
    a.rms = {t: 500.0 for t in range(0, 300)}
    a.rms.update({t: 2500.0 for t in range(300, 310)})
    assert abs(a.razao(310)[0] - 5.0) < 1e-6 and a.razao(30)[0] is None
    for nome in ("streamlink", "ffmpeg", "ffprobe"):
        assert programa(nome), f"{nome} não encontrado"
    import faster_whisper  # noqa: F401
    assert livre_gb() > 0
    pos.autoteste()   # filtro do gancho, tipo, tempos, janela do vertical, pico de áudio sintético, blocos
    # proteção: um corte pendente segura os segmentos que ele usa
    p, s = Protecao(), object()
    ident = p.pedir(s, 100, 140)
    assert p.usa(s, 95, 105) and p.usa(s, 135, 145) and not p.usa(s, 80, 100) and not p.usa(s, 140, 150)
    p.liberar(ident)
    assert not p.usa(s, 95, 105)
    # --layout: facecam é opt-in; valor desconhecido ou sem valor é uso errado (nunca vira o canal)
    assert ler_args(["canal"]) == ("canal", {"demo": False, "manter": False})
    assert ler_args(["canal", "--layout", "facecam", "--demo"]) == ("canal", {"demo": True, "manter": False, "layout": "facecam"})
    assert ler_args(["--layout", "facecam", "Canal"])[0] == "canal" and ler_args(["canal", "--layout", "xyz"]) is None
    assert ler_args(["canal", "--layout"]) is None
    print("ok")


def ler_args(args):
    """Devolve (canal, opções) ou None se o uso estiver errado."""
    opcoes, canal, i = {"demo": False, "manter": False}, None, 0
    valores = {"--buffer": ("buffer", int), "--fator": ("fator", float), "--minimo": ("minimo", int)}
    while i < len(args):
        a = args[i]
        if a in ("--demo", "--manter"):
            opcoes[a[2:]] = True
        elif a == "--layout" and i + 1 < len(args) and args[i + 1] in pos.LAYOUTS:
            opcoes["layout"] = args[i + 1]
            i += 1
        elif a in valores and i + 1 < len(args):
            nome, tipo = valores[a]
            try:
                opcoes[nome] = tipo(args[i + 1])
            except ValueError:
                return None
            i += 1
        elif not a.startswith("-") and canal is None:
            canal = a.lower().lstrip("#")
        else:
            return None
        i += 1
    return (canal, opcoes) if canal else None


if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True)
    # processos lançados em segundo plano (multi.sh) herdam SIGINT ignorado: religa, senão o parar.sh não pega
    signal.signal(signal.SIGINT, signal.default_int_handler)
    # SIGTERM (kill, earlyoom) faz o mesmo caminho do Ctrl+C: termina cortes pendentes e limpa o buffer
    signal.signal(signal.SIGTERM, signal.default_int_handler)
    args = sys.argv[1:]
    if args == ["--teste"]:
        autoteste()
    elif (lido := ler_args(args)) is not None:
        canal, opcoes = lido
        BUFFER_S = max(opcoes.get("buffer", BUFFER_S), 60)
        FATOR = opcoes.get("fator", FATOR)
        MINIMO = opcoes.get("minimo", MINIMO)
        LAYOUT = opcoes.get("layout", LAYOUT)
        main(canal, demo=opcoes["demo"], manter=opcoes["manter"])
    else:
        sys.exit(__doc__)
