import arcade

# Configurações da tela
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Jogo simples - Andar suave com aceleração + cenário + câmera"

# Velocidade máxima e aceleração
MAX_SPEED = 8
ACCELERATION = 0.2
FRICTION = 0.1


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.SKY_BLUE)

        # --- Câmera --- 👈 NOVO
        self.camera = arcade.Camera2D()

        # --- Listas de sprites ---
        self.all_sprites = arcade.SpriteList()
        self.scenery_list = arcade.SpriteList()
        self.ground_list = arcade.SpriteList()

        # --- Jogador ---
        self.walk_textures = [
            arcade.load_texture(r"..\jogo_arcade\imagens\player1\walk1.png"),
            arcade.load_texture(r"..\jogo_arcade\imagens\player1\walk2.png")
        ]

        self.player_sprite = arcade.Sprite()
        self.player_sprite.texture = self.walk_textures[0]
        self.player_sprite.scale = 6.0
        self.player_sprite.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2.6)
        self.all_sprites.append(self.player_sprite)

        # --- 🌳 CENÁRIO ---
        # Árvores
        for x in range(0, 5000, 400):  # 👈 aumentei o cenário para testar a câmera
            tree = arcade.SpriteSolidColor(80, 180, arcade.color.DARK_GREEN)
            tree.center_x = x
            tree.center_y = 400
            self.scenery_list.append(tree)

        # --- Tiles do chão ---
        ground_texture = arcade.load_texture(r"..\jogo_arcade\imagens\tiles\grass.jpg")
        tile_size = 64
        for x in range(0, 5000, tile_size):
            ground = arcade.Sprite()
            ground.texture = ground_texture
            ground.scale = 0.8
            ground.center_x = x + tile_size / 2
            ground.center_y = 64
            self.ground_list.append(ground)

        # --- Movimento ---
        self.velocity_x = 0
        self.moving_left = False
        self.moving_right = False
        self.facing_right = True

        # --- Animação ---
        self.current_texture = 0
        self.animation_timer = 0

    def on_draw(self):
        self.clear()

        # Ativa a câmera 👈 NOVO
        self.camera.use()

        # Desenha tudo dentro da câmera
        self.scenery_list.draw()
        self.ground_list.draw()
        self.all_sprites.draw()

    def on_update(self, delta_time: float):
        # --- Controle de aceleração e desaceleração ---
        target_speed = 0
        if self.moving_left:
            target_speed = -MAX_SPEED
            self.facing_right = False
        elif self.moving_right:
            target_speed = MAX_SPEED
            self.facing_right = True

        # Suaviza velocidade (lerp)
        self.velocity_x = arcade.math.lerp(self.velocity_x, target_speed, ACCELERATION)

        # Aplica atrito
        if not self.moving_left and not self.moving_right:
            if abs(self.velocity_x) > 0.1:
                self.velocity_x = arcade.math.lerp(self.velocity_x, 0, FRICTION)
            else:
                self.velocity_x = 0

        # Atualiza posição
        self.player_sprite.center_x += self.velocity_x

        # --- Direção e animação ---
        self.player_sprite.scale_x = abs(self.player_sprite.scale_x) if self.facing_right else -abs(self.player_sprite.scale_x)
        if abs(self.velocity_x) > 0.2:
            self.animation_timer += delta_time
            if self.animation_timer > 0.15:
                self.animation_timer = 0
                self.current_texture = (self.current_texture + 1) % 2
                self.player_sprite.texture = self.walk_textures[self.current_texture]
        else:
            self.player_sprite.texture = self.walk_textures[0]

        # --- Atualiza câmera --- 👈 NOVO
        self.center_camera_to_player(delta_time)

    def center_camera_to_player(self, delta_time):
        """Centraliza suavemente a câmera no jogador"""
        target_position = (
            self.player_sprite.center_x,
            self.player_sprite.center_y
        )
        # Smooth follow (lerp da posição da câmera)
        self.camera.position = arcade.math.lerp_2d(self.camera.position, target_position, 0.1)

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


def main():
    game = MyGame()
    arcade.run()


if __name__ == "__main__":
    main()
