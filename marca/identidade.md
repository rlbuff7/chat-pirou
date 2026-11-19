# Identidade: visual, legenda, tom de voz e ganchos

Atualizado em 18/11/2026. Vale para as 3 favoritas (Chat Pirou, Foi Clipado, Pico do Hype): a paleta e as regras são as mesmas, só muda o símbolo do avatar.

## 1. Direção visual

**Conceito: o sinal do pico.** O elemento gráfico da marca é uma linha de onda que sobe de repente (o gráfico do chat disparando). Aparece no avatar, no banner, na capa e como barra fina nos vídeos. Fundo escuro, um amarelo de alerta para o que importa, um magenta para o "pico".

**O que evitar de propósito:** logo, letras e artes oficiais de GTA 6 ou da Rockstar, e o degradê de pôr do sol rosa e laranja que é a cara do jogo. A paleta usa magenta, mas sempre chapado sobre carvão. Isso reduz risco de marca e de parecer canal oficial, e deixa a identidade servir para outros jogos.

### Paleta

| Papel | Nome | Hex | Uso |
|---|---|---|---|
| Fundo | Carvão | `#0B0B12` | fundos de capa, avatar, banner, texto sobre amarelo e magenta |
| Superfície | Grafite | `#1A1A24` | cartões, faixas de crédito, barras |
| Texto | Gelo | `#F5F7FA` | texto principal, legenda |
| Destaque principal | Amarelo sinal | `#FFD400` | palavra-chave da legenda, palavra do gancho, logo |
| Destaque do pico | Magenta pico | `#FF2E88` | barra de pico, setas, selo "PICO" |
| Apoio | Ciano elétrico | `#19E3FF` | links, @, detalhes pequenos |
| Alerta | Vermelho spoiler | `#FF3B30` | selo SPOILER |
| Seguro | Verde sem spoiler | `#22D47B` | selo SEM SPOILER |

Proporção sugerida em peça: 60% carvão/grafite, 25% gelo, 10% amarelo, 5% magenta/ciano.

### Contraste (calculado)

| Combinação | Razão | Pode usar para |
|---|---|---|
| Gelo sobre carvão | 18,3:1 | qualquer texto |
| Amarelo sobre carvão | 13,7:1 | qualquer texto |
| Ciano sobre carvão | 12,6:1 | qualquer texto |
| Carvão sobre magenta | 5,6:1 | texto pequeno em selo magenta |
| Carvão sobre vermelho | 5,5:1 | texto pequeno em selo SPOILER |
| Carvão sobre verde | 10,1:1 | texto pequeno em selo SEM SPOILER |
| Magenta sobre carvão | 5,6:1 | texto grande ou ícone |
| **Gelo sobre magenta** | **3,3:1** | **não usar em texto pequeno** |
| **Gelo sobre vermelho** | **3,3:1** | **não usar em texto pequeno** |

Regra: texto em selo magenta, vermelho ou verde é sempre carvão, nunca branco.

### Cores no formato do script de legenda (ASS, que usa BGR)

| Cor | Hex | ASS |
|---|---|---|
| Carvão | `#0B0B12` | `&H00120B0B` |
| Gelo | `#F5F7FA` | `&H00FAF7F5` |
| Amarelo | `#FFD400` | `&H0000D4FF` |
| Magenta | `#FF2E88` | `&H00882EFF` |
| Ciano | `#19E3FF` | `&H00FFE319` |

## 2. Tipografia (Google Fonts, gratuitas, licença livre)

| Uso | Fonte | Peso | Por quê |
|---|---|---|---|
| Logo, gancho na tela, capa | **Anton** | Regular | condensada e pesada, lê bem pequena e funciona em caixa alta |
| Legenda dos vídeos, @, selos | **Montserrat** | ExtraBold 800 (Black 900 para destaque) | legível em vídeo, tem os acentos do português |
| Descrições, crédito, textos longos | **Inter** | Medium 500 e SemiBold 600 | limpa, boa em tamanho pequeno |

Todas têm cedilha e acentos do português. Em qualquer fonte, teste com "ÇÃO, ÕES, É, À" antes de aprovar.

Para o script de legenda usar a Montserrat: instalar o arquivo `.ttf` em `~/.fonts` no WSL, rodar `fc-cache -f` e conferir o nome da família com `fc-list | grep -i montserrat`. O nome que vai no campo `Fontname` do ASS tem que ser igual ao que o `fc-list` mostra (por exemplo `Montserrat ExtraBold`). Hoje o script usa `DejaVu Sans`.

## 3. Estilo da legenda nos vídeos

Referência: o script atual (`clipador/clip_watcher.py`) gera 1080x1920, com o vídeo inteiro no meio sobre fundo desfocado, e legenda branca com contorno preto, centralizada, a 500 px da borda de baixo. O estilo abaixo mantém essa posição (que já fica acima da área coberta pela interface do TikTok e do Reels) e muda a cara.

