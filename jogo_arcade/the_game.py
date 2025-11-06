import arcade
from config import GameState, LARGURA_TELA, ALTURA_TELA, TITULO_JOGO
from views.cartas import ViewCartas

def main():
    window = arcade.Window(LARGURA_TELA, ALTURA_TELA, TITULO_JOGO)
    window.game_state = GameState()  # 🔹 Guarda o estado global
    window.show_view(ViewCartas())
    arcade.run()

if __name__ == "__main__":
    main()