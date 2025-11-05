import arcade
import random
from config import *
from sprites.inimigo import Inimigo


class ViewBatalha(arcade.View):
    def __init__(self, inimigo=None):
        super().__init__()
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self.camera_game = arcade.Camera2D()
        self.camera_gui = arcade.Camera2D()

        # Guarda o inimigo que iniciou a batalha
        self.inimigo = inimigo or Inimigo(x=LARGURA_TELA / 2, y=ALTURA_TELA * 0.72)
        self.inimigo_sprite = self.inimigo
        self.inimigo_lista = arcade.SpriteList([self.inimigo_sprite])

        # Status
        self.vida_jogador = 100
        self.level_jogador = 5
        self.ouro_jogador = 50
        self.vida_inimigo = 120
        self.max_vida_inimigo = 120
        self.mensagem = ""
        self.mensagem_timer = 0

        # Boxes
        self.box_largura = 220
        self.box_altura = 70
        spacing = 60
        total_width = 3 * self.box_largura + 2 * spacing
        self.start_x = LARGURA_TELA / 2 - total_width / 2
        self.start_y = 120
        self.box_coords = {
            "Luta": (self.start_x, self.start_y),
            "Item": (self.start_x + self.box_largura + spacing, self.start_y),
            "Fugir": (self.start_x + 2 * (self.box_largura + spacing), self.start_y),
        }

    def on_draw(self):
        self.clear()
        self.camera_game.use()

        # --- Barra de vida (posição base) ---
        barra_largura = 500
        barra_altura = 35
        barra_left = LARGURA_TELA / 2 - barra_largura / 2
        barra_bottom = ALTURA_TELA * 0.6  # ajuste se quiser mais alto/baixo

        # --- Ajusta posição do inimigo (usa atributos caso existam) ---
        self.inimigo_sprite.center_x = LARGURA_TELA / 2

        # pega altura segura do sprite (fallback se não existir atributo height)
        sprite_height = getattr(self.inimigo_sprite, "height", None)
        if sprite_height is None:
            # tenta obter pela textura, se houver
            textura = getattr(self.inimigo_sprite, "texture", None)
            sprite_height = getattr(textura, "height", 128)

        # posiciona o inimigo logo acima da barra
        self.inimigo_sprite.center_y = barra_bottom + barra_altura + (sprite_height / 2) + 30

        # desenha via SpriteList (funciona mesmo que Inimigo não implemente draw())
        self.inimigo_lista.draw()

        self.camera_gui.use()

        # --- Desenha a barra de vida ---
        arcade.draw_lbwh_rectangle_filled(barra_left, barra_bottom, barra_largura, barra_altura, arcade.color.DARK_RED)
        vida_width = barra_largura * (self.vida_inimigo / self.max_vida_inimigo)
        arcade.draw_lbwh_rectangle_filled(barra_left, barra_bottom, vida_width, barra_altura, COR_BARRA_VIDA_INIMIGO)

        # --- Nome do inimigo (opcional) ---
        arcade.draw_text(
            "INIMIGO",
            LARGURA_TELA / 2,
            barra_bottom + barra_altura + sprite_height + 60,
            arcade.color.WHITE, 26, anchor_x="center"
        )

        # --- Caixas e HUD (mesmo que antes) ---
        for nome, (x, y) in self.box_coords.items():
            arcade.draw_lbwh_rectangle_filled(x, y, self.box_largura, self.box_altura, COR_CAIXA)
            arcade.draw_text(nome, x + self.box_largura / 2, y + self.box_altura / 2, COR_TEXTO, 28,
                            anchor_x="center", anchor_y="center")

        base_x = 60
        arcade.draw_text(f"Vida: {self.vida_jogador}", base_x, 60, COR_TEXTO, 26)
        arcade.draw_text(f"Level: {self.level_jogador}", base_x, 100, COR_TEXTO, 26)
        arcade.draw_text(f"Ouro: {self.ouro_jogador}", base_x, 140, COR_TEXTO, 26)

        if self.mensagem_timer > 0:
            arcade.draw_text(self.mensagem, LARGURA_TELA / 2, self.start_y + 160, COR_MENSAGEM, 36, anchor_x="center")
            self.mensagem_timer -= 1


    def on_mouse_press(self, x, y, button, modifiers):
        for nome, (bx, by) in self.box_coords.items():
            if bx <= x <= bx + self.box_largura and by <= y <= by + self.box_altura:
                self.acao(nome)

    def acao(self, nome):
        if nome == "Luta":
            dano = random.randint(10, 25)
            self.vida_inimigo -= dano
            if self.vida_inimigo < 0:
                self.vida_inimigo = 0
            self.mensagem = f"Você causou {dano} de dano!"
            self.mensagem_timer = 120

            if self.vida_inimigo == 0:
                self.mensagem = "Inimigo derrotado! Voltando ao mundo..."
                self.mensagem_timer = 120
                arcade.schedule(self.voltar_mundo, 2)

        elif nome == "Item":
            cura = random.randint(15, 30)
            self.vida_jogador = min(self.vida_jogador + cura, 100)
            self.mensagem = f"Você recuperou {cura} de vida!"
            self.mensagem_timer = 120

        elif nome == "Fugir":
            self.mensagem = "Você fugiu da batalha!"
            self.mensagem_timer = 120
            arcade.schedule(self.voltar_mundo, 1)

    def voltar_mundo(self, delta_time):
        """Retorna à cena do mundo, removendo o inimigo de forma segura."""
        arcade.unschedule(self.voltar_mundo)

        estado = getattr(self.window, "game_state", None)
        if not estado or not hasattr(estado, "cena_mundo"):
            from views.mundo import ViewMundo
            self.window.show_view(ViewMundo())
            return

        mundo = estado.cena_mundo

        # Atualiza posição e direção do jogador
        mundo.player_sprite.center_x = estado.player_pos[0] - 100
        mundo.player_sprite.center_y = estado.player_pos[1]
        mundo.facing_right = estado.player_facing

        # ✅ Remoção segura do inimigo derrotado
        if self.vida_inimigo <= 0 and hasattr(mundo, "inimigos") and self.inimigo:
            if self.inimigo in mundo.inimigos:
                try:
                    self.inimigo.remove_from_sprite_lists()
                except Exception:
                    pass  # caso já tenha sido removido internamente

                try:
                    mundo.inimigos.remove(self.inimigo)
                except ValueError:
                    pass  # caso já não esteja mais na lista

            # marca como derrotado para não reaparecer
            if hasattr(self.inimigo, "id") and hasattr(estado, "inimigos_derrotados"):
                estado.inimigos_derrotados.add(f"inimigo_{self.inimigo.id}")

        # ✅ Corrige movimento e fundo ao retornar
        mundo.moving_left = False
        mundo.moving_right = False
        mundo.velocity_x = 0
        arcade.set_background_color(arcade.color.SKY_BLUE)

        self.window.show_view(mundo)
