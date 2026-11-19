# Repositórios do GitHub que podem ajudar no alcance (pesquisa de 19/11/2026)

Feita por um agente de pesquisa, só leitura: nada foi instalado, clonado ou rodado. As estrelas e datas
são de 19/11/2026. Nenhum desses projetos traz alcance sozinho. O que eles mudam é a **escolha do
momento**, o **custo de produção** e a **medição**. Nada de terceiros entra no projeto sem ok do dono
(regra 9).

## Os 5 primeiros a considerar

| # | O quê | Por quê | Custo e risco |
|---|---|---|---|
| 1 | **Ideia do [chopify](https://github.com/mehbul/chopify)** (MIT, ~107 estrelas, novo) | Junta áudio (peso 0,30), movimento (0,25), transcrição (0,25) e chat (0,20) para achar o momento, além de filtrar anúncio. Dá para copiar a ideia no `clip_watcher.py` sem instalar nada. | Projeto jovem, de um mantenedor só. Copiar a ideia não tem risco. |
| 2 | **[TwitchDownloader](https://github.com/lay295/TwitchDownloader)** (MIT, ~4,1 mil estrelas) | Baixa o chat completo de VODs antigos para calibrar o detector com dado real (chatters únicos, emotes) e usar como gabarito os cortes que deram view. | Endpoints não oficiais da Twitch. Baixar só o chat é leve. |
| 3 | **Heatmap do yt-dlp + Get Clips da Twitch** | Dois sinais grátis do que o público achou bom: o gráfico "mais assistidos" do YouTube e os clips que os próprios espectadores criaram (`vod_offset`). | O heatmap não aparece em live recém-encerrada (já vimos isso). O Get Clips exige app da Twitch (Client ID/Secret, grátis), que o dono cria. |
| 4 | **[Clips Kitty / clips-studio](https://github.com/ColinGPT9/clips-studio)** (AGPL-3.0, ~434 estrelas) | Comparar os picks dele num VOD com os do clipador para ver o que o nosso perde (usa chatters únicos e tem guia de GTA 6). | Recomenda GPU NVIDIA; sem ela é lento. Instalador não assinado. Publicação via serviços pagos com link de afiliado. |
| 5 | **[analytix](https://github.com/parafoxia/analytix)** (BSD-3, ~45 estrelas) | Puxa retenção e views do próprio canal pela YouTube Analytics API oficial e fecha o ciclo "postei, medi, ajustei". | Precisa de projeto no Google Cloud e OAuth do canal (dono). Projeto pequeno e pouco ativo. |

## Outros úteis

- **Lives do YouTube faladas:** [openshorts](https://github.com/mutonby/openshorts) (MIT, ~9,4 mil estrelas;
  pede Gemini e é pesado) e [ViralCutter](https://github.com/RafaelGodoyEbert/ViralCutter) (GPL-3.0, pt-BR;
  pede GPU e é redundante com o que já temos).
- **Ritmo e legenda:**
  - [auto-editor](https://github.com/WyattBlue/auto-editor) (Unlicense) corta silêncio; o ganho em live é pequeno.
  - [pycaps](https://github.com/francozanardi/pycaps) (MIT) faz legendas animadas para A/B de estilo.
  - [whisperX](https://github.com/m-bain/whisperX) dá timestamps por palavra melhores, mas é mais pesado.
- **Gravar lives do YouTube com buffer:** o próprio streamlink (já instalado) grava live do YouTube. Isso
  deixaria o clipador cortar Davy, Paulinho e Lipão ao vivo.
- **Tendência:**
  - [trendspyg](https://github.com/flack0x/trendspyg) (MIT) lê o Google Trends; é scraping e pode quebrar.
  - O TikTok Creative Center é oficial (não é repositório).
- **Agendar e postar pelas APIs oficiais:** [Postiz](https://github.com/gitroomhq/postiz-app) (AGPL-3.0,
  ~42 mil estrelas).
  - O gargalo são as auditorias: TikTok e YouTube só deixam post **privado** até o app ser auditado, e a
    Meta exige App Review.
  - Só vale se postar à mão ficar inviável.

## Evitar

- Bots de view, curtida, seguidor, comentário ou DM; "engagement pods"; funis de "comente X".
- APIs privadas e uploaders por cookie na conta principal (instagrapi, social-auto-upload, tiktok-uploader).
- Bots de "compilação automática dos clips mais vistos" que só republicam (conteúdo reaproveitado perde alcance).
- Licenças não comerciais (SupoClip, Clipify) e instaladores `.exe` não assinados de contas novas.
- Qualquer ferramenta que peça login, senha ou cookie das contas.

Fontes oficiais consultadas pelo agente:
- [Content Posting API do TikTok](https://developers.tiktok.com/doc/content-posting-api-reference-direct-post)
- [`videos.insert` do YouTube](https://developers.google.com/youtube/v3/docs/videos/insert)
- [Get Clips da Twitch](https://dev.twitch.tv/docs/api/reference/clips)
- [Publicação de conteúdo do Instagram](https://developers.facebook.com/documentation/instagram-platform/content-publishing)
- Documentação do Postiz.

As regras de "conteúdo não original" do TikTok vêm de blogs, não da política oficial: confirmar antes de
decidir algo grande.
