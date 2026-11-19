# Revisão de código do clipador (somente leitura)

Data: 2026-11-18, ~04:00 BRT. Escopo: `clip_watcher.py`, `pos.py`, `facecam.py`, `auto_lancamento.py`, `multi.sh`, `parar.sh`, `status.sh`, `agendar.sh`, `compilar.py`, `galeria.py` (só varredura: sem remoção/escrita de arquivos, sem rede).
Nada do projeto foi editado e nenhum processo foi iniciado ou morto. Os testes sintéticos ficaram em `/tmp/revisao` (python do .venv, `sys.dont_write_bytecode`).

Convenção: **[confirmado]** = li o código e/ou reproduzi com dado sintético. **[suspeita]** = o defeito de código está lá, mas o gatilho depende de algo que não consegui reproduzir.

Números de linha são os dos arquivos em 18/11 03:40.

---

## CRÍTICO

### C1. `agendar.sh` está sem proteção contra SIGHUP: se a sessão que o abriu fechar, nada liga às 07:40 [confirmado o fato; o gatilho é operacional]
- `agendar.sh:11-15`; processo real: `bash ./agendar.sh 07:40 10:30 12:00` (pid 1387), `tty pts/0`, filho de `/init` (uma sessão `wsl.exe`), com um `sleep 17108` como filho.
- Em `/proc/1387/status`: `SigIgn=0x4` (só SIGQUIT) e `SigCgt=0x10002` (SIGINT e SIGCHLD). **SIGHUP não é ignorado nem tratado.** Se o `wsl.exe`/pty que o criou fechar (fechar a janela, o terminal do Claude Code ser encerrado), o bash recebe SIGHUP e morre junto com o `sleep`. O `auto_lancamento.py` nunca roda e nenhum canal sobe, sem aviso (o log `auto.log` só tem a linha "agendado").
- O `multi.sh` faz certo (`setsid nohup ... < /dev/null`), só o agendador não.
- Atenuante: `/etc/wsl.conf` tem `systemd=true`, então a VM do WSL não desliga sozinha por falta de terminal. O risco é só o SIGHUP.
- Correção (relançar sem perder o agendamento, quando puder mexer): matar este e subir de novo desacoplado.
  ```bash
  setsid nohup ./agendar.sh 07:40 10:30 12:00 >> logs/agendar.out 2>&1 < /dev/null &
  ```
  Não precisa mudar o script. Se preferir não mexer no que está rodando, ao menos confirme às 07:41 se `logs/auto.log` tem a linha "inicio: ... candidatos".
- Efeito colateral parecido dentro do script: `auto_lancamento.log()` faz `print(..., flush=True)` (`auto_lancamento.py:26`) para o pty. Se o pty sumir sem SIGHUP chegar (EIO), o `print` levanta e derruba o supervisor (ver A6).

---

## ALTO

