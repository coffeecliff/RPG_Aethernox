import arcade
import os
from config import CAMINHO_INIMIGO

class Inimigo(arcade.Sprite):
    def __init__(self, scale=0.5, x=960, y=780):
        if not os.path.exists(CAMINHO_INIMIGO):
            raise FileNotFoundError(f"Imagem '{CAMINHO_INIMIGO}' não encontrada!")
        super().__init__(CAMINHO_INIMIGO, scale=scale)
        self.center_x = x
        self.center_y = y
        self.max_vida = 120
        self.vida = self.max_vida
        self.id_inimigo = None  # ← será atribuído em ViewMundo
