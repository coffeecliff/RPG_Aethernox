import arcade
from sprites.carta import Carta
from config import LARGURA_TELA, ALTURA_TELA, ESTATISTICAS_PERSONAGENS

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
        # Desenha as sprites das cartas
        self.sprites.draw()

        # Nome / texto de cada carta
        for carta in self.cartas:
            carta.draw_text()

        # Se houver alguma carta em hover, desenha painel de stats
        hovered = next((c for c in self.cartas if c.hovered), None)
        if hovered:
            self._draw_stats_panel_for(hovered)

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
                break

    def _draw_stats_panel_for(self, carta):
        """Desenha um painel com as estatísticas do personagem 'carta'.
        Compatível com versões antigas do arcade.
        """
        from config import ESTATISTICAS_PERSONAGENS, LARGURA_TELA, ALTURA_TELA

        stats = ESTATISTICAS_PERSONAGENS.get(carta.nome, None)
        if not stats:
            return

        # Dimensões do painel
        panel_w = 320
        panel_h = 200
        margin = 20
        panel_x = LARGURA_TELA - panel_w // 2 - margin
        panel_y = ALTURA_TELA // 2

        # Converte para coordenadas left/bottom
        left = panel_x - panel_w / 2
        bottom = panel_y - panel_h / 2

        # Fundo do painel (usando lbwh)
        arcade.draw_lbwh_rectangle_filled(left, bottom, panel_w, panel_h, arcade.color.DARK_SLATE_GRAY)

        # Borda do painel (quatro linhas)
        arcade.draw_line(left, bottom + panel_h, left + panel_w, bottom + panel_h, arcade.color.BLACK, 2)
        arcade.draw_line(left, bottom, left + panel_w, bottom, arcade.color.BLACK, 2)
        arcade.draw_line(left, bottom, left, bottom + panel_h, arcade.color.BLACK, 2)
        arcade.draw_line(left + panel_w, bottom, left + panel_w, bottom + panel_h, arcade.color.BLACK, 2)

        # Título
        title_x = left + 16
        title_y = bottom + panel_h - 28
        arcade.draw_text(
            f"{carta.nome}",
            title_x,
            title_y,
            arcade.color.WHITE,
            20,
            anchor_x="left"
        )

        # Linhas de estatísticas
        lines = [
            f"Vida: {stats.get('vida', '?')}",
            f"Ataque: {stats.get('ataque', '?')}",
            f"Defesa: {stats.get('defesa', '?')}",
            f"Velocidade: {stats.get('velocidade', '?')}",
        ]
        y_text = title_y - 36
        for line in lines:
            arcade.draw_text(line, title_x, y_text, arcade.color.LIGHT_GRAY, 16, anchor_x="left")
            y_text -= 26

        # Descrição
        descricao = stats.get("classe", "")
        if descricao:
            arcade.draw_text(
                descricao,
                title_x,
                y_text - 8,
                arcade.color.LIGHT_YELLOW,
                14,
                width=int(panel_w - 32),
                align="left",
                anchor_x="left",
                multiline=True
            )