### A1. O laço principal do `clip_watcher.py` não tem `try/except`: qualquer exceção mata o canal inteiro [confirmado a ausência; frequência do gatilho = suspeita]
- `clip_watcher.py:437-488` (laço), `:113` e `:481` (`livre_gb`), `:98-101`.
- Só `KeyboardInterrupt` é capturado (`:497`). Qualquer outra exceção cai no `finally`, o processo encerra e o canal para de gravar e de cortar. Ninguém religa (o `auto_lancamento` só religa até `--ate`, e só se o canal ainda estiver ao vivo como GTA VI).
- Fontes plausíveis em 8 h:
  1. `shutil.disk_usage("/mnt/c")` levantar `OSError` (EIO/ENOTCONN do drvfs/9p, por exemplo após o Windows suspender/hibernar). `DISCO_REF.exists()` na linha 100 não protege contra a corrida.
  2. `pos.anexar_csv(...)` (`:469`) levantar `OSError`/`csv.Error` (disco, `picos.csv` com aspas desbalanceadas por uma linha parcial de outro processo morto no meio).
  3. `pos.analisar_chat` (`:455`): rodei 20.000 casos aleatórios (emoji, `{}`/`%`/`\`, `ß`, `ŉ`, NUL, RLO, 120 caracteres) e **não** levantou nada, então esse risco é baixo.
- Correção: isolar o corpo de cada volta e a checagem de disco.
  ```python
  def livre_gb():
      try:
          alvo = DISCO_REF if DISCO_REF.exists() else PASTA
          return shutil.disk_usage(alvo).free / 1e9
      except OSError:
          return float("inf")        # não consegui medir: não para a gravação por isso
  ...
  while sessao.vivo():
      try:
          ...corpo atual da volta...
      except Exception as erro:
          print(f"erro na volta do laço (segue): {type(erro).__name__}: {erro}")
          proxima = time.time() + JANELA
  ```
  O mesmo vale para a thread do chat (`:273-296`): hoje só pega `OSError`; trocar por `except Exception`.

### A2. Sem handler de SIGTERM e filhos sem PDEATHSIG: se o python morrer sem limpeza, streamlink+ffmpeg ficam órfãos gravando sem limpeza e sem guarda de disco [confirmado a ausência; gatilho = suspeita]
- `clip_watcher.py:132-141` (Popen), `:194-206` (`encerrar`), `:565-567` (só SIGINT é religado).
- Gatilhos reais nesta máquina: `earlyoom -m 8 -s 60` está rodando (pid 176) e manda SIGTERM ao processo maior, que será um clip_watcher com o whisper carregado; também `kill <pid>`, `wsl --terminate`. SIGTERM mata o python na hora (sem `finally`). Os dois filhos continuam: o streamlink segue alimentando o ffmpeg, que segue gravando `seg_*.ts` **sem `limpar()`** (cresce ~3 GB/h por canal) e **sem a guarda de disco** (que mora no processo morto). O lock `.lock` é liberado, então o `auto_lancamento` sobe outro watcher; ele apaga a pasta do órfão (`:388-392`), o ffmpeg falha ao abrir o próximo segmento e sai, mas só nesse momento.
- Correção (poucas linhas, Linux):
  ```python
  import ctypes, os
  _libc = ctypes.CDLL("libc.so.6", use_errno=True)
  def _filho_morre_com_o_pai():
      _libc.prctl(1, signal.SIGTERM)          # PR_SET_PDEATHSIG
  # nos dois Popen e nos subprocess.run de cortar/pos: preexec_fn=_filho_morre_com_o_pai
  signal.signal(signal.SIGTERM, signal.default_int_handler)   # SIGTERM vira o mesmo desligamento limpo do Ctrl+C
  ```

### A3. Pós-produção: nenhum `timeout` nos subprocessos; um ffmpeg/whisper travado para a fila da noite toda [suspeita sobre o gatilho; o defeito é confirmado]
- `pos.py:400-413` (`ler_pcm`, `duracao_de`), `:626-630` (`fazer_vertical`), `:446` (`transcribe`), `facecam.py:70,87`; `clip_watcher.py:339` (`cortar`).
- A fila é única (`:398-400`). Se um item travar (ffmpeg lendo um mp4 truncado de um corte interrompido, whisper em laço de alucinação), todos os verticais seguintes ficam parados e `parar.sh` espera 900 s e desiste. Os `.mp4` horizontais continuam saindo (corte é outra thread), mas o produto principal (vertical) para. Mesma falha em `cortar`: um ffmpeg pendurado nunca chama `protecao.liberar` e a sessão nunca é apagada.
- Correção: `subprocess.run(..., timeout=300)` em `fazer_vertical`/`ler_pcm`/`duracao_de` (capturar `TimeoutExpired` e devolver `False`/`None`), `timeout=120` em `cortar`. Para o whisper, rodar `transcrever` com limite (thread + `join(timeout)`) ou aceitar o risco e registrar.

---

## MÉDIO

### M1. Segundo SIGINT durante o desligamento deixa o processo pendurado e o lock preso [confirmado por leitura]
- `clip_watcher.py:399-400` (`fila_pos` não é daemon), `:499-509`.
- `parar.sh` manda 1 SIGINT. O `finally` faz `t.join()` em cada corte e só depois `fila.put(None)`. Se chegar um segundo SIGINT (rodar `parar.sh` duas vezes porque "ainda terminando"; Ctrl+C duas vezes), a exceção sai do `finally` antes do `put(None)`. O interpretador então espera a thread não-daemon `fila_pos`, que está bloqueada em `fila.get()` para sempre. O processo nunca sai, o `.lock` fica preso, `multi.sh` diz "já está rodando" e o `auto_lancamento.rodando()` acha que está tudo certo.
- Correção:
  ```python
  finally:
      try:
          ...encerrar sessão, joins dos cortes...
      finally:
          fila.put(None)          # sempre, mesmo se interrompido
  ```
  e criar a thread com `daemon=True` (ou `signal.signal(SIGINT, SIG_IGN)` dentro do `finally`).

### M2. `TRAVADO_S = 90` é menor que um intervalo comercial: o watchdog reinicia a gravação no meio de um anúncio [suspeita; a causa é confirmada]
- `clip_watcher.py:74`, `:475-478`.
- O streamlink 8.6.3 filtra os segmentos de anúncio do Twitch (`plugins/twitch.py`, "Waiting for pre-roll ads to finish"; `ad=` nos segmentos), então durante o anúncio o ffmpeg não recebe dado e `lista.csv` não muda. Pods de anúncio de 120-180 s existem. Aos 90 s o laço dá `break`, cria sessão nova (que provoca novo pre-roll), **apaga o buffer inteiro da sessão antiga** (`faxina`, `:410-413`) e zera `base` (60 s sem detectar pico).
- Correção: `TRAVADO_S = 240`. Melhor ainda, só reiniciar se o `streamlink` não estiver vivo ou se passou de 240 s.

### M3. Depois de uma pausa do processo (suspensão do Windows, WSL congelado), o laço dispara uma rajada de janelas e falsos picos [confirmado por leitura]
- `clip_watcher.py:434-440`: `proxima += JANELA` sem comparar com o relógio.
- Cenário: o host dorme 3 min; ao voltar, o laço roda ~18 voltas seguidas sem `sleep`. A 1ª recebe todo o chat acumulado (que virou uma "janela" enorme: falso pico), as outras 17 recebem 0 e enchem `base` de zeros (`:472`). Com mediana 0, qualquer janela ≥ 10 msgs vira pico por 5 min.
- Correção: logo depois do `time.sleep`:
  ```python
  if time.time() - proxima > JANELA:          # ficou muito para trás: recomeça a contagem
      proxima = time.time() + JANELA
      chat.fechar_janela(); base = []
      continue
  ```

### M4. `cortar()` ignora o código de saída do ffmpeg: clipe parcial passa como sucesso [confirmado por leitura]
- `clip_watcher.py:339-345`: `check=False` e só se olha `saida.exists() and st_size > 0`. Se o ffmpeg falhar no meio (ENOSPC, segmento sumiu), o `.mp4` truncado existe com `st_size > 0`, é anunciado como "clipe pronto" e entra na fila de pós-produção. O mesmo vale para o vertical (`pos.py:631-633`, que só loga).
- Correção:
  ```python
  r = subprocess.run([...], stdin=subprocess.DEVNULL, check=False)
  if r.returncode != 0:
      saida.unlink(missing_ok=True); return False
  ```
  (também acrescentar `-nostdin` aos ffmpeg que não leem do pipe: hoje herdam o stdin do processo.)

### M5. Fila de pós-produção sem limite nem prioridade, e desligamento espera a fila inteira [confirmado por leitura]
- `clip_watcher.py:398` (`queue.Queue()` sem `maxsize`), `:504-505`.
- Medido no LEIAME: 17 s/clipe com a máquina livre; com 3 canais gravando + 3 whisper + 3 ffmpeg 1080p60 de pé o tempo sobe, e picos de DESCANSO=60 s dão até 1 pico/min/canal. Se a taxa de chegada passar a de saída, a fila só cresce (cada item é pequeno; o custo é atraso e, no `parar.sh`, esperar a fila toda, com limite de 900 s).
- Correção: ao encher (`fila.qsize() > 6`) pular o vertical `v35` e/ou descartar o item mais antigo; no SIGINT, `fila.put(None)` na frente (esvaziar com `fila.get_nowait()`) e só terminar o que está em andamento.

### M6. Acúmulo de horizontais em disco; a guarda de disco só para a gravação, nunca limpa clipes [confirmado por leitura; taxa = estimativa]
- `clip_watcher.py:70-71` (12 GB/14 GB), `:451` (nunca apaga `clipes/*.mp4`).
- Cada pico gera ~26 MB horizontal (medi 25,5-27,3 MB nos `_teste`) + vertical + `.srt/.ass/.txt`. Com 45,8 GB livres e reserva de 12 GB sobram ~34 GB, que a swap do WSL (`C:\wsl\swap.vhdx`, até 12 GB) também disputa. Isso dá ~900 picos no total antes da guarda parar a gravação. 3 canais x 8 h a 40 picos/h estoura. É improvável, mas a consequência é a pior possível: para tudo e só volta se alguém liberar espaço no C: (o vhdx não encolhe; ver B2).
- Correção barata: depois de `vertical pronto`, comprimir ou mover o horizontal original (`-c copy` já é o formato), ou subir `MINIMO`/`FATOR` nas lives de hype.

### M7. Lista de bloqueio do gancho falha em silêncio e fica vazia para sempre [confirmado por leitura]
- `pos.py:169-199`: se `filtro_gancho.txt` não abrir (caminho, permissão, edição no meio), `carregar_bloqueio` captura `OSError`, usa `linhas = []` e `bloqueio()` guarda esse resultado em cache (`_bloqueio`). Dali em diante `frase_segura`/`tem_bloqueado` deixam passar tudo (palavrão no gancho, máscara `c***` desligada), sem uma linha de log.
- Correção:
  ```python
  except OSError as erro:
      raise RuntimeError(f"filtro_gancho.txt ilegível: {erro}")   # e carregar no início do main
  ```
  e chamar `pos.bloqueio()` uma vez no `main()` para falhar na hora de subir, não no 1º pico. Hoje o arquivo existe (2334 bytes), então é risco de edição.

### M8. `auto_lancamento.py`: `rodando()` confia no pid sem checar o processo; slots nunca liberam; supervisor sem proteção [confirmado por leitura]
- `auto_lancamento.py:31-36` (`os.kill(pid, 0)`): depois de reiniciar o WSL, os PIDs recomeçam baixos; um `.pid` velho cujo número foi reaproveitado por outro processo é lido como "rodando" e o canal **nunca** é religado. `multi.sh:17-21` (`vivo`) já checa `/proc/$pid/cmdline`; `parar.sh:10` e `status.sh:7` não: `parar.sh` manda `kill -INT` para um processo qualquer com aquele número e espera 900 s.
- `auto_lancamento.py:78,80` (`--max 3`): o watcher não sai quando a live acaba nem quando o streamer troca de jogo (fica "esperando a live"), então 3 slots ocupados nunca voltam e candidato novo que abrir GTA VI não sobe. Os cortes de quem mudou de jogo continuam saindo com gancho/hashtags de GTA 6.
- `auto_lancamento.py:87`: casa título OU categoria. Título como "esperando GTA 6" numa live de Just Chatting ocupa slot.
- `auto_lancamento.py:75-97`: nenhum `try/except` na volta; uma exceção (JSON inesperado, `print` num pty morto) encerra o supervisor sem aviso (`agendar.sh` só continua dormindo até 12:00).
- Correções:
  ```python
  def rodando(canal):
      try:
          pid = int((LOGS / f"{canal}.pid").read_text().strip())
          return b"clip_watcher" in Path(f"/proc/{pid}/cmdline").read_bytes()
      except (OSError, ValueError):
          return False
  ```
  `[ -r /proc/$pid/cmdline ] && tr '\0' ' ' < /proc/$pid/cmdline | grep -q clip_watcher` em `parar.sh` e `status.sh`; `if meta is not None and not a.qualquer_jogo and 'grand theft auto vi' not in categoria.lower(): ignorar título`; e `try: ... except Exception as e: log(f"erro: {e}")` dentro do `while`.

### M9. Nome de canal sem validação + limpeza com `rmtree` no início [confirmado por leitura; improvável, destrutivo]
- `clip_watcher.py:556-557` (`ler_args`) aceita qualquer coisa que não comece com `-`; `:388-392` apaga todo subdiretório de `GRAVACOES / canal`. `./rodar.sh ..` apaga cada pasta dentro de `clipador/` (`.venv`, `clipes`, `logs`, `gravacoes`). `./rodar.sh .` apaga o buffer dos outros canais que estão rodando.
- Correção: em `ler_args`, `if not re.fullmatch(r"[a-z0-9_]{3,25}", canal): return None`; e no startup, só apagar se `velho.resolve().parent == (GRAVACOES / canal).resolve()`.

---

## BAIXO

- **B1. `--manter` não segura os segmentos da sessão viva.** `faxina()` (`clip_watcher.py:405-413`) chama `limpar()` sempre (`:409`); `manter` só impede `apagar_sessao`. O LEIAME promete "não apaga segmentos". Correção: `if s.vivo() and not manter: limpar(...)`.
- **B2. Guarda de disco nunca "retoma" sozinha por um motivo estrutural.** `clip_watcher.py:111-115,493`: a condição de volta é C: > 14 GB livres, mas o vhdx não encolhe (já avisado no LEIAME) e o `.wslconfig` não tem `sparseVhd`. Depois da parada, apagar o buffer não devolve espaço ao C:; o canal fica avisando a cada 60 s até alguém liberar espaço no Windows. Não é bug de cálculo (a conta `free/1e9` do `/mnt/c` está certa), é limite do desenho. Mitigação: `wsl --manage Ubuntu --set-sparse true` fora da noite, ou política de limpar `clipes/` antigos.
- **B3. Ctrl+C em primeiro plano atinge os ffmpeg filhos.** `cortar`/`fazer_vertical` herdam o grupo de processos do terminal, então um Ctrl+C no `./rodar.sh` encerra os ffmpeg em andamento e deixa clipes truncados com a mensagem "terminando os cortes". Com `multi.sh`+`parar.sh` (SIGINT só no python) não acontece. Correção: `start_new_session=True` nesses `subprocess.run`.
- **B4. `cortar()` pode produzir clipe de duração 0.** `pos.py:753-761`: se `ffprobe` falhar, `duracao_de` devolve 0.0, `janela_do_vertical(0, ...)` dá `(0, 0)` e o `-t 0.00` gera um mp4 vazio que passa em `st_size > 0`. Correção: `if dur_clipe <= 1: return None`.
- **B5. Clipe sem áudio:** `transcrever` levanta `IndexError` (confirmado, 3 s de vídeo mudo); está dentro do `try` (`pos.py:746-751`), então só imprime "legenda falhou" e o vertical sai sem legenda. Comportamento aceitável; só registrar que a mensagem não diz o motivo.
- **B6. `transcrever` baixa/carrega o modelo no 1º pico.** `pos.py:441-445`: se a carga falhar, `_whisper` continua `None` e **cada clipe** tenta carregar de novo. O modelo `small` está no cache (`~/.cache/huggingface/hub/models--Systran--faster-whisper-small`), então hoje só custa uns segundos no 1º clipe. Sugestão: pré-carregar no início de `pos_producao`.
- **B7. Chat: canal inexistente/renomeado não dá sinal.** `clip_watcher.py:273-296`: o JOIN em canal inexistente não devolve erro tratado, `contagem` fica 0 para sempre e nunca há pico. Correção barata: se `chat.total_recebido == 0` depois de 10 min de gravação, imprimir "chat mudo: confira o login". Mensagens vazias (`PRIVMSG #c :`) também contam (`:288-293`), pouco relevante.
- **B8. `Popen` sem `wait()` após `kill()`.** `clip_watcher.py:205-206`: sem `proc.wait()` o processo fica zumbi até o GC. Irrelevante.
- **B9. Chat/streamlink reconectam sem espera mínima.** `clip_watcher.py:422-429,437-496`: se o streamlink morrer logo depois de gravar 1 segmento, volta-se a criar sessão sem `sleep` (só o caminho "saiu antes de gravar" espera 15 s). Se houver falha repetida, cria uma conexão nova ao Twitch a cada poucos segundos. Correção: `time.sleep(5)` antes do `continue` do laço externo.
- **B10. `compilar.py`** lê `picos.csv` e considera `clipe.exists()` mesmo com o corte ainda em andamento (arquivo parcial): só rodar depois do `parar.sh`. `float('')` em `duracao()` (`:76`) derruba o script se um clipe estiver corrompido.

---

## O que testei e está OK (para não revisar de novo)

- **picos.csv com vários processos (`pos.py:686-711`):** 4 processos em paralelo x 60 linhas = 241 linhas (1 cabeçalho + 240), todas com 14 colunas, sem repetição nem linha partida; `flock` entre threads do mesmo processo também funciona (descritores diferentes). A numeração para a variante v35 é sequencial.
- **Corte por concat (`cortar`):** com ffmpeg `-f segment` igual ao do `Sessao` e um TS com offset de 5400 s (como o HLS da Twitch), os tempos do `lista.csv` saem relativos a 0 e o corte de 12 s saiu com 12,15 s e `start_time=0`. O último segmento é listado ao fechar o ffmpeg (EOF); em `+live` o arquivo é anexado a cada segmento fechado.
- **Proteção x limpeza (`Protecao`, `limpar`):** os critérios de `cortar` (`s[2] > inicio and s[1] < fim`) e de `Protecao.usa` (`seg_ini < f and seg_fim > i`) são idênticos; `pedir` roda na mesma thread que `limpar`, então não há janela entre decidir o corte e proteger. Nenhum corte lê segmento apagado.
- **Dois cortes no mesmo arquivo:** nome = canal + segundo; o descanso é de 60 s da posição gravada e cada canal é um processo (com `.lock` por canal), então dois picos do mesmo canal no mesmo segundo não ocorrem. Nome de vertical herda o stem do clipe.
- **ASS/filtro com caracteres difíceis (`pos.py:488-574,590-633`):** `{\an8}`, `a:b,c;d`, `100%`, `it's`, `[x]="q"`, emoji, `\N` dentro de palavra, palavra com `fim < ini`: o `limpo()` remove `\ { }`, o ASS é gerado e o ffmpeg renderiza OK (`True`). Canal `move_mind` (com `_`) funciona no nome do `.ass` e no `ass=nome:fontsdir=...`. Não há `drawtext` no caminho vivo (só em `compilar.py`, com `limpo()` próprio). Texto do gancho só passa por `frase_segura` (letras/`?!.,'-`), então não leva `{`/`:`/`%`.
- **Chat IRC (`Chat._ler`):** servidor falso: PING respondido com PONG, linha partida em dois `recv`, UTF-8 inválido (`\xff\xfe` vira U+FFFD, sem exceção), `:` dentro da mensagem, emoji, servidor fechando a conexão (`RECONNECT`) leva a reconexão com nick novo em 5 s. 6 mensagens contadas, nenhuma perdida.
- **Fuzz de `analisar_chat`/`gancho_ass`:** 20.000 casos, 0 exceções.
- **Vazamentos:** não achei crescimento ilimitado em 8 h (`recentes` tem `maxlen`, `base` ≤ 30, `cortes` é filtrado a cada pico, `apagados` cresce ~2.900 nomes, `protecao.faixas` é liberada no `finally`). `trava` (`.lock`) e o pipe do streamlink não são herdados pelos filhos (`close_fds` padrão, `sl.stdout.close()`).
- **`multi.sh`:** pid = o do python (setsid sem fork, `exec` no `rodar.sh`); duplicata evitada por `vivo()` (checa cmdline) e pelo `flock` do watcher; SIGINT religado em `clip_watcher.py:567` (corrige o SIGINT ignorado herdado de job em segundo plano).
- **`facecam.py` e `galeria.py`:** `decidir` nunca levanta (cai no v2 com motivo); `galeria` só lê (LOCK_SH), escreve `galeria.html` de forma atômica (`os.replace`) e captura exceções no `--assistir`.

## Ordem sugerida de correção (menor esforço primeiro)
1. C1: relançar `agendar.sh` com `setsid nohup` (ou ao menos checar às 07:41 o `auto.log`).
2. A1 (try/except + `livre_gb` seguro), A2 (SIGTERM + PDEATHSIG), M1 (`put(None)` no `finally`), M2 (`TRAVADO_S=240`).
3. M4 (returncode do corte), A3 (timeouts), M3 (rajada pós-pausa), M7/M9 (validações).
4. M8 (`rodando()` com cmdline, slots), M5/M6 (fila e disco), baixos.
