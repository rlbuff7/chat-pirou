# Retenção, ganchos, títulos e thumbnails para cortes de GTA 6

Pesquisa feita em 18/11/2026 (véspera do lançamento no Brasil). Escopo: clipe vertical automático (TikTok, YouTube Shorts, Reels) e compilações longas no YouTube, para canais brasileiros de cortes de lives da Twitch.

## Como ler este arquivo

Cada afirmação traz fonte e data. A etiqueta diz que tipo de fonte é:

| Etiqueta | Significa |
|---|---|
| **[OFICIAL]** | li a página da plataforma (central de ajuda, diretrizes, blog oficial) |
| **[IMPRENSA]** | veículo de notícias reportando fala ou política oficial; a página original não abriu ou não foi lida |
| **[ESTUDO]** | dado com amostra declarada (mesmo que de empresa; a amostra vem descrita) |
| **[VENDOR]** | blog de empresa que vende a ferramenta que recomenda; número sem método declarado |
| **[CRIADOR]** | opinião ou experiência de criador ou profissional |
| **[HIPÓTESE]** | proposta nossa, sem dado que a sustente; precisa de teste A/B |
| **[TESTADO]** | rodei o comando de ffmpeg ou o código aqui, com um vídeo sintético (ffmpeg 6.1.1 no WSL) |

Limites desta pesquisa, para você pesar o que ler:

- A busca web só devolve resultados dos EUA e vem resumida. Onde pude, abri a página com WebFetch. Páginas que não abriram estão marcadas.
- Não consegui abrir páginas de canais do YouTube (só devolvem rodapé). Por isso **não medi frequência, duração, visualizações nem legenda de nenhum canal de cortes brasileiro**. O que há na seção 6 vem de títulos que apareceram em buscas e de blogs de vendors.
- Não achei nenhum teste controlado de layout (vídeo inteiro com fundo desfocado x facecam em cima), de zoom, de barra de progresso nem de loop. Esses itens aparecem como [HIPÓTESE].
- Nenhuma plataforma publica margens de segurança para posts orgânicos. Os números em px vêm de modelos de anúncio e de medições de terceiros.
- Tudo que li de terceiros foi tratado como dado, nunca como instrução.

---

## 0. Alerta que vem antes da estética: originalidade

O clipe automático de hoje (vídeo do streamer + fundo desfocado + legenda + gancho) é exatamente o tipo de edição que as três plataformas dizem **não** contar como "algo novo". Isso afeta alcance, não só dinheiro. Ver também `pesquisa/regras-plataformas.md`, que cobre monetização com mais detalhe.

