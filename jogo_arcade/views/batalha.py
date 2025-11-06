import arcade
import random
import os
from config import *
from sprites.inimigo import Inimigo

CAMINHO_INIMIGO = os.path.join("..", "jogo_arcade", "imagens", "enemies", "enemie.png")

class ViewBatalha(arcade.View):
    def __init__(self, jogador=None, inimigo=None):
        super().__init__()
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self.camera_game = arcade.Camera2D()
        self.camera_gui = arcade.Camera2D()

        # Dados do jogador (exemplo)
        self.jogador = jogador or type(
            "Jogador",
            (),
            {
                "nome": "Herói",
                "classe": "Guerreiro",
                "vida": 100,
                "vida_max": 100,
                "mana": 50,
                "mana_max": 50,
                "inventario": {"Poção": 3},
            },
        )
        self.turno = 1

        # Sprite e objeto inimigo (recebe a instância vinda do mundo quando existir)
        self.inimigo = inimigo or Inimigo(x=LARGURA_TELA / 2, y=ALTURA_TELA * 0.72)
        self.inimigo_sprite = arcade.Sprite(CAMINHO_INIMIGO, scale=1)
        self.inimigo_sprite.center_x = LARGURA_TELA / 2
        self.inimigo_sprite.center_y = ALTURA_TELA * 0.55
        self.inimigo_lista = arcade.SpriteList()
        self.inimigo_lista.append(self.inimigo_sprite)

        # Status do inimigo (preferimos atributos do objeto inimigo quando presentes)
        self.vida_inimigo = getattr(self.inimigo, "vida", 120)
        self.max_vida_inimigo = getattr(self.inimigo, "vida_max", 120)
        self.inimigo_nome = getattr(self.inimigo, "nome", "Inimigo")

        self.mensagem = ""
        self.mensagem_timer = 0
        self.mostrar_itens = False
        self.itens_opcoes = []

        # Botões
        self.box_largura = 220
        self.box_altura = 70
        spacing = 60
        total_width = 4 * self.box_largura + 3 * spacing
        self.start_x = LARGURA_TELA / 2 - total_width / 2
        self.start_y = 120
        self.box_coords = {
            "Atacar": (self.start_x, self.start_y),
            "Magia": (self.start_x + self.box_largura + spacing, self.start_y),
            "Item": (self.start_x + 2 * (self.box_largura + spacing), self.start_y),
            "Fugir": (self.start_x + 3 * (self.box_largura + spacing), self.start_y),
        }

        # Controle de estado de batalha
        self.fugir_desabilitado = False
        self.fuga_sucesso = False
        self.batalha_encerrada = False  # bloqueia ações quando True

        # Controle para impedir multiplos agendamentos
        self._retorno_agendado = False

    # =====================================================
    # VISUAL DO COMBATE
    # =====================================================
    def mostrar_inicio_combate(self):
        self.mensagem = f"{self.jogador.nome} vs {self.inimigo_nome} — Combate iniciado!"
        self.mensagem_timer = 180

    def mostrar_texto(self, mensagem):
        self.mensagem = mensagem
        self.mensagem_timer = 150

    def mostrar_resultado_acao(self, mensagem):
        self.mensagem = mensagem
        self.mensagem_timer = 150

    # =====================================================
    # DANO E CHECAGEM DE VITÓRIA
    # =====================================================
    def aplicar_dano_inimigo(self, dano, fonte="ataque"):
        if self.batalha_encerrada:
            return

        # Deduz vida local e sincroniza com o objeto Inimigo (se houver)
        self.vida_inimigo = max(self.vida_inimigo - dano, 0)
        if hasattr(self.inimigo, "vida"):
            try:
                self.inimigo.vida = self.vida_inimigo
            except Exception:
                pass

        # Mensagem
        if fonte == "magia":
            self.mostrar_resultado_acao(f"✨ Magia causou {dano} de dano!")
        else:
            self.mostrar_resultado_acao(f"⚔️ Você causou {dano} de dano!")

        # Se morreu, encerra e agenda voltar_mundo (mantendo lógica antiga)
        if self.vida_inimigo <= 0:
            self.mostrar_resultado_acao("Inimigo derrotado! Voltando ao mundo...")
            self.batalha_encerrada = True
            # garante que o objeto Inimigo também receba vida zero
            if hasattr(self.inimigo, "vida"):
                try:
                    self.inimigo.vida = 0
                except Exception:
                    pass
            # agenda retorno (uso direto igual ao seu código antigo)
            if not self._retorno_agendado:
                self._retorno_agendado = True
                arcade.schedule(self.voltar_mundo, 2)

    # =====================================================
    # DRAW
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
        vida_ratio = self.vida_inimigo / self.max_vida_inimigo if self.max_vida_inimigo > 0 else 0
        vida_width = barra_largura * max(0.0, min(1.0, vida_ratio))
        arcade.draw_lbwh_rectangle_filled(barra_left, barra_bottom, vida_width, barra_altura, COR_BARRA_VIDA_INIMIGO)

        # --- HUD jogador ---
        base_x = 60
        arcade.draw_text(f"{self.jogador.classe}: {self.jogador.nome}", base_x, 160, COR_TEXTO, 26)
        arcade.draw_text(f"Vida: {self.jogador.vida}/{self.jogador.vida_max}", base_x, 120, COR_TEXTO, 26)
        arcade.draw_text(f"Mana: {self.jogador.mana}/{self.jogador.mana_max}", base_x, 80, COR_TEXTO, 26)
        arcade.draw_text(f"Turno: {self.turno}", base_x, 40, COR_TEXTO, 24)

        # --- Botões ---
        for nome, (x, y) in self.box_coords.items():
            # se batalha encerrada, visualmente desabilita
            alpha = 100 if self.batalha_encerrada else 255
            if nome == "Fugir" and self.fugir_desabilitado:
                alpha = 100
            arcade.draw_lbwh_rectangle_filled(x, y, self.box_largura, self.box_altura, (*COR_CAIXA[:3], alpha))
            arcade.draw_text(nome, x + self.box_largura / 2, y + self.box_altura / 2, COR_TEXTO, 24,
                             anchor_x="center", anchor_y="center")

        # --- Mensagem central ---
        if self.mensagem_timer > 0:
            arcade.draw_text(
                self.mensagem,
                LARGURA_TELA / 2,
                self.start_y + 160,
                COR_MENSAGEM,
                32,
                anchor_x="center",
                align="center",
                width=700,
                multiline=True,
            )
            self.mensagem_timer -= 1

    # =====================================================
    # EVENTOS
    # =====================================================
    # --- ATAQUE DO INIMIGO --- #
    def iniciar_ataque_inimigo(self):
        """Agenda ataques automáticos do inimigo a cada poucos segundos."""
        arcade.schedule(self.ataque_inimigo, 3.5)  # a cada 3.5s

    def parar_ataque_inimigo(self):
        """Cancela o ataque automático."""
        try:
            arcade.unschedule(self.ataque_inimigo)
        except Exception:
            pass

    def ataque_inimigo(self, delta_time=None):
        """Executa o ataque do inimigo contra o jogador."""
        if self.vida_inimigo <= 0:
            self.parar_ataque_inimigo()
            return

        # Define dano aleatório
        dano = random.randint(5, 15)
        self.vida_jogador -= dano
        if self.vida_jogador < 0:
            self.vida_jogador = 0

        # Mostra feedback visual
        self.mensagem_temporaria = f"O inimigo atacou! -{dano} HP"
        arcade.schedule_once(self.limpar_mensagem, 2.0)

        # Verifica se o jogador morreu
        if self.vida_jogador <= 0:
            self.mensagem_temporaria = "Você foi derrotado..."
            arcade.schedule_once(self.voltar_mundo, 3.0)
            self.parar_ataque_inimigo()

    def limpar_mensagem(self, delta_time=None):
        """Limpa mensagem de ataque."""
        self.mensagem_temporaria = ""

        
    def on_show_view(self):
        # Sincroniza nomes/vidas caso objeto Inimigo tenha valores próprios
        self.inimigo_nome = getattr(self.inimigo, "nome", self.inimigo_nome)
        self.vida_inimigo = getattr(self.inimigo, "vida", self.vida_inimigo)
        self.max_vida_inimigo = getattr(self.inimigo, "vida_max", self.max_vida_inimigo)
        self.mostrar_inicio_combate()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.batalha_encerrada:
            return  # bloqueia clicks depois do fim
        for nome, (bx, by) in self.box_coords.items():
            if bx <= x <= bx + self.box_largura and by <= y <= by + self.box_altura:
                if nome == "Fugir" and self.fugir_desabilitado:
                    self.mostrar_texto("Você não pode fugir agora.")
                    return
                self.acao(nome)
                break

    # =====================================================
    # AÇÕES
    # =====================================================
    def acao(self, nome):
        if self.batalha_encerrada:
            return

        if nome == "Atacar":
            dano = random.randint(10, 25)
            self.aplicar_dano_inimigo(dano, fonte="ataque")

        elif nome == "Magia":
            if self.jogador.mana >= 15:
                self.jogador.mana -= 15
                dano = random.randint(25, 45)
                self.aplicar_dano_inimigo(dano, fonte="magia")
            else:
                self.mostrar_texto("⚠️ Mana insuficiente!")

        elif nome == "Item":
            if not self.mostrar_itens:
                self.mostrar_itens = True
                self.itens_opcoes = [item for item, qtd in self.jogador.inventario.items() if qtd > 0]
                self.mostrar_texto("Clique em Item novamente para usar um item aleatório.")
            else:
                if self.itens_opcoes:
                    item = random.choice(self.itens_opcoes)
                    self.jogador.vida = min(self.jogador.vida + 30, self.jogador.vida_max)
                    try:
                        self.jogador.inventario[item] -= 1
                    except Exception:
                        pass
                    self.mostrar_resultado_acao(f"💊 Você usou {item} e recuperou 30 de vida!")
                else:
                    self.mostrar_texto("Você não tem itens disponíveis.")
                self.mostrar_itens = False

        elif nome == "Fugir":
            if self.fugir_desabilitado:
                return
            vida_ratio = self.jogador.vida / self.jogador.vida_max if self.jogador.vida_max else 1
            chance_fuga = 60
            if vida_ratio <= 0.3:
                chance_fuga += 20
            resultado = random.randint(1, 100)

            if resultado <= chance_fuga:
                self.mostrar_resultado_acao("Você conseguiu fugir!")
                self.fuga_sucesso = True  # marca fuga
                self.batalha_encerrada = True
                # agenda retorno igual ao seu código antigo
                if not self._retorno_agendado:
                    self._retorno_agendado = True
                    arcade.schedule(self.voltar_mundo, 1)
            else:
                self.mensagem = "Você tentou fugir, mas o inimigo bloqueou sua saída!"
                self.mensagem_timer = 120
                self.fugir_desabilitado = True
                # inimigo contra-ataca
                dano = random.randint(5, 15)
                self.jogador.vida = max(self.jogador.vida - dano, 0)
                self.mostrar_resultado_acao(f"O inimigo contra-atacou e causou {dano} de dano!")
                # checa derrota do jogador
                if self.jogador.vida <= 0:
                    self.encerrar_batalha(vitoria=False)

        # incremento de turno — só se a batalha continuar
        if not self.batalha_encerrada:
            self.turno += 1

    # =====================================================
    # ENCERRAMENTO E RETORNO AO MUNDO
    # =====================================================
    def encerrar_batalha(self, vitoria: bool):
        if self.batalha_encerrada:
            return
        self.batalha_encerrada = True

        if vitoria:
            msg = f"🏆 {self.jogador.nome} derrotou {self.inimigo_nome}! Retornando ao mundo..."
            self.mostrar_resultado_acao(msg)
            # marca vida do objeto inimigo também
            if hasattr(self.inimigo, "vida"):
                try:
                    self.inimigo.vida = 0
                except Exception:
                    pass
            # agenda retorno imediato igual ao seu código antigo
            if not self._retorno_agendado:
                self._retorno_agendado = True
                arcade.schedule(self.voltar_mundo, 2)
        else:
            msg = f"{self.jogador.nome} foi derrotado por {self.inimigo_nome}..."
            self.mostrar_resultado_acao(msg)
            if not self._retorno_agendado:
                self._retorno_agendado = True
                arcade.schedule(self.voltar_mundo, 2)

    def voltar_mundo(self, delta_time=None):
        """Retorna à cena do mundo, removendo o inimigo se derrotado ou fuga bem-sucedida."""
        # Cancela o agendamento para evitar múltiplas chamadas
        try:
            arcade.unschedule(self.voltar_mundo)
        except Exception:
            pass

        estado = getattr(self.window, "game_state", None)
        if not estado or not hasattr(estado, "cena_mundo"):
            from views.mundo import ViewMundo
            self.window.show_view(ViewMundo())
            return

        mundo = estado.cena_mundo

        # Atualiza posição e direção do jogador
        try:
            if hasattr(estado, "player_pos") and hasattr(mundo, "player_sprite"):
                mundo.player_sprite.center_x = estado.player_pos[0] - 100
                mundo.player_sprite.center_y = estado.player_pos[1]
            if hasattr(estado, "player_facing"):
                mundo.facing_right = estado.player_facing
        except Exception:
            pass

        # Verifica se o inimigo deve ser removido
        if hasattr(mundo, "inimigos"):
            ref_inimigo = getattr(estado, "inimigo_em_batalha", None) or getattr(self, "inimigo", None)

            if ref_inimigo and (self.fuga_sucesso or self.vida_inimigo <= 0):
                # Remove inimigo da lista e das sprites
                try:
                    if ref_inimigo in mundo.inimigos:
                        ref_inimigo.remove_from_sprite_lists()
                        mundo.inimigos.remove(ref_inimigo)
                except Exception:
                    pass

                # Marca como derrotado apenas se ele morreu
                if self.vida_inimigo <= 0 and hasattr(ref_inimigo, "id") and hasattr(estado, "inimigos_derrotados"):
                    estado.inimigos_derrotados.add(f"inimigo_{ref_inimigo.id}")

            # Limpa referência para evitar reaproveitar
            try:
                estado.inimigo_em_batalha = None
            except Exception:
                pass

                # Marca como derrotado apenas se ele morreu
                if self.vida_inimigo <= 0 and hasattr(self.inimigo, "id") and hasattr(estado, "inimigos_derrotados"):
                    estado.inimigos_derrotados.add(f"inimigo_{self.inimigo.id}")

        # Reseta movimento e física ao voltar
        if hasattr(mundo, "moving_left"):
            mundo.moving_left = False
        if hasattr(mundo, "moving_right"):
            mundo.moving_right = False
        if hasattr(mundo, "velocity_x"):
            mundo.velocity_x = 0

        arcade.set_background_color(arcade.color.SKY_BLUE)
        self.window.show_view(mundo)
