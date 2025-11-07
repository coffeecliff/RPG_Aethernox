import arcade
import random
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from config import *
from sprites.inimigo import Inimigo
from views.gameover import ViewGameOver
from pathlib import Path

# Caminho base do projeto (ajuste conforme a posição deste arquivo)
BASE_DIR = Path(__file__).resolve().parent.parent  # sobe um nível se este arquivo estiver dentro de /views/
IMAGENS_DIR = BASE_DIR / "imagens"

# Caminho do inimigo
CAMINHO_INIMIGO = IMAGENS_DIR / "enemies" / "enemie.png"

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
                    "inventario": {},
                    "moedas": 0,  # novo atributo de moedas
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
            self.jogador.inventario = getattr(self.jogador, "inventario", {})
            if not hasattr(self.jogador, "moedas"):
                self.jogador.moedas = 0  # inicia com 0 moedas
            if not hasattr(self.jogador, "xp"):
                self.jogador.xp = 0
            if not hasattr(self.jogador, "xp_proximo"):
                self.jogador.xp_proximo = 100
            if not hasattr(self.jogador, "level"):
                self.jogador.level = 1

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
        self.moedas_inimigo = getattr(self.inimigo, "moedas", random.randint(5, 20))  # moedas aleatórias por inimigo

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

        # Aplica dano
        self.vida_inimigo = max(self.vida_inimigo - dano, 0)
        if hasattr(self.inimigo, "vida"):
            try:
                self.inimigo.vida = self.vida_inimigo
            except Exception:
                pass

        # Mensagem do dano
        if fonte == "magia":
            self.mostrar_resultado_acao(f"✨ Magia causou {dano} de dano!")
        else:
            self.mostrar_resultado_acao(f"⚔️ Você causou {dano} de dano!")

        # Inimigo derrotado
        if self.vida_inimigo <= 0:
            self.batalha_encerrada = True
            self.jogador_pode_acionar = False  # bloqueia ações imediatamente

            moedas_ganhas = random.randint(25, 70)
            xp_ganho = random.randint(20, 40)
            self.jogador.moedas += moedas_ganhas
            self.jogador.xp += xp_ganho
            self.verificar_level_up()

            if hasattr(self.inimigo, "vida"):
                try:
                    self.inimigo.vida = 0
                except Exception:
                    pass

            self.mostrar_resultado_acao(
                f"Inimigo derrotado! Você ganhou {moedas_ganhas} moedas e {xp_ganho} XP. Voltando ao mundo..."
            )

            if not self._retorno_agendado:
                self._retorno_agendado = True
                arcade.schedule_once(self.voltar_mundo, 2)


    # =====================================================
    # DRAW
    # =====================================================
    def on_draw(self):
        self.clear()
        self.camera_game.use()
        self.inimigo_lista.draw()
        self.camera_gui.use()

        # HUD jogador (movido para o topo da tela)


        # HUD jogador (movido para o topo da tela)
        base_x = 60
        top_margin = ALTURA_TELA - 60  # ponto de partida próximo ao topo

        arcade.draw_text(f"{self.jogador.classe}: {self.jogador.nome}", base_x, top_margin, COR_TEXTO, 26)
        arcade.draw_text(f"Vida: {int(self.jogador.vida)}/{int(self.jogador.vida_max)}", base_x, top_margin - 50, COR_TEXTO, 26)
        mana_atual = int(getattr(self.jogador, "mana", 0))
        mana_max = int(getattr(self.jogador, "mana_max", 0))
        arcade.draw_text(f"Mana: {mana_atual}/{mana_max}", base_x, top_margin - 100, COR_TEXTO, 26)
        arcade.draw_text(f"Moedas: {self.jogador.moedas}", base_x, top_margin - 150, COR_TEXTO, 24)
        arcade.draw_text(f"Turno: {self.turno}", base_x, top_margin - 200, COR_TEXTO, 24)

        # ======= BARRA DE XP =======
        xp = getattr(self.jogador, "xp", 0)
        xp_proximo = getattr(self.jogador, "xp_proximo", 100)
        barra_xp_largura = 200
        barra_xp_altura = 20
        barra_xp_left = base_x
        barra_xp_bottom = top_margin - 240
        xp_ratio = min(1.0, xp / xp_proximo)
        arcade.draw_lbwh_rectangle_filled(barra_xp_left, barra_xp_bottom, barra_xp_largura, barra_xp_altura, arcade.color.GRAY)
        arcade.draw_lbwh_rectangle_filled(barra_xp_left, barra_xp_bottom, barra_xp_largura * xp_ratio, barra_xp_altura, arcade.color.GREEN)
        arcade.draw_text(f"XP: {xp}/{xp_proximo}", barra_xp_left + 10, barra_xp_bottom + 2, arcade.color.BLACK, 14)
        # Barra de vida do inimigo
        barra_largura, barra_altura = 500, 35
        barra_left = LARGURA_TELA / 2 - barra_largura / 2
        barra_bottom = self.inimigo_sprite.center_y + self.inimigo_sprite.height / 2 + 40
        arcade.draw_lbwh_rectangle_filled(barra_left, barra_bottom, barra_largura, barra_altura, arcade.color.DARK_RED)
        vida_ratio = self.vida_inimigo / self.max_vida_inimigo if self.max_vida_inimigo > 0 else 0
        vida_width = barra_largura * max(0.0, min(1.0, vida_ratio))
        arcade.draw_lbwh_rectangle_filled(barra_left, barra_bottom, vida_width, barra_altura, COR_BARRA_VIDA_INIMIGO)


        # === NOVO: Nível e XP ===
        nivel = getattr(self.jogador, "nivel", 1)
        xp = getattr(self.jogador, "xp", 0)
        xp_proximo = getattr(self.jogador, "xp_proximo", 100)

        arcade.draw_text(f"Level: {nivel}", base_x, top_margin - 230, COR_TEXTO, 24)

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
    def ganhar_xp(self, quantidade):
        """Adiciona XP e faz o jogador subir de nível se necessário."""
        self.jogador.xp += quantidade
        self.mostrar_texto(f"Você ganhou {quantidade} XP!")

        while self.jogador.xp >= self.xp_para_proximo_level:
            self.jogador.xp -= self.xp_para_proximo_level
            self.subir_level()

    def verificar_level_up(self):
        while self.jogador.xp >= self.jogador.xp_proximo:
            self.jogador.xp -= self.jogador.xp_proximo
            self.jogador.level += 1
            self.jogador.vida_max += 10
            self.jogador.vida = self.jogador.vida_max
            self.jogador.mana_max += 5
            self.jogador.mana = self.jogador.mana_max
            self.jogador.ataque += 2
            self.jogador.defesa += 1
            self.jogador.velocidade += 1
            self.jogador.moedas += 20  # recompensa extra
            self.jogador.xp_proximo = int(self.jogador.xp_proximo * 1.2)
            self.mostrar_texto(f"🎉 {self.jogador.nome} subiu para o nível {self.jogador.level}!")


    def subir_level(self):
        self.jogador.level += 1

        # Aumento de stats
        self.jogador.vida_max += 10
        self.jogador.mana_max += 5
        self.jogador.ataque += 2
        self.jogador.defesa += 1
        self.jogador.velocidade += 0.5

        # Recupera vida e mana
        self.jogador.vida = self.jogador.vida_max
        self.jogador.mana = self.jogador.mana_max

        # Recompensa em moedas
        moedas_ganhas = 50 + self.jogador.level * 10  # progressivo
        self.jogador.moedas += moedas_ganhas

        self.mostrar_resultado_acao(
            f"🏆 Level Up! Agora você é nível {self.jogador.level}.\n"
            f"Moedas recebidas: {moedas_ganhas}."
        )

        # Opcional: aumentar XP necessário para próximo nível (progressivo)
        self.xp_para_proximo_level = int(self.xp_para_proximo_level * 1.3)


    def on_show_view(self):
        self.inimigo_nome = getattr(self.inimigo, "nome", self.inimigo_nome)
        self.vida_inimigo = getattr(self.inimigo, "vida", self.vida_inimigo)
        self.max_vida_inimigo = getattr(self.inimigo, "vida_max", self.max_vida_inimigo)
        self.mostrar_inicio_combate()

        # No início da batalha, o jogador pode agir
        self.jogador_pode_acionar = True

    def on_mouse_press(self, x, y, button, modifiers):
        if self.batalha_encerrada:
            return

        # ===== Menu de itens =====
        if self.mostrar_itens:
            for i, nome_item in enumerate(self.itens_opcoes):
                ix = self.start_x + i * (self.box_largura + 20)
                iy = self.start_y + 100
                if ix <= x <= ix + self.box_largura and iy <= y <= iy + self.box_altura:
                    qtd = self.jogador.inventario.get(nome_item, 0)
                    if qtd > 0:
                        # Aplica efeito do item
                        if nome_item == "Poção de Vida":
                            self.jogador.vida = min(self.jogador.vida + 20, self.jogador.vida_max)
                            msg_efeito = "recuperou 20 de vida"
                        elif nome_item == "Poção de Mana":
                            self.jogador.mana = min(self.jogador.mana + 15, self.jogador.mana_max)
                            msg_efeito = "recuperou 15 de mana"
                        else:
                            msg_efeito = f"usou {nome_item}"

                        # Subtrai do inventário
                        self.jogador.inventario[nome_item] -= 1
                        if self.jogador.inventario[nome_item] <= 0:
                            del self.jogador.inventario[nome_item]

                        self.mostrar_resultado_acao(f"Você {msg_efeito}!")

                    else:
                        self.mostrar_resultado_acao("Você não tem mais deste item!")

                    self.mostrar_itens = False
                    return

            # Se clicou fora do item
            self.mostrar_itens = False
            self.mostrar_texto("Menu de itens fechado.")
            return

        # ===== Botões de ação =====
        for nome, (bx, by) in self.box_coords.items():
            if bx <= x <= bx + self.box_largura and by <= y <= by + self.box_altura:
                self.acao(nome)
                break



    # =====================================================
    # ATAQUES DO INIMIGO COM MACHINE LEARNING
    # =====================================================
    def ataque_inimigo_com_ml(self, delta_time):
        if self.batalha_encerrada or self.vida_inimigo <= 0:
            return

        # Chance de erro do inimigo (15%)
        if random.random() < 0.15:
            self.mostrar_resultado_acao(f"{self.inimigo_nome} errou o ataque!")
            self.jogador_pode_acionar = True
            self.turno += 1
            return

        # Lógica normal do ataque
        vida_jogador_ratio = self.jogador.vida / self.jogador.vida_max if self.jogador.vida_max else 1
        mana_jogador_ratio = self.jogador.mana / self.jogador.mana_max if self.jogador.mana_max else 1
        vida_inimigo_ratio = self.vida_inimigo / self.max_vida_inimigo if self.max_vida_inimigo else 1
        features = np.array([[vida_jogador_ratio, mana_jogador_ratio, vida_inimigo_ratio]])
        acao_predita = self.modelo_inimigo.predict(features)[0]

        if acao_predita == 0:
            dano = random.randint(5, 10)
        elif acao_predita == 1:
            dano = random.randint(10, 20)
        else:
            dano = random.randint(15, 25)

        self.jogador.vida = max(self.jogador.vida - dano, 0)
        self.dano_inimigo_mensagens.append({
            "texto": f"-{dano} HP",
            "x": LARGURA_TELA / 2,
            "y": ALTURA_TELA / 2,
            "timer": 60
        })

        # Libera jogador após o ataque
        self.jogador_pode_acionar = True
        self.turno += 1

        if self.jogador.vida <= 0:
            self.batalha_encerrada = True
            self.window.show_view(ViewGameOver(jogador_nome=self.jogador.nome))


    # =====================================================
    # AGENDAR ATAQUE
    # =====================================================
    def agendar_ataque_inimigo(self):
        if self.batalha_encerrada or self.vida_inimigo <= 0:
            return
        # Bloqueia ação do jogador (no caso de ataques subsequentes)
        self.jogador_pode_acionar = False
        arcade.schedule_once(self.ataque_inimigo_com_ml, 0.8)

    # =====================================================
    # AÇÃO DO JOGADOR
    # =====================================================
    def acao(self, nome):
        if self.batalha_encerrada:
            return

        if nome == "Atacar":
            if not self.jogador_pode_acionar:
                self.mostrar_texto("⏳ Aguarde o inimigo atacar!")
                return

            dano = random.randint(10, 25)
            self.aplicar_dano_inimigo(dano, fonte="ataque")

            # ⚡ Bloqueia jogador e agenda ataque do inimigo só depois de ação ofensiva
            self.jogador_pode_acionar = False
            self.agendar_ataque_inimigo()
            self.turno += 1

        elif nome == "Magia":
            if not self.jogador_pode_acionar:
                self.mostrar_texto("⏳ Aguarde o inimigo atacar!")
                return

            # Aqui, se magia for ofensiva, bloqueia turno e agenda ataque
            bloqueia_turno, dano = self.usar_magia()  # ajustar usar_magia para retornar se passou turno
            if bloqueia_turno:
                self.jogador_pode_acionar = False
                self.agendar_ataque_inimigo()
                self.turno += 1

        elif nome == "Item":
            # Não bloqueia jogador, não passa turno
            self.mostrar_itens = True
            self.itens_opcoes = [item for item, qtd in self.jogador.inventario.items() if qtd > 0]
            if not self.itens_opcoes:
                self.mostrar_texto("Você não tem itens disponíveis.")
                self.mostrar_itens = False
                return
            self.mostrar_texto("Escolha um item para usar (ou clique fora para cancelar).")

        elif nome == "Fugir":
            if not self.jogador_pode_acionar:
                self.mostrar_texto("⏳ Aguarde o inimigo atacar!")
                return

            self.fugir_desabilitado = True  

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
                self.mostrar_texto("Você tentou fugir, mas o inimigo bloqueou sua saída!")
                # ⚡ Só agenda ataque se realmente passou o turno
                self.jogador_pode_acionar = False
                self.agendar_ataque_inimigo()
                self.turno += 1


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
