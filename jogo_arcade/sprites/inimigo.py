import arcade
import os
from config import CAMINHO_INIMIGO

class Inimigo(arcade.Sprite):
    def __init__(
        self,
        nome="Goblin",
        classe="Inimigo",
        scale=0.5,
        x=960,
        y=780,
        vida_max=120,
        mana_max=60,
    ):
        # --- validação do arquivo de imagem ---
        if not os.path.exists(CAMINHO_INIMIGO):
            raise FileNotFoundError(f"Imagem '{CAMINHO_INIMIGO}' não encontrada!")

        super().__init__(CAMINHO_INIMIGO, scale=scale)
        self.center_x = x
        self.center_y = y

        # --- atributos gerais ---
        self.nome = nome
        self.classe = classe
        self.id_inimigo = None  # será atribuído na ViewMundo

        # --- status básicos (igual jogador) ---
        self.vida_max = vida_max
        self.vida = vida_max
        self.mana_max = mana_max
        self.mana = mana_max

        # --- estatísticas opcionais ---
        self.forca = 10
        self.defesa = 5
        self.inteligencia = 8
        self.velocidade = 4

    def __repr__(self):
        return f"<Inimigo nome={self.nome}, vida={self.vida}/{self.vida_max}, mana={self.mana}/{self.mana_max}>"
