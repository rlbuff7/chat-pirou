# Postagem automática (roteiro de cada rodada)

Autorizado pelo dono em 18/11/2026, ~16:20: "quero deixar automático, sem eu ter que falar nada". Vale para TikTok, YouTube Shorts e Instagram Reels da conta Chat Pirou. Qualquer coisa fora deste roteiro: parar e perguntar.

Ferramenta: `clipador/postagem.py` (rodar com `.venv/bin/python`). Registro: `C:\Users\<voce>\ChatPirou\clipes\postados.csv`. Textos: `marca/hashtags-e-titulos.md`.

## Ritmo

- **Um post a cada 1h30** em cada rede, de 09:00 a 01:00 (~10 por dia). Mudado pelo dono em 19/11 ~17:00 ("tente postar a cada 1h30, você tá demorando"); antes eram 6 por dia com 1 h. Conferir com `postagem.py hoje`.
- **Fila pronta:** deixar sempre 2 ou 3 cortes já feitos (vídeo em `Videos\chatpirou-postar` + `.txt`), para a rodada só postar. Fazer os cortes seguintes entre uma postagem e outra.
- Nunca postar clipe fraco só para bater número; se a fila zerar, avisar o dono.
- Instagram: crédito por escrito, **sem marcar o @ do streamer** (dono, 19/11: "sem marca não precisa").
- **Nunca ficar parado** (dono, 19/11 ~18:20): entre um post e outro, procurar o que está em alta (`clipador/virais.py` + Shorts/Reels mais vistos de GTA 6 do dia e o que o dono manda na DM), atualizar `pesquisa/virais-gta6.md` e fazer nossos cortes no mesmo formato a partir das lives (cellbit, Davy Jones, Paulinho, Lipão, alanzoka). Nunca reaproveitar o vídeo de outro canal.
- **Janela do Chrome minimizada** (`innerWidth` = 0 no `javascript_tool`): não postar. Com a janela minimizada a digitação aparece na tela mas não chega ao formulário (em 19/11 o TikTok publicou o 12 com a legenda "12-barco-davyjones"). Pedir ao dono para restaurar a janela.
- Nunca o mesmo clipe duas vezes na mesma rede (o `candidatos` já esconde os postados).
- Um clipe por rodada, postado nas três redes.

## Rodada, passo a passo

1. **Contagem.** `postagem.py hoje`. Se o último post foi há menos de 1h30, só reagendar para a hora certa.
2. **Candidatos.** `postagem.py candidatos --horas 6`. Se não houver nada bom, aumentar para `--horas 12`. Se ainda não houver, pular a rodada e avisar.
3. **Escolher um.** Critérios, em ordem:
   - é jogo de GTA 6 acontecendo (não pausa, almoço, propaganda, encerramento de live, tela de menu);
   - dá para entender sem contexto em 3 segundos;
   - variar o streamer (não 3 seguidos do mesmo);
   - **preferir o cellbit** quando houver clipe limpo dele (pedido do dono em 19/11: no Reels o 04 do cellbit fez 1.961 views; os do alanzoka, 171 e 232). O cellbit joga muita história: conferir com o mesmo rigor;
   - mais força do chat (`força` = mensagens / base).
4. **Conferir.** `postagem.py ver CLIPE` e olhar os 4 quadros (Read nas imagens) e a fala. Pular se tiver:
   - **spoiler de história** (cutscene, faixas pretas de cinema sem HUD, diálogo de enredo, tipo `historia`): proibido até 25/11;
   - nudez, violência gráfica na capa ou nos primeiros segundos;
   - live da Rockstar (oficial) ou conteúdo de outro canal sendo assistido;
   - xingamento pesado contra alguém, assunto pessoal do streamer.
5. **Gancho.** Se o gancho atual for genérico ("O CHAT EXPLODIU / N MSGS", "CLIMA DE HYPE"), escrever um específico (2 linhas curtas em caixa alta, só o que a fala, os quadros ou o chat confirmam) e rodar `postagem.py refazer CLIPE "LINHA 1" "LINHA 2"`. O vertical refeito sai em `clipes/postar/<canal>/`.
   **Formato que bomba (pesquisa de 19/11, `pesquisa/virais-gta6.md`):** gancho/título de **descoberta** ("DÁ PRA ... NO GTA 6", "O JASON TEM ...") ou **provocação** (pergunta curta) que não entrega o fim; corte de 20 a 30 s; preferir descobertas do jogo, bugs ("injogavel" no chat), tentativas de repetir o trailer.
   **Referência do dono (DM de 19/11, pescaria do Davy, 152 mil curtidas):** momento "fora de contexto" engraçado em 10 a 15 s, sem edição, legenda que provoca sem explicar. Detalhes em `plano/canais-por-criador.md`. A DM do Instagram é só para ler os vídeos que o dono manda (nunca responder).
   Live do YouTube que acabou há pouco ("post_live"): o `yt_corte.py baixar` já cai sozinho no modo de pedaços.
