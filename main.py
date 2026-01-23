import arcade
import random

# константы

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = 'Hyperclimb'

PLAYER_SCALE = 0.8
PLAYER_SPEED_X = 5
PLAYER_SPEED_Y = 2

GRAVITY = 0.4

COIN_SCALE = 0.5

# класс игрока

class Player(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__('player.png', PLAYER_SCALE)
        self.center_x = x
        self.center_y = y

        self.change_x = 0
        self.change_y = PLAYER_SPEED_Y

        self.coins = 0
        self.buffs = []
        self.debuffs = []

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.left < 0:
            self.left = 0
        if self.right > SCREEN_WIDTH:
            self.right = SCREEN_WIDTH

# окно игры

class HyperclimbGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.DARK_SLATE_BLUE)

        self.player = None
        self.player_list = None
        self.wall_list = None
        self.coin_list = None

        self.physics_engine = None

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        self.player = Player(SCREEN_WIDTH // 2, 100)
        self.player_list.append(self.player)

        for i in range(10):
            coin = arcade.Sprite('coin.png', COIN_SCALE)
            coin.center_x = random.randint(50, SCREEN_WIDTH - 50)
            coin.center_y = random.randint(200, 2000)
            self.coin_list.append(coin)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, self.wall_list, gravity_constant=GRAVITY
        )

    def on_draw(self):
        arcade.start_render()
        self.wall_list.draw()
        self.coin_list.draw()
        self.player_list.draw()

        arcade.draw_text(
            f'Coins: {self.player.coins}',
            10, SCREEN_HEIGHT - 30,
            arcade.color.WHITE, 16
        )

    def on_update(self, delta_time):
        self.player_list.update()
        self.physics_engine.update()

        coins_hit = arcade.check_for_collision_with_list(self.player, self.coin_list)
        for coin in coins_hit:
            coin.remove_from_sprite_lists()
            self.player.coins += 1

    def on_key_press(self, key, modifiers):
        if key == arcade.key.A:
            self.player.change_x = -PLAYER_SPEED_X
        elif key == arcade.key.D:
            self.player.change_x = PLAYER_SPEED_X

    def on_key_release(self, key, modifiers):
        if key == arcade.key.A or key == arcade.key.D:
            self.player.change_x = 0


def main():
    window = HyperclimbGame()
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()
