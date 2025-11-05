import arcade
import math
import os

# === CONFIGURAÇÕES DE TELA (iguais ao outro jogo) ===
LARGURA_TELA = 1920
ALTURA_TELA = 1080
TITULO_TELA = "Cartas Flutuantes com Sprites e Hover"

# === CONFIGURAÇÕES DAS CARTAS ===
ESCALA_CARTA = 0.4
ESCALA_HOVER = 0.45
AMPLITUDE_FLUTUACAO = 4
FREQUENCIA_FLUTUACAO = 0.8
AMPLITUDE_ROTACAO = 2
FREQUENCIA_ROTACAO = 0.5

# === CAMINHO DAS IMAGENS ===
IMAGENS = {
    "Mago":      r"..\jogo_arcade\imagens\character_cards\test.png",
    "Guerreiro": r"..\jogo_arcade\imagens\character_cards\test.png",
    "Arqueiro":  r"..\jogo_arcade\imagens\character_cards\test.png"
}


class Carta:
    def __init__(self, nome, x, y):
        self.nome = nome
        self.base_x = x
        self.base_y = y
        self.hovered = False
        self.current_scale = ESCALA_CARTA
        self.tempo = 0.0

        caminho_imagem = IMAGENS[nome]
        if not os.path.exists(caminho_imagem):
            raise FileNotFoundError(f"Imagem '{caminho_imagem}' não encontrada!")

        self.sprite = arcade.Sprite(caminho_imagem, ESCALA_CARTA)
        self.sprite.center_x = x
        self.sprite.center_y = y

    def update(self):
        self.tempo += 0.03

        # Flutuação e rotação sutis
        y_flutuante = self.base_y + math.sin(self.tempo * FREQUENCIA_FLUTUACAO) * AMPLITUDE_FLUTUACAO
        rotacao = math.sin(self.tempo * FREQUENCIA_ROTACAO) * AMPLITUDE_ROTACAO

        # Transição suave de escala (hover)
        target_scale = ESCALA_HOVER if self.hovered else ESCALA_CARTA
        self.current_scale += (target_scale - self.current_scale) * 0.1

        self.sprite.center_y = y_flutuante
        self.sprite.angle = rotacao
        self.sprite.scale = self.current_scale

    def draw_text(self):
        arcade.draw_text(
            self.nome,
            self.sprite.center_x,
            self.sprite.center_y - self.sprite.height * 0.6,
            arcade.color.WHITE,
            24,
            width=int(self.sprite.width),
            align="center",
            anchor_x="center",
            anchor_y="center"
        )

    def check_hover(self, x, y):
        self.hovered = self.sprite.left <= x <= self.sprite.right and self.sprite.bottom <= y <= self.sprite.top

    def check_click(self, x, y):
        if self.sprite.left <= x <= self.sprite.right and self.sprite.bottom <= y <= self.sprite.top:
            print(f"Carta clicada: {self.nome}")


class MeuJogo(arcade.Window):
    def __init__(self):
        super().__init__(LARGURA_TELA, ALTURA_TELA, TITULO_TELA)
        arcade.set_background_color(arcade.color.DARK_TAN)

        self.cartas = []
        self.sprites = arcade.SpriteList()

        nomes = ["Mago", "Guerreiro", "Arqueiro"]

        # Ajuste de espaçamento proporcional à nova tela
        espacamento = 400
        start_x = LARGURA_TELA // 2 - espacamento
        y = ALTURA_TELA // 2

        for i, nome in enumerate(nomes):
            x = start_x + i * espacamento
            carta = Carta(nome, x, y)
            self.cartas.append(carta)
            self.sprites.append(carta.sprite)

    def on_draw(self):
        self.clear()
        self.sprites.draw()
        for carta in self.cartas:
            carta.draw_text()

    def on_update(self, delta_time):
        for carta in self.cartas:
            carta.update()

    def on_mouse_motion(self, x, y, dx, dy):
        for carta in self.cartas:
            carta.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        for carta in self.cartas:
            carta.check_click(x, y)


def main():     
    MeuJogo()   
    arcade.run()


if __name__ == "__main__":
    main()