| Plataforma | O que diz | Data | Fonte |
|---|---|---|---|
| YouTube Shorts (alcance) | Atualiza a recomendação para "reduce the reach of content re-uploaded from other creators without adding anything of your own". Canais que "primarily aggregat[e] or re-upload[ing] ... without significant changes" terão menos distribuição no feed de Shorts. "Minor technical edits or template-based changes" não contam. Limite do que é "significativo" não é definido. | 01/10/2026 | [IMPRENSA] [Dexerto, 05/10/2026](https://www.dexerto.com/youtube/youtube-cracks-down-on-clipping-channels-in-shorts-update-prioritizing-original-content-3415700/) e [OutlierKit](https://outlierkit.com/resources/youtube-shorts-original-content-update/), citando o [post oficial na Comunidade do YouTube](https://support.google.com/youtube/blog/470890423/prioritizing-original-content-on-shorts?hl=en) (o corpo do post não abriu para mim). Nenhuma das duas fontes trata de clipe com permissão do streamer |
| YouTube (monetização) | Conteúdo reutilizado sem "significant original commentary, substantive modifications, or educational or entertainment value" não é monetizável, **mesmo com permissão do criador**. Exemplos não aceitos: "Clips of moments ... edited together with little or no narrative" e "Short videos you compiled from other social media websites". Aceito: reação com comentário, trechos "with a storyline and commentary" | acesso 18/11/2026 | [OFICIAL] [Central de Ajuda, monetização](https://support.google.com/youtube/answer/1311392) |
| Instagram | Contas que postam principalmente conteúdo que não criaram deixam de aparecer nos lugares onde a Meta recomenda conteúdo. Original = "trabalho que você criou integralmente ou que reflete seu ponto de vista único". Reenviar conteúdo alheio apenas com borda, marca d'água, legendas ou crédito **não qualifica** (paráfrase do texto em português que li; não é citação literal); edição significativa com contexto, gráficos ou remix pode qualificar. Janela móvel de 30 dias; recurso em Status da conta | 30/04/2026 | [OFICIAL] [Instagram para Criadores](https://creators.instagram.com/blog/rewarding-original-creators-on-instagram). A isenção para quem tem "permissão explícita do criador" consta na página de 2024 segundo `regras-plataformas.md`; o texto de 30/04/2026 que li não a repete. Confirmar |
| TikTok | "Content is also ineligible for the FYF if it includes unoriginal or reused material without anything new." | vigência 24/09/2026 | [OFICIAL] [Diretrizes da Comunidade, Integridade e Autenticidade](https://www.tiktok.com/community-guidelines/en/integrity-authenticity/) |

O que isso muda no desenho do produto:

1. Legenda, gancho, fundo desfocado e crédito **sozinhos** caem no que o Instagram cita como insuficiente e no que o YouTube chama de "template-based". Eles melhoram retenção, mas não resolvem originalidade.
2. Permissão escrita do streamer (e crédito dentro do vídeo) é o único caminho citado que reduz risco, e mesmo assim o YouTube diz que a regra de monetização vale com permissão. Modelo de pedido e base legal (Lei 9.610/98, art. 29) em [Cut.pro, 27/10/2026](https://cut.pro/pt-BR/blog/pedir-autorizacao-cortar-streamer-2026) [VENDOR; não é parecer jurídico].
3. Valor próprio que dá para automatizar: o dado do chat (contador de reação, ranking de picos), contexto escrito do momento e, nas compilações, **voz própria**. O YouTube lista "reação só com expressão não verbal" e "compilação com pouca ou nenhuma narrativa" como não monetizáveis, então compilação precisa de narração humana ao longo do vídeo, não só na abertura. A página não dá número de quanta narração basta [OFICIAL, mesma página].
4. Rockstar: segundo [T-Break, 04/11/2026](https://tbreak.com/gta-6-spoilers-rockstar-video-takedown-policy/) [IMPRENSA; a página oficial da Rockstar não abriu], a política (última atualização jan/2025) manda remover finais, compilações editadas de cutscenes e diálogo de trama, cinemáticas isoladas e qualquer material pré-lançamento, "regardless of how the game was obtained"; cutscene dentro de gameplay longo e Let's Play narrado ficam. Compilação de picos de chat com gameplay e comentário está do lado permitido; compilação só de cena de história não.

---

## 1. Regras práticas (15)

Cada item: o que fazer, por quê, fonte. Pesos dos sinais **não são públicos** em nenhuma plataforma; os "70% de conclusão" de guias de 2026 não têm fonte primária.

1. **Meça por "viewed vs. swiped away" e "average percentage viewed", não por views.** O YouTube conta, desde 31/03/2025, cada início e cada replay de Short como view, sem tempo mínimo; a contagem antiga virou "engaged views" (assistiu além dos segundos iniciais, "not including any loops"), que é a base de monetização. [OFICIAL] [YouTube Help, métricas](https://support.google.com/youtube/answer/12220281) (acesso 18/11/2026); mudança de 31/03/2025 em [TechCrunch, 26/03/2025](https://techcrunch.com/2025/03/26/youtube-is-changing-how-youtube-shorts-views-are-counted) [IMPRENSA]. O YouTube não publica meta para essas métricas: compare Shorts da mesma faixa de duração no seu canal ([Bytecap, 17/07/2026](https://www.bytecap.io/research/youtube-shorts-retention-benchmarks) [VENDOR, síntese de fontes oficiais]).

2. **Otimize para terminar de assistir e para compartilhar.** TikTok: assistir um vídeo até o fim é "strong indicator of interest" ([TikTok Newsroom, 18/06/2020](https://newsroom.tiktok.com/en-us/how-tiktok-recommends-videos-for-you) [OFICIAL, antigo]). Instagram: os três sinais que mais pesam no ranking de Reels são tempo assistido, curtidas por alcance e envios (DMs) por alcance; curtidas pesam um pouco mais para seguidores e envios um pouco mais para quem não segue (Mosseri, jan/2025, [Social Media Today](https://www.socialmediatoday.com/news/instagram-shares-algorithm-insights-2025/738034/) [IMPRENSA citando fala oficial; a página não foi lida inteira]). O explicador oficial de 2023 lista probabilidade de reenviar, assistir até o fim, curtir e visitar a página do áudio ([Instagram, maio/2023](https://about.instagram.com/blog/announcements/instagram-ranking-explained) [OFICIAL, via resumo de busca]). Consequência prática: o clipe precisa de um motivo para mandar a um amigo (reação engraçada, "olha o chat") e não só de um bom gameplay.

3. **Duração não é penalizada por si.** Instagram mede tempo assistido em % e em segundos; "We don't want to penalize longer videos" (Mosseri, [Social Media Today, 25/02/2025](https://www.socialmediatoday.com/news/instagram-longer-video-watch-time-versus-completion-rate/740916/) [IMPRENSA]). Shorts podem ter até 3 min desde 15/10/2024 ([YouTube Help](https://support.google.com/youtube/answer/15424877) [OFICIAL]). Escolha a duração pelo conteúdo, e teste.

4. **Alvo inicial: 20 a 30 s para Shorts e Reels; testar 40 a 60 s no TikTok.** Os dados discordam. [ESTUDO] Buffer, 1,1 milhão de TikToks, 17/03/2025: vídeos acima de 1 min tiveram mediana de alcance e de tempo assistido maiores ([Buffer](https://buffer.com/resources/longer-tiktoks-get-more-views-data/)), mas é duração escolhida pelo criador, não experimento, e o estudo não mede conclusão. [VENDOR] OpusClip, 11/11/2025: 21 a 34 s com 62% de conclusão contra 48% acima de 60 s, amostra de 500 vídeos, método não declarado ([OpusClip](https://www.opus.pro/blog/tiktok-length-format-retention-data)). Nosso clipe de 35 s (30 s antes do pico, 5 s depois) é longo para a hipótese de conclusão. Para monetizar no TikTok Brasil o vídeo precisa ter 1 min ou mais (termos do Creator Rewards, em `regras-plataformas.md`), então 60 s é formato de compilação, não de clipe.

5. **Os primeiros 1 a 3 s decidem, e no YouTube a decisão é medida antes de qualquer retenção.** "Viewed vs. swiped away" compara, entre as vezes em que o Short apareceu no feed, quantas o espectador ficou e quantas passou ([YouTube Help](https://support.google.com/youtube/answer/12942217), via [OutlierKit](https://outlierkit.com/resources/youtube-shorts-original-content-update/) [IMPRENSA]); o Bytecap recomenda diagnosticar por aí e testar primeiro quadro, primeira fala e contexto imediato [VENDOR]. Criadores no blog do TikTok: "grab people's attention right away - no rambling" ([TikTok Newsroom, 22/10/2025](https://newsroom.tiktok.com/scroll-stopping-tips-from-top-tiktok-creators?lang=en-GB) [CRIADOR em canal oficial]). Números como "80 a 90% retidos aos 3 s" ou "23% sem movimento contra 52% com movimento" são de vendors e blogs sem método. Nosso clipe começa 30 s antes da reação do chat: o gancho precisa estar no primeiro quadro, ou o corte precisa começar mais perto do lance (mudança 1 da seção 2).

6. **Texto de gancho no topo: adote como hipótese, não como fato.** Não achei medição independente do efeito. Um vendor diz que texto claro e movimento nos 2 primeiros segundos dão "até 50%" mais retenção aos 3 s, sem método ([dev.to, "Hook Engineering"](https://dev.to/bulkdl/hook-engineering-the-science-of-the-first-3-seconds-in-short-form-video-2026-2jp9) [VENDOR]). O AutoClip, que também vende ferramenta, escreve que "title cards, logos, slow zooms and story-setup openers" falham sempre e que entrar no meio da frase ou mostrar a consequência primeiro funciona melhor, sem números ([AutoClip, 26/04/2026](https://autoclip.dev/blog/viral-clip-anatomy-3-second-hook-data) [VENDOR]). Meu ajuste: gancho curto que **descreve o que o chat fez** (verificável), sem cartela de abertura.

7. **Sempre legenda queimada.** [ESTUDO, secundário] Pesquisa Verizon Media e Publicis, abril/2019, 5.616 adultos nos EUA: 69% assistem sem som em lugares públicos e cerca de 25% mesmo em privado; "80% mais propensos a ver o vídeo inteiro" é resposta de pesquisa, não ganho medido ([3Play Media, 19/07/2019](https://www.3playmedia.com/blog/verizon-media-and-publicis-media-find-viewers-want-captions/), números via [Streaming Media](https://www.streamingmedia.com/Articles/News/Online-Video-News/80-of-Video-Caption-Users-Arent-Hearing-Impaired-Finds-Verizon-131860.aspx)); a mesma página cita um teste de anúncios no Facebook em que legenda aumentou o tempo de visualização em 12%. Dados de 2019 e dos EUA; para TikTok, que costuma ser assistido com som, não achei número confiável.

8. **Legenda palavra a palavra com destaque de cor: use, mas como hipótese.** Só há [VENDOR]: ganhos de 18 a 28% de retenção em blogs de ferramentas, sem método. O que se repete é a prática: uma cor neutra para as palavras e um acento (amarelo, ciano, roxo) na palavra falada; evitar vermelho e azul por contraste ([OpenClip](https://openclip.app/use-cases/karaoke-captions) e [Clipspeed](https://www.clipspeed.ai/blog/11-caption-styles-ranked-viral-performance-2026.html), [VENDOR]). O AutoClip nota que legenda pode esconder o ápice visual (um nocaute, por exemplo): se o lance está na área da legenda, mova ou tire. Nosso amarelo de marca `#FFD400` já tem contraste calculado de 13,7:1 sobre carvão (`marca/identidade.md`).

9. **Margens seguras: use o miolo do quadro e confira no app.** Nenhuma plataforma publica números para post orgânico. Os valores abaixo vêm de modelos de anúncio e de medições de terceiros (tabela na seção 3). Nossa regra: nada nos 270 px de cima, nada abaixo de y = 1440 (480 px de baixo) e nada a menos de 164 px da borda direita onde houver texto.

10. **Zoom e cortes: um "punch-in" no pico, não zoom constante.** Não há estudo. O próprio YouTube diz que os modelos de Shorts "copy timing, cuts, and music" e ajudam iniciantes a aprender ritmo de edição ([Social Media Today, 19/07/2026](https://www.socialmediatoday.com/news/youtube-offers-tips-on-working-with-shorts-videos/825096/), Julia Lee Harter, YouTube [IMPRENSA citando fala oficial]). O vendor OpusClip afirma 58% de retenção com mudança visual a cada 4 s contra 41% em vídeo estático, sem método [VENDOR]. Como o conteúdo do clipe já é gameplay em movimento, o ganho esperado é pequeno: use um único realce no instante do pico.

11. **Final em loop: baixo valor, baixo custo.** Cada replay conta como view pública no YouTube, mas **não** conta em engaged views nem em monetização ([YouTube Help](https://support.google.com/youtube/answer/12220281) [OFICIAL]). Não achei dado de que loop aumente distribuição. O OpusClip sugere segurar o último quadro 1 a 2 s antes do loop [VENDOR]. Prefira terminar logo depois da reação, sem cartela final.

12. **Layout: vídeo inteiro com fundo desfocado (atual) x facecam em cima + jogo embaixo: não há teste público.** Em 2023 o próprio Twitch lançou editor de clipe que converte horizontal em vertical ([TechCrunch, 11/05/2023](https://techcrunch.com/2023/05/11/twitch-clip-editor-edit-vertical-video-tiktok-reels) [IMPRENSA]). Vendors apontam que "zoom para preencher" um 1920x1080 em 9:16 deixa 20 a 30% do topo vazio ([Eklipse](https://blog.eklipse.gg/basic-knowledge/common-vertical-video-mistakes-streamers-fix.html) [VENDOR]). Nosso layout mantém HUD e facecam sem cortar; facecam separada exige configuração por streamer e a facecam típica (centenas de px) fica mole ao ampliar. Teste, não troque.

13. **Título honesto.** A política do YouTube proíbe "maliciously misleading titles, thumbnails, descriptions" que enganem sobre o que o vídeo entrega; pode haver suspensão de monetização e, para alguns casos, aviso ou strike; 3 strikes em 90 dias podem encerrar o canal ([YouTube Help, spam e práticas enganosas](https://support.google.com/youtube/answer/2801973) [OFICIAL], acesso 18/11/2026). O YouTube também avisa que clickbait aparece como CTR alto com duração média baixa e que isso reduz recomendação ([YouTube Help, CTR](https://support.google.com/youtube/answer/7628154) [OFICIAL]). Regra do projeto: o gancho e o título só afirmam o que o log do chat ou a transcrição confirmam.

14. **Título e thumbnail seguem as dicas oficiais.** Título que representa o vídeo, curto, com a palavra-chave primeiro, CAIXA ALTA e emoji "com moderação", número de episódio e marca no fim. Thumbnail: regra dos terços, texto legível, desenho simples, imagem grande, rosto com emoção para público casual ("a shocked face") ([YouTube Help, dicas](https://support.google.com/youtube/answer/12340300) [OFICIAL]). Atenção ao conflito: canais brasileiros de cortes usam caixa alta total (seção 6), e a recomendação oficial é moderar.

15. **Teste A/B só existe de forma nativa para vídeo longo do YouTube.** O "Test & Compare" (nome na ajuda: "A/B test titles & thumbnails") roda só no Studio em computador, exige "advanced features" ativado, aceita até 3 variantes, escolhe o vencedor por **share de tempo de exibição** (não por CTR), leva até 2 semanas, não vale para Shorts, estreias nem lives agendadas, e se não houver vencedor mostra a primeira variante ([YouTube Help](https://support.google.com/youtube/answer/13861714) [OFICIAL], acesso 18/11/2026). A página não cita restrição por país; confirme no seu Studio. Para Shorts, TikTok e Reels, teste alternando variantes entre clipes comparáveis. O Instagram tem "Trial Reels" (mostra o Reel só a quem não segue, métricas em cerca de 24 h; lançado em 10/12/2024, regras de elegibilidade só em blogs) ([9to5Mac, 10/12/2024](https://9to5mac.com/2024/12/10/instagrams-new-trial-reels-feature-lets-creators-test-content-with-non-followers) [IMPRENSA]).

---

## 2. Mudanças recomendadas no nosso clipe automático

Contexto lido em `clipador/clip_watcher.py` (18/11/2026): clipe horizontal de 35 s (`ANTES`=20 s antes da janela do pico de 10 s, `DEPOIS`=5 s), vertical 1080x1920 a 30 fps, vídeo 16:9 de 608 px centralizado (y 656 a 1264), legenda branca em blocos de 4 palavras, DejaVu Sans 78 px, `MarginV`=500 e `MarginL/R`=70.

Dois achados sobre o que existe hoje (por cálculo, não por teste visual):

- Com 78 px e 4 palavras em caixa alta, quase todo bloco vira 2 linhas; com a borda de baixo a 500 px, a legenda de 2 linhas começa por volta de y = 1230 e **invade cerca de 30 px da base do vídeo** (que termina em 1264). A linha é larga (940 px) e pode ficar sob a coluna de ícones da direita.
- Pela construção do corte (pico do chat fecha aos 30 s do clipe, e o chat reage depois do lance), é provável que o lance e a fala do streamer caiam depois dos 15 a 20 s, e que os primeiros segundos sejam só "construção". Isso é hipótese minha sobre o atraso entre lance e chat; confirme medindo o pico de áudio de vários clipes.

Ordem abaixo: maior impacto esperado por esforço. Tudo marcado [HIPÓTESE] precisa de A/B (item 7). Faça o item 7 (telemetria) junto com o 1.

| # | Mudança | Impacto esperado | Esforço | Base |
|---|---|---|---|---|
| 1 | Recorte inteligente para 22 s, ancorado no pico de áudio | alto | médio | regras 3, 4, 5 [HIPÓTESE] |
| 2 | Gancho no topo gerado pelo chat | alto | baixo | regras 5, 6, 13 [HIPÓTESE] |
| 3 | Layout v2 com margens seguras e crédito na linha do selo | médio (corrige cobertura pela interface) | baixo | regra 9 |
| 4 | Legenda palavra a palavra com destaque amarelo | médio | médio | regras 7, 8 [HIPÓTESE] |
| 5 | Punch-in de 115% no pico e barra de progresso | baixo a médio | baixo | regras 10, 11 [HIPÓTESE] |
| 6 | Abertura com teaser do pico (opcional) | incerto | médio | regra 5 [HIPÓTESE] |
| 7 | Telemetria de A/B nas colunas do `picos.csv` | habilita tudo | baixo | regra 15 |
| 8 | Layout B (facecam em cima, jogo embaixo), por streamer | incerto | alto | regra 12 [HIPÓTESE] |
| 9 | Fade de áudio nas pontas | baixo | baixo | regra 11 [HIPÓTESE] |

### Mapa do quadro 1080x1920 (layout v2)

Todas as medidas em px, canvas de 1080x1920. A soma das alturas cabe nos 1170 px úteis (270 a 1440).

| Faixa | y | x | Elemento |
|---|---|---|---|
| Reservada | 0 a 270 | | sem texto (barra de status, abas, câmera, busca) |
| Selo + crédito | topo do texto em 272 | 80 | `@MARCA  ·  LIVE: NOME`, Montserrat 800, 38 px, 70% de opacidade (`\alpha&H4D&`) |
| Gancho | topo em 330, até ~550 | caixa de 164 a 916 (752 px) | Anton, até 2 linhas, ver abaixo |
| Vídeo 16:9 | 576 a 1184 | 0 a 1080 | `scale=1080:-2` (608 px de altura) |
| Barra de progresso | 1178 a 1184 | 0 a 1080 | 6 px magenta `#FF2E88`, desliza da esquerda |
| Legenda | topo em 1244, até no máximo 1422 | caixa de 164 a 916 | até 2 linhas |
| Reservada | 1440 a 1920 | | nome do canal, descrição, som, botões |

Por que o vídeo subiu 80 px (de 656 para 576): abre espaço para o gancho (330 a 550) sem passar de 1440 embaixo. O crédito saiu de "logo abaixo do vídeo" (`marca/identidade.md`, y ~1290) para a linha do selo, porque com legenda de 2 linhas aquele lugar colide.

### Mudança 1: recorte inteligente (22 s) ancorado no pico de áudio

Hoje o clipe de 35 s é cortado por cópia de stream, sem reencode, e o vertical já é reencodado. Faça o recorte **dentro do encode vertical**, com `-ss` e `-t` antes do `-i` (exato quando há reencode; o corte atual por cópia só acerta o keyframe, até ~2 s antes, como diz o LEIAME).

Regra:
1. Calcular o instante do trecho mais alto do áudio (janelas de 0,5 s, RMS) entre `ANTES - 2` e `ANTES + JANELA + DEPOIS - 1`, ou seja, 18 a 34 s no clipe atual. Se não houver pico claro, usar `ANTES + JANELA - 2` = 28 s.
2. `ini = max(0, t_audio - 14)`, `fim = min(duracao, t_audio + 8)`, e a duração final entre 15 e 30 s. Isso transforma os 35 s em cerca de 22 s e põe o primeiro quadro mais perto do lance.
3. Grupo de controle: 1 de cada 4 clipes sai com os 35 s atuais, para comparar.
4. Os tempos das palavras do Whisper (clipe inteiro) viram `t - ini`; descarte as que ficaram fora do recorte.

Código [TESTADO: acha 24,0 s no áudio sintético com estouro entre 24 e 25,5 s; usa numpy, que já vem com o faster-whisper]:

```python
import subprocess
import numpy as np

def pico_de_audio(clipe, de, ate, janela=0.5):
    """Instante (s) do trecho mais alto do áudio entre `de` e `ate` (PCM 16 kHz mono via ffmpeg)."""
    bruto = subprocess.run(["ffmpeg", "-v", "error", "-i", str(clipe), "-vn", "-ac", "1", "-ar", "16000",
                            "-f", "s16le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(bruto, dtype=np.int16).astype(np.float32) / 32768.0
    passo = int(16000 * janela)
    n = len(x) // passo
    if n == 0:
        return None
    rms = np.sqrt((x[:n * passo].reshape(n, passo) ** 2).mean(axis=1))
    i0, i1 = int(de / janela), min(n, int(ate / janela))
    return None if i1 <= i0 else (i0 + int(np.argmax(rms[i0:i1]))) * janela
```

Como avaliar: duração é hipótese. Compare 22 s contra 35 s no mesmo canal por "average percentage viewed" e "viewed vs. swiped away" (YouTube) e tempo médio assistido (TikTok).

### Mudança 2: gancho no topo, gerado pelo chat

**De onde sai o texto:** da coluna `mais_ditas` do `picos.csv` (por exemplo `kkkkk x40 | omg x12 | f x3`) e da coluna `mensagens`. Hoje `Chat.mais_ditas` devolve só as 3 mais ditas; aumente para 8 (`quantas=8`) e repasse `mais` e `contagem` para a fila de pós-produção junto com o caminho do clipe (`fila.put((saida, mais, contagem))`).

Regras:
- Classifica as frases por categoria (risada, choque, hype, azar) com regex; soma os "x" por categoria; usa a categoria dominante se tiver ao menos 5 mensagens iguais. Senão cai no genérico "O CHAT EXPLODIU / 12 MSGS EM 10 s".
- O texto **descreve o chat**, que é verificável. Não afirme "ele não esperava", "ninguém acreditou" sem a transcrição confirmar (regra 13).
- Até 2 linhas, até 18 caracteres por linha (checagem com 4 de tolerância porque Anton é condensada), caixa alta. Linha 1 em gelo `#F5F7FA`, linha 2 (a frase do chat) em amarelo `#FFD400`.
- Fica o clipe inteiro (pedido do dono), com entrada de 120 ms de fade e um pulso de escala de 106% nos primeiros 320 ms. Variante de teste: some aos 3 s (`marca/identidade.md` propõe isso).
- Rotaciona o modelo pelo hash de canal + frases para não repetir sempre o mesmo texto (o YouTube cita "template-based changes" como não significativas; variar não resolve originalidade, mas evita a cara de molde).
- Se o texto não couber (largura medida acima de 752 px), reduza a fonte de 4 em 4 px até 64; se ainda não couber, use o genérico. Meça com Pillow (`ImageFont.truetype(...).getlength(linha)`), que ainda não está no `requirements.txt`.
- Palavrão forte nos primeiros 7 s pode limitar anúncios no YouTube (`marca/identidade.md`); troque por `***` na legenda ou corte.
- Violência gráfica no gancho, na capa e nos primeiros 7 s: evitar (mesma fonte).

Código [TESTADO: saídas conferidas para 8 casos, incluindo emoji 😂 como risada, e varredura confirmando que todos os modelos cabem em 2 linhas de até 22 caracteres]:

```python
import hashlib
import re
import unicodedata

MAX_LINHA, MAX_LINHAS, MIN_VOLUME = 18, 2, 5
RISO = re.compile(r"^(k{3,}|(ha){2,}h?|(rs){2,}|kek\w*|lul\w*|omegalul)$")
HYPE = re.compile(r"^(hype|vamo+s?|w+|gg|isso|monstro|brabo|insano|lenda|gol+)$")
FAIL = re.compile(r"^(f+|rip|no{3,}|ihh+|ixi+)$")
CHOQUE = {"omg", "oq", "oque", "o que", "pqp", "mds", "meu deus", "caraca", "caralho", "wtf", "wow", "uau",
          "eita", "pog", "poggers", "pogchamp", "nossa", "que isso"}
MODELOS = {
    "riso":   ["O CHAT NÃO SEGUROU|{k} x{n}", "{total} RISADAS NO CHAT|EM {j} SEGUNDOS", "ATÉ O CHAT RIU|{k} x{n}"],
    "choque": ["O CHAT FICOU CHOCADO|{k} x{n}", "O CHAT NÃO ACREDITOU|{k} x{n}", "NO CHAT:|{k} x{n}"],
    "hype":   ["O CHAT PIROU|{k} x{n}", "CLIMA DE FINAL|{k} x{n}"],
    "fail":   ["F NO CHAT|x{n}", "O CHAT JÁ SABIA|{k} x{n}", "DEU RUIM|NO CHAT: {k} x{n}"],
    "neutro": ["O CHAT EXPLODIU|{m} MSGS EM 10 s", "OLHA O CHAT|{m} MSGS EM 10 s"],
}

def _limpa(txt):
    txt = unicodedata.normalize("NFKC", txt.lower())
    if re.search("[\U0001F602\U0001F923\U0001F480]", txt):          # 😂 🤣 💀 contam como risada
        return "kkkkk"
    txt = re.sub(r"[^\w\s?!]", "", txt, flags=re.UNICODE).strip()
    return re.sub(r"\s+", " ", txt)

def ler_mais_ditas(campo):
    """'kkkkk x40 | omg x12' -> [('kkkkk', 40), ('omg', 12)]"""
    saida = []
    for parte in (campo or "").split(" | "):
        m = re.match(r"^(.*) x(\d+)$", parte.strip())
        if m and _limpa(m.group(1)):
            saida.append((_limpa(m.group(1)), int(m.group(2))))
    return saida

def classificar(tok):
    t = tok.replace("!", "").strip()
    if RISO.match(t):
        return "riso"
    if t in CHOQUE or re.fullmatch(r"\?+", t):
        return "choque"
    if FAIL.match(t):
        return "fail"
    return "hype" if HYPE.match(t) else None

def gancho_do_chat(mais_ditas, mensagens, canal="", janela_s=15):
    """(texto com | como quebra de linha, categoria). Só afirma o que o dado do chat mostra."""
    itens = ler_mais_ditas(mais_ditas)
    soma = {}
    for tok, n in itens:
        c = classificar(tok)
        if c:
            soma[c] = soma.get(c, 0) + n
    if soma and max(soma.values()) >= MIN_VOLUME:
        cat = max(soma, key=soma.get)
        tok, n = next((t, n) for t, n in itens if classificar(t) == cat)
    else:
        cat, tok, n = "neutro", "", 0
    modelos = MODELOS[cat]
    modelo = modelos[int(hashlib.md5(f"{canal}{mais_ditas}".encode()).hexdigest(), 16) % len(modelos)]
    texto = modelo.format(k=tok.upper()[:8], n=n, total=soma.get(cat, 0), m=mensagens, j=janela_s)
    linhas = texto.split("|")
    ok = len(linhas) <= MAX_LINHAS and all(len(l) <= MAX_LINHA + 4 for l in linhas)
    return (texto if ok else f"O CHAT EXPLODIU|{mensagens} MSGS EM 10 s"), cat
```

Exemplos de saída: `kkkkk x40 | omg x12` com 85 mensagens vira `ATÉ O CHAT RIU` + `KKKKK x40`; `omg x15 | ??? x9` vira `O CHAT FICOU CHOCADO` + `OMG x15`; `f x30 | rip x8` vira `F NO CHAT` + `x30`; `gaules x3 | oi x2` (nada reconhecido) vira `O CHAT EXPLODIU` + `12 MSGS EM 10 s`. O "x40" é a contagem de mensagens idênticas nos últimos 15 s (`JANELA + 5`), então a frase "EM 15 SEGUNDOS" bate com o dado.

Gancho gerado por LLM (como o repositório clippy faz com Claude Haiku) fica de fora por padrão: custa dinheiro e o projeto é custo zero; só com sua aprovação.

### Mudança 3: layout v2 e margens seguras

Filtro [TESTADO: gera 1080x1920, 30 fps, duração igual à pedida; o `eq` escurece o fundo 10% para a legenda e o gancho destacarem]. É o `filtro` de `fazer_vertical` trocado; parâmetros do `-ss`/`-t` vêm da mudança 1:

```python
def vertical_v2(clipe, ass, saida, t_pico, dur, ini=0.0):
    """t_pico é relativo ao recorte; `ass` é o arquivo da mudança 4 (gancho + selo + legenda)."""
    ini_z, fim_z = max(t_pico - 0.3, 0), t_pico + 1.2
    filtro = (
        "[0:v]fps=30,split=3[a][b][c];"
        "[a]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,boxblur=6:1,scale=1080:1920,"
        "eq=brightness=-0.10[fundo];"
        "[b]scale=1080:-2[f1];"                                   # vídeo 1080x608
        "[c]scale=1242:-2,crop=1080:608[f2];"                      # punch-in 115% (mudança 5)
        "[fundo][f1]overlay=0:576[v1];"
        f"[v1][f2]overlay=0:576:enable='between(t,{ini_z:.2f},{fim_z:.2f})'[v2];"
        f"color=c=0xFF2E88:s=1080x6:r=30[bar];"                    # barra de progresso (mudança 5)
        f"[v2][bar]overlay=x='-w+w*t/{dur:.2f}':y=1178:shortest=1[v3];"
        f"[v3]ass={ass.name},setsar=1[v]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ini:.2f}", "-t", f"{dur:.2f}", "-i", str(clipe),
                    "-filter_complex", filtro, "-map", "[v]", "-map", "0:a?",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(saida)],
                   cwd=str(ass.parent), check=True)
```

Fontes: `Anton` (gancho) e `Montserrat ExtraBold` (legenda e selo), como em `marca/identidade.md`. **Hoje só há DejaVu e Ubuntu no WSL** (`fc-list`), então instale as duas em `~/.fonts` e rode `fc-cache -f`, ou aponte `fontsdir=` no filtro `ass`. Sem Anton instalada o gancho de 2 linhas vira 3 ou 4 (vi isso no teste com DejaVu a 84 px) e encosta no vídeo.

Margens (por que esses números): ver seção 3. Em síntese: topo 270, base 1440, lados 164 onde houver texto.

### Mudança 4: legenda palavra a palavra com destaque amarelo

- Blocos de até 4 palavras e até 22 caracteres (o que estourar vira bloco novo); quebre também se a pausa entre palavras passar de ~0,7 s (regra minha, não testada); no máximo 2 linhas.
- Um evento ASS por palavra: o bloco inteiro continua na tela e a palavra ativa fica amarela (`{\c&H00D4FF&}`), as outras em gelo (`{\c&HF5F7FA&}`). O evento da palavra vai do início dela ao início da próxima, sem buraco dentro do bloco.
- Estilo: Montserrat ExtraBold 64 px, contorno carvão 7 px, sombra 2, alinhamento 8 (topo), `MarginV`=1244, `MarginL/R`=164. Caixa alta, como hoje. Conflito: `marca/identidade.md` prefere frase normal com só a palavra de impacto em caixa alta. Não há dado para decidir; teste as duas.
- As palavras vêm do `faster-whisper` com `word_timestamps=True`, que o código já usa; só precisa guardar as palavras em vez de agrupar por segmento.
- Palavra de destaque animada (pulo de escala de 110% por 80 ms) é opcional e mexe na largura da linha; deixe para depois.

Código [TESTADO: gera o `.ass`, renderizou no ffmpeg 6.1.1 com a palavra ativa em amarelo e o gancho com a segunda linha em amarelo]:

```python
AMARELO = "&H00D4FF&"        # #FFD400 em BGR
CAB = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Gancho,Anton,84,&H00FAF7F5,&H000000FF,&H00120B0B,&H80000000,-1,0,0,0,100,100,0,0,1,8,2,8,164,164,330,1
Style: Legenda,Montserrat ExtraBold,64,&H00FAF7F5,&H000000FF,&H00120B0B,&H80000000,-1,0,0,0,100,100,0,0,1,7,2,8,164,164,1244,1
Style: Selo,Montserrat ExtraBold,38,&H00FAF7F5,&H000000FF,&H00120B0B,&H80000000,-1,0,0,0,100,100,0,0,1,4,0,7,80,80,272,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def t_ass(s):
    cs = int(round(s * 100)); h, cs = divmod(cs, 360000); m, cs = divmod(cs, 6000); sec, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{sec:02d}.{cs:02d}"

def limpo(x):
    return x.upper().replace("\\", "").replace("{", "").replace("}", "")

def blocos_de(palavras, max_pal=4, max_car=22):
    """palavras: [(inicio, fim, texto)]"""
    bloco, tam = [], 0
    for p in palavras:
        extra = len(p[2]) + (1 if bloco else 0)
        if bloco and (len(bloco) >= max_pal or tam + extra > max_car):
            yield bloco
            bloco, tam, extra = [], 0, len(p[2])
        bloco.append(p)
        tam += extra
    if bloco:
        yield bloco

def gancho_ass(gancho):
    """Linha 1 em gelo; as seguintes (a frase do chat) em amarelo."""
    linhas = [limpo(l) for l in gancho.split("|")]
    return linhas[0] + "".join("\\N{\\c" + AMARELO + "}" + l for l in linhas[1:])

def escrever_ass(palavras, gancho, selo, dur, destino):
    out = [CAB]
    out.append(f"Dialogue: 2,{t_ass(0)},{t_ass(dur)},Selo,,0,0,0,,{{\\alpha&H4D&}}{limpo(selo)}\n")
    out.append(f"Dialogue: 1,{t_ass(0)},{t_ass(dur)},Gancho,,0,0,0,,"
               r"{\fad(120,0)\t(0,160,\fscx106\fscy106)\t(160,320,\fscx100\fscy100)}" + gancho_ass(gancho) + "\n")
    for bloco in blocos_de(palavras):
        for k, (ini, fim, _) in enumerate(bloco):
            fim_ev = bloco[k + 1][0] if k + 1 < len(bloco) else fim
            texto = " ".join((f"{{\\c{AMARELO}}}" if j == k else "{\\c&HF5F7FA&}") + limpo(p[2])
                             for j, p in enumerate(bloco))
            out.append(f"Dialogue: 0,{t_ass(ini)},{t_ass(fim_ev)},Legenda,,0,0,0,,{texto}\n")
    destino.write_text("".join(out), encoding="utf-8")
```

(O `{\alpha&H4D&}` do selo é sintaxe padrão de ASS, mas não foi renderizado no meu teste, que usou o selo opaco.)

### Mudança 5: punch-in no pico e barra de progresso

Os dois já estão no filtro da mudança 3 [TESTADO: com `-ss 10 -t 22` o zoom cai no instante certo e a barra chega a ~66% no 14,5 s].

- Punch-in: ampliação de 115% (`scale=1242:-2,crop=1080:608`) de `t_pico - 0.3` a `t_pico + 1.2` s, com corte seco. É barato (uma ramificação a mais), ao contrário do zoom lento contínuo com `zoompan`, que no meu teste ficou cerca de 2 vezes mais lento (máquina carregada, número ruidoso). Não achei estudo que mostre ganho.
- Barra de progresso: 6 px, magenta de marca `#FF2E88`, na base do vídeo. [HIPÓTESE]: a ideia é que a barra dá noção de que o clipe é curto e acaba logo; não achei dado.

### Mudança 6: abertura com teaser do pico (opcional)

Repetir 1,5 s do pico no começo, antes do clipe, para o primeiro quadro já ter ação. [HIPÓTESE]; o AutoClip chama isso de "visible consequence first" sem números. Teste só depois das mudanças 1 a 4.

Filtro [TESTADO apenas quanto à duração: 22 s + 1,5 s = 23,5 s; não avaliei a qualidade visual]. `TP` é o pico em segundos no recorte:

```
[0:v]fps=30,split=2[main][tz];
[tz]trim=start=TP-0.4:end=TP+1.1,setpts=PTS-STARTPTS[tzv];
[main]setpts=PTS-STARTPTS[mv];
[tzv][mv]concat=n=2:v=1:a=0[vv];
[0:a]asplit=2[am][at];
[at]atrim=start=TP-0.4:end=TP+1.1,asetpts=PTS-STARTPTS[atz];
[am]asetpts=PTS-STARTPTS[amm];
[atz][amm]concat=n=2:v=0:a=1[aa]
```

Com o teaser, some 1,5 s a todos os tempos do `.ass`, ao `t_pico` e à duração da barra.

### Mudança 7: telemetria de A/B

Sem isso não há como saber o que funcionou. Acrescente ao `picos.csv` (ou a um CSV por clipe) as colunas: `variante_duracao` (22 ou 35), `variante_gancho` (categoria e modelo), `variante_legenda` (caixa alta ou frase), `layout` (A ou B), `t_pico_audio`, `ini_recorte`, `dur_final`. Depois de 24 a 48 h de postado, exporte do YouTube Studio (Shorts) e do TikTok e junte pelo nome do arquivo.

Método mínimo [HIPÓTESE, sem fonte]: mude **uma** variável por vez; pelo menos 30 clipes por variante por plataforma; compare medianas, não médias; use "viewed vs. swiped away" e "average percentage viewed" no YouTube, tempo médio assistido e "full video views" no TikTok, e envios por alcance no Instagram (regra 2). Atribua a variante por número do clipe (par ou ímpar) para não escolher na mão.

### Mudança 8: layout B (facecam em cima, jogo embaixo), por streamer

Só vale para streamer com facecam num retângulo fixo. [HIPÓTESE], esforço alto: precisa de um arquivo de configuração por streamer (`{"canal": {"cam": [x, y, w, h]}}`), e a facecam típica tem poucas centenas de px, então ampliar além de ~2x fica mole (use `flags=lanczos` e limite a largura a 720 px). O orçamento de altura aperta: gancho de 1 linha (120) + cam 720x405 + jogo 1080x608 já soma 1133 dos 1170 px úteis, sem espaço para legenda; a legenda teria de ir **sobre** o terço inferior do jogo e o gancho sobre a cam. Comando-base [esta forma exata NÃO foi executada; uma variante parecida, com a cam em 1080x608 e o jogo recortado em 1080x1080, rodou sem erro num vídeo sintético]:

```
[0:v]fps=30,split=3[a][b][c];
[a]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,boxblur=6:1,scale=1080:1920,eq=brightness=-0.10[fundo];
[b]crop=CAM_W:CAM_H:CAM_X:CAM_Y,scale=720:405:flags=lanczos[cam];
[c]scale=1080:-2[jogo];
[fundo][cam]overlay=180:276[v1];
[v1][jogo]overlay=0:700[v]
```

Teste primeiro com um streamer só e compare com o layout atual no mesmo tipo de momento.

### Mudança 9: fade de áudio nas pontas

`-af "afade=t=in:d=0.1,afade=t=out:st={dur-0.25}:d=0.25"` evita estalo no ponto do loop e no corte. [HIPÓTESE], baixo valor; não testei.

---

## 3. Margens seguras: o que as fontes dizem e o que adotamos

Nenhuma plataforma publica números para post orgânico; as fontes abaixo vêm de anúncios ou de medição de terceiros. As margens de anúncio (base ~660 a 672 px) são maiores porque o anúncio tem botão de chamada e aviso.

| Fonte | Tipo | Data | Topo | Base | Esquerda | Direita |
|---|---|---|---|---|---|---|
| TikTok, modelo "In-Feed Standard" medido por [ManyPixels](https://www.manypixels.co/blog/social-media-design/tiktok-ad-specs) | medição de modelo oficial de anúncio, [VENDOR] | 11/11/2026 | 240 | 660 (1.014 no pior caso, com âncora e legenda de 4 linhas) | 120 | 120 mais coluna de ícones de 180 px |
| Meta, anúncios em Stories e Reels ([página oficial](https://www.facebook.com/business/help/980593475366490), só o título abriu) | percentuais citados por guias de terceiros | acesso 18/11/2026 | 14% (~270) | 35% (~672) | 6% (~65) | 6% (~65) |
| [Adaptly](https://adaptlypost.com/blog/social-media-safe-zones-2026-complete-guide), orgânico | estimativa, [VENDOR] | sem data (cita 2026) | TikTok 108, Reels 210, Shorts 120 | TikTok 320, Reels 310, Shorts 300 (360 com descrição aberta) | TikTok 60 | TikTok 120, Reels 84, Shorts 96 |
| [Reap](https://reap.video/blog/short-form-video-safe-zones), "conservador" para as três | recomendação editorial, não oficial, [VENDOR] | 07/09/2026 | ~288 | 480 a 672 | 108 a 162 | 108 a 162 |
| Google Ads, vídeo vertical ([ajuda](https://support.google.com/google-ads/answer/9128498)) | os números estão numa imagem que não consegui ler; terceiros citam 288, 672, 48, 192 | acesso 18/11/2026 | | | | |

**Adotado (conservador para orgânico):** topo 270; texto nunca abaixo de y = 1440 (base de 480); a legenda termina em 1422; texto a 164 px das bordas laterais para escapar da coluna de ícones; o vídeo em si pode ocupar a largura toda. Confira num celular real em cada app antes de fixar: o TikTok muda a interface conforme o tamanho da legenda e do formato de anúncio (ManyPixels e Reap avisam o mesmo).

---

## 4. Títulos e legendas: 15 modelos para cortes de GTA 6

Princípios:

- **[OFICIAL]** (YouTube Help, dicas de título): o título representa o vídeo, é curto e põe a palavra-chave primeiro; caixa alta e emoji com moderação; episódio e marca no fim. Há dois tipos: o "pesquisável" (diz o que o espectador vai ver) e o "intrigante" (desperta curiosidade).
- **[OFICIAL]** A política de isca enganosa (regra 13) vale para título, thumbnail e descrição: cada modelo abaixo diz a condição para usar.
- **Observado, não oficial:** os títulos de cortes brasileiros que apareceram em buscas seguem um molde: nome do streamer primeiro, caixa alta, verbo no passado, virada ("MAS FOI PEGO!"), exagero ("JOGADA DO SÉCULO"), e às vezes um rótulo entre colchetes ou um sufixo "| Cortes do X" (seção 6). Isso conflita com "caixa alta com moderação" do YouTube; recomendo caixa alta no gancho de tela e no título de Short, e frase normal no título de vídeo longo, e medir.
- Todos sem spoiler de história. Se o clipe mostrar trama, use o selo SPOILER (`marca/identidade.md`).
- `[STREAMER]` = nome do streamer; `[N]` = número real tirado do `picos.csv`.

| # | Fórmula | Título de exemplo | Gancho na tela (linha 1 / linha 2) | Use só se o clipe mostrar |
|---|---|---|---|---|
| 1 | Dado do chat (automático) | O chat explodiu: 40 "KKKKK" em 15 segundos | O CHAT NÃO SEGUROU / KKKKK x40 | pico com risada dominante no log |
| 2 | Primeira vez | [STREAMER] vendo o primeiro minuto de GTA 6 | PRIMEIRO MINUTO / DE GTA 6 | os primeiros minutos do jogo |
| 3 | Pergunta de curiosidade | O que foi isso? O chat não entendeu a cena de [STREAMER] | O QUE FOI ISSO? / ?? x[N] | confusão real no chat e na fala |
| 4 | Expectativa x resultado | Ele achou que ia dar certo no GTA 6 | DEU RUIM / NO CHAT: F x[N] | uma falha clara |
| 5 | Contagem de reação | [N] mensagens em 10 segundos: o pico do chat de [STREAMER] | O CHAT EXPLODIU / [N] MSGS EM 10 s | qualquer pico (modelo genérico seguro) |
| 6 | Superlativo com limite | A fuga da polícia mais absurda do primeiro dia de GTA 6 | COMO ELE ESCAPOU? / | uma fuga de verdade |
| 7 | Bug | O bug mais engraçado do dia 1 de GTA 6 | ISSO NÃO ERA / PRA ACONTECER | bug real e visível no clipe |
| 8 | Silêncio e explosão | [STREAMER] ficou mudo 5 segundos. Aí o chat explodiu | SILÊNCIO... / E AÍ? | silêncio de fato (confira a transcrição) |
| 9 | Ranking (compilação) | Top 5 picos do chat no lançamento de GTA 6 | TOP 5 / DO CHAT | 5 clipes reais do dia |
| 10 | Versus | [STREAMER] vs. o trânsito de GTA 6 | [STREAMER] VS / O TRÂNSITO | cena de trânsito |
| 11 | Citação do chat | "Meu Deus" 15 vezes no chat de [STREAMER] | NO CHAT: / MEU DEUS x15 | a frase aparecer no log |
| 12 | Pesquisável | GTA 6: como é a primeira hora? Reação ao vivo | GTA 6 / PRIMEIRA HORA | trecho da primeira hora |
| 13 | Selo sem spoiler | Sem spoiler: a reação do chat ao mapa de GTA 6 | SEM SPOILER / O CHAT PIROU | nenhuma cena de história |
| 14 | Série numerada | O chat pirou no GTA 6 \| #12 \| Cortes de [STREAMER] | O CHAT PIROU / #12 | consistência de canal (número no fim, como pede o YouTube) |
| 15 | Pergunta ao público | Você teria feito diferente? [STREAMER] no GTA 6 | E VOCÊ? / FARIA DIFERENTE? | uma decisão discutível do streamer |

Legenda (descrição) de cada post, com crédito (regra do tom de voz em `marca/identidade.md`):

```
{TÍTULO}
Live: {STREAMER}, twitch.tv/{canal}. Clipe com crédito {e com autorização, se houver}.
Assista completo: {link do canal ou do VOD}
{Sem spoiler da história | SPOILER: cena de história}
```

Hashtags: não achei evidência de efeito de quantidade ou de hashtag específica; use poucas e relevantes (jogo, streamer, "cortes").

---

## 5. Thumbnails das compilações (YouTube, 1280x720)

Valem para o vídeo longo do `compilar.py` (1920x1080 com cartelas de 1,5 s). Para Shorts, TikTok e Reels a "capa" é um quadro de 1080x1920: use o quadro do pico com o gancho em texto no centro.

**Base oficial** [OFICIAL, [YouTube Help, dicas](https://support.google.com/youtube/answer/12340300)]: regra dos terços, texto legível, design simples, imagem grande, emoção no rosto para público casual. **Base de dados** [VENDOR, [vidIQ, 14/07/2026](https://vidiq.com/blog/post/youtube-thumbnail-tips/)]: em 500 vídeos de alta performance de 30 nichos publicados até 30/06/2026, 69% tinham rosto (80% entre os 50 que mais superaram), a mediana de texto era 5 palavras e 56% usavam alto contraste; a própria vidIQ avisa que isso mostra o que tinham em comum, não o que causa clique. Recomendações dela: texto de 3 a 5 palavras em sans pesada com contorno, rosto de um quarto a um terço do quadro, ponto focal único, nada importante no canto inferior direito (marca de duração), checar em tamanho de feed. Formato: 1280x720, JPG ou PNG, até 2 MB, largura mínima 640.

Especificação:

| Item | Valor |
|---|---|
| Arquivo | 1280x720, JPG qualidade alta, até 2 MB |
| Fundo | quadro do pico do clipe nº 1 do ranking (instante do pico de áudio, mudança 1), recorte 16:9 com zoom suave, contraste +15% e saturação +25% |
| Rosto/reação | recorte da facecam do mesmo instante (config por streamer, a mesma da mudança 8) em quadrado de 420x420 em x=820, y=190; ocupa ~14% da área. Se não houver facecam detectável, trocar por segundo quadro do gameplay, sem rosto |
| Texto | 2 a 4 palavras em Anton, **amarelo `#FFD400`** com contorno carvão `#0B0B12` de 10 px, canto superior esquerdo (x=48, y=40), tamanho mínimo 100 px (a 168x94 de feed de celular o texto ainda fica com ~12 px de altura) |
| Selo | "TOP 5" em fundo magenta `#FF2E88`, texto carvão (contraste 5,6:1, `identidade.md`), x=48, y=190 |
| Áreas livres | canto inferior direito 200x70 (duração); bordas de 40 px (corte do feed no celular) |
| Faixa de leitura | faixa carvão a 45% de opacidade atrás do texto (y 0 a 300) |
| Verdade | o quadro tem de existir no vídeo; não usar arte, logo nem imagem oficial de GTA 6 (risco de marca, `identidade.md`); sem violência gráfica (a política de monetização de games do YouTube é severa com violência gráfica em thumbnail e nos 7 primeiros segundos, segundo `identidade.md` e [Dexerto](https://www.dexerto.com/gta/youtube-updates-gaming-violence-monetization-rules-ahead-of-gta-6-launch-3405945/) [IMPRENSA]) |
| Setas e círculos | no máximo 1 ou 2 (vidIQ) |

Comando [TESTADO com um vídeo sintético: gera 1280x720 com texto, selo e recorte de "facecam"; troque a fonte por Anton]:

```bash
ffmpeg -y -ss $T_PICO -i clipe.mp4 -filter_complex "
[0:v]split=2[g][c];
[g]crop=1440:810:0:135,scale=1280:720,eq=contrast=1.15:saturation=1.25,drawbox=x=0:y=0:w=1280:h=300:color=0x0B0B12@0.45:t=fill[bg];
[c]crop=480:480:$CAM_X:$CAM_Y,scale=420:420[cam];
[bg][cam]overlay=x=820:y=190[v1];
[v1]drawtext=fontfile=$FONTE:text='O CHAT PIROU':fontsize=104:fontcolor=0xFFD400:borderw=10:bordercolor=0x0B0B12:x=48:y=40,
drawtext=fontfile=$FONTE:text='TOP 5 DO DIA':fontsize=64:fontcolor=0x0B0B12:box=1:boxcolor=0xFF2E88:boxborderw=18:x=48:y=190[o]" \
  -map "[o]" -frames:v 1 -q:v 2 thumb.jpg
```

(No comando de teste o recorte do rosto ficou em y=250; subi para y=190 aqui para não encostar na marca de duração. Esse y=190 não foi renderizado.)

**Três variantes para o "Test & Compare"** (regra 15; o vencedor sai por tempo de exibição, então a variante mais chamativa não necessariamente vence):
- A, "dado": texto "TOP 5 DO CHAT" + selo, sem rosto.
- B, "reação": facecam grande (até 33% do quadro) + 2 palavras ("NÃO ACREDITOU").
- C, "cena": quadro do jogo em zoom + 1 palavra ("PIROU").

**Fluxo Short para compilação** (YouTube, [Social Media Today, 19/07/2026](https://www.socialmediatoday.com/news/youtube-offers-tips-on-working-with-shorts-videos/825096/) [IMPRENSA citando fala oficial de Julia Lee Harter]): o Short deve ter o link de "Related Videos" para a compilação, apontar para o link ou mostrar a thumbnail, e os primeiros segundos do vídeo longo "should confirm they made the right choice". Para a compilação: melhor momento nos primeiros 30 s, capítulos (o `compilar.py` já gera o `.txt`), voz própria no começo e entre os clipes (seção 0, itens 2 e 3), e créditos dos canais na descrição.

---

## 6. Padrões de canais de cortes no Brasil (o que consegui verificar)

**Aviso:** não consegui abrir páginas de canais, então **não há dados de frequência, duração, visualização ou estilo de legenda medidos**. Abaixo, o que apareceu, com a fonte de cada coisa.

- **Há canais oficiais e canais de fã.** "Cortes do Gaules [OFICIAL]" e "Cortes do Flow [OFICIAL]" existem; vídeos do Gaules apontam para o canal de cortes, o de VODs e o principal na descrição (resultado de busca, 18/11/2026). Também aparecem canais de fã ("Gaules e as Mulas" se descreve como canal de cortes da tribo; "Cortes dos Streamers [OFICIAL]" mostra e-mail comercial; "Cortando Streamer"). Um blog de vendor de 2022 diz que canais de cortes costumam ser do dono do canal original ou de parceiro estratégico, e cita "Talk Flow" como grande canal não oficial com autorização do podcast ([invideo, 28/05/2022](https://invideo.io/pt/blog/canal-de-cortes-no-youtube-como-criar-um-e-comecar-a-ganhar-dinheiro/) [VENDOR]). Isso ajuda a explicar por que nenhuma dessas fontes mostra canal de cortes 100% automático e sem acordo.
- **Títulos observados** (resultados de busca, sem número de views): "GAULES TENTOU FAZER A JOGADA DO SÉCULO MAS FOI PEGO!" ([vídeo](https://www.youtube.com/watch?v=ooCqAba8KnE)), "ELE OPEROU O ZYWOO NO ULTIMO ROUND" ([vídeo](https://www.youtube.com/watch?v=3C_XxFAFnxI)), "GAULES FALA PELA 1° VEZ SOBRE SUA RIVALIDADE COM O XQC NA TWITCH" ([vídeo](https://www.youtube.com/watch?v=L-YrbMH9EU8)), "PAVINATTO PERDE a PACIÊNCIA no Flow" (Cortes do Flow, via [Recapio](https://recapio.com/digest/pavinatto-perde-a-paciencia-no-flow-by-cortes-do-flow-oficial)), "CASIMIRO REAGE: VAI DAR NAMORO #01 ... | Cortes do Casimito" (via Wikipédia). Padrão comum: caixa alta, nome do streamer ou do convidado primeiro, verbo no passado ou no presente de narração, virada no fim, exagero, às vezes número de episódio e sufixo do canal. Esses são vídeos de YouTube, não Shorts, e a maioria é de CS ou podcast, não GTA.
- **Frequência e duração** só aparecem em vendor: "mínimo de 5 clipes por semana, em ao menos duas plataformas" e "40 a 90 s é o ponto certo em 2026" para Reels e TikTok ([Cut.pro, 29/05/2026](https://cut.pro/pt-BR/blog/clipar-streamer-crescer-do-zero-2026) [VENDOR]), sem dado; contradiz a faixa de 21 a 34 s do OpusClip (regra 4). Tratar como opinião.
- **Crédito:** o mesmo guia sugere que o **nome da conta** carregue o do streamer ("Melhores do [Streamer]") e que, depois de 3 a 4 semanas entregando, o clipador mande os clipes ao streamer para ele compartilhar [VENDOR]; não fala de crédito dentro do vídeo. Nossa mudança 3 põe o crédito no selo e a descrição repete.
- **Pagamento a clipadores no Brasil:** Kick paga cerca de US$ 40 a 50 por 100 mil views para espalhar cortes no TikTok e no Shorts, e o MrBeast US$ 50 por 100 mil, segundo [Cut.pro, 03/07/2026](https://cut.pro/pt-BR/blog/streamers-pagam-clipadores-mercado-2026) [VENDOR citando Tubefilter]; o mesmo post diz que no Brasil os valores ainda são menores e não dá faixa. Outro blog fala em R$ 15 a R$ 40 por clipe para criadores pequenos [VENDOR, sem fonte]. Para canal automático sem acordo, não conte com isso.

---

## 7. Recursos públicos encontrados e se confiar

| Recurso | O que é | Confiável? |
|---|---|---|
| [YouTube Help: conteúdo reutilizado](https://support.google.com/youtube/answer/1311392) | política de monetização com exemplos de clipes e compilações | Sim, oficial. Leitura obrigatória |
| [YouTube Help: A/B test de títulos e thumbnails](https://support.google.com/youtube/answer/13861714) | regras do Test & Compare | Sim, oficial |
| [Instagram para Criadores, originalidade](https://creators.instagram.com/blog/rewarding-original-creators-on-instagram) | o que conta como original (30/04/2026) | Sim, oficial |
| [TikTok, Integridade e Autenticidade](https://www.tiktok.com/community-guidelines/en/integrity-authenticity/) | regra de reuso e inelegibilidade para o For You | Sim, oficial |
| [Meta, texto e zona segura em anúncios de Reels](https://www.facebook.com/business/help/980593475366490) | números oficiais de margem para anúncios | Oficial, mas só o título abriu para mim |
| [clippy](https://github.com/hamzaskewl/clippy) (GitHub, MIT) | detector de pico de chat da Twitch com clipe automático; compara rajada de 5 s com base de 30 s (limiar adaptativo de 1,5x a 2,5x), mínimo de 500 espectadores, e manda as últimas 50 mensagens ao Claude Haiku 4.5 para classificar o momento | Código aberto, pequeno e não auditado por mim. A ideia de janela curta contra base longa é parecida com a nossa; a classificação por LLM é paga. Só leitura |
| [Ssemble Clip Rewards](https://www.ssemble.com/pt/clip-rewards) | mercado de campanhas pagas por mil views verificadas (TikTok, Reels, Shorts, X) | **Cautela.** Faixa de pagamento inconsistente na própria página (US$ 0,10 a 15 no topo, ~0,35 a 4 no FAQ); pagamento só após 1.000 views e revisão de 5 dias; Brasil fora da lista de 51 países de saque do Stripe, só entra campanha de parceiro; números de usuários sem fonte. [VENDOR] |
| [Cut.pro, blog em português](https://cut.pro/pt-BR/blog/pedir-autorizacao-cortar-streamer-2026) | modelo de mensagem para pedir autorização, base na Lei 9.610/98, acordo de uma página com prazo de retirada de 48 h | Útil como modelo; é vendor e não é parecer jurídico |
| [OpusClip](https://www.opus.pro/blog/tiktok-length-format-retention-data), [vidIQ](https://vidiq.com/blog/post/youtube-thumbnail-tips/) | estudos de vendor | Úteis para hipóteses; amostra pequena ou sem método |
| [Buffer, 1,1 milhão de TikToks](https://buffer.com/resources/longer-tiktoks-get-more-views-data/) | estudo de duração x alcance | Amostra grande; confunde duração escolhida com causa |
| Artefatos públicos de claude.ai | busca restrita ao domínio claude.ai por "short-form video captions hook safe zone clipping" | **Nada útil.** Voltaram 3 artefatos sem relação (resenha de uma ferramenta de vídeo, um framework de NPC, um texto sobre pistas de localização). Não li o conteúdo. O mecanismo de busca não indexa bem esses links; se você tiver um link específico, passe e eu leio |

Programas pagos por view (Whop, Vyro, Kick Clipping Program, campeonatos de cortes) estão descritos em `pesquisa/regras-plataformas.md`; nada disso foi reverificado aqui.

---

## 8. Conflitos com `marca/identidade.md` para você decidir

| Ponto | `identidade.md` | Esta pesquisa | Sugestão |
|---|---|---|---|
| Legenda | frase normal, só a palavra de impacto em caixa alta | caixa alta (como hoje) | teste A/B; nenhum dado decide |
| Posição do crédito | logo abaixo do vídeo, y ~1290 | linha do selo, y 272 | a legenda de 2 linhas colide com y 1290 |
| Duração do gancho | some em 2 a 3 s | fixo no clipe inteiro (pedido do dono) | teste A/B |
| Faixa do gancho | y 300 a 620, Anton 100 px | y 330 a 550, Anton 84 px, caixa de 752 px | se Anton a 100 px couber em 752 px de largura, mantenha 100 |
| Vídeo | centralizado (y 656 a 1264) | y 576 a 1184 | espaço para o gancho |

## 9. Próximos testes, em ordem

1. Instalar Anton e Montserrat ExtraBold no WSL e rodar o layout v2 num clipe real do `gaules-20261118-023651.mp4` para ver as quebras de linha reais (meu teste usou DejaVu e vídeo sintético).
2. Ligar a telemetria (mudança 7) antes de mudar qualquer coisa, para ter a linha de base do clipe de hoje.
3. Mudanças 1 e 2 juntas por 2 dias; depois 4; depois 5.
4. Pedir autorização por escrito ao streamer antes de publicar (seção 0).
5. Conferir no celular, em cada app, as margens da seção 3.