### Estilo proposto

- **Fonte:** Montserrat ExtraBold, 76 px (em um quadro de 1080 de largura).
- **Cor:** gelo `#F5F7FA`; **palavra-chave** em amarelo `#FFD400`.
- **Contorno:** carvão `#0B0B12`, 8 px, com sombra leve de 2 px.
- **Posição:** centralizada embaixo, a 500 px da borda inferior (como hoje).
- **Quebra:** no máximo 2 linhas de uns 20 caracteres, 2 a 5 palavras por bloco, cada bloco entre 0,4 e 1,2 segundo na tela.
- **Texto:** frase normal (não tudo em caixa alta, que cansa); caixa alta só em palavra de impacto.
- **Palavrão forte:** no YouTube, palavrão pesado nos primeiros 7 segundos pode limitar anúncios (a regra muda, confira no Studio). Troque por `***` na legenda ou corte o trecho.

Linha de estilo pronta para o ASS (substitui a linha `Style: Padrao` do script):

```
Style: Padrao,Montserrat ExtraBold,76,&H00FAF7F5,&H000000FF,&H00120B0B,&H80000000,0,0,0,0,100,100,0,0,1,8,2,2,80,80,500,1
```

(O campo de negrito fica em 0 porque a família "Montserrat ExtraBold" já é pesada; com `-1` o renderizador pode engrossar de novo.)

Para destacar uma palavra em amarelo dentro do texto de uma legenda (nesse comando a cor vai em BBGGRR, 6 dígitos; `{\r}` volta ao estilo normal):

```
{\c&H00D4FF&}PIROU{\r}
```

Isso exige mudar o script para marcar a palavra-chave; é opcional e não faz parte desta pasta de marca. Teste um clipe de 10 segundos antes de rodar em tudo.

### Elementos fixos no vídeo vertical (1080x1920)

| Elemento | Onde | Como |
|---|---|---|
| Gancho | faixa do topo, y entre 300 e 620 | Anton 100 px, gelo, 1 palavra em amarelo, até 2 linhas, até 6 palavras, some em 2 a 3 s |
| Selo da marca | canto superior esquerdo, y 270, x 80 | símbolo + `@marca` em Montserrat 800, 40 px, 70% de opacidade |
| Selo de spoiler | ao lado do selo da marca, nos primeiros 3 s | SPOILER (vermelho, texto carvão) ou SEM SPOILER (verde, texto carvão) |
| Crédito do streamer | logo abaixo do vídeo, y por volta de 1290 | Inter 600, 38 px: `Live: NOME DO STREAMER` (fixo no clipe inteiro) |
| Barra do pico | borda do vídeo ou rodapé | linha fina de 6 px em magenta, opcional |

### Áreas seguras (valores de referência, confira no app)

Não coloque nada importante nos 250 px de cima, nos 480 px de baixo nem nos 140 px da borda direita, que são cobertos por botões e legenda das redes. Manter texto de verdade nos 1080 x 1080 do centro serve para qualquer recorte (1:1, 4:5, 3:4).

## 4. Capa de vídeo e thumbnail

| Formato | Medida | Regras |
|---|---|---|
| YouTube vídeo longo | 1280 x 720 (16:9, até 2 MB, JPG ou PNG; pode exportar em 1920 x 1080) | frame mais forte do momento, ampliado; 2 a 4 palavras em Anton amarela com contorno carvão; selo da marca num canto; testar em 168 x 94 px (miniatura de celular) |
| YouTube Shorts | 1080 x 1920 | quadro escolhido do vídeo, com o gancho em texto; manter o texto no centro |
| TikTok | 1080 x 1920 | quadro de 1 s com o gancho; texto no centro |
| Instagram Reels | 1080 x 1920 (grade do perfil corta em 3:4, e fontes divergem sobre isso) | texto inteiro dentro do quadrado central de 1080 x 1080 |
| X | 1600 x 900 (16:9) | miniatura do vídeo com o gancho |

