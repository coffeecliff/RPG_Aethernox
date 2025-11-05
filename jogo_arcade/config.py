import os
import arcade

# game_state.py
class GameState:
    def __init__(self):
        self.cena_mundo = None  # guardará instância de ViewMundo
        self.player_pos = (0, 0)
        self.player_facing = True
        self.inimigos_derrotados = set()


# ================== CONFIGURAÇÕES GERAIS ==================
LARGURA_TELA = 1920
ALTURA_TELA = 1080
TITULO_JOGO = "Jogo Integrado: Cartas -> Mundo -> Luta"

# Caminhos de imagens
IMAGENS_CARTAS = {
    "Mago": os.path.join("..", "jogo_arcade", "imagens", "character_cards", "test.png"),
    "Guerreiro": os.path.join("..", "jogo_arcade", "imagens", "character_cards", "test.png"),
    "Arqueiro": os.path.join("..", "jogo_arcade", "imagens", "character_cards", "test.png")
}
CAMINHO_INIMIGO = os.path.join("..", "jogo_arcade", "imagens", "enemies", "enemie.png")

PLAYER1_IDLE = [
    os.path.join("..", "jogo_arcade", "sprites", "joana", "idle1.png"),
    os.path.join("..", "jogo_arcade", "sprites", "joana", "idle2.png"),
    os.path.join("..", "jogo_arcade", "sprites", "joana", "idle3.png")
]
PLAYER1_WALK = [
    os.path.join("..", "jogo_arcade", "sprites", "joana", "walk1.png"),
    os.path.join("..", "jogo_arcade", "sprites", "joana", "walk2.png"),
    os.path.join("..", "jogo_arcade", "sprites", "joana", "walk3.png"),
    os.path.join("..", "jogo_arcade", "sprites", "joana", "walk4.png")
]

PLAYER2_WALK = [
    os.path.join("..", "jogo_arcade", "sprites", "mage", "idle1.jpg"),
    os.path.join("..", "jogo_arcade", "sprites", "mage", "idle1.jpg")
]

PLAYER3_WALK = [
    os.path.join("..", "jogo_arcade", "sprites", "archer", "idle1.jpg"),
    os.path.join("..", "jogo_arcade", "sprites", "archer", "idle1.jpg")
]

# ================== CENA DE CARTAS ==================
ESCALA_CARTA = 0.4
ESCALA_HOVER = 0.45
AMPLITUDE_FLUTUACAO = 4
FREQUENCIA_FLUTUACAO = 0.8
AMPLITUDE_ROTACAO = 2
FREQUENCIA_ROTACAO = 0.5

# ================== CENA DO MUNDO ==================
MAX_SPEED = 8
ACCELERATION = 0.2
FRICTION = 0.1
ANIMATION_SPEED = 0.20

# ================== CENA DE BATALHA ==================
COR_CAIXA = arcade.color.LIGHT_GRAY
COR_TEXTO = arcade.color.BLACK
COR_BARRA_VIDA_INIMIGO = arcade.color.RED
COR_MENSAGEM = arcade.color.YELLOW
