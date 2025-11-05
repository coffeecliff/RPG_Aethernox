import arcade
import os
import random

# ---------- CONFIGURAÇÕES ----------
LARGURA_TELA = 1920
ALTURA_TELA = 1080
TITULO_TELA = "Batalha Simulada - Estilo Undertale"

CAMINHO_INIMIGO = r"..\jogo_arcade\imagens\enemies\enemie.png"

# Cores
COR_CAIXA = arcade.color.LIGHT_GRAY
COR_TEXTO = arcade.color.BLACK
COR_BARRA_VIDA_INIMIGO = arcade.color.RED
COR_MENSAGEM = arcade.color.YELLOW

class CenaBatalha(arcade.Window):
    def __init__(self):
        super().__init__(LARGURA_TELA, ALTURA_TELA, TITULO_TELA)
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        # --- Carregar inimigo ---
        if not os.path.exists(CAMINHO_INIMIGO):
            raise FileNotFoundError(f"Imagem '{CAMINHO_INIMIGO}' não encontrada!")

        self.inimigo_sprite = arcade.Sprite(CAMINHO_INIMIGO, scale=0.7)
        self.inimigo_sprite.center_x = LARGURA_TELA / 2
        self.inimigo_sprite.top = ALTURA_TELA - 50

        self.inimigo_lista = arcade.SpriteList()
        self.inimigo_lista.append(self.inimigo_sprite)

        # --- Status ---
        self.vida_jogador = 100
        self.level_jogador = 5
        self.ouro_jogador = 50

        self.vida_inimigo = 120
        self.max_vida_inimigo = 120

        # --- Mensagem temporária ---
        self.mensagem = ""
        self.mensagem_timer = 0

        # --- Boxes de ação (posição fixa) ---
        self.box_largura = 200
        self.box_altura = 60
        spacing = 40
        total_width = 3*self.box_largura + 2*spacing
        self.start_x = LARGURA_TELA/2 - total_width/2
        self.start_y = 150
        self.box_coords = {
            "Luta": (self.start_x, self.start_y),
            "Item": (self.start_x + self.box_largura + spacing, self.start_y),
            "Fugir": (self.start_x + 2*(self.box_largura + spacing), self.start_y)
        }

    def on_draw(self):
        self.clear()

        # --- Desenhar inimigo ---
        self.inimigo_lista.draw()

        # --- Barra de vida do inimigo ---
        barra_largura = 400
        barra_altura = 30
        barra_left = LARGURA_TELA/2 - barra_largura/2
        barra_bottom = self.inimigo_sprite.bottom - 40
        arcade.draw_lbwh_rectangle_filled(barra_left, barra_bottom, barra_largura, barra_altura, arcade.color.DARK_RED)
        vida_width = barra_largura * (self.vida_inimigo / 120)
        arcade.draw_lbwh_rectangle_filled(barra_left, barra_bottom, vida_width, barra_altura, COR_BARRA_VIDA_INIMIGO)

        # --- Informações do jogador ---
        margin_x = 30
        margin_y = 30
        arcade.draw_text(f"Vida: {self.vida_jogador}", margin_x, margin_y, COR_TEXTO, 24)
        arcade.draw_text(f"Level: {self.level_jogador}", margin_x, margin_y + 40, COR_TEXTO, 24)
        arcade.draw_text(f"Ouro: {self.ouro_jogador}", margin_x, margin_y + 80, COR_TEXTO, 24)

        # --- Boxes de ação ---
        for nome, (x, y) in self.box_coords.items():
            arcade.draw_lbwh_rectangle_filled(x, y, self.box_largura, self.box_altura, COR_CAIXA)
            arcade.draw_text(nome, x + self.box_largura/2 - (30 if nome!="Fugir" else 40), 
                             y + self.box_altura/2 - 15, COR_TEXTO, 24)

        # --- Mensagem ---
        if self.mensagem_timer > 0:
            arcade.draw_text(self.mensagem, LARGURA_TELA/2, self.start_y + 100, COR_MENSAGEM, 32,
                             anchor_x="center")
            self.mensagem_timer -= 1

    def on_mouse_press(self, x, y, button, modifiers):
        for nome, (bx, by) in self.box_coords.items():
            if bx <= x <= bx+self.box_largura and by <= y <= by+self.box_altura:
                self.acao(nome)

    def acao(self, nome):
        if nome == "Luta":
            dano = random.randint(10, 25)
            self.vida_inimigo -= dano
            if self.vida_inimigo < 0: self.vida_inimigo = 0
            self.mensagem = f"Você causou {dano} de dano!"
            self.mensagem_timer = 120
        elif nome == "Item":
            cura = random.randint(15, 30)
            self.vida_jogador += cura
            if self.vida_jogador > 100: self.vida_jogador = 100
            self.mensagem = f"Você recuperou {cura} de vida!"
            self.mensagem_timer = 120
        elif nome == "Fugir":
            self.mensagem = "Você fugiu da batalha!"
            self.mensagem_timer = 120
            self.vida_inimigo = 120  # reset
            self.vida_jogador = 100  # reset

def main():
    CenaBatalha()
    arcade.run()

if __name__ == "__main__":
    main()
