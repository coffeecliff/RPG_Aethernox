import os
import arcade
from pathlib import Path
 
# game_state.py
class GameState:
    def __init__(self):
        self.cena_mundo = None  # guardará instância de ViewMundo
        self.player_pos = (0, 0)
        self.player_facing = True
        self.inimigos_derrotados = set()
        self.jogador = None  # 🔹 jogador persistente entre batalhas
 
 
# ================== ESTATÍSTICAS ==================
ESTATISTICAS_PERSONAGENS = {
    "Guerreiro": {
        "vida": 120,
        "ataque": 15,
        "defesa": 10,
        "mana": 30,
        "mana_max": 30,
        "velocidade": 5,
        "classe": "Forte em combate corpo a corpo, alta resistência.",
    },
 
    "Mago": {
        "vida": 80,
        "ataque": 25,
        "defesa": 5,
        "mana": 100,
        "mana_max": 100,
        "velocidade": 7,
        "classe": "Alta magia, mas pouca defesa física.",
    },
 
    "Arqueiro": {
        "vida": 100,
        "ataque": 18,
        "defesa": 8,
        "mana": 50,
        "mana_max": 50,
        "velocidade": 10,
        "classe": "Ágil e preciso, equilíbrio entre ataque e defesa.",
    },
}
 
 
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
ANIMATION_SPEED = 0.2
 
 
# ================== CENA DE BATALHA ==================
COR_CAIXA = arcade.color.LIGHT_GRAY
COR_TEXTO = arcade.color.BLACK
COR_BARRA_VIDA_INIMIGO = arcade.color.RED
COR_MENSAGEM = arcade.color.YELLOW
 
 
# ================== CONFIGURAÇÕES GERAIS ==================
LARGURA_TELA = 1920
ALTURA_TELA = 1080
TITULO_JOGO = "Jogo Integrado: Cartas -> Mundo -> Luta"
 
 
# ============================================================
# CAMINHOS 100% CORRIGIDOS COM PATHLIB
# ============================================================
 
BASE_DIR = Path(__file__).resolve().parent
 
IMAGENS_DIR = BASE_DIR / "imagens"
SPRITES_DIR = BASE_DIR / "sprites"
 
# Cartas
IMAGENS_CARTAS = {
    "Mago": IMAGENS_DIR / "character_cards" / "card.png",
    "Guerreiro": IMAGENS_DIR / "character_cards" / "card.png",
    "Arqueiro": IMAGENS_DIR / "character_cards" / "card.png",
}
 
# Inimigos
CAMINHO_INIMIGO = IMAGENS_DIR / "enemies" / "enemie.png"
 
# PLAYER 1 (Joana)
PLAYER1_IDLE = [
    SPRITES_DIR / "joana" / "idle1.png",
    SPRITES_DIR / "joana" / "idle1.png",
    SPRITES_DIR / "joana" / "idle1.png",
    SPRITES_DIR / "joana" / "idle1.png",
    SPRITES_DIR / "joana" / "idle2.png",
    SPRITES_DIR / "joana" / "idle3.png",
    SPRITES_DIR / "joana" / "idle3.png",
    SPRITES_DIR / "joana" / "idle3.png",
]
 
PLAYER1_WALK = [
    SPRITES_DIR / "joana" / "walk1.png",
    SPRITES_DIR / "joana" / "walk2.png",
    SPRITES_DIR / "joana" / "walk3.png",
    SPRITES_DIR / "joana" / "walk4.png",
]
 
# PLAYER 2 (Mage)
PLAYER2_IDLE = [
    SPRITES_DIR / "mage" / "idle1.jpg",
    SPRITES_DIR / "mage" / "idle1.jpg",
]
 
PLAYER2_WALK = [
    SPRITES_DIR / "mage" / "idle1.jpg",
    SPRITES_DIR / "mage" / "idle1.jpg",
]
 
# PLAYER 3 (Archer)
PLAYER3_IDLE = [
    SPRITES_DIR / "mage" / "idle1.jpg",
    SPRITES_DIR / "mage" / "idle1.jpg",
]
 
PLAYER3_WALK = [
    SPRITES_DIR / "archer" / "idle1.jpg",
    SPRITES_DIR / "archer" / "idle1.jpg",
]