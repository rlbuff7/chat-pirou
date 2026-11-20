# Um canal de cortes para cada criador

Pedido do dono em 19/11/2026, ~16:20: "montar uma estrutura pra postar para cada canal corte específico para cada criador". Pedido de novo em 20/11, ~03:30: "monte o planejamento de cada canal específico para cada criador de conteúdo de GTA e variáveis". **Nenhuma conta nova foi criada.** Este documento é o plano; as contas são do dono (senha, código, telefone).

Dados de 20/11, madrugada: coleta pública do YouTube (`clipador/virais.py`, 13 buscas, 463 Shorts de 20 canais), lives de cada criador (`yt-dlp`), o replay do chat das lives do Davy e as duas DMs de referência do dono. "Mediana" é a mediana de views dos últimos 25 Shorts do canal; o múltiplo mede quanto um vídeo superou o próprio canal.

## Resumo: em que ordem abrir

| Ordem | Criador | Por quê |
|---|---|---|
| **1ª leva** | **Lipão** | Maior público dos cinco (14,1 mi inscritos) e quase ninguém cortando ele em GTA 6. É o maior buraco. |
| **1ª leva** | **Davy Jones** | As duas referências do dono são dele e explodiram (pescaria 152 mil curtidas, sinuca 238 mil). Tem concorrência, mas o formato dele é claro. |
| 2ª leva | Paulinho o Loko | Público enorme (lives de 1,7 a 7,4 mi de views), nenhum canal de corte de GTA 6 dele apareceu nas buscas. |
| 2ª leva | cellbit | Nosso melhor Reel (~2 mil, 10x os outros), mas o YouTube já tem dois canais gigantes dele. Abrir quando ele voltar a jogar só GTA (desde 19/11 20:08 alterna com o Tenebrae Lux, outro jogo, na mesma categoria). |
| Não abrir | alanzoka | O mais disputado (Terrorzoka, Shorts from Brazuka, corvozoka, Zeltra). Fica só no guarda-chuva `@chatpirou`. |

Isso muda o plano de 19/11 (1ª leva era Davy e cellbit): o cellbit desce porque a concorrência dele no YouTube faz mediana de 103 mil, e o Lipão sobe porque ninguém ocupa o espaço.

`@chatpirou` continua como guarda-chuva: o melhor do dia de todos e as compilações por tema.

## Ficha de cada criador

### Lipão (1ª leva)

- **Onde:** YouTube `@LipaoGamer`, 14,1 mi inscritos.
- **Quando faz live:** de manhã cedo e longas (18/11 06:29 por 11,8 h; 19/11 12:48 por 9,6 h), às vezes curta à noite (18/11 19:56, 1,7 h). **Próxima já marcada: 20/11 ~09:00, "Dando FUGA em MUNDO ABERTO (Parte 4)".**
- **Público:** 1 a 3,9 mi de views por live.
- **Concorrência:** quase nenhuma. Só achamos o "GTA 6 dos Streamers BR" ("Lipão descobriu que no GTA 6 não dá pra roubar o carro do vizinho", 31 mil).
- **O que funciona:** descoberta de mecânica ("descobriu que no GTA 6 dá / não dá pra..."). As lives dele são "explorando o mundo aberto", com pouca missão de história e menos risco de spoiler. O nosso 15 (dinheiro com tinta no roubo ao banco) é desse tipo.
- **Gancho e título:** "O LIPÃO DESCOBRIU QUE..." / "DÁ PRA ... NO GTA 6?". Título sem o fim.
- **Duração:** 20 a 30 s.
- **Ferramenta:** clipador (`yt-lipaogamer`) quando a vaga estiver livre; se não, o replay do chat depois da live (ver "Ferramentas").
- **Hashtags:** `#GTA6 #lipaogamer #GTAVI #cortesdelive #ChatPirou`.
- **Crédito:** `youtube.com/@LipaoGamer`.

### Davy Jones (1ª leva)

