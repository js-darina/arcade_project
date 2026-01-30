import arcade
from random import randint

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class MenuView(arcade.View):
    """Главное меню"""

    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.WHITE

        # Тексты пересчитываются каждый кадр в on_draw()
        self.main_text = arcade.Text(
            'HyperCar', 0, 0, arcade.color.BLACK,
            font_size=40, anchor_x='center'
        )
        self.space_text = arcade.Text(
            'Нажмите SPACE, чтобы начать!', 0, 0,
            arcade.color.BLACK, font_size=20, anchor_x='center'
        )

    def on_draw(self):
        self.clear()
        self.main_text.x = self.window.width / 2
        self.main_text.y = self.window.height / 2 + 50
        self.space_text.x = self.window.width / 2
        self.space_text.y = self.window.height / 2 - 50

        self.main_text.draw()
        self.space_text.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            game_view = GameView()
            self.window.show_view(game_view)


class GameView(arcade.View):

    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.WHITE

        self.sprite_list = arcade.SpriteList()

        # игровой персонаж
        self.player = arcade.Sprite(None)

        self.player.center_x = 100
        self.player.center_y = 100
        self.player.scale = 0.5

        # препятствие
        self.wall = arcade.Sprite(None)
        self.wall.center_x = randint(1, 800)
        self.wall.center_y = 600
        self.wall.scale = 0.6

        # добавляем спрайты в список
        self.sprite_list.append(self.player)
#       self.sprite_list.append(self.wall)

        self.player_speed = 5
        self.walls_speed = 3

    def on_draw(self):
        self.clear()
        self.sprite_list.draw()
        self.wall.change_y = -self.walls_speed

    def on_update(self, delta_time):
        self.sprite_list.update()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            pause_view = PauseView(self)
            self.window.show_view(pause_view)
        # Движение персонажа
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player.change_x = -self.player_speed
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player.change_x = self.player_speed

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.RIGHT, arcade.key.A, arcade.key.D):
            self.player.change_x = 0


class PauseView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.background_color = arcade.color.WHITE

        self.pause_text = arcade.Text(
            'ПАУЗА', 0, 0, arcade.color.BLACK,
            font_size=40, anchor_x='center'
        )
        self.space_text = arcade.Text(
            'SPACE - продолжить | ESC - в меню', 0, 0,
            arcade.color.BLACK, font_size=20, anchor_x='center'
        )

    def on_draw(self):
        self.clear()
        self.pause_text.x = self.window.width / 2
        self.pause_text.y = self.window.height / 2 + 25
        self.space_text.x = self.window.width / 2
        self.space_text.y = self.window.height / 2 - 25

        self.pause_text.draw()
        self.space_text.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.window.show_view(self.game_view)  # возврат в игру
        elif key == arcade.key.ESCAPE:
            self.window.show_view(MenuView())  # в главное меню


if __name__ == '__main__':
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, 'HyperCar')
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()
