import arcade
from config import *

# ============================================================
# CLASSE LOJA — FUNCIONA COMO UM ELEMENTO NO MUNDO
# ============================================================
caminho_imagem_loja = IMAGENS_DIR / "loja.png"

class Loja(arcade.Sprite):
    def __init__(self, x, y, id=0, imagem=None, scale=1.0):
        self.id = id
        self.aberta = False
        self.text_objects = []

        # Itens da loja
        self.itens = [
            {"number": "[1]", "nome": "Poção de Vida", "efeito": "+20 HP", "preco": 30, "tipo": "consumivel"},
            {"number": "[2]", "nome": "Poção de Mana", "efeito": "+15 MP", "preco": 25, "tipo": "consumivel"},
            {"number": "[3]", "nome": "Espada de Ferro", "efeito": "+5 ATQ", "preco": 100, "tipo": "equipamento"},
            {"number": "[4]", "nome": "Armadura Leve", "efeito": "+3 DEF", "preco": 80, "tipo": "equipamento"},
        ]
        self._criar_textos_otimizados()

        # --- imagem da loja ---
        if imagem is None:
            # caminho padrão
            imagem = IMAGENS_DIR / "loja.png"

        if not os.path.exists(imagem):
            raise FileNotFoundError(f"Imagem da loja não encontrada: {imagem}")

        super().__init__(filename=str(imagem), scale=scale)
        self.center_x = x
        self.center_y = y


    # ========================================================
    # NOVO: cria objetos de texto otimizados
    # ========================================================
    def _criar_textos_otimizados(self):
        """Cria objetos arcade.Text (muito mais leves que draw_text)"""
        self.text_objects.clear()
        start_y = ALTURA_TELA - 250
        for i, item in enumerate(self.itens):
            y = start_y - i * 40
            texto = arcade.Text(
                f"{item['nome']} - {item['efeito']} ({item['preco']}G)",
                180,
                y,
                arcade.color.BLACK,
                18,
            )
            self.text_objects.append(texto)

    # ========================================================
    # NOVO: função que desenha a janela fixa
    # ========================================================
    def draw_janela(self, jogador, camera=None):
        if not self.aberta:
            return

        # === Converter posição da loja para coordenadas de tela ===
        offset_x, offset_y = (0, 0)
        if camera:
            # a câmera tem uma posição que desloca o mundo — precisamos compensar isso
            offset_x = -camera.position[0] + LARGURA_TELA / 2
            offset_y = -camera.position[1] + ALTURA_TELA / 2

        # === Configurações básicas ===
        largura_janela = 420
        altura_janela = 300
        margem = 20

        # Posição base da janela (acima da loja, convertida p/ tela)
        loja_x_tela = self.center_x + offset_x
        loja_y_tela = self.center_y + offset_y

        left = loja_x_tela - largura_janela / 2
        right = loja_x_tela + largura_janela / 2
        bottom = loja_y_tela + self.height / 2 + 20
        top = bottom + altura_janela

        # === Ajuste para não sair da tela ===
        if left < margem:
            right += (margem - left)
            left = margem
        if right > LARGURA_TELA - margem:
            left -= (right - (LARGURA_TELA - margem))
            right = LARGURA_TELA - margem
        if top > ALTURA_TELA - margem:
            diff = top - (ALTURA_TELA - margem)
            top -= diff
            bottom -= diff

        # === Fundo e moldura ===
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, arcade.color.BEIGE)
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, arcade.color.BLACK, border_width=3)

        # === Título ===
        arcade.draw_text(
            "🏪 Loja de Itens",
            (left + right) / 2,
            top - 40,
            arcade.color.BLACK,
            22,
            anchor_x="center",
            bold=True,
        )

        # === Itens ===
        start_y = top - 80
        for i, item in enumerate(self.itens):
            y = start_y - i * 35
            texto = f"{item['number']} {item['nome']} - {item['efeito']} ({item['preco']}G)"
            arcade.draw_text(texto, left + 30, y, arcade.color.BLACK, 16)

        # === Ouro do jogador ===
        arcade.draw_text(
            f"Seu ouro: {jogador.moedas} Moedas",  # antes era jogador.ouro
            left + 30,
            bottom + 25,
            arcade.color.DARK_YELLOW,
            18,
            bold=True,
        )

    # ========================================================
    # NOVO: compra de item
    # ========================================================
    def aplicar_item(self, jogador, item):
        tipo = item.get("tipo")
        nome = item["nome"]

        if tipo == "consumivel":
            if nome == "Poção de Vida":
                jogador.vida += 20
                if jogador.vida > jogador.vida_max:
                    jogador.vida = jogador.vida_max
            elif nome == "Poção de Mana":
                jogador.mana += 15
                if jogador.mana > jogador.mana_max:
                    jogador.mana = jogador.mana_max
        elif tipo == "equipamento":
            # Só adiciona ao inventário, não aplica stats ainda
            jogador.inventario[nome] = jogador.inventario.get(nome, 0) + 1

    def comprar_item(self, jogador, indice):
        """Permite comprar um item pelo índice"""
        if indice < 0 or indice >= len(self.itens):
            return  # índice inválido

        item = self.itens[indice]

        if jogador.moedas >= item["preco"]:
            jogador.moedas -= item["preco"]  # gasta as moedas do jogador

            # Armazena no inventário
            jogador.inventario[item["nome"]] = jogador.inventario.get(item["nome"], 0) + 1

            # Aplica efeito imediato somente se for consumível
            if item["tipo"] == "consumivel":
                self.aplicar_item(jogador, item)

            arcade.play_sound(arcade.sound.load_sound(":resources:sounds/coin5.wav"))

        else:
            # Som de erro se não houver moedas suficientes
            arcade.play_sound(arcade.sound.load_sound(":resources:sounds/error3.wav"))


    # ========================================================
    # NOVO: controle por teclado
    # ========================================================
    def on_key_press(self, key, modifiers, jogador):
        """Controle de navegação e compra"""
        if not self.aberta:
            return
        if key == arcade.key.ESCAPE:
            self.fechar_loja()
        elif key == arcade.key.KEY_1:
            self.comprar_item(jogador, 0)
        elif key == arcade.key.KEY_2:
            self.comprar_item(jogador, 1)
        elif key == arcade.key.KEY_3:
            self.comprar_item(jogador, 2)
        elif key == arcade.key.KEY_4:
            self.comprar_item(jogador, 3)