**Regras de monetização e segurança nas capas e nos 7 primeiros segundos:** a política do YouTube para violência em jogos mudou em 2026 (segundo [reportagem da Dexerto](https://www.dexerto.com/gta/youtube-updates-gaming-violence-monetization-rules-ahead-of-gta-6-launch-3405945/)): violência gráfica nos 7 primeiros segundos continua sem anúncio, e compilações feitas só para chocar podem perder toda a monetização. Por isso: **nada de sangue, tortura ou violência gráfica na capa nem nos 7 primeiros segundos**, e compilação precisa de edição e comentário. Confira a política atual no YouTube Studio.

## 5. Avatar e banner por rede

Medidas de referência (a maior parte vem de guias de terceiros; o app mostra a medida certa na hora do upload).

| Rede | Avatar | Banner ou capa | Observação |
|---|---|---|---|
| YouTube | 800 x 800 (aparece em círculo) | 2048 x 1152 mínimo (recomendado 2560 x 1440), até 6 MB | área segura, a que aparece em todos os aparelhos: 1235 x 338 no centro (no upload de 2048 x 1152) |
| TikTok | 400 x 400 (mínimo recomendado de 200 x 200) | não tem banner | círculo, símbolo no centro |
| Instagram | 320 x 320 (pode subir 1080 x 1080) | não tem banner; capas dos destaques em 1080 x 1920 com o símbolo no centro | círculo de uns 110 px na tela |
| X | 400 x 400 | cabeçalho 1500 x 500 | o avatar cobre o canto inferior esquerdo do cabeçalho; texto à direita |
| Twitch e Kick (futuro) | 256 x 256 (Twitch) | 1200 x 480 (Twitch) | só quando houver lives; medidas não oficiais |

### Símbolo do avatar por marca

Avatar simples, que lê em 40 px: carvão de fundo, 1 símbolo em amarelo, 1 detalhe em magenta.

- **Chat Pirou:** balão de chat com uma linha de pico (onda subindo) dentro. Monograma "CP" em Anton como alternativa.
- **Foi Clipado:** marcas de corte de enquadramento (quatro cantos) ao redor de um triângulo de play, com um carimbo inclinado "CLIPADO" no banner.
- **Pico do Hype:** gráfico de pico em linha que forma um "P", com a ponta no topo em magenta.

### Banner (todas as marcas)

Carvão, a linha de onda do chat atravessando de ponta a ponta (amarela, com o pico em magenta), nome da marca em Anton, e uma linha em Inter: "Cortes de lives | GTA 6 e mais". Sem logo de jogo, sem print de personagem. Dá para montar em Canva ou Figma no plano gratuito.

## 6. Tom de voz

**Em uma frase:** amigo que viu a live com você, zoeiro e ligeiro, que sempre dá o crédito.

- **Português do dia a dia de gamer.** Gíria moderada e natural ("pirou", "clipado", "absurdo"), sem forçar meme velho.
- **Frase curta.** Gancho de até 6 palavras, legenda de até 2 linhas.
- **Zoeira no momento, não na pessoa.** Ri do fail e do chat, nunca humilha streamer, jogador ou comentarista.
- **Crédito sempre, em todo post.** É a marca do respeito.
- **Honesto no título.** O que o título promete tem que acontecer no vídeo (sem isca falsa).
- **Zero spoiler sem aviso.** Veja `legendas-e-hashtags.md`.
- **Emoji com moderação:** 1 ou 2 por legenda; os da marca são 🤯 (Chat Pirou), 🎬 (Foi Clipado) e 🚀 (Pico do Hype).

| Faça | Evite |
|---|---|
| "O chat não perdoou 😂" | "Esse otário..." |
| "Ele achou que ia dar certo" | título que promete uma coisa e entrega outra |
| "SPOILER: reação a uma cena da história" | falar o final, mortes ou reviravoltas no título |
| agradecer o streamer nos comentários | brigar com comentário de ódio (apague e siga) |

## 7. Dez exemplos de títulos e ganchos de corte

Todos sem spoiler de história e sem alegar nada sobre mecânica do jogo que a gente ainda não viu. Troque `[STREAMER]` pelo nome do streamer.

| # | Tipo | Título (YouTube e legenda) | Gancho na tela (primeiros 2 s) |
|---|---|---|---|
| 1 | Lançamento | O chat pirou no primeiro minuto de GTA 6 | "PRIMEIRO MINUTO" |
| 2 | Fail | Ele achou que ia dar certo. O chat já sabia que não. | "DEU RUIM" |
| 3 | Reação | [STREAMER] não esperava essa reação do chat | "O CHAT NÃO PERDOA" |
| 4 | Ação e humor | A fuga da polícia mais absurda da live | "COMO ELE ESCAPOU?" |
| 5 | Dica | 5 coisas pra fazer antes da história (sem spoiler) | "FAÇA ISSO ANTES" |
| 6 | PC | Pra quem joga no PC: o que a galera do console já está vivendo | "ENQUANTO O PC NÃO CHEGA" |
| 7 | Bug | O bug mais engraçado do primeiro dia | "ISSO NÃO ERA PRA ACONTECER" |
| 8 | Reação | Ele ficou mudo por 5 segundos. Depois o chat explodiu. | "SILÊNCIO... E AÍ?" |
| 9 | Notícia | GTA 6 no PC: o que já foi dito e o que é só boato | "E O PC?" |
| 10 | Compilação | Os 5 picos do chat da semana de lançamento (sem spoiler) | "TOP 5 DO CHAT" |

Os números 5, 9 e 10 vão melhor nos sub-canais `_news` e `_top` quando eles existirem; até lá, saem no guarda-chuva.
