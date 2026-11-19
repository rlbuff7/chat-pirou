#!/usr/bin/env python3
"""Gera as artes de perfil do Chat Pirou (avatar, banner do YouTube, cabeçalho do X).

Uso (no WSL): python3 marca/artes/gerar.py
Saída: marca/artes/*.svg (fonte editável), *.png (para subir) e previa.png (conferência).
Paleta e fontes: marca/identidade.md. Precisa de ffmpeg com librsvg e do Pillow do sistema.
"""
import random
import shutil
import subprocess
from pathlib import Path

AQUI = Path(__file__).resolve().parent
FONTES = AQUI.parent.parent / "clipador" / "fontes"

CARVAO, GRAFITE, GELO = "#0B0B12", "#1A1A24", "#F5F7FA"
AMARELO, MAGENTA, CIANO = "#FFD400", "#FF2E88", "#19E3FF"


def instalar_fontes():
    """O librsvg acha fonte pelo fontconfig: copia Anton e Montserrat para a pasta do usuário."""
    destino = Path.home() / ".local/share/fonts/chatpirou"
    if not (destino / "Anton-Regular.ttf").exists():
        destino.mkdir(parents=True, exist_ok=True)
        for f in FONTES.glob("*.ttf"):
            shutil.copy(f, destino)
        subprocess.run(["fc-cache", "-f", str(destino)], check=True)


def pts(lista):
    return " ".join(f"{x:.0f},{y:.0f}" for x, y in lista)


def linha(lista, cor, larg, extra=""):
    return (f'<polyline points="{pts(lista)}" fill="none" stroke="{cor}" stroke-width="{larg}" '
            f'stroke-linecap="round" stroke-linejoin="round" {extra}/>')


def onda(x0, x1, base, pico_x, pico_y, amp, semente, passo=(38, 70)):
    """Linha do chat: quase plana, com um pico que dispara. Devolve (antes, pico, depois)."""
    rnd = random.Random(semente)
    antes, x = [(x0, base)], x0
    while x < pico_x - 110:
        x += rnd.randint(*passo)
        antes.append((min(x, pico_x - 70), base + rnd.uniform(-amp, amp)))
    pico = [(pico_x - 70, base), (pico_x, pico_y), (pico_x + 60, base + amp * 2.2), (pico_x + 105, base)]
    depois, x = [(pico_x + 105, base)], pico_x + 105
    while x < x1:
        x += rnd.randint(*passo)
        depois.append((min(x, x1), base + rnd.uniform(-amp, amp)))
    antes.append(pico[0])
    return antes, pico, depois


def desenhar_onda(antes, pico, depois, larg, fundo=CARVAO, cor=AMARELO):
    """Amarelo na linha, magenta no pico, com um contorno da cor do fundo para o pico 'saltar'."""
    return "\n".join([
        linha(antes, cor, larg), linha(depois, cor, larg),
        linha(pico, fundo, larg + larg * 0.65), linha(pico, MAGENTA, larg),
    ])


BALAO = ("M320 300 H760 A90 90 0 0 1 850 390 V640 A90 90 0 0 1 760 730 H480 L345 850 "
         "L372 730 H320 A90 90 0 0 1 230 640 V390 A90 90 0 0 1 320 300 Z")


def avatar(cheio):
    """1080x1080: balão de chat com a linha do chat dentro; o pico estoura a borda do balão."""
    if cheio:
        balao = f'<path d="{BALAO}" fill="{AMARELO}" stroke="{AMARELO}" stroke-width="56" stroke-linejoin="round"/>'
        cor_linha = CARVAO
    else:
        balao = f'<path d="{BALAO}" fill="{GRAFITE}" stroke="{AMARELO}" stroke-width="56" stroke-linejoin="round"/>'
        cor_linha = AMARELO
    antes = [(300, 590), (365, 590), (405, 556), (448, 612), (490, 585), (555, 585)]
    pico = [(555, 585), (640, 175), (702, 628), (742, 585)]
    depois = [(742, 585), (790, 585)]
    fundo_pico = CARVAO
    corpo = "\n".join([
        linha(antes, cor_linha, 46), linha(depois, cor_linha, 46),
        linha(pico, fundo_pico, 76), linha(pico, MAGENTA, 46),
    ])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">\n'
            f'<rect width="1080" height="1080" fill="{CARVAO}"/>\n{balao}\n{corpo}\n</svg>\n')


