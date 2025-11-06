# views/gameover.py
import arcade
from config import LARGURA_TELA, ALTURA_TELA, COR_TEXTO

class ViewGameOver(arcade.View):
    def __init__(self, jogador_nome="Herói"):
        super().__init__()
        self.jogador_nome = jogador_nome
        self.timer = 0  # Para voltar automaticamente ou animação se quiser

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "GAME OVER",
            LARGURA_TELA / 2,
            ALTURA_TELA / 2 + 50,
            arcade.color.RED,
            64,
            anchor_x="center"
        )
        arcade.draw_text(
            f"{self.jogador_nome} foi derrotado...",
            LARGURA_TELA / 2,
            ALTURA_TELA / 2 - 20,
            COR_TEXTO,
            32,
            anchor_x="center"
        )
        arcade.draw_text(
            "Pressione [R] para reiniciar",
            LARGURA_TELA / 2,
            ALTURA_TELA / 2 - 80,
            COR_TEXTO,
            24,
            anchor_x="center"
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R:
            # Reinicia o jogo mostrando a tela de cartas
            from views.cartas import ViewCartas
            self.window.show_view(ViewCartas())
            # Resetar jogador se quiser começar do zero
            from config import GameState
            self.window.game_state.jogador = None
