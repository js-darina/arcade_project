import arcade
from random import randint, choice
import json
import os


SAVE_FILE = "savefile.json"

def save_game(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_game():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        return data
    else:
        return {"coins": 0}

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

SPAWN_RATE_WALLS = 90  # препятствие будет повляться каждые 90 кадорв (1.5 сек)
SPAWN_RATE_COINS = 30
SPAWN_RATE_EFFECTS = 180


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

        self.coins_text = arcade.Text(
            f'Монеты: {load_game()['coins']}', 0, 0,
            arcade.color.BLACK, font_size=20, anchor_x='center'
        )

    def on_draw(self):
        self.clear()
        self.main_text.x = SCREEN_WIDTH // 2
        self.main_text.y = SCREEN_HEIGHT // 2 + 50
        self.space_text.x = SCREEN_WIDTH // 2
        self.space_text.y = SCREEN_HEIGHT // 2 - 50
        self.coins_text.x = SCREEN_WIDTH // 2
        self.coins_text.y = SCREEN_HEIGHT // 2 - 100

        self.coins_text.draw()
        self.main_text.draw()
        self.space_text.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            game_view = GameView()
            self.window.show_view(game_view)


class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background = arcade.Sprite('assets/images/road.png')
        self.background.center_x = SCREEN_WIDTH // 2
        self.background.center_y = SCREEN_HEIGHT // 2
        self.background.width = SCREEN_WIDTH
        self.background.height = SCREEN_HEIGHT

        self.background_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.walls_list = arcade.SpriteList()
        self.lives_list = arcade.SpriteList()
        self.coins_list = arcade.SpriteList()
        self.collected_coins_list = arcade.SpriteList

        # Задний фон
        self.background_list.append(self.background)

        # Игрок
        self.player = arcade.Sprite('assets/images/red_car.png')
        self.player.center_x = 100
        self.player.center_y = 100
        self.player.scale = 0.08
        self.player_list.append(self.player)

        # Жизни
        self.lives_count = 3
        self.create_lives()

        # Эффекты
        self.effects_count = 0
        self.types_effects = ['buff', 'debuff']
        self.types_buffs = ['speed_down', 'more_coins', 'add_live']
        self.types_debuffs = ['speed_up', 'less_coins']

        # Скорости
        self.player_speed = 5
        self.objects_speed = 3

        # Препятствия
        self.walls_count = 0

        # Монеты
        self.coins_count = 0
        saved_data = load_game()
        self.collected_coins_count = 0

    def create_lives(self):
        # Создаем спрайты сердечек для отображения жизней
        for i in range(self.lives_count):
            heart = arcade.Sprite('assets/images/heart.png')
            heart.center_x = 30 + i * 65
            heart.center_y = SCREEN_HEIGHT - 30
            heart.scale = 0.03
            self.lives_list.append(heart)

    def on_draw(self):
        self.clear()
        self.background_list.draw()
        self.player_list.draw()
        self.walls_list.draw()
        self.coins_list.draw()
        self.lives_list.draw()
        arcade.draw_text(
            f'Монеты: {self.collected_coins_count}',
            325, SCREEN_HEIGHT - 35,  # x, y
            arcade.color.YELLOW,  # цвет текста
            25  # размер шрифта
        )

    def on_update(self, delta_time):
        self.player.center_x = max(70, min(SCREEN_WIDTH - 70, int(self.player.center_x)))

        self.player_list.update()

        # Создаем препятствия
        self.walls_count += 1
        if self.walls_count % SPAWN_RATE_WALLS == 0:
            wall = arcade.Sprite('assets/images/bg_car1.png')
            wall.scale = 0.08
            wall.center_x = randint(70, SCREEN_WIDTH - 70)
            wall.center_y = SCREEN_HEIGHT + 100
            self.walls_list.append(wall)

        # Двигаем препятствия
        for obs in self.walls_list:
            obs.center_y -= self.objects_speed
            if obs.top < 0:
                obs.remove_from_sprite_lists()

        # Создаем монеты
        self.coins_count += 1
        if self.coins_count % SPAWN_RATE_COINS == 0:
            coin = arcade.Sprite('assets/images/coin.gif')
            coin.update_animation()
            coin.scale = 0.07
            coin.center_x = randint(70, SCREEN_WIDTH - 70)
            coin.center_y = SCREEN_HEIGHT + 100
            self.coins_list.append(coin)

        # Двигаем монеты
        for obs in self.coins_list:
            obs.center_y -= self.objects_speed
            if obs.top < 0:
                obs.remove_from_sprite_lists()

        # Проверка столкновений с препятствиями
        walls_hit_list = arcade.check_for_collision_with_list(self.player, self.walls_list)
        for wall in walls_hit_list:
            wall.remove_from_sprite_lists()
            self.lives_count -= 1
            if self.lives_count >= 0:
                self.lives_list.pop()  # удаляем одно сердечко
            if self.lives_count <= 0:
                game_over_view = GameOverView()
                self.window.show_view(game_over_view)

        # Проверка столкновений с монетами
        coins_hit_list = arcade.check_for_collision_with_list(self.player, self.coins_list)
        for coin in coins_hit_list:
            coin.remove_from_sprite_lists()
            self.collected_coins_count += 1
            save_game(
                {'coins': load_game()['coins'] + 1}
            )


    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            pause_view = PauseView(self)
            self.window.show_view(pause_view)
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.player.change_x = -self.player_speed
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.player.change_x = self.player_speed

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.RIGHT, arcade.key.A, arcade.key.D):
            self.player.change_x = 0

class GameOverView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.BLACK
        self.text = arcade.Text("Игра окончена", 0, 0, arcade.color.RED, 40, anchor_x='center')
        self.restart_text = arcade.Text("SPACE - начать заново", 0, 0, arcade.color.WHITE, 20, anchor_x='center')
        self.menu_text = arcade.Text("ESC - в меню", 0, 0, arcade.color.WHITE, 20, anchor_x='center')

    def on_draw(self):
        self.clear()
        self.text.x = self.window.width / 2
        self.text.y = self.window.height / 2 + 50
        self.restart_text.x = self.window.width / 2
        self.restart_text.y = self.window.height / 2 - 50
        self.menu_text.x = self.window.width / 2
        self.menu_text.y = self.window.height / 2 - 100
        self.text.draw()
        self.restart_text.draw()
        self.menu_text.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            game_view = GameView()
            self.window.show_view(game_view)
        elif key == arcade.key.ESCAPE:
            game_view = MenuView()
            self.window.show_view(game_view)


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
