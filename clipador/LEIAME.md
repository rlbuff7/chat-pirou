# Clipador

Acompanha lives da Twitch, conta o chat e corta cada pico de mensagens. Para cada pico saem:
o clipe horizontal de 35 s (`.mp4` original, sem reencode, é ele que vai para a compilação), a legenda
`.srt` em português, uma versão vertical 1080x1920 pronta para Shorts/Reels/TikTok (gancho no topo, legenda
palavra a palavra, crédito `twitch.tv/<canal>`) e um `.txt` com título, legenda e hashtags do post.
Ver "Pós-produção" abaixo.

## Na noite do lançamento

Tudo de dentro de `~/gta6-cortes/clipador/` (no Windows: `\\wsl.localhost\Ubuntu\home\<usuario>\gta6-cortes\clipador\`).

```bash
./rodar.sh --teste                      # deve imprimir "ok"
./multi.sh canal1 canal2 canal3         # sobe um processo por canal, em segundo plano
./status.sh                             # como está cada canal + espaço livre no C:
tail -f logs/canal1.log                 # acompanhar um canal
./parar.sh                              # no fim: Ctrl+C em todos e espera terminar cortes/verticais
python3 compilar.py                     # melhores momentos do dia (hoje, top 10)
```

Pode subir os canais antes da live abrir: cada processo espera o canal ficar no ar e começa
sozinho. Se a live cair, ele espera e grava num buffer novo.

## Como funciona o buffer (por que o disco não enche)

O streamlink manda o vídeo para o ffmpeg, que grava segmentos de 10 s em
`gravacoes/<canal>/<sessao>/seg_NNNNNN.ts` e escreve `lista.csv` com início e fim de cada um.
Segmentos com mais de `BUFFER_S` (600 s) são apagados, menos os que algum corte pendente ainda vai usar.
Cada canal ocupa cerca de 0,5 GB (1080p60) e fica estável, em vez de ~3 GB por hora.

- A posição do corte vem do tempo dos segmentos (`lista.csv`), nunca do relógio. O relógio só
  é usado se ainda não existir nenhum segmento (aparece "aviso: ... usando o relógio" no log).
- Guarda de disco: a cada minuto olha o espaço livre do C: (`/mnt/c`, é onde o disco virtual do WSL
  cresce). Abaixo de 12 GB para de gravar e imprime um aviso grande com `!!!`; só volta acima de 14 GB.
  Nada fora de `gravacoes/` é apagado.
- `--manter` não apaga segmentos (só use com muito disco: ~3 GB por hora por canal).
- Aviso: o disco virtual do WSL (ext4.vhdx) nunca encolhe sozinho. Espaço apagado no Linux é
  reaproveitado pelo próprio WSL, mas o C: só recupera se alguém compactar o vhdx.

## Calibrar FATOR e MINIMO

Uma janela de chat (10 s) vira pico quando tem pelo menos `MINIMO` mensagens **e** pelo menos `FATOR` vezes a
mediana das últimas 30 janelas (5 min). Valores no topo de `clip_watcher.py`, ou por canal na linha de comando
sem editar nada: `./multi.sh canal --fator 4 --minimo 15`.

- Corta demais (clipes sem graça): suba `FATOR` (4, 5) e/ou `MINIMO`.
- Corta de menos / perde lance: desça `FATOR` (2,5, 2) ou `MINIMO` (canal pequeno: 4 ou 5).
- Mude um valor por vez, olhe `clipes/picos.csv` (mensagens, mediana da base, frases mais ditas) e
  compare com o que realmente aconteceu na live.
- Entre dois picos do mesmo canal há 60 s de descanso (`DESCANSO`).
- O clipe pega `ANTES`=20 s antes da janela do pico e `DEPOIS`=5 s depois (o chat reage depois do lance).

## O que cada arquivo faz

| Arquivo | Função |
|---|---|
| `rodar.sh CANAL [--demo] [--manter] [--buffer N] [--fator X] [--minimo N] [--layout facecam]` | um canal, em primeiro plano; `--demo` força um corte após ~90 s (teste) |
| `multi.sh C1 C2 ... [opções do rodar.sh]` | um processo por canal em segundo plano (log em `logs/<canal>.log`, PID em `logs/<canal>.pid`); não sobe duplicado; opções repassadas a todos |
| `parar.sh [CANAL]` | Ctrl+C e espera terminar cortes, legendas e verticais pendentes (até 15 min) |
| `status.sh` | por canal: vivo e desde quando, picos/clipes/verticais, último pico, buffer, espaço livre do C: |
| `compilar.py [AAAA-MM-DD] [--top N] [--incluir-demo]` | compilação do dia, ver abaixo |
| `clip_watcher.py` | o programa principal (docstring tem o uso) |
| `pos.py` | pós-produção (tipo, gancho, pico de áudio, vertical, legenda, `.txt` de post); `./rodar.sh` não o chama, mas `.venv/bin/python pos.py CLIPE.mp4 --canal X [--mais "kkkkk x40 \| omg x12"] [--msgs 85] [--completo] [--layout facecam]` refaz a pós-produção de um clipe que já existe; `pos.py --teste` roda só os testes dele |
| `facecam.py` | acha a webcam do streamer (OpenCV) e devolve o recorte do layout facecam; `.venv/bin/python facecam.py CLIPE.mp4 --canal X` mostra a decisão; `facecam.py --teste` roda só os testes dele |
| `filtro_gancho.txt` | lista de bloqueio do gancho (palavrões, ofensas, ódio, spam); um termo por linha, editável |
| `fontes/` | Anton (gancho) e Montserrat ExtraBold (legenda, crédito), usadas pelo ffmpeg sem instalar nada |
| `requirements.txt` | versões do .venv (o `av` precisa ser 16.0.1; o OpenCV, 4.x, só serve ao layout facecam) |

## Onde saem os arquivos

- `clipes/<canal>-AAAAMMDD-HHMMSS.mp4` e `.srt`: clipe horizontal e legenda
- `clipes/verticais/<canal>/<nome do clipe>_<tipo>_<v22|v35>.mp4`: vertical pronto (junto: `.ass` da
  legenda e `.txt` com o post pronto)
- `clipes/picos.csv`: um registro por pico (horário, mensagens, mediana, posição gravada x relógio, frases mais ditas,
  `tipo`, `variante` e `gancho`)
- `clipes/facecam/<canal>.json` e `clipes/facecam/decisoes.csv`: cache da webcam por canal e o registro de cada decisão
  do layout facecam (usou, ou caiu no v2 e por quê); só existem se o `--layout facecam` for usado
- `clipes/verticais.csv`: um registro por vertical (`t_pico_audio_s`, `ini_s` e `dur_s` do recorte, `pos_producao_s`)
- `../conteudo/compilacoes/AAAA-MM-DD-topN.mp4` e `.txt` (capítulos no formato YouTube + créditos dos canais)
- `gravacoes/`: só o buffer temporário; `logs/`: um log por canal

`compilar.py` ranqueia por `mensagens / max(mediana_base, 1)`, pega os N melhores clipes horizontais
que ainda existem, ordena por horário e junta em 1920x1080 60 fps com cartela de 1,5 s
("CORTE n" e canal) entre eles. Cortes de `--demo` ficam de fora, a menos que use `--incluir-demo`.

## Pós-produção (onda 2)

Especificação: `../pesquisa/retencao-e-ganchos.md` (seção 2 e mapa do quadro). Tudo no `pos.py`.

- **Tipo do corte** (grátis, só pelo texto do chat nos últimos 15 s): `humor` (kkk, lol, lmao, risadas),
  `falha` (F, rip, morreu, nooo), `hype` (pog, poggers, omg, caraca, hype, `!!!`), `susto` (susto, aaaa, credo,
  socorro), `historia` (spoiler, cutscene, história, final, trama) e `geral`. A categoria com mais mensagens
  (mínimo 3 e 10% da janela) vence; história basta 2 mensagens (é a que mais pede olho humano). Vai na coluna `tipo`,
  no nome do vertical e no `.txt`.
- **Gancho** (faixa de cima, caixa alta, até 2 linhas, Anton): linha 1 do modelo do tipo ("O CHAT NÃO SEGUROU"),
  linha 2 amarela com a frase do chat e quantas vezes ("KKKKK x40"). A frase só entra se passar no filtro:
  sem link, `@`, comando de bot (`!`), número longo, emote-código ilegível, mais de 4 palavras e sem nenhum
  termo de `filtro_gancho.txt`. Risada sempre sai padronizada como `KKKKK`. Sem frase segura, entra o modelo genérico
  do tipo com os números do próprio log ("O CHAT EXPLODIU / 85 MSGS EM 10 s"); em `historia` nunca aparece frase do
  chat (pode ser spoiler); com o chat quase parado (`--demo`) sai "MOMENTO CLIPADO / AO VIVO NA TWITCH". Nome de
  usuário nunca é lido nem mostrado. Os modelos ficam em `MODELOS_FRASE` e `MODELOS_GENERICOS` no `pos.py`;
  o texto é medido com a própria fonte e encolhe de 84 para 64 px antes de desistir.
- **Layout 1080x1920** (margens seguras: nada nos 270 px de cima nem abaixo de y = 1440, texto a 164 px das bordas):
  crédito `twitch.tv/<canal>` em y 272 (pequeno, 70% opaco, o clipe todo), gancho em y 330 a ~560, vídeo 16:9 inteiro em
  y 576 a 1184 sobre o fundo desfocado e 10% mais escuro, legenda a partir de y 1244 (no máximo 2 linhas, nunca invade o vídeo).
- **Legenda palavra a palavra**: blocos de até 4 palavras e 2 linhas (quebra também em pausa maior que 0,7 s), um evento
  ASS por palavra, a falada em amarelo `#FFD400` e as outras em gelo. Palavrão forte (termos com `!` no filtro) vira `c***`
  nos primeiros 7 s do vertical. O `.srt` do clipe de 35 s continua sendo gerado como antes.
- **Recorte ancorado no pico de áudio**: dentro do clipe, acha a janela de 0,5 s com mais volume entre 18 e 34 s (se não
  houver pico claro, usa 28 s) e o vertical fica com 22 s: 14 s antes do pico e o resto depois, sem passar do começo nem do
  fim. **1 em cada 4 verticais** (o 4º, 8º... pico do `picos.csv`, qualquer canal) sai com os 35 s inteiros, `v35`, como
  controle A/B; os outros são `v22`. A variante está no nome do arquivo e na coluna `variante`.
- **`.txt` do post** ao lado de cada vertical: título para Shorts, legenda de TikTok/Reels e descrição do YouTube com o
  crédito ao streamer (modelo de `../marca/legendas-e-hashtags.md`) e as hashtags do tipo. Quando o tipo é `historia`
  vem marcado `[revisar spoiler]`. `[MARCA]` e a URL do vídeo original ficam para preencher; o texto assume GTA 6.
- Não implementado (itens 5, 6 e 9 da pesquisa): punch-in no pico, barra de progresso, teaser de abertura, fade de áudio.
  O item 8 (layout B, facecam) existe como opção: ver abaixo.

Tempo medido (WSL, 8 núcleos, máquina livre, clipe 1080p): 17 s por clipe `v22` (legenda ~6 s, vertical ~12 s) e 26 s
no `v35` com fonte de 60 fps.

### Layout facecam (opcional, item 8 da pesquisa)

O layout v2 continua o padrão. `--layout facecam` (em `rodar.sh`, `multi.sh` e no `pos.py` avulso) troca o vertical por:
gancho e crédito onde estão no v2, faixa do rosto em y 576 a 936 (a webcam recortada, ampliada para 640x360 e nítida
no meio da própria imagem desfocada), fio magenta, e o jogo recortado do centro em y 936 a 1440, ocupando a largura
toda; a legenda cai sobre a parte de baixo do jogo (y 1244, mesma posição do v2). O vertical sai com `_fc` no nome.

```bash
./multi.sh canal1 canal2 --layout facecam          # ao vivo, só para esses canais
.venv/bin/python pos.py clipes/canal-AAAAMMDD-HHMMSS.mp4 --canal canal --layout facecam   # refaz um clipe já cortado
```

- Como acha a webcam (`facecam.py`): 6 quadros do clipe, Haar cascade do próprio OpenCV (`cv2.data.haarcascades`, nada é
  baixado), rosto que aparece em pelo menos metade dos quadros, pequeno (até 22% da largura) e com o centro a no máximo 25%
  da borda mais próxima (webcam é overlay de canto ou lateral; rosto grande no meio é foto, IRL ou personagem).
  Recorte 16:9 centrado no rosto, com 3 vezes a largura dele.
- Sem rosto confiável o clipe sai no layout v2 sozinho; o motivo vai para o log ("facecam: sem webcam confiável, ficou
  no layout v2: ...") e para `clipes/facecam/decisoes.csv`. Também cai no v2 se o OpenCV não estiver instalado.
- Cache por canal em `clipes/facecam/<canal>.json`: os clipes seguintes só conferem em 3 quadros se o rosto continua
  no recorte; se a confiança cair (1 de 3), recalcula. "Sem webcam" vale por 20 min; o recorte positivo, por 12 h.
  Apague o `.json` para forçar a redetecção.
- Custo medido: +0,5 s (cache) a +1,5 s (detecção nova) e cerca de +2 a 4 s no ffmpeg por clipe, máquina com outras cargas.
- Limites: o recorte não enxerga a borda da caixa da webcam (usa 3x a largura do rosto), então em webcam pequena pode sobrar
  um filete do jogo ou de fundo; o jogo perde ~8% em cima e embaixo (a legenda cobre o HUD de baixo); se a webcam também
  aparece no jogo recortado, ela se repete pequena. Só um rosto por canal (o mais estável perto da borda). O
  `auto_lancamento.py`/`agendar.sh` seguem no v2: para facecam ao vivo, suba os canais com `multi.sh ... --layout facecam`.

## Limites conhecidos

- Só Twitch (chat por IRC anônimo, sem conta). O pico é medido pelo chat, não pelo vídeo.
- O corte copia o stream (rápido, sem perda), então começa no keyframe anterior: o início pode vir até ~2 s antes.
- O "agora" é o fim do último segmento fechado mais o que já correu do aberto; o erro é de ~1 s.
  Há ainda o atraso natural entre vídeo e chat (alguns segundos), coberto pelo `ANTES`.
- O streamlink 8 já pula os anúncios (a flag `--twitch-disable-ads` foi desativada); a gravação
  fica um pouco mais curta que o relógio a cada intervalo, e por isso nada usa o relógio para cortar.
- Se uma live fica sem segmento novo por 90 s, a gravação é reiniciada (buffer novo).
- Pós-produção numa fila só: ~17 s por clipe (26 s no `v35` de 60 fps), com a máquina livre.
  Com muitos picos em vários canais a fila pode atrasar (o clipe horizontal sai na hora). O vertical é 30 fps.
- A primeira legenda baixa o modelo `small` (~0,5 GB); o `faster-whisper` roda na CPU (8 núcleos).
- Legenda em português forçado: fala em outro idioma sai traduzida de forma estranha. Ruído/música pode gerar texto solto.
- Cuidado com outros programas pesados em paralelo: o encode do vertical usa vários núcleos.
