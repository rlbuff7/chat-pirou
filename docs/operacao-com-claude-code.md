# Como a operação roda com o Claude Code

A Chat Pirou é tocada por uma pessoa com a ajuda do [Claude Code](https://claude.com/claude-code)
(assistente de programação no terminal) e da extensão Claude in Chrome. Este documento conta como isso
funciona e quais limites ficaram fixos. O dono decide e aprova; o assistente executa dentro de um roteiro escrito.

## Ciclo de cada rodada

O assistente roda em loop (`/loop`, que define sozinho o tempo até a próxima rodada) seguindo o
[roteiro de postagem](../plano/postagem-automatica.md):

1. **Conferir o ritmo** (`postagem.py hoje`): um post a cada 1h30 por rede, das 09:00 à 01:00.
2. **Escolher o clipe.**
   - Fontes: os candidatos do clipador (Twitch) ou as reações achadas pelo `yt_corte.py` (YouTube).
   - Prioridade: jogo acontecendo, entende sem contexto, variar o streamer.
3. **Conferir.** Olhar os quadros (folha de quadros) e a fala. Descartar:
   - spoiler de história (cutscene, missão);
   - nudez;
   - pausa ou almoço;
   - conteúdo de outro canal.
4. **Gancho e textos.**
   - Gancho de duas linhas no formato que viraliza (descoberta, provocação, curiosidade com guia).
   - Legenda e título por rede, sempre com crédito.
   - Legenda automática revisada à mão quando o reconhecimento de voz erra.
5. **Preparar** (`postagem.py preparar`): comprime o vídeo e copia para a pasta liberada para envio.
6. **Postar** pelo navegador, numa aba só, rede por rede: TikTok, YouTube Shorts e Instagram Reels.
7. **Registrar o link** (`postagem.py registrar`) e **limpar** os vídeos do que já saiu nas três redes
   (`postagem.py limpar --executar`).
8. **Avisar o dono** com os links e agendar a próxima rodada.

Entre uma rodada e outra o assistente não fica parado:
- roda o `virais.py` e lê os Shorts e Reels de GTA 6 em alta;
- olha as referências que o dono manda;
- atualiza `pesquisa/virais-gta6.md`;
- deixa 2 ou 3 cortes prontos na fila.

## Limites fixos

- **Login, senha, códigos e 2FA são só do dono.** O assistente nunca digita senha nem código.
- **Nada de mensagem em nome do canal:**
  - sem DM;
  - sem resposta;
  - sem curtir ou seguir em massa;
  - a caixa de mensagens só é lida, para ver as referências que o dono manda.
- **Nunca clicar em "Promover"** nem em nada pago.
- **Parar e perguntar** em qualquer coisa fora do roteiro:
  - captcha, verificação de conta ou termo para aceitar;
  - aviso de direitos autorais, post removido;
  - o mesmo erro duas vezes.
- **Apagar:**
  - só o que o dono liberou (os vídeos de posts já publicados);
  - o resto, item a item, de preferência pela Lixeira;
  - apagar um post publicado precisa de ok do dono.
- **API paga** (modelos de IA por API, serviços de corte na nuvem) só com ok e custo informado antes.

## Pegadinhas que custaram tempo (e a solução)

| Problema | Solução |
|---|---|
| Janela do Chrome minimizada: o texto aparece no campo, mas não chega ao formulário (o TikTok publicou com o nome do arquivo como legenda) | Conferir se a janela está restaurada (`innerWidth` > 0) antes de postar; se não estiver, pedir ao dono ou abrir uma janela nova |
| TikTok: digitar `@canal` abre a lista de menções e às vezes engole a linha | Digitar o crédito em partes, com espera; um espaço depois do `@canal` fecha a lista; conferir os blocos do editor antes de publicar |
| TikTok: apagar o nome do arquivo com Backspace perde teclas | `Ctrl+A` e um Backspace só |
| YouTube Studio: `Esc` fecha o diálogo de envio | Nunca apertar Esc; se fechar, reabrir pelo rascunho |
| YouTube: `@canal` na descrição vira menção e quebra um link `youtube.com/@canal` | Escrever "Live do X no YouTube: @canal" |
| Instagram: o Reels vem cortado em 1:1 | Trocar o recorte para "Original" e escolher a capa num quadro com o gancho |
| Live do YouTube recém-encerrada não deixa baixar só o trecho | `yt_corte.py baixar` cai no modo de pedaços (`post_live`) |
| Disco do WSL só cresce | Buffer rotativo no clipador e `postagem.py limpar` depois de cada post |