def texto(x, y, conteudo, tam, cor=GELO, fonte="Anton", peso="400", ancora="middle", extra=""):
    return (f'<text x="{x}" y="{y}" text-anchor="{ancora}" font-family="{fonte}" font-weight="{peso}" '
            f'font-size="{tam}" fill="{cor}" {extra}>{conteudo}</text>')


def banner_youtube():
    """2560x1440. Área que aparece em todo aparelho: 1546x423 no centro (x 507-2053, y 508-931)."""
    a, p, d = onda(-20, 2580, 905, 1965, 548, 13, semente=19)
    return "\n".join([
        '<svg xmlns="http://www.w3.org/2000/svg" width="2560" height="1440" viewBox="0 0 2560 1440">',
        f'<rect width="2560" height="1440" fill="{CARVAO}"/>',
        desenhar_onda(a, p, d, 22),
        # sem o @ aqui: o YouTube já mostra o @ logo abaixo do banner
        texto(1190, 750, f'CHAT <tspan fill="{AMARELO}">PIROU</tspan>', 215, extra='letter-spacing="7"'),
        texto(1190, 835, "Cortes de lives  |  GTA 6 e mais", 54, fonte="Montserrat", peso="800"),
        "</svg>", ""])


def cabecalho_x():
    """1500x500. O avatar cobre o canto de baixo à esquerda; o texto fica no centro-direita."""
    a, p, d = onda(-20, 1520, 428, 1335, 92, 9, semente=7, passo=(30, 55))
    return "\n".join([
        '<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="500" viewBox="0 0 1500 500">',
        f'<rect width="1500" height="500" fill="{CARVAO}"/>',
        desenhar_onda(a, p, d, 14),
        texto(790, 238, f'CHAT <tspan fill="{AMARELO}">PIROU</tspan>', 150, extra='letter-spacing="5"'),
        texto(790, 298, "Cortes de lives  |  GTA 6 e mais", 36, fonte="Montserrat", peso="800"),
        texto(790, 350, "@chat.pirou no TikTok, Instagram e YouTube", 27, cor=CIANO, fonte="Montserrat", peso="800"),
        "</svg>", ""])


def renderizar(nome, svg):
    (AQUI / f"{nome}.svg").write_text(svg, encoding="utf-8")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(AQUI / f"{nome}.svg"), "-frames:v", "1",
                    str(AQUI / f"{nome}.png")], check=True)


def previa():
    """Folha de conferência: avatares em círculo nos tamanhos reais e banners com a área segura."""
    from PIL import Image, ImageDraw
    folha = Image.new("RGB", (1400, 1560), "#2a2a33")
    d = ImageDraw.Draw(folha)
    for i, nome in enumerate(["avatar-a", "avatar-b"]):
        img = Image.open(AQUI / f"{nome}.png").convert("RGB")
        x0 = 30 + i * 690
        for tam, dx, dy in [(330, 0, 0), (110, 360, 110), (40, 500, 145)]:
            peq = img.resize((tam, tam), Image.LANCZOS)
            masc = Image.new("L", (tam, tam), 0)
            ImageDraw.Draw(masc).ellipse((0, 0, tam - 1, tam - 1), fill=255)
            folha.paste(peq, (x0 + dx, 20 + dy), masc)
        d.text((x0, 360), nome.upper(), fill="#ffffff")
    yt = Image.open(AQUI / "banner-youtube.png").convert("RGB").resize((1340, 754), Image.LANCZOS)
    k = 1340 / 2560
    dy = ImageDraw.Draw(yt)
    dy.rectangle((507 * k, 508 * k, 2053 * k, 931 * k), outline="#19E3FF", width=2)
    folha.paste(yt, (30, 390))
    d.text((30, 1150), "BANNER YOUTUBE (retangulo ciano = o que aparece no celular)", fill="#ffffff")
    xh = Image.open(AQUI / "cabecalho-x.png").convert("RGB").resize((1000, 333), Image.LANCZOS)
    ImageDraw.Draw(xh).ellipse((20, 200, 200, 380), fill="#555566")  # onde o avatar cobre no X
    folha.paste(xh, (30, 1180))
    d.text((30, 1525), "CABECALHO X (circulo cinza = avatar por cima)", fill="#ffffff")
    folha.save(AQUI / "previa.png")


def main():
    instalar_fontes()
    renderizar("avatar-a", avatar(cheio=False))
    renderizar("avatar-b", avatar(cheio=True))
    renderizar("banner-youtube", banner_youtube())
    renderizar("cabecalho-x", cabecalho_x())
    previa()
    print("ok:", ", ".join(sorted(p.name for p in AQUI.glob("*.png"))))


if __name__ == "__main__":
    main()
