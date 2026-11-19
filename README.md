# Chat Pirou: máquina de cortes de lives de GTA 6

Código aberto da **Chat Pirou**, uma rede de cortes de lives de GTA 6 em português
(TikTok, YouTube Shorts e Instagram Reels). O projeto acompanha lives na Twitch e no YouTube, acha os
momentos em que o chat ou o streamer "piram", corta, gera o vídeo vertical 1080x1920 com legenda palavra a
palavra e gancho, e organiza a postagem com crédito ao streamer.

Tudo aqui foi montado e testado na semana do lançamento do GTA 6 (novembro de 2026), num notebook com
Windows 11, WSL (Ubuntu) e 16 GB de RAM, sem placa de vídeo dedicada.

> **Antes de usar:** é um projeto de fã, sem vínculo com a Rockstar Games nem com a Take-Two. Cortes são do
> conteúdo de outras pessoas: dê crédito em todo post, respeite as regras de cada plataforma e tire do ar
> na hora se o streamer pedir. Veja [Uso responsável](#uso-responsável).

---

## O que tem aqui

| Pasta | O que é |
|---|---|
| [`clipador/`](clipador/) | O robô. Grava lives da Twitch, conta o chat, corta os picos e faz a pós-produção (vertical, legenda, gancho, texto do post). Também corta lives do YouTube e pesquisa o que está viralizando. |
| [`plano/`](plano/) | Planejamento da rede, o **roteiro de postagem** passo a passo e o plano de um canal por criador. |
| [`pesquisa/`](pesquisa/) | Regras das plataformas, retenção e ganchos, streamers, o que viralizou em GTA 6 e a auditoria das skills do GitHub usadas. |
| [`marca/`](marca/) | Identidade visual (cores, fontes, avatar, banner), bios, hashtags e títulos, mensagens para streamers. |
| [`docs/`](docs/) | Como a operação roda no dia a dia com o Claude Code. |

## Como funciona

```
 Twitch (live)                                YouTube (live ou VOD)
     │ streamlink + ffmpeg                        │ yt-dlp
     ▼                                            ▼
 buffer rotativo de 10 min                    yt_corte.py
 (segmentos de 10 s, disco estável)            ├─ comentarios: minutagens que o público marcou
     │                                          ├─ audio + reacoes: picos de voz e risada do streamer
 chat por IRC anônimo (sem conta)              ├─ baixar: só o trecho (ou pedaços, se a live acabou de acabar)
     │ pico = muitas msgs vs. mediana           └─ vertical: mesma pós-produção do clipador
     ▼
 clip_watcher.py corta ~35 s em volta do pico
     ▼
 pos.py: tipo do momento (humor, susto, história...), gancho tirado do chat,
         legenda com faster-whisper, recorte vertical 1080x1920, crédito do canal, .txt do post
     ▼
 triagem humana (galeria.html / postagem.py ver) → conferência de spoiler → texto → postagem
     ▼
 postagem.py registrar / hoje / limpar (registro dos links e limpeza do que já saiu)

 virais.py: Shorts de GTA 6 mais vistos da semana, medidos pelo múltiplo da mediana do próprio canal
```

**Por que o chat:** numa live, o momento bom quase sempre aparece primeiro no chat (spam de "KKKKK",
"OMG", emote). O `clip_watcher.py` conta mensagens em janelas de 10 s e marca pico quando passa de
`FATOR` vezes a mediana dos últimos 5 minutos. Lives do YouTube não têm esse chat fácil, então o
`yt_corte.py` usa o **áudio**: volume do streamer contra a mediana dos 5 minutos em volta e um detector
simples de risada. Ele transcreve só os picos para você ler o que aconteceu sem assistir horas de live.

## Instalação, passo a passo

Testado em Ubuntu 24.04 no WSL 2 (Windows 11). Em Linux puro funciona igual. Em Windows sem WSL, não.

1. **WSL e Ubuntu** (no PowerShell do Windows, como administrador): `wsl --install -d Ubuntu`.
   Reinicie e abra o Ubuntu.
2. **Pacotes do sistema:**
   ```bash
   sudo apt update && sudo apt install -y git ffmpeg python3-full nodejs
   ```
   O `nodejs` serve ao yt-dlp (decifra os links do YouTube).
3. **Código:**
   ```bash
   git clone https://github.com/rlbuff7/chat-pirou.git ~/gta6-cortes
   cd ~/gta6-cortes/clipador
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```
4. **Configuração local** (só se for usar o `postagem.py` com pastas do Windows):
   ```bash
   cp local.conf.example local.conf   # e troque <seu usuario do Windows>
   ```
   O `local.conf` fica fora do git.
5. **Testes:**
   ```bash
   .venv/bin/python pos.py --teste      # pós-produção
   .venv/bin/python facecam.py --teste  # recorte da webcam (opcional)
   ./rodar.sh --teste                   # deve imprimir "ok"
   ```
6. **Primeiro corte de verdade** (qualquer canal ao vivo da Twitch):
   ```bash
   ./rodar.sh nome_do_canal --demo      # força um corte depois de ~90 s
   ```
   O vertical sai em `clipes/verticais/<canal>/`.

> **Memória:** cada canal gravando usa até ~1 GB de RAM com o modelo de legenda carregado. Com 16 GB,
> grave no máximo 2 canais ao mesmo tempo. **Disco:** o buffer ocupa ~0,5 GB por canal e não cresce.
> O guarda de disco para de gravar abaixo de 12 GB livres.
>
> **Processos longos:** rode o clipador com `setsid nohup ... &` num terminal que fica aberto, não como
> tarefa de fundo de um assistente ou IDE, que pode ser encerrada e levar o clipador junto.

## Uso

### Lives da Twitch (`clipador/`)

```bash
./multi.sh canal1 canal2                 # um processo por canal, em segundo plano
./status.sh                              # quem está gravando, picos, clipes, espaço livre
./parar.sh [canal]                       # para e termina os cortes pendentes
.venv/bin/python auto_lancamento.py --lista candidatos.txt --ate 03:00 --max 2   # liga sozinho em quem estiver em GTA VI
./galeria.sh                             # gera clipes/galeria.html para escolher os melhores
.venv/bin/python compilar.py             # compilação do dia para o YouTube
```

Para calibrar a sensibilidade (`--fator`, `--minimo`), veja [`clipador/LEIAME.md`](clipador/LEIAME.md).

### Lives do YouTube (`clipador/yt_corte.py`)

```bash
.venv/bin/python yt_corte.py comentarios URL               # minutagens citadas nos comentários
.venv/bin/python yt_corte.py audio URL canal-live1          # baixa só o áudio (7 h ≈ 300 MB)
.venv/bin/python yt_corte.py reacoes clipes/yt/canal/canal-live1.m4a --n 30   # top 30 reações, com a fala
.venv/bin/python yt_corte.py baixar URL 1:57:15 2:01:15 canal-momento        # só o trecho
.venv/bin/python yt_corte.py varrer clipes/yt/canal/canal-momento.mp4         # folha de quadros para conferir
.venv/bin/python yt_corte.py vertical ARQUIVO canal youtube.com/@canal "LINHA 1 DO GANCHO" "LINHA 2"
```

Se a live acabou há poucos minutos, o YouTube ainda não montou o vídeo ("post_live"). Nesse caso o
`baixar` busca sozinho só os pedaços de ~5 s do trecho pedido.

### O que está viralizando (`clipador/virais.py`)

```bash
.venv/bin/python virais.py --canais 15 --por-canal 30
```

O script busca Shorts de GTA 6 da semana (só páginas públicas, sem login) e pega os últimos Shorts de cada
canal. Cada vídeo é medido pelo **múltiplo da mediana do próprio canal**: um vídeo de 100 mil views num
canal que costuma fazer 1 mil vale mais como ideia que 1 milhão num canal que faz 1 milhão. O resultado e
a leitura dos formatos estão em [`pesquisa/virais-gta6.md`](pesquisa/virais-gta6.md).

### Postagem (`clipador/postagem.py`)

```bash
.venv/bin/python postagem.py candidatos --horas 6    # melhores clipes ainda não postados
.venv/bin/python postagem.py ver CLIPE               # 4 quadros + a fala, para conferir spoiler
.venv/bin/python postagem.py refazer CLIPE "LINHA 1" "LINHA 2"   # gancho escrito à mão
.venv/bin/python postagem.py preparar VIDEO NN-nome  # comprime para < 9,5 MB e copia para a pasta de envio
.venv/bin/python postagem.py registrar NN-nome CLIPE tiktok LINK
.venv/bin/python postagem.py hoje                    # quantos posts por rede hoje
.venv/bin/python postagem.py limpar --executar       # apaga os vídeos dos posts que já saíram nas 3 redes
```

O envio em si é feito no navegador, conta logada pelo dono, seguindo o
[roteiro de postagem](plano/postagem-automatica.md). O projeto **não** usa robô de upload, login
automático nem API não oficial. Veja [`docs/operacao-com-claude-code.md`](docs/operacao-com-claude-code.md).

## O que aprendemos sobre alcance (resumo)

Detalhes e números em [`pesquisa/virais-gta6.md`](pesquisa/virais-gta6.md) e
[`pesquisa/retencao-e-ganchos.md`](pesquisa/retencao-e-ganchos.md).

- **Curto:** 20 a 30 s, um momento só.
- **O gancho não conta o fim.** Formatos que funcionam:
  - descoberta: "TEM UM PS5 DENTRO DO GTA 6", "TEM O MAPA DO GTA 5 DENTRO DO GTA 6";
  - provocação: "Será que arrumaram essa geladeira?";
  - promessa contra o que aconteceu: "jurou que ia jogar na moral… e".
- **Curiosidade com guia:** a legenda diz como achar ("no quintal da casa do Jason tem um barco…") e fecha
  com uma pergunta.
- **Temas que puxam:** easter eggs e detalhes do mapa, bugs, bichos, tentar repetir cena do trailer,
  compilação de vários streamers no mesmo tema.
- **Crédito do streamer em todo post**, sem emoji demais e com 5 hashtags fixas
  ([`marca/hashtags-e-titulos.md`](marca/hashtags-e-titulos.md)).

## Uso responsável

- **Crédito sempre:** o vertical já sai com `twitch.tv/<canal>` ou `youtube.com/@canal` na tela, e o texto
  do post repete o crédito.
- **Pedido do streamer é lei:** se o criador pedir, o corte sai do ar na hora. Modelos de mensagem estão em
  [`marca/mensagens-streamers.md`](marca/mensagens-streamers.md).
- **Spoiler:** nada de história na primeira semana. O clipador marca `[revisar spoiler]` e o roteiro
  manda conferir os quadros antes de postar.
- **Regras das plataformas:** resumo em [`pesquisa/regras-plataformas.md`](pesquisa/regras-plataformas.md).
  Corte puro não costuma monetizar (conteúdo reutilizado).
- **Música:** o rádio do jogo pode gerar reivindicação de Content ID. Reivindicação só de música, sem strike
  e sem limite de alcance, foi aceita. Qualquer outra, o post para.

## Segurança

- **Nenhuma senha, token, cookie ou chave de API neste repositório**, e o código não pede nenhuma.
  - O chat da Twitch é lido por IRC anônimo (`justinfan`).
  - O yt-dlp e o `virais.py` só leem páginas públicas, sem login.
- O `.gitignore` bloqueia vídeos, áudios, gravações, logs, `.env`, cookies e o `local.conf`.
- Contas das redes: senha, 2FA e códigos ficam só com o dono, num gerenciador de senhas. Ver
  [`marca/checklist-contas.md`](marca/checklist-contas.md).
- **Ferramentas de terceiros:** o que foi avaliado está em [`pesquisa/skills-github.md`](pesquisa/skills-github.md).
  Ficou de fora o que manda vídeo para nuvem ou pede chave paga.
- Se achar um problema de segurança, abra uma *issue* sem colocar dado sensível nela.

## Licença

Código sob [MIT](LICENSE) (exceções em [NOTICE.md](NOTICE.md)): pode usar, copiar, modificar e distribuir, inclusive comercialmente, desde que
mantenha o aviso de copyright. **Sem garantia:** o software é fornecido "no estado em que se encontra".

Ficam de fora da MIT:
- as fontes, sob licença OFL (`clipador/fontes/LICENCA.txt`);
- o material de referência em `pesquisa/ref-maquina-cortes/`, sob MIT de outro autor;
- a marca Chat Pirou.

GTA e Rockstar Games são marcas de seus donos.

## Créditos

- [streamlink](https://github.com/streamlink/streamlink), [yt-dlp](https://github.com/yt-dlp/yt-dlp),
  [FFmpeg](https://ffmpeg.org/), [faster-whisper](https://github.com/SYSTRAN/faster-whisper) e
  [OpenCV](https://opencv.org/).
- Fontes [Anton](https://fonts.google.com/specimen/Anton) e
  [Montserrat](https://fonts.google.com/specimen/Montserrat).
- Os streamers, que fazem o conteúdo de verdade.
