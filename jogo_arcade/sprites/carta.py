import arcade
import math
import os
from config import *

class Carta:
    def __init__(self, nome, x, y):
        self.nome = nome
        self.base_x = x
        self.base_y = y
        self.hovered = False
        self.current_scale = ESCALA_CARTA
        self.tempo = 0.0

        caminho_imagem = IMAGENS_CARTAS[nome]
        if not os.path.exists(caminho_imagem):
            raise FileNotFoundError(f"Imagem '{caminho_imagem}' não encontrada!")
        self.sprite = arcade.Sprite(caminho_imagem, ESCALA_CARTA)
        self.sprite.center_x = x
        self.sprite.center_y = y

    def update(self):
        self.tempo += 0.03
        y_flutuante = self.base_y + math.sin(self.tempo * FREQUENCIA_FLUTUACAO) * AMPLITUDE_FLUTUACAO
        rotacao = math.sin(self.tempo * FREQUENCIA_ROTACAO) * AMPLITUDE_ROTACAO
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
