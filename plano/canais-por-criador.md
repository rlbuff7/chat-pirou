# Um canal de cortes para cada criador (plano para depois)

Pedido do dono em 19/11/2026, ~16:20: "montar uma estrutura pra postar para cada canal corte específico para cada criador, por exemplo um canal somente para Davy Jones, outro só para cellbit". **Salvo para depois; nada foi criado.** Substitui a linha `@chatpirou_<streamer>` da seção 4 do `planejamento.md`, que só abria esse canal com autorização do streamer.

## Por que vale

- Quem segue corte de um streamer quer **só aquele streamer**. Um canal por criador deixa o algoritmo achar esse público mais rápido do que o canal geral.
- Os números já apontam isso: no Reels, o cellbit fez ~10x os outros (04: 1.975 views). O Reel que o dono mandou de referência (mayckon321, pescaria do Davy Jones) tem 152 mil curtidas em 19 h.
- É o formato que dá para vender ao streamer depois ("canal oficial de cortes do X"), item 2 da seção 7 do `planejamento.md`.

## Os canais

| Criador | Onde faz live | Como cortamos | Ordem |
|---|---|---|---|
| Davy Jones | YouTube `@Gameplayrj` | `yt_corte.py` (comentários, reações por áudio, baixar trecho) | 1ª leva |
| cellbit | Twitch `cellbit` | clipador (chat) | 1ª leva |
| Paulinho o Loko | YouTube `@PaulinhoLOKOoficial` | `yt_corte.py` | 2ª leva |
| Lipão | YouTube `@LipaoGamer` | `yt_corte.py` | 2ª leva |
| alanzoka | Twitch `alanzoka` | clipador (chat) | 2ª leva |

`@chatpirou` continua sendo o canal guarda-chuva, com os melhores de todos.

**Nome (proposta, conferir se está livre):** `@<criador>.chatpirou` no TikTok e no Instagram, `@<criador>chatpirou` no YouTube (ex.: `@davy.chatpirou`). Nome de exibição "Cortes do Davy Jones | Chat Pirou". A bio diz "Canal de fã, não oficial. Cortes das lives do Davy Jones" e traz o link da live. **Nunca** parecer a conta do próprio streamer (foto dele como avatar, nome igual, "oficial"): é falsidade ideológica nas regras das três redes e derruba a conta. O avatar é o balão do Chat Pirou com a cor do canal.

## Quando abrir

- **Gatilho:** 3 ou mais cortes bons por dia daquele criador durante 3 dias seguidos. Se não houver material, o canal fica parado, e conta nova parada morre.
- **1ª leva: Davy Jones e cellbit.** A 2ª leva só abre quando a 1ª estiver postando todo dia há 7 dias.

## O que só o dono faz

- Criar as contas, com senha, código, 2FA e telefone.
  - YouTube: um canal novo (conta de marca) dentro do mesmo Google `chatpirou924@gmail.com`. Não precisa de e-mail novo.
  - Instagram: "Adicionar conta" na Central de Contas (até 5 contas por login).
  - TikTok: e-mail novo ou o apelido `chatpirou924+davy@gmail.com`, que cai na mesma caixa.
- Decidir a questão do vídeo repetido (abaixo).
- Mandar a mensagem ao streamer (`marca/mensagens-streamers.md`) avisando do canal dedicado. Com um canal só dele, a chance de ele ver é maior, e é melhor que ele saiba pela gente.

## Decisão pendente: o mesmo corte em duas contas?

O `planejamento.md` diz "sem vídeo repetido entre contas": as redes marcam conteúdo repetido como não original e cortam o alcance das duas contas. Opções:

1. **Exclusivo (recomendado):** cada corte vai para um só lugar. O canal do criador fica com tudo dele, e o `@chatpirou` só recebe compilações e "melhores da semana" com vários streamers (formato de 60 s, que no YouTube puxou 28x no Lobby de Arquivos).
2. **Os melhores nos dois:** o `@chatpirou` também posta o top 1 do dia de cada criador, refeito com outro gancho e outro corte. O risco de "não original" é menor, mas existe.

## Limite real (capacidade)

- Hoje cada corte leva ~25 a 30 min para sair nas 3 redes pelo Chrome (fora achar e editar o corte). 5 canais × 3 redes × 6 posts = 90 envios por dia, o que não cabe.
- **Proposta:** cada canal de criador começa com **2 a 3 posts por dia**, só TikTok e Shorts (o Reels vem depois). O guarda-chuva cai para 3 por dia.
- Máquina: o clipador grava no máximo 2 lives da Twitch ao mesmo tempo (RAM). Os criadores do YouTube são cortados depois, do VOD, pelo `yt_corte.py`, o que não pesa.

## O que muda no código e no roteiro

- `postados.csv`: nova coluna `conta`. O `postagem.py hoje` passa a contar por conta e por rede.
- `postagem-automatica.md`:
  - ganha a lista de contas;
  - ganha o limite de cada conta;
  - ganha um passo novo antes de publicar: **conferir o @ da conta ativa**. Trocar de conta no mesmo Chrome é fácil e postar na conta errada também.
- Textos: um `hashtags-e-titulos.md` por canal, com as hashtags do criador.
- Um `NN-nome.txt` por post, com a conta de destino na primeira linha.

## Formato de referência mandado pelo dono (DM, 19/11)

Reel de `mayckon321`, "Essa pescaria @gameplayrj está um pouco estranha", com 152 mil curtidas em 19 h e 14 s de duração.
- **Como foi feito:** celular filmando a tela da live do Davy no minijogo de pesca. O Davy aparece sério, olhando para a câmera, e o braço gira o molinete fora do quadro.
- **De onde vem a graça:** fora de contexto, o gesto parece outra coisa.
- **Edição:** nenhuma, sem texto na tela.
- **Legenda:** marca o streamer.
- **Por que espalhou:** os comentários fazem o trabalho. O primeiro tem 36 mil curtidas, e o vídeo vive da piada que cada um completa.

**O que levar para os nossos:** corte curto (10 a 15 s), um momento só, "fora de contexto" engraçado, legenda que provoca sem explicar ("essa pescaria está um pouco estranha") e @ do streamer.
