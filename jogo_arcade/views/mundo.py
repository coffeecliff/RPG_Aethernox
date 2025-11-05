import arcade
import os
from config import *
from sprites.inimigo import Inimigo

class ViewMundo(arcade.View):
    def __init__(self):
        super().__init__()

        # Caminho da imagem de fundo
        background_path = os.path.join("../jogo_arcade/imagens", "ceu.jpg")

        # Cria um SpriteList para o fundo
        self.background_list = arcade.SpriteList()
        self.background_sprite = arcade.Sprite(background_path)
        self.background_sprite.center_x = LARGURA_TELA // 3
        self.background_sprite.center_y = ALTURA_TELA // 3
        self.background_list.append(self.background_sprite)

        self.camera = arcade.Camera2D()

        # Outros elementos do jogo
        self.scenery_list = arcade.SpriteList()
        self.ground_list = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()

        estado = getattr(self.window, "game_state", None)
        if estado and estado.cena_mundo:
            anterior = estado.cena_mundo
            self.all_sprites = anterior.all_sprites
            self.scenery_list = anterior.scenery_list
            self.ground_list = anterior.ground_list
            self.player_sprite = anterior.player_sprite
            self.walk_textures = anterior.walk_textures
            self.velocity_x = anterior.velocity_x
            self.moving_left = anterior.moving_left
            self.moving_right = anterior.moving_right
            self.facing_right = anterior.facing_right
            self.current_texture = anterior.current_texture
            self.animation_timer = anterior.animation_timer
            self.inimigos = anterior.inimigos
            return

        # --- Criação inicial ---
        self.all_sprites = arcade.SpriteList()
        self.scenery_list = arcade.SpriteList()
        self.ground_list = arcade.SpriteList()

        # Player
        # Escolhe sprite do player conforme a carta selecionada
        # Player
        estado = getattr(self.window, "game_state", None)
        personagem = getattr(estado, "personagem_escolhido", "Guerreiro")

        if personagem == "Mago":
            from config import PLAYER2_WALK as PLAYER_WALK, PLAYER2_IDLE as PLAYER_IDLE
        elif personagem == "Arqueiro":
            from config import PLAYER3_WALK as PLAYER_WALK, PLAYER3_IDLE as PLAYER_IDLE
        else:
            from config import PLAYER1_WALK as PLAYER_WALK, PLAYER1_IDLE as PLAYER_IDLE

        # Carrega texturas
        self.walk_textures = [arcade.load_texture(p) for p in PLAYER_WALK]
        self.idle_textures = [arcade.load_texture(p) for p in PLAYER_IDLE]

        self.player_sprite = arcade.Sprite()
        self.player_sprite.texture = self.idle_textures[0]
        self.player_sprite.scale = 0.2
        self.player_sprite.center_x = LARGURA_TELA // 2
        self.player_sprite.center_y = ALTURA_TELA // 2.7
        self.all_sprites.append(self.player_sprite)


        # Cenário
        for x in range(0, 5000, 400):
            tree = arcade.SpriteSolidColor(80, 180, arcade.color.DARK_GREEN)
            tree.center_x = x
            tree.center_y = 400
            self.scenery_list.append(tree)

        ground_texture = arcade.load_texture(os.path.join("..", "jogo_arcade", "imagens", "tiles", "grass.jpg"))
        tile_size = 64
        for x in range(0, 5000, tile_size):
            ground = arcade.Sprite()
            ground.texture = ground_texture
            ground.scale = 0.8
            ground.center_x = x + tile_size / 2
            ground.center_y = 64
            self.ground_list.append(ground)

        # --- Inimigos múltiplos ---
        self.inimigos = arcade.SpriteList()
        posicoes_inimigos = [(2400, 290), (3000, 290), (3600, 290)]  # adicione quantos quiser
        estado = getattr(self.window, "game_state", None)

        for i, (x, y) in enumerate(posicoes_inimigos, start=1):
            nome_inimigo = f"inimigo_{i}"
            if not estado or nome_inimigo not in estado.inimigos_derrotados:
                inimigo = Inimigo(x=x, y=y)
                inimigo.id = i
                self.inimigos.append(inimigo)
                self.all_sprites.append(inimigo)

        # Movimento
        self.velocity_x = 0
        self.moving_left = False
        self.moving_right = False
        self.facing_right = True
        self.current_texture = 0
        self.animation_timer = 0

    def on_draw(self):
        self.clear()
        self.camera.use()

        # Desenha o fundo (como SpriteList)
        self.background_list.draw()

        # Depois os outros
        self.scenery_list.draw()
        self.ground_list.draw()
        self.all_sprites.draw()


    def on_update(self, delta_time):
        target_speed = 0
        if self.moving_left:
            target_speed = -MAX_SPEED
            self.facing_right = False
        elif self.moving_right:
            target_speed = MAX_SPEED
            self.facing_right = True

        self.velocity_x = arcade.math.lerp(self.velocity_x, target_speed, ACCELERATION)
        if not self.moving_left and not self.moving_right:
            self.velocity_x = arcade.math.lerp(self.velocity_x, 0, FRICTION) if abs(self.velocity_x) > 0.1 else 0

        self.player_sprite.center_x += self.velocity_x
        self.player_sprite.scale_x = abs(self.player_sprite.scale_x) if self.facing_right else -abs(self.player_sprite.scale_x)

        # --- Animação ---
        # Se o player está se movendo
        if abs(self.velocity_x) > 0.2:
            self.animation_timer += delta_time
            if self.animation_timer > ANIMATION_SPEED:
                self.animation_timer = 0
                self.current_texture = (self.current_texture + 1) % len(self.walk_textures)
                self.player_sprite.texture = self.walk_textures[self.current_texture]

        # Se o player parou
        else:
            # Assim que para, troca imediatamente para o idle sem delay
            if self.player_sprite.texture not in self.idle_textures:
                self.animation_timer = 0
                self.current_texture = 0
                self.player_sprite.texture = self.idle_textures[0]

            # Depois disso, roda a animação idle normalmente
            self.animation_timer += delta_time
            if self.animation_timer > ANIMATION_SPEED * 2:
                self.animation_timer = 0
                self.current_texture = (self.current_texture + 1) % len(self.idle_textures)
                self.player_sprite.texture = self.idle_textures[self.current_texture]


        # Centraliza câmera
        target_position = (self.player_sprite.center_x, self.player_sprite.center_y)
        self.camera.position = arcade.math.lerp_2d(self.camera.position, target_position, 0.1)

        # Colisão com inimigos
        for inimigo in self.inimigos:
            if arcade.check_for_collision(self.player_sprite, inimigo):
                self.window.game_state.cena_mundo = self
                self.window.game_state.player_pos = (self.player_sprite.center_x, self.player_sprite.center_y)
                self.window.game_state.player_facing = self.facing_right

                from views.batalha import ViewBatalha
                batalha = ViewBatalha(inimigo)
                self.window.show_view(batalha)
                break

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.moving_left = True
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.moving_right = True

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.moving_left = False
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.moving_right = False