6. **Textos** (sem emoji, padrão de `hashtags-e-titulos.md`): título do Shorts com streamer + "GTA 6" nos primeiros 40 caracteres; legenda TikTok/Reels com primeira linha, `Live do <streamer>: twitch.tv/<canal>`, chamada de enviar e 5 hashtags; descrição do YouTube com crédito, aviso de canal de fã e `#GTA6 #<streamer> #Shorts`. Salvar em `C:\Users\<voce>\ChatPirou\clipes\NN-nome.txt` (NN de `postagem.py proximo`).
7. **Preparar.** `postagem.py preparar VIDEO NN-nome` (comprime para menos de 9,5 MB e copia para `Videos\chatpirou-postar`).
8. **Postar** no Chrome **Browser 1** (`chatpirou924@gmail.com`), **numa aba só** (a digitação só funciona na aba da frente; navegar a mesma aba de rede em rede). Se o `file_upload` recusar o arquivo, a sessão perdeu a pasta: pedir ao dono `/add-dir C:\Users\<voce>\Videos\chatpirou-postar`. Se a captura de tela travar, seguir por `find` e `javascript_tool`. Ordem:
   - **TikTok:** `tiktok.com/tiktokstudio/upload` → `file_upload` no input de vídeo (achar com `read_page`/`find`: aparece como `button type="file"`) → descrição (apagar o nome do arquivo com `ctrl+a` e `BackSpace`; Backspace repetido perde teclas; hashtags uma a uma, 2 s entre elas, com espaço) → **conferir os blocos `[data-block=true]` por JS** (já sumiram o crédito e a 1ª hashtag) → conferir público "Todos", sem selo de IA e de publicidade → Publicar (e "Publicar agora" se perguntar). Pegar o link em `a[href*="/video/"]` na página de conteúdo.
   - **YouTube:** `studio.youtube.com/channel/UCWb9jNoPmEI3qkG9IAurcrQ/videos/upload?d=ud` → `file_upload` → título, descrição (depois do título, a caixa de descrição muda de lugar: medir de novo os `#textbox` e conferir `document.activeElement` antes de digitar) → "No, it's not made for kids" → Show more: AI "No", Category "Gaming", Game title "Grand Theft Auto VI" → Next x3 → Public → Publish. Copiar o link do aviso.
   - **Instagram:** Criar → `file_upload` no input do diálogo → recorte **Original** (vem 1:1 por padrão) → capa: arrastar para um quadro com o gancho → legenda → rótulo de IA desligado → Compartilhar → esperar "Reel compartilhado".
9. **Registrar** cada rede: `postagem.py registrar NN-nome CLIPE REDE LINK`.
10. **Limpar** (dono, 19/11: "o que já foi postado vá apagando"): `postagem.py limpar --executar` apaga os vídeos dos posts que já saíram nas 3 redes (WSL de vez; cópias do Windows para a Lixeira). Ficam o `.txt`, o `postados.csv` e os `.reacoes.txt`.
11. **Avisar o dono** em 2 linhas (o que saiu, links) e agendar a próxima rodada.

## Parar e avisar (não insistir)

**Exceção decidida pelo dono em 19/11:** reivindicação do Content ID só de **música** (rádio do jogo), em que o YouTube diz "não afeta o alcance" e "não é strike", pode publicar. Qualquer outra reivindicação (vídeo, bloqueio, alcance restrito, strike): parar e avisar.

No YouTube, `@canal` na descrição vira menção e quebra o link `youtube.com/@canal`: escrever só "Live do X no YouTube: @canal". Nunca apertar Escape no diálogo de envio (fecha o diálogo).

Captcha, pedido de login ou código, verificação de conta, termo para aceitar, aviso de direitos autorais ou violação, post removido ou restrito, mudança de tipo de conta, ou o mesmo erro duas vezes. Nunca mandar DM. Nunca clicar em "Promover"/"Promote" (é pago).

## Noite do lançamento (18 para 19/11)

- Às 22:30: `./parar.sh` e ligar a noite com `setsid nohup .venv/bin/python auto_lancamento.py --lista candidatos-noite.txt --ate 03:00 --max 2 > logs/auto.out 2>&1 &` dentro de um `wsl.exe` em primeiro plano. O WSL precisa estar acordado (VS Code ou terminal WSL aberto).
- Não cortar a live oficial da Rockstar (02:00).
- A partir de 00:00 as lives entram na história: redobrar o passo 4.
