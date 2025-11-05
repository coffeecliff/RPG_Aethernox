import arcade
from sprites.carta import Carta
from config import LARGURA_TELA, ALTURA_TELA

class ViewCartas(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.DARK_TAN)
        self.cartas = []
        self.sprites = arcade.SpriteList()
        nomes = ["Mago", "Guerreiro", "Arqueiro"]
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
            if carta.sprite.left <= x <= carta.sprite.right and carta.sprite.bottom <= y <= carta.sprite.top:
                # Guarda a escolha do jogador no estado do jogo
                if not hasattr(self.window, "game_state"):
                    from config import GameState
                    self.window.game_state = GameState()

                self.window.game_state.personagem_escolhido = carta.nome

                # Import local evita circularidade
                from views import ViewMundo
                self.window.show_view(ViewMundo())
