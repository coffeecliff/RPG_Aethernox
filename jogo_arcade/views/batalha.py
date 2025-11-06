import arcade
import random
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from config import *
from sprites.inimigo import Inimigo
from views.gameover import ViewGameOver

CAMINHO_INIMIGO = os.path.join("..", "jogo_arcade", "imagens", "enemies", "enemie.png")

class ViewBatalha(arcade.View):
    def __init__(self, jogador=None, inimigo=None):
        super().__init__()
        arcade.set_background_color(arcade.color.DARK_TAN)
        self.camera_game = arcade.Camera2D()
        self.camera_gui = arcade.Camera2D()

        # ======= JOGADOR =======
        if jogador is None:
            # Cria um jogador padrão (Guerreiro)
            classe_default = "Guerreiro"
            stats = ESTATISTICAS_PERSONAGENS[classe_default]
            self.jogador = type(
                "Jogador",
                (),
                {
                    "nome": "Herói",
                    "classe": classe_default,
                    "vida": stats["vida"],
                    "vida_max": stats["vida"],
                    "mana": stats["mana"],        
                    "mana_max": stats["mana"],
                    "ataque": stats["ataque"],
                    "defesa": stats["defesa"],
                    "velocidade": stats["velocidade"],
                    "inventario": {"Poção": 3},
                },
            )
        else:
            # jogador já existente, garante atributos básicos
            self.jogador = jogador
            classe = getattr(jogador, "classe", "Guerreiro")
            stats = ESTATISTICAS_PERSONAGENS.get(classe, {})

            self.jogador.vida_max = stats.get("vida", getattr(self.jogador, "vida_max", 100))
            self.jogador.vida = getattr(self.jogador, "vida", self.jogador.vida_max)

            self.jogador.mana_max = stats.get("mana_max", 50)
            self.jogador.mana = min(getattr(self.jogador, "mana", self.jogador.mana_max), self.jogador.mana_max)

            self.jogador.ataque = stats.get("ataque", getattr(self.jogador, "ataque", 10))
            self.jogador.defesa = stats.get("defesa", getattr(self.jogador, "defesa", 5))
            self.jogador.velocidade = stats.get("velocidade", getattr(self.jogador, "velocidade", 5))
            self.jogador.inventario = getattr(self.jogador, "inventario", {"Poção": 3})

        self.turno = 1

        # Sprite e objeto inimigo
        self.inimigo = inimigo or Inimigo(x=LARGURA_TELA / 2, y=ALTURA_TELA * 0.72)
        self.dano_inimigo_mensagens = []
        self.inimigo_sprite = arcade.Sprite(CAMINHO_INIMIGO, scale=1)
        self.inimigo_sprite.center_x = LARGURA_TELA / 2
        self.inimigo_sprite.center_y = ALTURA_TELA * 0.55
        self.inimigo_lista = arcade.SpriteList()
        self.inimigo_lista.append(self.inimigo_sprite)

        # Status do inimigo
        self.vida_inimigo = getattr(self.inimigo, "vida", 120)
        self.max_vida_inimigo = getattr(self.inimigo, "vida_max", 120)
        self.inimigo_nome = getattr(self.inimigo, "nome", "Inimigo")

        self.mensagem = ""
        self.mensagem_timer = 0
        self.mostrar_itens = False
        self.itens_opcoes = []
        self.jogador_pode_acionar = True

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

        self.fugir_desabilitado = False
        self.fuga_sucesso = False
        self.batalha_encerrada = False
        self._retorno_agendado = False

        # =====================================================
        # MACHINE LEARNING PARA INIMIGO
        # =====================================================
        # Features: [vida_jogador_ratio, mana_jogador_ratio, vida_inimigo_ratio]
        # Labels: 0 = ataque fraco, 1 = ataque forte, 2 = magia
        X = np.array([
            [1.0, 1.0, 1.0],
            [0.5, 1.0, 0.8],
            [0.3, 0.5, 0.7],
            [0.7, 0.2, 0.4],
            [0.2, 0.1, 0.2],
            [0.9, 0.5, 0.9]
        ])
        y = np.array([0, 1, 1, 2, 2, 0])
        self.modelo_inimigo = RandomForestClassifier(n_estimators=10)
        self.modelo_inimigo.fit(X, y)

    # =====================================================
    # MÉTODOS DE COMBATE
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

    def aplicar_dano_inimigo(self, dano, fonte="ataque"):
        if self.batalha_encerrada:
            return

        self.vida_inimigo = max(self.vida_inimigo - dano, 0)
        if hasattr(self.inimigo, "vida"):
            try:
                self.inimigo.vida = self.vida_inimigo
            except Exception:
                pass

        if fonte == "magia":
            self.mostrar_resultado_acao(f"✨ Magia causou {dano} de dano!")
        else:
            self.mostrar_resultado_acao(f"⚔️ Você causou {dano} de dano!")

        if self.vida_inimigo <= 0:
            self.mostrar_resultado_acao("Inimigo derrotado! Voltando ao mundo...")
            self.batalha_encerrada = True
            if hasattr(self.inimigo, "vida"):
                try:
                    self.inimigo.vida = 0
                except Exception:
                    pass
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

        # Barra de vida do inimigo
        barra_largura, barra_altura = 500, 35
        barra_left = LARGURA_TELA / 2 - barra_largura / 2
        barra_bottom = self.inimigo_sprite.center_y + self.inimigo_sprite.height / 2 + 40
        arcade.draw_lbwh_rectangle_filled(barra_left, barra_bottom, barra_largura, barra_altura, arcade.color.DARK_RED)
        vida_ratio = self.vida_inimigo / self.max_vida_inimigo if self.max_vida_inimigo > 0 else 0
        vida_width = barra_largura * max(0.0, min(1.0, vida_ratio))
        arcade.draw_lbwh_rectangle_filled(barra_left, barra_bottom, vida_width, barra_altura, COR_BARRA_VIDA_INIMIGO)

        # HUD jogador
        base_x = 60
        arcade.draw_text(f"{self.jogador.classe}: {self.jogador.nome}", base_x, 160, COR_TEXTO, 26)
        arcade.draw_text(f"Vida: {int(self.jogador.vida)}/{int(self.jogador.vida_max)}", base_x, 120, COR_TEXTO, 26)
        mana_atual = int(getattr(self.jogador, "mana", 0))
        mana_max = int(getattr(self.jogador, "mana_max", 0))
        arcade.draw_text(f"Mana: {mana_atual}/{mana_max}", base_x, 80, COR_TEXTO, 26)
        arcade.draw_text(f"Turno: {self.turno}", base_x, 40, COR_TEXTO, 24)

        # Botões
        for nome, (x, y) in self.box_coords.items():
            alpha = 100 if self.batalha_encerrada else 255
            if nome == "Fugir" and self.fugir_desabilitado:
                alpha = 100
            arcade.draw_lbwh_rectangle_filled(x, y, self.box_largura, self.box_altura, (*COR_CAIXA[:3], alpha))
            arcade.draw_text(nome, x + self.box_largura / 2, y + self.box_altura / 2, COR_TEXTO, 24,
                             anchor_x="center", anchor_y="center")

        # Mensagem central
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

        for msg in self.dano_inimigo_mensagens:
            arcade.draw_text(
                msg["texto"],
                msg["x"],
                msg["y"],
                arcade.color.RED,
                28,
                anchor_x="center",
                anchor_y="center"
            )
            msg["y"] += 1.5
            msg["timer"] -= 1
        self.dano_inimigo_mensagens = [m for m in self.dano_inimigo_mensagens if m["timer"] > 0]

        # Menu de itens
        if self.mostrar_itens:
            menu_width = len(self.itens_opcoes) * (self.box_largura + 20) - 20
            menu_height = self.box_altura + 20
            menu_x = self.start_x
            menu_y = self.start_y + 90
            menu_bottom = 20
            menu_top = 350

            arcade.draw_lrbt_rectangle_filled(0, LARGURA_TELA, menu_bottom, menu_top, arcade.color.FRENCH_BISTRE)
            arcade.draw_lrbt_rectangle_outline(0, LARGURA_TELA, menu_bottom, menu_top, arcade.color.BLACK, border_width=4)
            for i, item in enumerate(self.itens_opcoes):
                ix = self.start_x + i * (self.box_largura + 20)
                iy = self.start_y + 100
                arcade.draw_lbwh_rectangle_filled(ix, iy, self.box_largura, self.box_altura, arcade.color.DARK_TAN)
                arcade.draw_text(item, ix + self.box_largura / 2, iy + self.box_altura / 2, arcade.color.WHITE, 24,
                                 anchor_x="center", anchor_y="center")

    # =====================================================
    # EVENTOS
    # =====================================================
    def on_show_view(self):
        self.inimigo_nome = getattr(self.inimigo, "nome", self.inimigo_nome)
        self.vida_inimigo = getattr(self.inimigo, "vida", self.vida_inimigo)
        self.max_vida_inimigo = getattr(self.inimigo, "vida_max", self.max_vida_inimigo)
        self.mostrar_inicio_combate()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.batalha_encerrada:
            return
        if self.mostrar_itens:
            for i, item in enumerate(self.itens_opcoes):
                ix = self.start_x + i * (self.box_largura + 20)
                iy = self.start_y + 100
                if ix <= x <= ix + self.box_largura and iy <= y <= iy + self.box_altura:
                    self.jogador.vida = min(self.jogador.vida + 30, self.jogador.vida_max)
                    try:
                        self.jogador.inventario[item] -= 1
                    except Exception:
                        pass
                    self.mostrar_resultado_acao(f"Você usou {item} e recuperou 30 de vida!")
                    self.mostrar_itens = False
                    return
            self.mostrar_itens = False
            self.mostrar_texto("Menu de itens fechado.")
            return

        for nome, (bx, by) in self.box_coords.items():
            if bx <= x <= bx + self.box_largura and by <= y <= by + self.box_altura:
                if nome == "Fugir" and self.fugir_desabilitado:
                    self.mostrar_texto("Você não pode fugir agora.")
                    return
                self.acao(nome)
                break

    # =====================================================
    # ATAQUES DO INIMIGO COM MACHINE LEARNING
    # =====================================================
    def ataque_inimigo_com_ml(self, delta_time):
        if self.batalha_encerrada or self.vida_inimigo <= 0:
            return

        vida_jogador_ratio = self.jogador.vida / self.jogador.vida_max if self.jogador.vida_max else 1
        mana_jogador_ratio = self.jogador.mana / self.jogador.mana_max if self.jogador.mana_max else 1
        vida_inimigo_ratio = self.vida_inimigo / self.max_vida_inimigo if self.max_vida_inimigo else 1
        features = np.array([[vida_jogador_ratio, mana_jogador_ratio, vida_inimigo_ratio]])
        acao_predita = self.modelo_inimigo.predict(features)[0]

        if acao_predita == 0:
            dano = random.randint(5, 10)
            texto = f"Inimigo causou {dano} de dano!"
        elif acao_predita == 1:
            dano = random.randint(10, 20)
            texto = f"Inimigo causou {dano} de dano!"
        else:
            dano = random.randint(15, 25)
            texto = f"Inimigo usou magia e causou {dano} de dano!"

        self.jogador.vida = max(self.jogador.vida - dano, 0)
        self.dano_inimigo_mensagens.append({
            "texto": f"-{dano} HP",
            "x": LARGURA_TELA / 2,
            "y": ALTURA_TELA / 2,
            "timer": 60
        })

        if self.jogador.vida <= 0:
            self.batalha_encerrada = True
            self.window.show_view(ViewGameOver(jogador_nome=self.jogador.nome))

    def agendar_ataque_inimigo(self):
        if self.batalha_encerrada or self.vida_inimigo <= 0:
            return
        arcade.schedule_once(self.ataque_inimigo_com_ml, 0.8)

    # =====================================================
    # MAGIA, AÇÃO E FUGA
    # =====================================================
    def usar_magia(self):
        custo_mana = 20
        if self.jogador.mana >= custo_mana:
            self.jogador.mana -= custo_mana
            dano = self.jogador.ataque * random.uniform(1.2, 1.5)
            self.aplicar_dano_inimigo(int(dano), fonte="magia")
            self.mostrar_texto(f"✨ {self.jogador.classe} lançou Magia! Dano: {int(dano)}")
            self.agendar_ataque_inimigo()
            self.turno += 1
        else:
            self.mostrar_texto("⚠️ Mana insuficiente!")

    def acao(self, nome):
        if self.batalha_encerrada:
            return

        if nome == "Atacar":
            dano = random.randint(10, 25)
            self.aplicar_dano_inimigo(dano, fonte="ataque")
            self.agendar_ataque_inimigo()
            self.turno += 1
        elif nome == "Magia":
            self.usar_magia()
        elif nome == "Item":
            self.mostrar_itens = True
            self.itens_opcoes = [item for item, qtd in self.jogador.inventario.items() if qtd > 0]
            if not self.itens_opcoes:
                self.mostrar_texto("Você não tem itens disponíveis.")
                self.mostrar_itens = False
                return
            self.mostrar_texto("Escolha um item para usar (ou clique fora para cancelar).")
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
                self.fuga_sucesso = True
                self.batalha_encerrada = True
                if not self._retorno_agendado:
                    self._retorno_agendado = True
                    arcade.schedule(self.voltar_mundo, 1)
            else:
                self.mensagem = "Você tentou fugir, mas o inimigo bloqueou sua saída!"
                self.mensagem_timer = 120
                self.fugir_desabilitado = True
                dano = random.randint(5, 15)
                self.jogador.vida = max(self.jogador.vida - dano, 0)
                self.mostrar_resultado_acao(f"O inimigo contra-atacou e causou {dano} de dano!")
                if self.jogador.vida <= 0:
                    self.encerrar_batalha(vitoria=False)

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
            if hasattr(self.inimigo, "vida"):
                try:
                    self.inimigo.vida = 0
                except Exception:
                    pass
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
        try:
            if hasattr(estado, "player_pos") and hasattr(mundo, "player_sprite"):
                mundo.player_sprite.center_x = estado.player_pos[0] - 100
                mundo.player_sprite.center_y = estado.player_pos[1]
            if hasattr(estado, "player_facing"):
                mundo.facing_right = estado.player_facing
        except Exception:
            pass
        if hasattr(mundo, "inimigos"):
            ref_inimigo = getattr(estado, "inimigo_em_batalha", None) or getattr(self, "inimigo", None)
            if ref_inimigo and (self.fuga_sucesso or self.vida_inimigo <= 0):
                try:
                    if ref_inimigo in mundo.inimigos:
                        ref_inimigo.remove_from_sprite_lists()
                        mundo.inimigos.remove(ref_inimigo)
                except Exception:
                    pass
                if self.vida_inimigo <= 0 and hasattr(ref_inimigo, "id") and hasattr(estado, "inimigos_derrotados"):
                    estado.inimigos_derrotados.add(f"inimigo_{ref_inimigo.id}")
            try:
                estado.inimigo_em_batalha = None
            except Exception:
                pass
        if hasattr(mundo, "moving_left"):
            mundo.moving_left = False
        if hasattr(mundo, "moving_right"):
            mundo.moving_right = False
        if hasattr(mundo, "velocity_x"):
            mundo.velocity_x = 0
        self.window.show_view(mundo)