- **Onde:** YouTube `@Gameplayrj`, 8,7 mi inscritos. O chat chama ele de "mago".
- **Quando faz live:** duas por dia, de manhã (18/11 06:31 por 11,3 h; 19/11 08:35 por 7,5 h) e no fim da tarde (18/11 17:58; 19/11 18:24, de 3 a 4 h).
- **Público:** a live de estreia fez 10,7 mi de views; as outras, de 1,1 a 3,4 mi.
- **Concorrência:**
  - "Cortes do Davy Jones [OFICIAL]": mediana de 11 mil; o melhor é "DAVY JONES NO GTA 6 KKKKKKKKKKKK", com 148 mil.
  - "Davy Jones GTA 6" e "Vice Cortes": menores.
  - A **CazéTV** também corta o Davy: a sinuca fez 238 mil curtidas em 7 h.
  - Como já existe um canal que se diz oficial, o nosso precisa deixar claro que é "canal de fã".
- **O que funciona:** **minijogo e momento fora de contexto.** As duas referências do dono são isso:
  - **Pescaria:** 14 s, sem texto, 152 mil curtidas.
  - **Sinuca:** "foi iniciar uma partida de sinuca e... IMPOSSÍVEL". O comentário do topo ("Criado em apartamento é isso aí") tem 31 mil curtidas.
  - A sinuca virou piada recorrente: na live de 19/11 à noite, o chat passou meia hora falando dela.
  - Também puxa a reação dele a detalhe do jogo ("LUCÍA OU LÚCIA?", "O QUE TEM NO FIM DO MUNDO DO GTA 6?").
- **O que não cortar:** o Davy faz muita missão de história (escavadeira, porto, corrida com o Yago, a ponte). Missão e cutscene ficam de fora na primeira semana.
- **Gancho e título:** curto, provoca sem explicar. Exemplos: "o Davy na sinuca do GTA 6...", "essa pescaria tá um pouco estranha". Pouco ou nenhum texto na tela.
- **Duração:** 10 a 20 s.
- **Ferramenta:** replay do chat (pico de "kkkk" e palavra-chave, ex.: "sinuca") e depois `yt_corte.py baixar`.
- **Hashtags:** `#GTA6 #davyjones #GTAVI #cortesdelive #ChatPirou`.
- **Crédito:** `youtube.com/@Gameplayrj`.

### Paulinho o Loko (2ª leva)

- **Onde:** YouTube `@PaulinhoLOKOoficial`, 7,8 mi inscritos (na Twitch é `paulinholokobr`).
- **Quando faz live:** 18/11 07:35 (7,4 h), 18/11 20:39 (5,1 h), 19/11 13:28 (3 h).
- **Público:** 1,7 a 7,4 mi de views por live. Vem do GTA RP, com público mais novo.
- **Concorrência:** nenhum canal de corte de GTA 6 dele apareceu nas buscas.
- **O que funciona (hipótese, falta medir):** reação exagerada e "fazendo besteira" no mundo aberto, no estilo do RP dele.
- **Gancho e título:** "O PAULINHO TENTOU ... NO GTA 6 E DEU NISSO" (formato "tentou X e deu nisso", que já funcionou com o alanzoka).
- **Duração:** 20 a 30 s.
- **Ferramenta:** replay do chat.
- **Hashtags:** `#GTA6 #paulinhooloko #GTAVI #cortesdelive #ChatPirou`.
- **Crédito:** `youtube.com/@PaulinhoLOKOoficial`.

### cellbit (2ª leva)

- **Onde:** Twitch `cellbit`.
- **Quando faz live:** nos dias 18 e 19, de manhã e à noite (ligamos o clipador às 07:40 e às 22:02 de 18/11).
- **Concorrência pesada:**
  - "Cellbit Lives": mediana de 103 mil. Destaques: "ele entrou num LOOP TEMPORAL" (968 mil) e "Cellbit encontrou algo PARANORMAL no GTA 6" (149 mil).
  - "Cellbit VODS": mediana de 56 mil. Destaque: "cellbit é o mestre das cores?" (2,2 mi).
