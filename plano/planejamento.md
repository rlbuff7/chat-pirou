# Planejamento: rede de canais de cortes de GTA 6

Versão de 18/11/2026, madrugada. Base: `pesquisa/` (regras, streamers, retenção, skills) e `marca/`.
Tudo marcado com [verificar] veio de fonte secundária ou incerta.

## Resumo
- **Marca:** **Chat Pirou** (`@chatpirou`). É a favorita e o único @ livre nas 6 redes (ver `marca/disponibilidade-handles.md`). A escolha final é sua.
- **Produto:** cortes dos momentos em que o chat de uma live explode, detectados e cortados automaticamente. O vertical já sai com legenda, gancho e crédito ao streamer.
- **Vantagem:** velocidade (o clipe sai uns 30 a 60 s depois do pico) e timing: até sair a versão de PC, quem joga no PC só vê GTA 6 por clipes.
- **Fases:** 1 marca na semana do lançamento → +1 ou 2 canais de nicho na semana 2 → até 5 canais em 4 a 5 semanas, cada um com conteúdo próprio.
- **Dinheiro:** nas primeiras semanas a receita esperada é zero, o foco é seguidor. A primeira receita realista vem de quem paga por corte (campanhas de clipping e acordo com streamer). Para monetizar pelas plataformas, os formatos precisam ter 1 min ou mais e voz própria.

## 1. Posicionamento
"Quem decide o que é momento é o chat." A rede não escolhe os lances no gosto, ela mostra onde o chat pirou. Isso dá:
- um critério objetivo e automático (picos do chat);
- uma identidade que serve para qualquer jogo depois do GTA 6;
- ganchos naturais, porque o próprio chat vira o texto ("O CHAT NÃO SEGUROU / KKKKK x40").

## 2. Redes e o papel de cada uma

| Rede | Papel | Formato | Ritmo na semana 1 (por conta) |
|---|---|---|---|
| TikTok | crescimento principal | vertical 20–35 s | dia 1: 2–3; depois 3–5/dia, com ≥ 2 h entre posts |
| YouTube Shorts | crescimento + funil para o canal | o mesmo vertical | 2–3/dia |
| YouTube (longo) | compilação "melhores do dia" | horizontal 5–12 min (`compilar.py`) | 1/dia |
| Instagram Reels | os melhores do dia | vertical | 1–2/dia |
| X | tempo real na noite do lançamento | clipe curto + texto | 3–6/dia nos dias de pico |
| Twitch, Kick | só reservar o @ | — | — |

Conta nova que posta muito no primeiro dia corre risco de ser tratada como spam. Comece baixo, suba se o alcance não cair, e nunca poste o mesmo vídeo em duas contas da rede.

## 3. Linhas de conteúdo
1. **Corte de pico** (automático, ~80% dos posts): um lance, 20–35 s, gancho do chat no topo, legenda palavra a palavra, crédito `twitch.tv/<canal>`.
2. **Top do dia (≥ 1 min)**: ranking de 3 a 5 lances com texto ou voz sua entre eles. É o formato que entra nos programas de monetização (o TikTok exige vídeo de 1 min ou mais; o YouTube exige valor próprio).
3. **Contexto:** "o que aconteceu na live do X", com narração sua. Original de verdade.
4. **Evitar na semana 1:** spoiler do modo história. O clipador marca esses clipes como `[revisar spoiler]`.

Critério para postar um clipe: (a) prende nos 2 primeiros segundos; (b) dá para entender sem contexto; (c) não tem spoiler de história; (d) não tem ofensa nem dado pessoal; (e) leva crédito do streamer.

## 4. A rede de canais (até 5)

| Canal | Foco | Quando abrir | Gatilho |
|---|---|---|---|
| `@chatpirou` | guarda-chuva, todos os melhores | 18–19/11 | — |
| `@chatpirou_fun` | humor e falhas | semana 2 | clipes do tipo humor/falha acima da mediana do canal principal por 5+ dias |
| `@<criador>.chatpirou` | um criador só (Davy Jones e cellbit primeiro) | pedido do dono em 19/11; plano em `plano/canais-por-criador.md` | 3+ cortes bons/dia do criador por 3 dias |
| `@chatpirou_top` | rankings e compilações de 1 min ou mais | semana 3 | compilações com retenção boa no YouTube |
| `@chatpirou_hist` | história, missões, teorias | depois de 2–3 semanas (passou o risco de spoiler) | demanda nos comentários |

Regra para abrir um canal: o anterior está postando todo dia há 7 dias **e** há conteúdo exclusivo para o novo (3 ou mais clipes por dia daquele tipo/streamer). O clipador já etiqueta cada clipe por tipo e por streamer, então a separação sai sozinha.

