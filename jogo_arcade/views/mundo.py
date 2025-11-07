import arcade
import os
import random
from config import *
from sprites.inimigo import Inimigo
from views.batalha import ViewBatalha
from sprites.loja import Loja
from types import SimpleNamespace


class ViewMundo(arcade.View):
    def __init__(self):
        super().__init__()

        # Caminho base do projeto
        BASE_DIR = Path(__file__).resolve().parent.parent  # sobe um nível se este arquivo estiver em /views/
        IMAGENS_DIR = BASE_DIR / "imagens"
        

        # Caminho do fundo
        background_path = IMAGENS_DIR / "mundo1" / "cenario1.png"

        estado = getattr(self.window, "game_state", None)
        
        # Carrega a textura do fundo
        self.background = arcade.load_texture(background_path)

        # Estado do jogo, se existir
        self.estado = getattr(self.window, "game_state", None)

        # Fundo — largo e em loop horizontal, mas sem se mover sozinho
        self.background_list = arcade.SpriteList()

        # Tamanho total do fundo (ex: 3x mais largo que a tela)
        LARGURA_TOTAL_FUNDO = LARGURA_TELA * 3

        # Carrega a textura e cria múltiplas cópias lado a lado
        num_repeticoes = (LARGURA_TOTAL_FUNDO // LARGURA_TELA) + 2
        for i in range(num_repeticoes):
            bg = arcade.Sprite(background_path)
            bg.center_x = (i * LARGURA_TELA) + (LARGURA_TELA // 2)
            bg.center_y = ALTURA_TELA // 2.6
            self.background_list.append(bg)

        # Câmera
        self.camera = arcade.Camera2D()

        # Listas
        self.scenery_list = arcade.SpriteList()
        self.ground_list = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()

        # --- Restaura o estado anterior se existir ---
        if estado and estado.cena_mundo:
            anterior = estado.cena_mundo
            self.__dict__.update(anterior.__dict__)
            return

        # --- Criação inicial ---
        estado = getattr(self.window, "game_state", None)
        personagem = getattr(estado, "personagem_escolhido", "Guerreiro")

        if personagem == "Mago":
            from config import PLAYER2_WALK as PLAYER_WALK, PLAYER2_IDLE as PLAYER_IDLE
        elif personagem == "Arqueiro":
            from config import PLAYER3_WALK as PLAYER_WALK, PLAYER3_IDLE as PLAYER_IDLE
        else:
            from config import PLAYER1_WALK as PLAYER_WALK, PLAYER1_IDLE as PLAYER_IDLE

        # Texturas e sprite do jogador
        self.walk_textures = [arcade.load_texture(p) for p in PLAYER_WALK]
        self.idle_textures = [arcade.load_texture(p) for p in PLAYER_IDLE]
        self.player_sprite = arcade.Sprite()
        self.player_sprite.texture = self.idle_textures[0]
        self.player_sprite.scale = 0.25
        self.player_sprite.center_x = LARGURA_TELA // 2
        self.player_sprite.center_y = ALTURA_TELA // 2.7
        self.all_sprites.append(self.player_sprite)

        # Cria jogador (objeto de status)
        if estado.jogador is None:
            stats = ESTATISTICAS_PERSONAGENS[personagem]
            estado.jogador = SimpleNamespace(
                nome="Herói",
                classe=personagem,
                vida=stats["vida"],
                vida_max=stats["vida"],
                mana=50,
                mana_max=50,
                ataque=stats["ataque"],
                defesa=stats["defesa"],
                velocidade=stats["velocidade"],
                inventario={"Poção": 3},
                ouro=100,      # antigo
                moedas=100,    # <<< adicione aqui
            )
        self.jogador = estado.jogador
        # Garante que moedas sempre exista
        if not hasattr(self.jogador, "moedas"):
            self.jogador.moedas = getattr(self.jogador, "ouro", 0)

        # --- Cenário ---
        for x in range(0, 5000, 400):
            tree = arcade.SpriteSolidColor(80, 180, arcade.color.DARK_GREEN)
            tree.center_x = x
            tree.center_y = 400
            self.scenery_list.append(tree)


        # --- Inimigos ---
        self.inimigos = arcade.SpriteList()
        posicoes_inimigos = [(2400, 340), (3000, 340), (3600, 340), (3800, 340), (4000, 340), (4200, 340)]
        if estado:
            for i, (x, y) in enumerate(posicoes_inimigos, start=1):
                nome_inimigo = f"inimigo_{i}"
                if nome_inimigo not in estado.inimigos_derrotados:
                    inimigo = Inimigo(x=x, y=y)
                    inimigo.id = i
                    self.inimigos.append(inimigo)
                    self.all_sprites.append(inimigo)

        # --- Lojas ---
        self.lojas = []
        posicoes_lojas = [(800, 340), (2800, 340)]

        for i, (x, y) in enumerate(posicoes_lojas):
            loja = Loja(x=x, y=y, id=i)
            self.lojas.append(loja)
            self.all_sprites.append(loja)

        self.loja_aberta = None  # controle da loja atual

        # Movimento
        self.velocity_x = 0
        self.moving_left = False
        self.moving_right = False
        self.facing_right = True
        self.current_texture = 0
        self.animation_timer = 0

    # ---------------------------------------------------------------------
    def on_draw(self):
        self.clear()

        # desenha o mundo com câmera
        self.camera.use()
        self.background_list.draw()
        self.scenery_list.draw()
        self.all_sprites.draw()

        # --- Janela da loja (fixa na tela) ---
        if self.loja_aberta:
            self.loja_aberta.aberta = True
            self.loja_aberta.draw_janela(self.jogador, camera=self.camera)


    # ---------------------------------------------------------------------


    def on_update(self, delta_time):
        # Movimento horizontal
        target_speed = 0
        if self.moving_left:
            target_speed = -MAX_SPEED
            self.facing_right = False
        elif self.moving_right:
            target_speed = MAX_SPEED
            self.facing_right = True

        self.velocity_x = arcade.math.lerp(self.velocity_x, target_speed, ACCELERATION)
        if not self.moving_left and not self.moving_right:
            self.velocity_x = (
                arcade.math.lerp(self.velocity_x, 0, FRICTION)
                if abs(self.velocity_x) > 0.1
                else 0
            )

        self.player_sprite.center_x += self.velocity_x
        self.player_sprite.scale_x = (
            abs(self.player_sprite.scale_x)
            if self.facing_right
            else -abs(self.player_sprite.scale_x)
        )

        # Animação
        if abs(self.velocity_x) > 0.2:
            self.animation_timer += delta_time
            if self.animation_timer > ANIMATION_SPEED:
                self.animation_timer = 0
                self.current_texture = (self.current_texture + 1) % len(self.walk_textures)
                self.player_sprite.texture = self.walk_textures[self.current_texture]
        else:
            if self.player_sprite.texture not in self.idle_textures:
                self.animation_timer = 0
                self.current_texture = 0
                self.player_sprite.texture = self.idle_textures[0]
            self.animation_timer += delta_time
            if self.animation_timer > ANIMATION_SPEED * 2:
                self.animation_timer = 0
                self.current_texture = (self.current_texture + 1) % len(self.idle_textures)
                self.player_sprite.texture = self.idle_textures[self.current_texture]

        # Câmera segue jogador
        target_position = (self.player_sprite.center_x, self.player_sprite.center_y)
        self.camera.position = arcade.math.lerp_2d(self.camera.position, target_position, 0.1)

        # --- Colisões com inimigos ---
        for inimigo in self.inimigos:
            if arcade.check_for_collision(self.player_sprite, inimigo):
                self.window.game_state.cena_mundo = self
                self.window.game_state.player_pos = (
                    self.player_sprite.center_x,
                    self.player_sprite.center_y,
                )
                self.window.game_state.player_facing = self.facing_right
                self.window.game_state.inimigo_em_batalha = inimigo
                batalha = ViewBatalha(jogador=self.jogador, inimigo=inimigo)
                self.window.show_view(batalha)
                break

        # --- Colisão com loja ---
        if not self.loja_aberta:
            for loja in self.lojas:
                if arcade.check_for_collision(self.player_sprite, loja):
                    self.loja_aberta = loja
                    break
        else:
            # Se o jogador se afastar, fecha a loja
            if not arcade.check_for_collision(self.player_sprite, self.loja_aberta):
                self.loja_aberta = None

    # ---------------------------------------------------------------------
    def on_key_press(self, key, modifiers):
        # Movimento
        if key in (arcade.key.A, arcade.key.LEFT):
            self.moving_left = True
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.moving_right = True

        # Controle da loja (só quando aberta)
        if self.loja_aberta:
            self.loja_aberta.on_key_press(key, modifiers, self.jogador)

    # ---------------------------------------------------------------------
    def on_key_release(self, key, modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.moving_left = False
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.moving_right = False