- **O que funciona:** título em minúsculas com cara de mistério ("ele entrou num LOOP TEMPORAL", "QUE ISSO JASON...") e reação exagerada.
- **Nosso histórico:** o Reel dele fez ~2 mil, 10x os nossos outros.
- **O que não cortar:** o quebra-cabeça em preto e branco (discos, símbolos, páginas, telefone) **não é GTA 6**: é o Tenebrae Lux. Desde 19/11 20:08 ele alterna os dois jogos e deixa a categoria em GTA VI de brincadeira (escreve "(sim ainda é gta 6)" na tela). O clipador corta igual, porque decide pela categoria. Conferir o jogo no quadro antes de qualquer corte dele. Na triagem de 20/11 ~05:40, os 45 cortes depois das 20:35 eram todos do Tenebrae Lux.
- **Estratégia:** no YouTube é difícil vencer os dois canais grandes. Abrir primeiro no Reels e no TikTok, e postar rápido (até 1 h depois do momento).
- **Ferramenta:** clipador (Twitch).
- **Hashtags:** `#GTA6 #cellbit #GTAVI #cortesdelive #ChatPirou`.

### alanzoka (fica no guarda-chuva)

- **Onde:** Twitch `alanzoka`. A live de 19/11 teve 1,3 mi de pessoas.
- **Concorrência:**
  - Terrorzoka: mediana de 95 mil; "Será que arrumaram essa geladeira?" fez 3,3 mi.
  - Shorts from Brazuka: mediana de 96 mil.
  - corvozoka: canal pequeno, mas fez 98x a própria mediana com o título "Jogo: GTA 6 #alanzoka...", sem descrever nada.
  - Zeltra.
- **O que funciona:** legenda mínima ("Jogo: GTA 6") mais uma frase-meme ("Ladrão que rouba ladrão...", "A rockstar não ia deixar essa passar né").
- **Decisão:** sem canal próprio. Os melhores dele entram no `@chatpirou`, e testamos lá o formato "título que não descreve nada" (variável 3, abaixo).

## O que bombou hoje fora dos criadores (vale para o guarda-chuva)

- **Bugs e "injogável":** "Injogável?" (Gazeta, 353x a mediana), "10 PIORES BUGS DO GTA 6" (62x), "O Bug mais bizarro do GTA 6 era mentira?" (175 mil). Compilação de bugs dos nossos streamers é a vaga mais óbvia.
- **Curiosidade do jogo:** "A ROCKSTAR TEVE QUE DEIXAR O TEMPO MAIS LENTO NO GTA 6" (31x), "GTA 6 VAI SER IMPOSSÍVEL DE ZERAR" (59x), "detalhes ABSURDOS no GTA 6" (700 mil), "20 COISAS ABSURDAS QUE JÁ ACHARAM" (16x).
- **Compilação de streamers:** "MOMENTOS ENGRAÇADOS DOS STREAMERS NO GTA 6" (556 mil), "TOP 5 MOMENTOS DO PRIMEIRO DIA" (16x).
- **Pergunta que o público faz:** "Dá para trair em GTA 6?" e "COMO É ABASTECER O CARRO EM GTA 6?" (Flow Games). Combina com o "trair a Lucia" que bombou ontem.
- **Polêmica e notícia** ("O Alanzoka pode perder o canal por causa do GTA 6?", 2,2 mi): fora do nosso formato. Não fazemos.

## Variáveis

### Fixas em cada canal (vão na ficha e não mudam)

| Variável | Valor por canal |
|---|---|
| Nome e @ | `@<criador>.chatpirou` (TikTok e Instagram), `@<criador>chatpirou` (YouTube). Conferir se estão livres. |
| Nome de exibição | "Cortes do <Criador> \| Chat Pirou" |
| Bio | "Canal de fã, não oficial. Cortes das lives do <Criador>." + link da live |
| Avatar | balão do Chat Pirou na cor do canal. Nunca a foto do streamer. |
| Crédito | link do canal do criador em todo post |
| Hashtags | as 5 da ficha |
| Fonte do corte | clipador (Twitch e YouTube ao vivo) ou replay do chat (YouTube depois da live) |
| Spoiler | regra da ficha (o que não cortar) |
| Ritmo inicial | 2 a 3 posts por dia, só TikTok e Shorts; o Reels entra depois |