## 5. Rotina diária
1. O clipador grava e corta sozinho. Saem os verticais com um `.txt` de legenda sugerida ao lado.
2. Triagem rápida (você, ou eu se você pedir), pelo critério da seção 3.
3. Postar: X e TikTok na hora, Shorts em seguida, os melhores no Reels.
4. Fim do dia: `python3 compilar.py` gera a compilação + capítulos para o YouTube.
5. Anotar por post: views na 1ª hora, % assistido, compartilhamentos, seguidores ganhos. No dia 3 e no dia 7, comparar formatos e streamers e cortar o que fica abaixo da própria mediana.

## 6. Roteiro do lançamento

| Quando (BRT) | O quê |
|---|---|
| **18/11 07:40** | o clipador ligou sozinho (cellbit, stolenbr) e fez o primeiro vertical; parou às 07:42 por falta de memória no Windows. Religar pelo `LEIAME.md` |
| 18/11 manhã | você escolhe o nome, cria as contas (`marca/checklist-contas.md`) e, se quiser, posta os primeiros clipes |
| 18/11 22:30 | `./status.sh` e conferir que o PC não vai suspender; num terminal do WSL que fica aberto: `.venv/bin/python auto_lancamento.py --lista candidatos-noite.txt --ate 03:00` (ou `./multi.sh alanzoka paulinholokobr luquet4`) |
| 19/11 00:00 | lançamento no Brasil (por fuso local). Sprint de postagem até ~03:00 |
| 19/11 02:00 | live oficial no YouTube: **não cortar** (sem autorização) |
| 19/11 manhã | compilação "melhores da noite" no YouTube |
| 19–25/11 | rotina diária; avaliação no dia 3 e no dia 7 |

Canais da noite: principais `alanzoka`, `paulinholokobr`, `luquet4`; reservas `cellbit`, `jonvlogs`, `stolenbr`. Lista completa e ordem em `clipador/candidatos.txt` e `pesquisa/streamers.md`.

## 7. Dinheiro, do mais provável ao menos provável
1. **Campanhas de clipping pagas por view** (Whop, Vyro, campeonatos via Pix) e **Kick Clipping Program**. É o caminho mais curto. Saque no Brasil [verificar].
2. **Acordo direto com streamer** (canal dedicado aos cortes dele). Modelos de mensagem em `marca/mensagens-streamers.md`.
3. **YouTube YPP:** 1.000 inscritos + 4.000 h ou 10 mi de views de Shorts em 90 dias. Corte puro não monetiza, mesmo com permissão (conteúdo reutilizado). Precisa de voz ou comentário próprio. Possível mudança de requisitos em 01/02/2027 [verificar].
4. **TikTok Creator Rewards (BR):** 10 mil seguidores, 100 mil views em 30 dias, vídeos de 1 min ou mais.
5. **Instagram e X:** nada confirmado para o Brasil [verificar].

## 8. Riscos

| Risco | O que fazemos |
|---|---|
| Remoção por direitos / streamer reclamar | crédito em todo post; pedir autorização; priorizar quem autorizar; tirar do ar na hora se pedirem |
| Conteúdo "não original" (alcance baixo, sem monetização) | gancho, contexto, ranking e voz própria nos formatos ≥ 1 min |
| Spoiler derrubado / público irritado | sem história na semana 1; marcação automática `[revisar spoiler]` |
| Conta nova marcada como spam | ritmo crescente; sem vídeo repetido entre contas |
| Ofensa do chat aparecer no gancho | filtro de palavras + gancho genérico + sua revisão antes de postar |
| Disco cheio (C: com ~46 GB) | buffer rotativo (~0,5 GB por canal) e parada automática abaixo de 12 GB |
| PC suspender ou reiniciar à noite | suspensão "Nunca" na tomada; Windows Update pausado |
| Política da Rockstar ("uso não comercial") | [verificar] antes de monetizar; sem logo ou nome "GTA" na marca |

## 9. Decisões do dono (18/11, 11:20)
1. Nome: **Chat Pirou** (`@chatpirou`), confirmado. Os textos de post já saem com "| Chat Pirou" e #ChatPirou.
2. Contas: TikTok criado como @chat.pirou. Instagram e YouTube: @chat.pirou (livres às 11:45). X, Twitch e Kick: @chatpirou (sem ponto). Ordem: TikTok → Instagram → YouTube → X.
3. E-mail de contato: chatpirou924@gmail.com (já nas bios, legendas e modelos de mensagem).
4. Postar: sim, ele posta.
5. Streamers: ele diz que os streamers deixam cortar. O crédito `twitch.tv/<canal>` continua em todo post, e o clipe sai do ar se alguém pedir.
6. Skills instaladas (versões auditadas): Clip-Forge, content-skills (viral-*), youtube-agent-skill (yt-*), mais os guias da maquina-cortes-gta em `pesquisa/ref-maquina-cortes/`. O ffmpeg-skill ficou de fora.
7. Limpeza feita: caches do Notion, do uv e do npm, e instaladores velhos na Lixeira (+2,7 GB). Ficou para depois: ajustar o swap e a RAM do WSL (~8 GB) e compactar o disco do WSL (~12 GB).
8. Em aberto: etiquetar clipes com IA (Haiku via API, pago) só se a regra grátis do chat errar muito.
