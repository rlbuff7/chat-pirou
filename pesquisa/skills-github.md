# Skills e ferramentas do GitHub para os canais de cortes de GTA 6

Pesquisa somente leitura feita em 18/11/2026. Nada foi clonado, instalado ou executado: só busca no GitHub (`gh search`, `gh api`) e leitura de arquivos de texto soltos (SKILL.md, README, scripts de instalação, código Python/JS) baixados para uma pasta temporária e lidos como dado.

Estrelas e datas são de 18/11/2026. "Último commit" é a data do commit mais recente na branch padrão. Estrelas são um sinal fraco: três repositórios têm crescimento ou proporção estranha (ver "Alertas gerais").

## Tabela resumo

| Nome | Estrelas | Último commit | Serve para | Risco | Recomendação |
|---|---:|---|---|---|---|
| [lowdevco/Clip-Forge](https://github.com/lowdevco/Clip-Forge) | 57 | 2026-11-13 | Cortes de gameplay: acha momentos por som/movimento, layout facecam + jogo, hook, legenda ASS animada, punch-in, slowmo, corta silêncio. Tudo em ffmpeg + ASS | baixo | **instalar** |
| [pedroxcardoso/maquina-cortes-gta](https://github.com/pedroxcardoso/maquina-cortes-gta) | 44 | 2026-11-12 | Skill feita para cortes de GTA 6 em pt-BR: escolha de ganchos com nota, metade streamer/metade vídeo, legenda palavra a palavra (Remotion), SFX | baixo | **instalar** (com ressalvas de licença do Remotion e de conteúdo) |
| [vyralcontent/content-skills](https://github.com/vyralcontent/content-skills) | 249 | 2026-06-22 | Ganchos, CTAs, legendas e regras de TikTok, Reels e Shorts (só texto/markdown) | baixo | **instalar** |
| [Jakeschincariol/youtube-agent-skill](https://github.com/Jakeschincariol/youtube-agent-skill) | 6.322 | 2026-09-16 | Nota de gancho, lint de título + thumbnail, leitor de retenção (CSV do Studio), Shorts, capítulos; 6 scripts Python sem dependência | baixo | **instalar** |
| [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) | 7.824 | 2026-11-18 | 42 ferramentas ffmpeg com contrato fixo: loudness, silêncio, reframe, legenda, export e checagem por plataforma | baixo (muito código) | **instalar** (opcional, via git com SHA fixo) |
| [AgriciDaniel/claude-shorts](https://github.com/AgriciDaniel/claude-shorts) | 425 | 2026-04-10 | Pipeline longo→short: faster-whisper, rubrica de nota, reframe com MediaPipe, ajuste de borda de corte por áudio | baixo | só inspirar |
| [sergebulaev/youtube-skills](https://github.com/sergebulaev/youtube-skills) | 101 | 2026-10-27 | Títulos "honestos", brief de thumbnail, roteirista de gancho | baixo-médio | só inspirar (ou instalar só 3 pastas, sem `lib/`) |
| [WyattBlue/auto-editor](https://github.com/WyattBlue/auto-editor) | 5.971 | 2026-11-18 | Cortar silêncio/parada por áudio ou movimento; traz 5 skills próprias | baixo-médio | instalar (opcional) |
| [francozanardi/pycaps](https://github.com/francozanardi/pycaps) | 234 | 2026-09-30 | Legenda animada por palavra com CSS; aceita nossa transcrição (SRT/JSON) | baixo-médio | instalar (opcional, alpha, pesado na CPU) |
| [remotion-dev/skills](https://github.com/remotion-dev/skills) | 7.446 | 2026-11-16 | Skills oficiais do Remotion (legendas estilo TikTok, SRT, transcrição) | baixo | só inspirar (só vale se adotarmos Remotion) |
| [Edualnog/medusa-clip](https://github.com/Edualnog/medusa-clip) | 24 | 2026-06-23 | Cortes de gameplay: detecção de facecam (YuNet), karaokê, hooks, fusão de sinais | médio | só inspirar (AGPL; evitar o .exe) |
| [RafaelGodoyEbert/ViralCutter](https://github.com/RafaelGodoyEbert/ViralCutter) | 482 | 2026-09-10 | Cortes em pt-BR: WhisperX, legenda estilo Hormozi, face tracking | médio | só inspirar (GPL-3.0) |
| [appariciojunior/video-editor-skills](https://github.com/appariciojunior/video-editor-skills) | 462 | 2026-10-23 | Só conhecimento (DaVinci): números de pacing, limpeza de legenda em pt-BR | baixo | só inspirar (licença CC BY-NC) |
| [kamilstanuch/Autocrop-vertical](https://github.com/kamilstanuch/Autocrop-vertical) | 466 | 2026-02-15 | 16:9 para 9:16 com YOLOv8 + ffmpeg | baixo | só inspirar (sem licença) |
| [Vibha-Ramprakash/claude-caption-styles](https://github.com/Vibha-Ramprakash/claude-caption-styles) | 20 | 2026-11-12 | 7 estilos de legenda animada (Chrome + ffmpeg) | baixo | só inspirar (feito para talking head) |
| [Vibha-Ramprakash/claude-video-effects](https://github.com/Vibha-Ramprakash/claude-video-effects) | 1.037 | 2026-11-12 | 51 efeitos para talking head (botão Seguir, lean-in) | baixo | só inspirar |
| [NaufalRizqullah/opensource-clipping](https://github.com/NaufalRizqullah/opensource-clipping) | 316 | 2026-11-13 | Clipper completo (face tracking, karaokê, B-roll, uploaders) | médio | só inspirar |
| [0jc1/py-autovod](https://github.com/0jc1/py-autovod) | 32 | 2026-11-01 | Baixa live, corta com IA, sobe sozinho | médio | só inspirar |
| [paullabs/edit-labs-ai](https://github.com/paullabs/edit-labs-ai) | 91 | 2026-11-08 | Plugin pt-BR: cortes de podcast, colagem, Vox; recomenda Higgsfield | médio | evitar (sem licença) |
| [opus-pro/opus-skills](https://github.com/opus-pro/opus-skills) | 35 | 2026-10-16 | Skill oficial do OpusClip (nuvem) | médio-alto | evitar |
| [ChatCut-Inc/agent-plugin](https://github.com/ChatCut-Inc/agent-plugin) | 1.056 | 2026-11-12 | Editor hospedado via MCP | alto | **evitar** |
| [oil-oil/oil-cover](https://github.com/oil-oil/oil-cover) | 302 | 2026-11-16 | Capas/thumbnails via API paga (foco chinês) | médio-alto | evitar |
| [digitalsamba/claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit) | 2.634 | 2026-11-17 | Produção de vídeo (voz IA, Runpod/Modal, Remotion) | médio | evitar (outro caso de uso) |
| [hassancs91/claude-youtube-editor](https://github.com/hassancs91/claude-youtube-editor) | 384 | 2026-11-05 | Talking head para Remotion + upload no YouTube | médio | evitar (outro caso de uso) |
| [jianfch/stable-ts](https://github.com/jianfch/stable-ts) | 2.282 | 2026-05-30 | Timestamps por palavra do Whisper | baixo | evitar (repositório arquivado) |
| [m-bain/whisperX](https://github.com/m-bain/whisperX) | 25.437 | 2026-11-12 | Alinhamento por palavra, diarização | baixo | só inspirar (o faster-whisper já dá `word_timestamps`) |
| Listas "awesome-claude-skills" (ComposioHQ 79.757; travisvn 15.857; BehiSecc 10.449) | — | push 2026-09-18 / 04-28 / 11-02 | Índices de links, sem curadoria de segurança | médio | só inspirar (não instalar em massa) |

Triados só por metadados e varredura, sem leitura a fundo: [FujiwaraChoki/supoclip](https://github.com/FujiwaraChoki/supoclip) (3.465, AGPL-3.0, webapp Docker estilo OpusClip), [linzzzzzz/openclip](https://github.com/linzzzzzz/openclip) (580, MIT), [iart-ai/tiktok-video-skills](https://github.com/iart-ai/tiktok-video-skills) (28, MIT, só markdown + 3 scripts .sh), [Breakthrough/PySceneDetect](https://github.com/Breakthrough/PySceneDetect) (5.550, BSD-3), [lay295/TwitchDownloader](https://github.com/lay295/TwitchDownloader) (4.077, MIT, baixa/renderiza chat de VOD), [ClipsAI/clipsai](https://github.com/ClipsAI/clipsai) (575, MIT, parado desde 01/2024), [unconv/captacity](https://github.com/unconv/captacity) (141, MIT, parado desde 06/2024).

## Alertas gerais de segurança e confiança

1. **"Cole isto no Claude: instale esta skill".** Jakeschincariol e Clip-Forge propõem isso no README. Na prática o agente baixa e roda um instalador que ninguém leu. Instale sempre à mão, com `git clone` + `git checkout <SHA>` (SHAs abaixo, os mesmos que eu li) e só depois copie.
2. **`npx skills add ...` e `/plugin marketplace add ...` pegam o HEAD sem fixar versão.** O conteúdo de uma skill é instrução para o agente; se o autor mudar depois, muda o que o agente faz. O pacote do npm também pode diferir do GitHub (não verifiquei os tarballs).
3. **Estrelas suspeitas.** `youtube-agent-skill` (6.322 estrelas, 1.793 forks) e `ffmpeg-skill` (7.824 estrelas) têm menos de 3 meses de vida; `Autocrop-vertical` tem 1.973 forks para 466 estrelas. Não investiguei a origem. Julgue pelo código, não pelo número.
4. **Clones em massa.** A busca por "awesome claude skills" traz dezenas de repositórios com nomes tipo `r08-composiohq-awesome-claude-skills-seo` e contagens de estrelas quase idênticas (50 a 56). Parecem derivados automáticos; não confie.
5. **Listas awesome.** Sem licença, com patrocinadores no topo do README (Atlas Cloud, APIMart) e sem revisão de segurança dos itens listados.
6. **Hardware.** O Clipador roda em CPU (8 núcleos, faster-whisper `small`). Remotion e pycaps renderizam com Chromium e custam minutos por clipe; ffmpeg + ASS custa segundos. Isso pesa mais que estrelas na escolha.
7. **Idioma.** Quase todas as heurísticas de gancho/título (listas de palavras vagas, fórmulas) estão em inglês. Funcionam como esqueleto; a tradução e o ajuste para pt-BR são nossos.
8. **Direitos.** Cortar live de terceiro e postar tem risco de política de conteúdo reutilizado e de direitos autorais, independente da ferramenta. O próprio Clip-Forge avisa para pedir permissão. A skill de GTA usa por padrão o trailer da Rockstar como metade de baixo. Vale cruzar com `regras-plataformas.md`.

## Auditorias detalhadas

Método: lista de arquivos do repositório, leitura de SKILL.md, README, scripts de instalação e dos scripts que tocam rede/shell, e varredura por padrões (curl/wget com pipe, `eval/exec/shell=True`, base64, POST/upload, chaves e variáveis de ambiente, caminhos sensíveis como `.ssh`/`.aws`/cookies, instruções do tipo "não conte ao usuário", telemetria, domínios externos). Nenhum conteúdo lido foi tratado como instrução.

### 1. lowdevco/Clip-Forge — baixo risco

- **Dados:** 57 estrelas, 2 forks, criado em 13/11/2026 (5 dias), último commit 2026-11-13, licença MIT, commit lido `c548c0860105`.
- **O que faz:** skill com os comandos `/clip-gameplay`, `/clip-podcast`, `/clip-video`, `/clip-sports`, `/clip-tutorial`, `/clip-edit`. No modo gameplay (`references/gameplay.md`): `scout.py` ranqueia trechos por som e movimento e conta mudanças no kill feed (região ROI); `analyze_audio.py` acha gritos e risadas do streamer; `render.py` (35 KB) monta o clipe com layouts `auto|speaker|center|blur|split|stack`, hook com palavras de destaque (`*assim*`), legenda ASS em 4 estilos (`bold|clean|neon|fire`), beats com punch/shake/flash, slowmo, `tighten` (corta silêncio > 0,7 s), loudnorm e marca d'água. `faces.py` e `track.py` usam YuNet + OpenCV para achar e seguir a facecam. Efeitos sonoros são sintetizados com numpy (`sfx.py`), sem baixar áudio.
- **Encaixe no nosso pipeline:** usa o mesmo caminho técnico do `clip_watcher.py` (ffmpeg + ASS + faster-whisper em CPU). Duas formas de uso: (a) rodar a skill sobre os `clipes/*.mp4` horizontais para gerar a versão "editada" (facecam em cima, jogo embaixo, hook, legenda com destaque, punch-in no pico); (b) ler `build_ass()` e o cálculo de crop em `render.py` e portar para `fazer_vertical()`. Para GTA 6 não há kill feed: use o scout sem `--roi` e o `analyze_audio.py` para achar a reação.
- **Instalação (NÃO executei):** ver "Top 5". Dependências Python do README: `opencv-python numpy yt-dlp faster-whisper`. Use um venv separado, porque o Clipador fixa `av==16.0.1` e `faster-whisper==1.2.1`.
- **Segurança:**
  - `tools/build.py --install` só copia arquivos para `~/.claude/skills/{clip-forge,clip-gameplay,clip-podcast,clip-video}` (apaga a pasta de destino de mesmo nome antes). Sem rede.
  - Rede só em: `fetch.py` (yt-dlp), `transcribe.py` (baixa modelo sherpa-onnx de `github.com/k2-fsa/sherpa-onnx/releases`, só se o faster-whisper não existir), `check_setup.py` (HEAD em sites para saber se há internet) e `assets/pc/get_video.bat` (yt-dlp, para uso no Claude chat).
  - Sem `curl | sh`, sem `eval/exec`, sem base64, sem chave de API, sem telemetria, sem instrução escondida para o agente. A SKILL manda perguntar antes de instalar coisas no PC.
  - Dois `.onnx` versionados no repositório: calculei o sha256 e são idênticos, byte a byte, aos do OpenCV Zoo (`2023mar` = `8f2383e4...2fa4`, igual ao hash que o medusa-clip fixa; `2026may` = `ebafce4e...f0f0`).
  - Ressalvas: repositório muito novo e de autor único (divulga um perfil de Instagram); legenda de download padrão `en.*,ml.*` no `fetch.py` (irrelevante para nós); o `render.py` não foi lido linha a linha, só o cabeçalho, a lógica de ASS e as chamadas de subprocess (todas ffmpeg/ffprobe).

### 2. pedroxcardoso/maquina-cortes-gta — baixo risco

- **Dados:** 44 estrelas, 8 forks, criado em 12/11/2026, último commit 2026-11-12, MIT, commit lido `4381b0ca90ee`.
- **O que faz:** transforma vídeo de streamer/podcast em 3 a 5 cortes 9:16 sobre GTA 6, estilo metade streamer (em cima) e metade vídeo/gameplay (embaixo). O Claude lê a transcrição e escolhe os cortes com a rubrica de `references/ganchos.md` (nota 0 a 10: lacuna de curiosidade 0-3, fato específico 0-2, conflito/opinião 0-2, entra direto, payoff, se entende sozinho; descarta abaixo de 6; "penalize promessa que o corte não cumpre"). Legenda palavra a palavra em caixa alta com a palavra falada em amarelo, corte de pausas, zoom nos cortes, popups com imagem, SFX, marca d'água, final "Seguir → Seguindo". Edição em Remotion; transcrição com whisper.cpp.
- **O que mais vale aqui:** `references/estilo-referencias.md` traz números medidos de vídeos de referência: plano de 1,5 a 2,7 s com zoom 100%↔120% sem swoosh, pausa entre frases > 0,3 s vira 0,2 s, mix final em cerca de −14 LUFS com pico ≤ −1 dBTP, menos de 15 efeitos por 35 s, 3 layouts alternando. Também sugere ler o gráfico "mais reproduzido" do YouTube para achar o pico de retenção.
- **Encaixe:** os clipes horizontais do Clipador entram como `source`. Como já temos faster-whisper, dá para usar só a parte de edição e os guias de gancho; o motor Remotion pesa em CPU.
- **Instalação (NÃO executei):** ver "Top 5". O instalador instala o motor (Remotion 4.0.543, versões exatas, no `package.json`), baixa o Chrome headless do Remotion e whisper.cpp 1.5.5 com o modelo `small`.
- **Segurança:**
  - `install.sh`/`install.ps1`: copiam a skill para `~/.claude/skills/` (apagam pastas de mesmo nome) e chamam `scripts/setup.mjs`. O `.ps1` sugere `-ExecutionPolicy Bypass` só para o próprio arquivo local.
  - `setup.mjs`: `npm install` na pasta `~/.maquina-cortes-gta/engine`, `npx remotion browser ensure`, `@remotion/install-whisper-cpp`. Escreve só em `~/.maquina-cortes-gta`. Confere (não instala) ffmpeg e yt-dlp.
  - Chaves opcionais: `ELEVENLABS_API_KEY` (usada só contra `api.elevenlabs.io`, gera 3 efeitos curtos, gasta crédito) e `GOOGLE_API_KEY`/`GOOGLE_CSE_ID` (busca de imagens pela API oficial). Sem elas, pula. A SKILL diz "nunca peça nem escreva a chave no chat" e "não use cookies do navegador sem ele pedir".
  - Sem `curl | sh`, `eval`, base64, telemetria ou instrução escondida. `sound-effects` é cópia de terceiros (glebis, MIT) declarada em `THIRD_PARTY.md`.
  - Ressalvas: (1) **Remotion não é MIT**: é grátis para pessoa física e empresa com até 3 funcionários; acima disso exige licença paga. (2) A SKILL sugere automatizar o YouTube (Playwright + `agent-reach`) para ler o "mais reproduzido": é cinza em termos de ToS; ignore essa parte. (3) Usa por padrão o trailer da Rockstar e imagens do Google como material: direitos. (4) Apaga e recria `~/.claude/skills/sound-effects` se já existir.

### 3. vyralcontent/content-skills — baixo risco

- **Dados:** 249 estrelas, 36 forks, último commit 2026-06-22, MIT, commit lido `349e495d9702`.
- **O que faz:** 7 skills em markdown: `viral-hooks` (hook em 3 camadas visual/verbal/texto, arquétipos, anti-padrões), `viral-short-form`, `viral-short-form-ideas`, `viral-tiktok-content`, `viral-youtube-shorts`, `viral-instagram-reels` (inclui diagnóstico de flop), `viral-captions-and-ctas`. O texto admite que não prevê viralização e lista "clickbait sem payoff" como anti-padrão.
- **Encaixe:** base para os ganchos, textos na tela e CTAs de cada plataforma; combina com a rubrica de `maquina-cortes-gta`.
- **Segurança:** só `.md` e `assets` de texto; zero scripts. Domínio externo apenas `vyralcontent.com` (divulgação). Sem instrução oculta nem pedido de chave. Em inglês.

### 4. Jakeschincariol/youtube-agent-skill — baixo risco

- **Dados:** 6.322 estrelas, 1.793 forks, criado e último commit em 2026-09-16 (um único dia de commits), MIT, commit lido `a2feb2104981`, 32 KB, 24 arquivos.
- **O que faz:** 11 skills (`yt-script`, `yt-package`, `yt-edit`, `yt-comment`, `yt-plan`, `yt-viral`, `yt-retention`, `yt-shorts`, `yt-seo`, `yt-chapters`, `yt-audit`) e 6 scripts Python sem dependência: `hookscore.py` (painel de 5 propriedades em 21 fórmulas de gancho), `title.py` (limites de 60/40 caracteres, thumbnail com no máximo 3 palavras que não repete o título, teto de 2 palavras em caixa alta), `deadair.py` (lista de cortes a partir de SRT), `retention.py` (lê o CSV de retenção do Studio e aponta vazamento de gancho, "penhascos" e declive, com a fala daquele segundo), `chapters.py`, `swipe.py`.
- **Encaixe:** é a parte de "retenção" e "título/thumbnail como um par". Depois de publicar, exporte a curva de retenção de cada Short e rode `retention.py` para ver em que segundo o público sai. Passe os ganchos candidatos por `hookscore.py`. O README admite que o score é heurística calibrada em 74 hooks e não prevê resultado.
- **Segurança:** os scripts só usam `json/re/csv/os/sys/statistics` e abrem arquivos locais; nenhuma chamada de rede, `subprocess` ou `eval`. O README diz que nada publica e nada toca credenciais. `yt-viral` manda coletar listagens públicas (pode usar `yt-dlp --flat-playlist`) e "nunca sessão logada". Lê o arquivo opcional `~/.claude/youtube/voice.md`. Domínios externos: `opusjake.ai` (site do autor). Ressalvas: crescimento de estrelas anômalo; listas de palavras e fórmulas em inglês.

### 5. kajisho5/ffmpeg-skill — baixo risco, mas enorme

- **Dados:** 7.824 estrelas, 727 forks, criado em 03/09/2026, último commit 2026-11-18, MIT, versão 3.11.1, commit lido `07c84812bb6b`.
- **O que faz:** instalador (`bin/install.js`) copia `SKILL.md`, `scripts/`, `templates/`, `mcp/` para `~/.claude/skills/ffmpeg-skill`. 42 ferramentas em Python (stdlib): `cut`, `silence` (inclui `--filler`), `scenes --highlights`, `caption`, `fit`/`crop`/`cropdetect` (reframe), `loudness`, `export`/`render` com `templates/` (`tiktok.json`, `youtube-shorts.json`, `reels.json`...), `check.py --platform` (confere duração, proporção, fps, loudness) e `look.py` (contact sheet para o agente olhar). Fluxo "medir primeiro, verificar no fim", sempre `--dry-run`. Declara explicitamente que não decide "o que é interessante" nem composição de thumbnail.
- **Encaixe:** dá ao Claude uma camada ffmpeg determinística (loudness para −14 LUFS, validação do vertical antes de postar, corte de silêncio) sem ele improvisar comandos. Não substitui o `clip_watcher.py`; é ferramenta de pós.
- **Segurança:** li `bin/install.js`, `SKILL.md`, `PRIVACY.md`, `server.json`, `mcp/server.py` (só biblioteca padrão e módulos locais) e varri os 60+ scripts `.py`: nenhum `urllib/requests/socket/http`. O PRIVACY diz que não há telemetria nem chave; a única rede é a do motor de transcrição que você mesmo instalar (baixa modelo). O MCP é stdio local. O `.claude/settings.json` do repositório habilita plugins da Trail of Bits, mas só vale se você abrir a pasta clonada no Claude Code: **não abra o clone no Claude Code**. A `.claude/skills/*` do repositório são skills de desenvolvimento do próprio projeto e não vão no payload do instalador. Ressalvas: o plugin oficial é montado em uma branch `plugin` por CI (não auditei essa branch; por isso recomendo o instalador a partir do `main` fixado por SHA); base de ~3 MB de Python que não li inteira; crescimento de estrelas anômalo.

### 6. AgriciDaniel/claude-shorts — baixo risco

- **Dados:** 425 estrelas, 85 forks, último commit 2026-04-10 (push em 07/2026), MIT, commit `a369fad9d842`.
- **O que faz:** skill interativa `/shorts` em 10 passos: faster-whisper, detecta tipo de conteúdo, Claude pontua 8 a 12 trechos por rubrica (gancho 0,30; coerência isolada 0,25; intensidade emocional 0,20; densidade de valor 0,15; payoff 0,10), `snap_boundaries.py` ajusta bordas de corte para pontos naturais do áudio, `compute_reframe.py` reenquadra com MediaPipe (rosto) ou cursor, legenda Remotion (Bold/Bounce/Clean), export por plataforma.
- **Segurança:** `setup.sh` cria venv e instala `torch` (índice oficial pytorch.org), `faster-whisper`, `mediapipe`, `numpy`, `opencv-python` (versões em faixa `>=`, sem fixar) e `npm install` do Remotion; `install.sh` só copia arquivos (usa `rsync`). Scripts só chamam ffmpeg/ffprobe via subprocess; nenhuma rede nem chave. Sem instrução oculta.
- **Encaixe:** a rubrica ponderada e o ajuste de borda por áudio valem ouro para os nossos cortes por pico de chat (o clipe pega 20 s antes e 5 s depois; começar na frase certa melhora a retenção). O reframe é pensado para talking head; para facecam em canto, o Clip-Forge se encaixa melhor. Remotion pesa na CPU.

### 7. sergebulaev/youtube-skills — baixo-médio

- **Dados:** 101 estrelas, último commit 2026-10-27, MIT.
- **O que faz:** 9 skills (`yt-title-optimizer`, `yt-thumbnail-brief`, `yt-hook-scripter`, `yt-description-writer`, `yt-repurposer`, `yt-content-planner`, `yt-channel-optimizer`, `yt-audience-insights`, `yt-community-post-writer`). Pontos bons: título "não pode prometer mais do que os primeiros 30 s entregam", mínimo de 3 variantes, thumbnail com até 4 palavras que não repete o título, cartão de aprovação antes de qualquer ação. Traz `references/untrusted-content.md` (conteúdo buscado é dado, nunca instrução) e scripts de verificação de segredos.
- **Segurança:** a pasta `lib/` tem clientes para **Publora** (publicar em redes, chave `PUBLORA_API_KEY`), **Pixfaro** (geração de imagem paga) e **YouTube Data API** (chave gratuita, só leitura de comentários/estatísticas). Sem chaves, nada sai da máquina. Há funil comercial (links para Publora e para a agência do autor). Se instalar, copie só `skills/yt-title-optimizer`, `skills/yt-thumbnail-brief` e `skills/yt-hook-scripter` (mais `references/`), sem `lib/`, e nunca defina essas chaves.

### 8. WyattBlue/auto-editor — baixo-médio

- **Dados:** 5.971 estrelas, 744 forks, criado em 2020, último commit 2026-11-18, Unlicense (domínio público), commit `689097a6857f`.
- **O que faz:** CLI em Nim que corta "espaço morto" por volume (`--edit audio:-30dB`), movimento (`--edit motion`), preto ou palavra na legenda; `--margin` para respiro; exporta para Premiere/Resolve/Final Cut/EDL ou `clip-sequence`. Repositório traz 5 skills (`skills/auto-editor*`).
- **Encaixe:** tirar pausas e silêncio dos clipes antes do vertical (reduz tempo morto sem mexer no pipeline). Alternativa mais leve: `silence`/`tighten` do ffmpeg-skill ou do Clip-Forge.
- **Segurança:** **não está mais no pip.** A instalação oficial é baixar um binário da página de Releases (`auto-editor-linux-x86_64` etc.), **sem assinatura e sem checksum publicados** ("ignore os avisos de desenvolvedor desconhecido", diz a documentação). Não instale pelo pip (versão antiga abandonada). Os `SKILL.md` que li são documentação de uso, sem instruções ocultas. Os `curl | bash` achados são do CI (Homebrew) do próprio repositório, não do usuário final. Alternativa mais segura: compilar a partir do código (`nimble`), o que exige toolchain Nim.

### 9. francozanardi/pycaps — baixo-médio

- **Dados:** 234 estrelas, último commit 2026-09-30, MIT, alpha, commit `e2d36edfa08e`.
- **O que faz:** legendas animadas escritas em CSS (classe `.word-being-narrated`), animações, efeitos (emoji, máquina de escrever, SFX), tags por palavra. CLI: `pycaps render --input v.mp4 --template minimalist --transcript t.json` (aceita `whisper_json`, `pycaps_json`, `srt`, `vtt`).
- **Encaixe:** troca a legenda ASS simples do `fazer_vertical()` por legenda palavra a palavra com destaque, reaproveitando a transcrição que o Clipador já gera. Custo: renderiza cada legenda com Chromium (Playwright), lento em CPU.
- **Segurança:** o README promove a API hospedada tscaps.io (envia vídeo para nuvem; não use). O renderer padrão baixa o Chromium via `playwright install chromium`; a primeira execução baixa modelo Whisper. A opção `[fast]` usa Google Cloud Speech-to-Text (evite). `ai/gpt.py` lê `PYCAPS_OPENAI_API_KEY` opcional para marcar palavras com IA (manda texto ao OpenAI; deixe sem chave). A instalação é `pip install git+https://...` (sem PyPI): fixe o SHA.

### 10. Itens "só inspirar" lidos com menos profundidade

- **Edualnog/medusa-clip** (24 estrelas, 2026-06-23, AGPL-3.0): motor Python `medusacut` bem estruturado (`signals/fusion.py` junta energia de áudio, movimento e cena; `reframe/facecam.py` acha a webcam com YuNet baixado com sha256 fixado; `caption/karaoke.py`; `hooks/`; `thumbnail.py`). **Risco médio:** o aplicativo é distribuído como `.exe/.dmg/.AppImage` **sem assinatura** (o README manda `iwr ... -OutFile ...; .\MedusaClip.exe`) e o julgamento "multimodal" envia frames e transcrição ao provedor de LLM escolhido (OpenRouter/OpenAI/Anthropic) com a sua chave. Leia o código `agent/src/medusacut` para copiar ideias; não rode o instalador. AGPL: copiar código para um serviço exige abrir o seu.
- **RafaelGodoyEbert/ViralCutter** (482, 2026-09-10, GPL-3.0): autor brasileiro, WhisperX, legendas "Hormozi" com destaque por palavra, auto-crop 9:16, split de 2 pessoas, tradução de legenda, exporta XML para Premiere. **Médio:** `install_dependencies.bat` roda `irm https://astral.sh/uv/install.ps1 | iex` (instalador conhecido do `uv`, mas é pipe para shell com `ExecutionPolicy ByPass`); `scripts/transcribe_cuts.py` usa `subprocess.run(..., shell=True)`; usa chave Gemini/GPT opcional; exige Visual C++ Build Tools. Bom para ler o estilo de legenda e o pipeline em pt-BR.
- **appariciojunior/video-editor-skills** (462, 2026-10-23, **CC BY-NC 4.0**): zero código, só método para DaVinci Resolve Studio. `vlog-pacing` traz números úteis (silêncio < −43 dB por ≥ 0,25 s; margens de palavra −0,08 s/+0,12 s; zoom alternando 100%/107,5%; punch-in 115% só na punchline) e `captions` traz regras de limpeza em português (cê → você, tá → está, "né" → "não é"). Licença não comercial: use as ideias, não copie o texto para um canal monetizado.
- **kamilstanuch/Autocrop-vertical** (466, 2026-02-15, sem licença): 7 arquivos, YOLOv8 + ffmpeg, `pip install -r requirements.txt`; varredura limpa. Sem licença = sem direito de reuso; só ler.
- **Vibha-Ramprakash/claude-caption-styles** (20) e **claude-video-effects** (1.037): MIT segundo o README (o GitHub marca a licença como "outra", pois o arquivo `LICENSE` não é detectado; confira o texto antes de reutilizar). Estilos de legenda renderizados via Chrome local + ffmpeg (as fontes vêm do Google Fonts na hora do render) e efeitos que seguem o rosto (YuNet MIT + MediaPipe Apache-2.0, `.onnx`/`.tflite` versionados). Pensados para talking head; os dois têm funil para um estúdio pago do autor.
- **NaufalRizqullah/opensource-clipping** (316): traz uploaders automáticos para YouTube e Facebook (tokens OAuth), chave Gemini, `gdown` e donation links. Evite automatizar upload com ferramenta de terceiros.
- **0jc1/py-autovod** (32): baixa lives (Twitch, Kick, YouTube), corta com IA via OpenRouter e sobe com `youtubeuploader`; `install.sh` usa `sudo`. Só como referência de arquitetura.
- **remotion-dev/skills** (7.446, 2026-11-16, o GitHub não detectou licença): oficial; `remotion-captions/` explica exibir legendas estilo TikTok, importar SRT e transcrever. Só markdown e utilitários de build; sem achados. Útil se um dia adotarmos Remotion.

### 11. Itens a evitar

- **ChatCut-Inc/agent-plugin** (1.056, Apache-2.0): editor hospedado em `chatcut.io`/`api.chatcut.io` (envia mídia à nuvem deles). **Alto:** as skills mandam o agente rodar `irm https://chatcut.io/install.ps1 | iex` e buscar um guia remoto com `curl -fsSL https://chatcut.io/desktop` e "segui-lo". É instrução remota mutável dentro da skill: o servidor deles pode mudar o que o agente faz.
- **opus-pro/opus-skills** (35, MIT): skill oficial do OpusClip. Exige `OPUSCLIP_API_KEY` (plano pago), sobe o vídeo para a nuvem e inclui `copy-video-style/scripts/telemetry.mjs`, que envia eventos anônimos ao Mixpanel (documentado, com `OPUSCLIP_NO_TELEMETRY=1` para desligar). Contraria o nosso "custo zero" e envia gravações de terceiros para fora.
- **paullabs/edit-labs-ai** (91): **sem licença**; 598 arquivos, 129 MB; baixa pacotes `.zip` da própria release (`editlabs-assets`) e cria ambientes Python com `rembg`; README traz link afiliado do Higgsfield. A parte `corte-viral` (decupagem, uso da legenda automática do YouTube) é interessante em pt-BR, mas sem licença não podemos reaproveitar.
- **oil-oil/oil-cover** (302, licença não declarada): gera capas com API paga (ZenMux), com um servidor local de interface de credenciais. Foco em plataformas chinesas. Não serve.
- **digitalsamba/claude-code-video-toolkit** (2.634, MIT) e **hassancs91/claude-youtube-editor** (384, MIT): dependem de serviços pagos ou nuvem (ElevenLabs, Runpod/Modal e Ideogram no primeiro; ElevenLabs, fal.ai, AssemblyAI, Notion e upload ao YouTube no segundo, vários opcionais); o primeiro sugere `curl -LsSf https://astral.sh/uv/install.sh | sh` no README. São para vídeo narrado, não para cortes de live.
- **jianfch/stable-ts**: arquivado em 2026-05; use `word_timestamps=True` do faster-whisper.

## Top 5 para aprovar

Comandos para você rodar depois de aprovar, em um terminal do mesmo ambiente onde o Claude Code roda (WSL se for ele). Cada um fixa o SHA que eu li. Os clones vão para `~/skills-src/` (fora do projeto). **Não abra essas pastas clonadas no Claude Code.** Se o SHA ficar para trás, releia o diff antes de avançar.

### 1. lowdevco/Clip-Forge (57 estrelas, risco baixo)

Por quê: é a única que trata gameplay + facecam de forma nativa e usa ffmpeg + ASS, o mesmo caminho do Clipador, sem Chromium nem nuvem. Entrega hook, legenda com destaque, punch-in, slowmo, corte de silêncio e checagem de loudness.

```bash
git clone https://github.com/lowdevco/Clip-Forge ~/skills-src/Clip-Forge
git -C ~/skills-src/Clip-Forge checkout c548c0860105
python3 ~/skills-src/Clip-Forge/tools/build.py --install
# dependências, em venv separado do Clipador (ele fixa av==16.0.1 e faster-whisper==1.2.1):
python3 -m venv ~/skills-src/clipforge-venv
~/skills-src/clipforge-venv/bin/pip install opencv-python numpy faster-whisper
```

### 2. pedroxcardoso/maquina-cortes-gta (44 estrelas, risco baixo)

Por quê: é a skill mais parecida com o nosso nicho: pt-BR, GTA 6, ganchos com nota e estilo de edição medido em vídeos de referência (ritmo, pausa, loudness). Ressalvas: Remotion pede licença paga acima de 3 funcionários; renderiza devagar em CPU; trate trailer da Rockstar e imagens do Google como risco de direitos; ignore a parte de automatizar o "mais reproduzido" com Playwright.

```bash
git clone https://github.com/pedroxcardoso/maquina-cortes-gta ~/skills-src/maquina-cortes-gta
git -C ~/skills-src/maquina-cortes-gta checkout 4381b0ca90ee
bash ~/skills-src/maquina-cortes-gta/install.sh
# só os guias, sem motor: cp -r ~/skills-src/maquina-cortes-gta/skills/maquina-cortes-gta/references ~/gta6-cortes/pesquisa/ref-maquina-cortes/
```

### 3. vyralcontent/content-skills (249 estrelas, risco baixo)

Por quê: só markdown, MIT, cobre gancho, texto na tela, CTA e regras de TikTok/Reels/Shorts, com aviso explícito contra clickbait sem payoff. Cobre o item "ganchos que não enganam" sem executar nada.

```bash
git clone https://github.com/vyralcontent/content-skills ~/skills-src/content-skills
git -C ~/skills-src/content-skills checkout 349e495d9702
mkdir -p ~/.claude/skills && cp -r ~/skills-src/content-skills/skills/* ~/.claude/skills/
```

### 4. Jakeschincariol/youtube-agent-skill (6.322 estrelas, risco baixo)

Por quê: dá a parte de retenção que falta: ler o CSV de retenção do Studio e dizer em que segundo o público sai, nota de gancho e lint de título + thumbnail como par. Os 6 scripts são Python puro e sem rede. Heurísticas em inglês: adaptar. Desconfie das estrelas.

```bash
git clone https://github.com/Jakeschincariol/youtube-agent-skill ~/skills-src/youtube-agent-skill
git -C ~/skills-src/youtube-agent-skill checkout a2feb2104981
cp -r ~/skills-src/youtube-agent-skill/skills/yt-* ~/.claude/skills/
mkdir -p ~/.claude/youtube && cp ~/skills-src/youtube-agent-skill/templates/voice.md ~/.claude/youtube/voice.md
```

### 5. kajisho5/ffmpeg-skill (7.824 estrelas, risco baixo, volume alto)

Por quê: dá ao Claude uma camada ffmpeg determinística (loudness, silêncio, reframe, `check --platform` antes de postar) sem rede e sem chave. Opcional: só traz valor se o Claude for operar ffmpeg além do que o `clip_watcher.py` já faz. Instalação pelo instalador do repositório, não pelo `npx`, para não depender do tarball do npm.

```bash
git clone https://github.com/kajisho5/ffmpeg-skill ~/skills-src/ffmpeg-skill
git -C ~/skills-src/ffmpeg-skill checkout 07c84812bb6b
node ~/skills-src/ffmpeg-skill/bin/install.js
# exige Python 3.10+ e FFmpeg 6.1+; verificar depois: python3 ~/.claude/skills/ffmpeg-skill/scripts/_contract.py doctor
```

Fora do top 5, mas boas para uma segunda rodada: `AgriciDaniel/claude-shorts` (rubrica de nota e ajuste de borda de corte), `francozanardi/pycaps` (legenda animada por palavra, se aceitarmos o custo em CPU) e `WyattBlue/auto-editor` (corte de silêncio; binário sem assinatura).

## Lacunas

- **Thumbnails:** não achei nada específico para gaming que valha instalar. O que há é brief em texto (sergebulaev, Jakeschincariol) ou geração por API paga (oil-cover). Para o nosso caso, extrair o frame do pico com ffmpeg e compor com Pillow é mais simples; os guias de brief dessas skills ajudam a decidir o que colocar.
- **Detecção por pico de chat da Twitch:** já temos. As referências achadas (`hougesen/twitch-highlight-finder`, `xurei/twitch-highlights-logger`, 9 e 34 estrelas) são menores e mais velhas que o nosso `clip_watcher.py`.
- **Não verifiquei:** conteúdo dos pacotes npm/PyPI (só os repositórios), branches além da padrão, histórico de commits em busca de código removido, nem a veracidade das estrelas.
