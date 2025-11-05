import arcade
import random
import os
from config import *
from sprites.inimigo import Inimigo


CAMINHO_INIMIGO = os.path.join("..", "jogo_arcade", "imagens", "enemies", "enemie.png")


class ViewBatalha(arcade.View):
    def __init__(self, inimigo=None):
        super().__init__()
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self.camera_game = arcade.Camera2D()
        self.camera_gui = arcade.Camera2D()

        # Guarda o inimigo que iniciou a batalha
        self.inimigo = inimigo or Inimigo(x=LARGURA_TELA / 2, y=ALTURA_TELA * 0.72)

        # 🔹 Tamanho ajustado do inimigo
        self.inimigo_sprite = arcade.Sprite(CAMINHO_INIMIGO, scale=1)
        self.inimigo_sprite.center_x = LARGURA_TELA / 2
        self.inimigo_sprite.center_y = ALTURA_TELA * 0.55
        self.inimigo_lista = arcade.SpriteList()
        self.inimigo_lista.append(self.inimigo_sprite)

        # Status do jogador e inimigo
        self.vida_jogador = 100
        self.level_jogador = 5
        self.ouro_jogador = 50
        self.vida_inimigo = 120
        self.max_vida_inimigo = 120
        self.mensagem = ""
        self.mensagem_timer = 0

        # Configuração dos botões
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

        # Controle do botão "Fugir"
        self.fugir_desabilitado = False
        self.fuga_sucesso = False  # <- controla se o player fugiu com sucesso

    # =====================================================
    #                         DESENHO
    # =====================================================
    def on_draw(self):
        self.clear()
        self.camera_game.use()
        self.inimigo_lista.draw()
        self.camera_gui.use()

        # --- Barra de vida do inimigo ---
        barra_largura, barra_altura = 500, 35
        barra_left = LARGURA_TELA / 2 - barra_largura / 2
        barra_bottom = self.inimigo_sprite.center_y + self.inimigo_sprite.height / 2 + 40
        arcade.draw_lbwh_rectangle_filled(barra_left, barra_bottom, barra_largura, barra_altura, arcade.color.DARK_RED)
        vida_width = barra_largura * (self.vida_inimigo / self.max_vida_inimigo)
        arcade.draw_lbwh_rectangle_filled(barra_left, barra_bottom, vida_width, barra_altura, COR_BARRA_VIDA_INIMIGO)

        # --- Botões ---
        for nome, (x, y) in self.box_coords.items():
            if nome == "Fugir" and self.fugir_desabilitado:
                alpha = 100  # transparente se falhou em fugir
            else:
                alpha = 255
            cor_botao = (*COR_CAIXA[:3], alpha)
            arcade.draw_lbwh_rectangle_filled(x, y, self.box_largura, self.box_altura, cor_botao)
            arcade.draw_text(
                nome,
                x + self.box_largura / 2,
                y + self.box_altura / 2,
                COR_TEXTO,
                28,
                anchor_x="center",
                anchor_y="center",
            )

        # --- HUD jogador ---
        base_x = 60
        arcade.draw_text(f"Vida: {self.vida_jogador}", base_x, 60, COR_TEXTO, 26)
        arcade.draw_text(f"Level: {self.level_jogador}", base_x, 100, COR_TEXTO, 26)
        arcade.draw_text(f"Ouro: {self.ouro_jogador}", base_x, 140, COR_TEXTO, 26)

        # --- Mensagem temporária ---
        if self.mensagem_timer > 0:
            arcade.draw_text(
                self.mensagem,
                LARGURA_TELA / 2,
                self.start_y + 160,
                COR_MENSAGEM,
                36,
                anchor_x="center",
                align="center",
                multiline=True,
                width=600,
            )
            self.mensagem_timer -= 1

    # =====================================================
    #                    EVENTOS DE CLIQUE
    # =====================================================
    def on_mouse_press(self, x, y, button, modifiers):
        for nome, (bx, by) in self.box_coords.items():
            if nome == "Fugir" and self.fugir_desabilitado:
                continue  # se já falhou, botão inativo
            if bx <= x <= bx + self.box_largura and by <= y <= by + self.box_altura:
                self.acao(nome)
                break

    # =====================================================
    #                      AÇÕES
    # =====================================================
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
            vida_ratio = self.vida_jogador / 100
            chance_fuga = 60
            if vida_ratio <= 0.3:
                chance_fuga += 20
            resultado = random.randint(1, 100)

            if resultado <= chance_fuga:
                self.mensagem = "Você conseguiu fugir!"
                self.mensagem_timer = 120
                self.fuga_sucesso = True  # ✅ marca fuga bem-sucedida
                arcade.schedule(self.voltar_mundo, 1)
            else:
                self.mensagem = "Você tentou fugir, mas o inimigo bloqueou sua saída!"
                self.mensagem_timer = 120
                self.fugir_desabilitado = True

                # Inimigo contra-ataca
                dano = random.randint(5, 15)
                self.vida_jogador = max(self.vida_jogador - dano, 0)
                self.mensagem += f"\nO inimigo contra-atacou e causou {dano} de dano!"

    # =====================================================
    #                VOLTAR AO MUNDO
    # =====================================================
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

        # ✅ Se inimigo foi derrotado OU fuga bem-sucedida, remove do mapa
        if hasattr(mundo, "inimigos") and hasattr(self, "inimigo") and self.inimigo:
            if self.fuga_sucesso or self.vida_inimigo <= 0:
                if self.inimigo in mundo.inimigos:
                    try:
                        self.inimigo.remove_from_sprite_lists()
                    except Exception:
                        pass
                    try:
                        mundo.inimigos.remove(self.inimigo)
                    except ValueError:
                        pass

                # Só marca como derrotado se ele morreu (não fuga)
                if self.vida_inimigo <= 0 and hasattr(self.inimigo, "id") and hasattr(estado, "inimigos_derrotados"):
                    estado.inimigos_derrotados.add(f"inimigo_{self.inimigo.id}")

        # Corrige movimento e fundo ao retornar
        mundo.moving_left = False
        mundo.moving_right = False
        mundo.velocity_x = 0
        arcade.set_background_color(arcade.color.SKY_BLUE)

        self.window.show_view(mundo)