### Para testar (uma por vez)

- **Como testar:** cada teste dura 3 dias por canal. A régua é a mesma do yt-viral: views em 24 h divididas pela mediana do próprio canal. Também anotamos os seguidores ganhos por post.
- **Onde anotar:** no `postados.csv`, numa coluna `teste`.

| # | Variável | A | B | Por que testar |
|---|---|---|---|---|
| 1 | Gancho na tela | descoberta ("DÁ PRA... NO GTA 6") | provocação ("será que...") | os dois aparecem no topo das coletas |
| 2 | Texto na tela | gancho + legenda palavra a palavra | nenhum texto (fora de contexto) | a pescaria do Davy bombou sem texto |
| 3 | Título | descreve o momento | não descreve ("Jogo: GTA 6 #criador") | o corvozoka fez 98x sem descrever |
| 4 | Duração | 10 a 15 s | 20 a 30 s | completar o vídeo conta mais em vídeo curto |
| 5 | Caixa do título | CAIXA ALTA | minúsculas | os canais do cellbit usam minúsculas e têm a maior mediana |
| 6 | Hora do post | até 1 h depois do momento | fila no horário fixo | quem posta primeiro leva o momento |
| 7 | Legenda (CTA) | pergunta ao público | "manda pra quem..." | os comentários fazem o vídeo andar (sinuca: 31 mil curtidas no comentário) |

## Ferramentas

- **Replay do chat do YouTube (novo em 20/11):** o `yt-dlp --write-subs --sub-langs live_chat` baixa o chat inteiro de uma live que já acabou, com o segundo de cada mensagem. Contar o "kkkk" por minuto e buscar palavras ("sinuca", "bug", "injogável") acha o momento sem gravar a live. Com 8 GB de RAM e o clipador limitado a um canal, é assim que os criadores do YouTube entram. Virou o comando `yt_corte.py picos_chat URL` (20/11).
- **Clipador:** uma vaga só (8 GB). A ordem de `candidatos-8gb.txt` vale quando dois abrem live juntos; quem abre antes pega a vaga.

## O que só o dono faz

- Criar as contas, com senha, código, 2FA e telefone:
  - YouTube: canal novo (conta de marca) no mesmo Google `chatpirou924@gmail.com`.
  - Instagram: "Adicionar conta" na Central de Contas, até 5 por login.
  - TikTok: e-mail novo ou o apelido `chatpirou924+lipao@gmail.com`.
- Decidir a questão do vídeo repetido (abaixo).
- Avisar o streamer (`marca/mensagens-streamers.md`).

## Decisão pendente: o mesmo corte em duas contas?

1. **Exclusivo (recomendado):** cada corte vai para um só lugar. O `@chatpirou` fica com compilações por tema ("bugs dos streamers", "streamers tentando sinuca") e o melhor da semana.
2. **Os melhores nos dois:** o `@chatpirou` também posta o top 1 do dia de cada criador, refeito com outro gancho. As redes marcam conteúdo repetido como não original e cortam o alcance das duas contas, então o risco existe.

## Limite real

- Cada corte leva ~25 a 30 min para sair nas 3 redes pelo Chrome. Dois canais novos com 2 a 3 posts por dia em 2 redes dão 8 a 12 envios a mais por dia, o que cabe se o guarda-chuva cair para 3 ou 4 por dia.
- O Instagram derrubou a conta por checagem de robô em 19/11 com ~10 Reels por dia. Nas contas novas: no máximo 2 Reels por dia na primeira semana.

## O que muda no código e no roteiro

- `postados.csv`: colunas `conta` e `teste`. O `postagem.py hoje` passa a contar por conta.
- `postagem-automatica.md`: lista de contas, limite de cada uma e um passo antes de publicar: **conferir o @ da conta ativa**.
- Um `NN-nome.txt` por post, com a conta de destino na primeira linha.
