import arcade
from random import randint, choice
import json
import os
import warnings
from arcade.exceptions import PerformanceWarning


BASE_DIR = os.path.dirname(__file__)
SAVE_FILE = os.path.join(BASE_DIR, "assets", "savefile.json")

DEFAULT_SAVE_DATA = {
    "coins": 0,
    "owned_skins": ["red"],      # купленные скины машин
    "selected_skin": "red",      # выбранный скин машины
    "owned_trails": ["default"], # купленные трейлы
    "selected_trail": "default", # выбранный трейл
}

# Настройки уровней сложности
DIFFICULTY_SETTINGS = {
    "easy": {
        "label": "Лёгкий",
        "player_speed": 6,
        "objects_speed": 2,
        "spawn_walls": 110,
        "spawn_coins": 40,
        "spawn_effects": 240,
    },
    "medium": {
        "label": "Средний",
        "player_speed": 5,
        "objects_speed": 3,
        "spawn_walls": 90,
        "spawn_coins": 30,
        "spawn_effects": 200,
    },
    "hard": {
        "label": "Сложный",
        "player_speed": 5,
        "objects_speed": 4,
        "spawn_walls": 70,
        "spawn_coins": 25,
        "spawn_effects": 160,
    },
}

# Скины машин (можно привязать к разным спрайтам при желании)
SKINS = {
    "red": {
        "name": "Красный стандарт",
        "price": 0,
        "texture": "assets/images/red_car.png",
    },
    "blue": {
        "name": "Синий болид",
        "price": 200,
        "texture": "assets/images/red_car.png",  # пока та же текстура
    },
    "green": {
        "name": "Зелёный ракетный",
        "price": 400,
        "texture": "assets/images/red_car.png",  # пока та же текстура
    },
}

SKIN_IDS = list(SKINS.keys())

# Текстуры эффектов (баффов/дебаффов)
EFFECT_TEXTURES = {
    "speed_down":   "assets/images/slow_down.png",
    "more_coins":   "assets/images/double_coins.png",
    "add_live":     "assets/images/extra_life.png",
    "shield":       "assets/images/shield.png",
    "speed_up":     "assets/images/speed_up.png",
    "less_coins":   "assets/images/less_coins.png",
}

# Трейлы (визуальные эффекты за машиной)
TRAILS = {
    "default": {
        "name": "Без эффекта",
        "price": 0,
        "color": (255, 255, 255, 0),
        "enabled": False,
    },
    "gold": {
        "name": "Золотой след",
        "price": 150,
        "color": (255, 215, 0, 180),
        "enabled": True,
    },
    "blue_neon": {
        "name": "Синий неон",
        "price": 250,
        "color": (0, 191, 255, 180),
        "enabled": True,
    },
}

TRAIL_IDS = list(TRAILS.keys())


def asset_path(*parts: str) -> str:
    """Путь к ассетам относительно файла."""
    return os.path.join(BASE_DIR, "assets", *parts)


# Отключаем навязчивое предупреждение Arcade о draw_text в консоли
warnings.filterwarnings("ignore", category=PerformanceWarning)


def load_game():
    """Загрузка прогресса игры с защитой от пустого/битого файла."""
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                raw = f.read().strip()
                if not raw:
                    return DEFAULT_SAVE_DATA.copy()
                f.seek(0)
                data = json.load(f)
            merged = DEFAULT_SAVE_DATA.copy()
            merged.update(data or {})
            return merged
    except (json.JSONDecodeError, OSError):
        pass
    return DEFAULT_SAVE_DATA.copy()


def save_game(data):
    """Сохранение прогресса игры."""
    os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)
    merged = load_game()
    merged.update(data or {})
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=4, ensure_ascii=False)

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
        self.selected_difficulty = "medium"

        # Тексты пересчитываются каждый кадр в on_draw()
        self.main_text = arcade.Text(
            'HyperCar', 0, 0, arcade.color.BLACK,
            font_size=40, anchor_x='center'
        )
        self.space_text = arcade.Text(
            'SPACE - старт (Средний)', 0, 0,
            arcade.color.BLACK, font_size=20, anchor_x='center'
        )
        self.difficulty_text = arcade.Text(
            '1 - лёгкий | 2 - средний | 3 - сложный', 0, 0,
            arcade.color.BLACK, font_size=16, anchor_x='center'
        )
        self.shop_text = arcade.Text(
            'S - магазин', 0, 0,
            arcade.color.BLACK, font_size=20, anchor_x='center'
        )

        self.coins_text = arcade.Text(
            f"Монеты: {load_game()['coins']}", 0, 0,
            arcade.color.BLACK, font_size=20, anchor_x='center'
        )

    def on_draw(self):
        self.clear()
        # Обновляем текст с количеством монет и текущей сложностью
        current_data = load_game()
        current_coins = current_data.get("coins", 0)
        label = DIFFICULTY_SETTINGS.get(self.selected_difficulty, {}).get("label", self.selected_difficulty)
        self.coins_text.text = f"Монеты: {current_coins}"
        self.space_text.text = f"SPACE - старт ({label})"

        self.main_text.x = SCREEN_WIDTH // 2
        self.main_text.y = SCREEN_HEIGHT // 2 + 50
        self.space_text.x = SCREEN_WIDTH // 2
        self.space_text.y = SCREEN_HEIGHT // 2 - 50
        self.coins_text.x = SCREEN_WIDTH // 2
        self.coins_text.y = SCREEN_HEIGHT // 2 - 100
        self.difficulty_text.x = SCREEN_WIDTH // 2
        self.difficulty_text.y = SCREEN_HEIGHT // 2 - 140
        self.shop_text.x = SCREEN_WIDTH // 2
        self.shop_text.y = SCREEN_HEIGHT // 2 - 180

        self.coins_text.draw()
        self.main_text.draw()
        self.space_text.draw()
        self.difficulty_text.draw()
        self.shop_text.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            game_view = GameView(self.selected_difficulty)
            self.window.show_view(game_view)
        elif key == arcade.key.KEY_1:
            self.selected_difficulty = "easy"
        elif key == arcade.key.KEY_2:
            self.selected_difficulty = "medium"
        elif key == arcade.key.KEY_3:
            self.selected_difficulty = "hard"
        elif key == arcade.key.S:
            shop_view = ShopView()
            self.window.show_view(shop_view)


class GameView(arcade.View):
    def __init__(self, difficulty: str = "medium"):
        super().__init__()

        self.difficulty = difficulty
        self.config = DIFFICULTY_SETTINGS.get(self.difficulty, DIFFICULTY_SETTINGS["medium"])

        # Два фоновых спрайта для бесконечной прокрутки дороги
        self.background_list = arcade.SpriteList()
        for i in range(2):
            bg = arcade.Sprite(asset_path("images", "road.png"))
            bg.center_x = SCREEN_WIDTH // 2
            bg.center_y = SCREEN_HEIGHT // 2 + i * SCREEN_HEIGHT
            bg.width = SCREEN_WIDTH
            bg.height = SCREEN_HEIGHT
            self.background_list.append(bg)
        self.player_list = arcade.SpriteList()
        self.walls_list = arcade.SpriteList()
        self.lives_list = arcade.SpriteList()
        self.coins_list = arcade.SpriteList()
        self.collected_coins_list = arcade.SpriteList()
        self.effects_list = arcade.SpriteList()

        # Игрок
        self.save_data = load_game()
        skin_id = self.save_data.get("selected_skin", "red")
        skin_cfg = SKINS.get(skin_id, SKINS["red"])
        player_texture = asset_path("images", os.path.basename(skin_cfg["texture"]))

        self.player = arcade.Sprite(player_texture)
        self.player.center_x = 100
        self.player.center_y = 100
        self.player.scale = 0.08
        self.player_list.append(self.player)

        # Трейл
        trail_id = self.save_data.get("selected_trail", "default")
        self.trail_config = TRAILS.get(trail_id, TRAILS["default"])
        self.trail_points = []

        # Жизни
        self.lives_count = 3
        self.create_lives()

        # Эффекты
        self.effects_count = 0
        self.types_effects = ['buff', 'debuff']
        self.types_buffs = ['speed_down', 'more_coins', 'add_live', 'shield']
        self.types_debuffs = ['speed_up', 'less_coins']

        # Скорости
        self.base_player_speed = self.config["player_speed"]
        self.base_objects_speed = self.config["objects_speed"]
        self.player_speed = self.base_player_speed
        self.objects_speed = self.base_objects_speed

        # Модификаторы от баффов/дебаффов и сложности
        self.reward_multiplier = 1.0
        self.reward_effect_time = 0.0
        self.speed_effect_time = 0.0
        self.shield_time = 0.0
        self.game_time = 0.0
        self.difficulty_multiplier = 1.0
        self.speed_multiplier = 1.0

        # Препятствия
        self.walls_count = 0
        self.spawn_rate_walls = self.config["spawn_walls"]
        self.lane_centers = [
            SCREEN_WIDTH // 2 - 200,
            SCREEN_WIDTH // 2,
            SCREEN_WIDTH // 2 + 200,
        ]

        # Монеты
        self.coins_count = 0
        self.collected_coins_count = 0
        self.spawn_rate_coins = self.config["spawn_coins"]

        # Эффекты (спавн)
        self.spawn_rate_effects = self.config["spawn_effects"]

        # Текстовые объекты HUD
        self.coins_text = arcade.Text(
            f"Монеты: {self.collected_coins_count}",
            325, SCREEN_HEIGHT - 35,
            arcade.color.YELLOW,
            25,
        )
        label = DIFFICULTY_SETTINGS.get(self.difficulty, {}).get("label", self.difficulty)
        self.difficulty_text = arcade.Text(
            f"Сложность: {label}",
            10, SCREEN_HEIGHT - 35,
            arcade.color.WHITE,
            16,
        )
        self.effects_text = arcade.Text(
            "",
            10, SCREEN_HEIGHT - 60,
            arcade.color.LIGHT_GREEN,
            14,
        )

    def create_lives(self):
        for i in range(self.lives_count):
            heart = arcade.Sprite(asset_path("images", "heart.png"))
            heart.center_x = 30 + i * 65
            heart.center_y = SCREEN_HEIGHT - 30
            heart.scale = 0.03
            self.lives_list.append(heart)

    def create_obstacle_sprite(self) -> arcade.Sprite:
        """Создаёт спрайт препятствия с разными видами и текстурами."""
        variant = randint(0, 4)
        if variant == 0:
            # Обычная встречная машина
            wall = arcade.Sprite(asset_path("images", "bg_car1.png"))
            wall.scale = 0.08
        elif variant == 1:
            # Большая тяжёлая машина
            wall = arcade.Sprite(asset_path("images", "bg_car1.png"))
            wall.scale = 0.1
            wall.color = (255, 220, 220)
        elif variant == 2:
            # Узкая быстрая машина
            wall = arcade.Sprite(asset_path("images", "bg_car1.png"))
            wall.scale = 0.07
            wall.color = (200, 255, 200)
        elif variant == 3:
            # Машина того же типа, но немного наклонённая
            wall = arcade.Sprite(asset_path("images", "bg_car1.png"))
            wall.scale = 0.085
            wall.angle = 10
            wall.color = (220, 220, 255)
        else:
            # "Спорткар" с текстурой игрока
            wall = arcade.Sprite(asset_path("images", "red_car.png"))
            wall.scale = 0.08
            wall.color = (255, 200, 200)
        return wall

    def get_free_lanes_for_pickups(self) -> list[int]:
        """Возвращает полосы, где сейчас нет препятствий на видимой дороге.

        Это помогает, чтобы монеты/эффекты не появлялись "внутри" машин.
        """
        free_lanes: list[int] = []
        for lane_x in self.lane_centers:
            blocked = False
            for wall in self.walls_list:
                # Проверяем только стены примерно на экране (и немного выше/ниже)
                if abs(wall.center_x - lane_x) < 80 and -100 <= wall.center_y <= SCREEN_HEIGHT + 150:
                    blocked = True
                    break
            if not blocked:
                free_lanes.append(lane_x)
        return free_lanes

    def on_draw(self):
        self.clear()
        self.background_list.draw()
        # Рисуем трейл
        if self.trail_config.get("enabled", False):
            r, g, b, a = self.trail_config["color"]
            for x, y, life in self.trail_points:
                alpha = int(a * life)
                color = (r, g, b, alpha)
                arcade.draw_circle_filled(x, y, 12 * life, color)

        self.player_list.draw()

        # Визуальный щит вокруг игрока
        if self.shield_time > 0:
            shield_alpha = 80 if self.shield_time > 1.0 else int(80 * self.shield_time)
            shield_color_fill = (135, 206, 250, shield_alpha)
            shield_color_border = (173, 216, 230, 180)
            radius = 55
            arcade.draw_circle_filled(
                self.player.center_x,
                self.player.center_y,
                radius,
                shield_color_fill,
            )
            arcade.draw_circle_outline(
                self.player.center_x,
                self.player.center_y,
                radius,
                shield_color_border,
                border_width=3,
            )

        self.walls_list.draw()
        self.coins_list.draw()
        self.effects_list.draw()
        self.lives_list.draw()

        # Обновляем и рисуем HUD
        self.coins_text.text = f"Монеты: {self.collected_coins_count}"
        label = DIFFICULTY_SETTINGS.get(self.difficulty, {}).get("label", self.difficulty)
        self.difficulty_text.text = f"Сложность: {label}"

        active_effects = []
        if self.speed_effect_time > 0:
            mult = "0.5x" if self.objects_speed < self.base_objects_speed else "1.5x"
            active_effects.append(f"Скорость: {mult}")
        if self.reward_effect_time > 0:
            active_effects.append(f"Монеты x{self.reward_multiplier:g}")
        if self.shield_time > 0:
            active_effects.append("Щит")

        self.effects_text.text = " | ".join(active_effects) if active_effects else ""

        self.coins_text.draw()
        self.difficulty_text.draw()
        if self.effects_text.text:
            self.effects_text.draw()

    def on_update(self, delta_time):
        self.player.center_x = max(70, min(SCREEN_WIDTH - 70, int(self.player.center_x)))

        self.player_list.update()

        # Обновление общего времени и сложности
        self.game_time += delta_time
        # Множитель сложности растёт со временем, но ограничен
        self.difficulty_multiplier = 1.0 + min(self.game_time / 60.0, 1.5)

        # Прокрутка фона
        for bg in self.background_list:
            bg.center_y -= self.objects_speed
            if bg.center_y <= -SCREEN_HEIGHT // 2:
                bg.center_y += SCREEN_HEIGHT * 2

        # Обновление таймеров эффектов
        if self.speed_effect_time > 0:
            self.speed_effect_time -= delta_time
            if self.speed_effect_time <= 0:
                self.speed_multiplier = 1.0

        if self.reward_effect_time > 0:
            self.reward_effect_time -= delta_time
            if self.reward_effect_time <= 0:
                self.reward_multiplier = 1.0

        if self.shield_time > 0:
            self.shield_time -= delta_time

        # Пересчёт скорости объектов с учётом сложности и эффектов
        self.objects_speed = self.base_objects_speed * self.difficulty_multiplier * self.speed_multiplier

        # Создаем препятствия
        self.walls_count += 1
        current_spawn_walls = max(int(self.spawn_rate_walls / self.difficulty_multiplier), 30)
        if self.walls_count % current_spawn_walls == 0:
            wall = self.create_obstacle_sprite()
            wall.center_x = choice(self.lane_centers)
            wall.center_y = SCREEN_HEIGHT + 100
            self.walls_list.append(wall)

        # Двигаем препятствия
        for obs in self.walls_list:
            obs.center_y -= self.objects_speed
            if obs.top < 0:
                obs.remove_from_sprite_lists()

        # Создаем монеты
        self.coins_count += 1
        if self.coins_count % self.spawn_rate_coins == 0:
            # Несколько типов монет с разной ценностью
            roll = randint(1, 10)
            if roll <= 6:
                value = 10
                scale = 0.06
            elif roll <= 9:
                value = 25
                scale = 0.08
            else:
                value = 50
                scale = 0.1

            # Пытаемся выбрать полосу, где нет препятствий на видимой дороге
            free_lanes = self.get_free_lanes_for_pickups()
            if free_lanes:
                coin = arcade.Sprite(asset_path("images", "coin.gif"))
                coin.update_animation()
                coin.scale = scale
                coin.center_x = choice(free_lanes)
                coin.center_y = SCREEN_HEIGHT + 100
                coin.value = value
                self.coins_list.append(coin)

        # Двигаем монеты
        for coin in list(self.coins_list):
            coin.center_y -= self.objects_speed
            if coin.top < 0:
                coin.remove_from_sprite_lists()
                continue
            # Если монета "въехала" в препятствие, удаляем её
            if arcade.check_for_collision_with_list(coin, self.walls_list):
                coin.remove_from_sprite_lists()

        # Создаем эффекты (баффы/дебаффы)
        self.effects_count += 1
        if self.effects_count % self.spawn_rate_effects == 0:
            kind = choice(self.types_effects)
            if kind == 'buff':
                effect_type = choice(self.types_buffs)
            else:
                effect_type = choice(self.types_debuffs)

            # Берём текстуру из словаря EFFECT_TEXTURES
            tex_rel = EFFECT_TEXTURES.get(effect_type, "assets/images/coin.gif")
            texture = os.path.join(BASE_DIR, tex_rel)

            # Пытаемся заспавнить эффект не поверх препятствия
            free_lanes = self.get_free_lanes_for_pickups()
            if free_lanes:
                effect = arcade.Sprite(texture)
                effect.scale = 0.12
                effect.center_x = choice(free_lanes)
                effect.center_y = SCREEN_HEIGHT + 100
                effect.kind = kind
                effect.effect_type = effect_type
                self.effects_list.append(effect)

        # Двигаем эффекты
        for eff in self.effects_list:
            eff.center_y -= self.objects_speed
            if eff.top < 0:
                eff.remove_from_sprite_lists()

        # Проверка столкновений с препятствиями
        walls_hit_list = arcade.check_for_collision_with_list(self.player, self.walls_list)
        for wall in walls_hit_list:
            wall.remove_from_sprite_lists()
            if self.shield_time > 0:
                continue
            self.lives_count -= 1
            if self.lives_count >= 0:
                if self.lives_list:
                    self.lives_list.pop()  # удаляем одно сердечко
            if self.lives_count <= 0:
                game_over_view = GameOverView(self.difficulty)
                self.window.show_view(game_over_view)

        # Проверка столкновений с монетами
        coins_hit_list = arcade.check_for_collision_with_list(self.player, self.coins_list)
        for coin in coins_hit_list:
            coin.remove_from_sprite_lists()
            value = getattr(coin, "value", 10)
            reward = int(value * self.reward_multiplier)
            self.collected_coins_count += reward
            self.save_data["coins"] += reward
            save_game(self.save_data)

        # Проверка столкновений с эффектами
        effects_hit_list = arcade.check_for_collision_with_list(self.player, self.effects_list)
        for eff in effects_hit_list:
            eff.remove_from_sprite_lists()
            self.apply_effect(getattr(eff, "effect_type", None))

        # Обновление трейла
        if self.trail_config.get("enabled", False):
            self.trail_points.append((self.player.center_x, self.player.center_y, 1.0))
            new_points = []
            decay = 0.8 * delta_time
            for x, y, life in self.trail_points:
                life -= decay
                if life > 0:
                    new_points.append((x, y, life))
            self.trail_points = new_points

    def apply_effect(self, effect_type: str | None):
        """Применение баффов и дебаффов."""
        if effect_type is None:
            return

        if effect_type == "speed_down":
            self.speed_multiplier = 0.5
            self.speed_effect_time = 10.0
        elif effect_type == "speed_up":
            self.speed_multiplier = 1.5
            self.speed_effect_time = 10.0
        elif effect_type == "more_coins":
            self.reward_multiplier = 2.0
            self.reward_effect_time = 30.0
        elif effect_type == "less_coins":
            self.reward_multiplier = 0.5
            self.reward_effect_time = 30.0
        elif effect_type == "add_live":
            if self.lives_count < 5:
                self.lives_count += 1
                heart = arcade.Sprite(asset_path("images", "heart.png"))
                heart.center_x = 30 + (self.lives_count - 1) * 65
                heart.center_y = SCREEN_HEIGHT - 30
                heart.scale = 0.03
                self.lives_list.append(heart)
        elif effect_type == "shield":
            self.shield_time = 10.0


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
    def __init__(self, difficulty: str = "medium"):
        super().__init__()
        self.difficulty = difficulty
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
            game_view = GameView(self.difficulty)
            self.window.show_view(game_view)
        elif key == arcade.key.ESCAPE:
            self.window.show_view(MenuView())


class ShopView(arcade.View):
    """Магазин скинов и трейлов."""

    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.DARK_SLATE_GRAY

        self.save_data = load_game()
        self.category = "skins"  # 'skins' или 'trails'
        self.selected_index = 0

        self.title_text = arcade.Text(
            "Магазин", 0, 0, arcade.color.WHITE,
            font_size=40, anchor_x="center"
        )

    @property
    def current_ids(self):
        return SKIN_IDS if self.category == "skins" else TRAIL_IDS

    def on_draw(self):
        self.clear()

        # Заголовок
        self.title_text.x = SCREEN_WIDTH // 2
        self.title_text.y = SCREEN_HEIGHT - 80
        self.title_text.draw()

        # Монеты
        coins = self.save_data.get("coins", 0)
        arcade.draw_text(
            f"Монеты: {coins}",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120,
            arcade.color.GOLD, 20, anchor_x="center"
        )

        # Категории
        skins_color = arcade.color.YELLOW if self.category == "skins" else arcade.color.WHITE
        trails_color = arcade.color.YELLOW if self.category == "trails" else arcade.color.WHITE
        arcade.draw_text(
            "Скины (←) ", SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT - 160,
            skins_color, 18, anchor_x="center"
        )
        arcade.draw_text(
            "(→) Трейлы", SCREEN_WIDTH // 2 + 80, SCREEN_HEIGHT - 160,
            trails_color, 18, anchor_x="center"
        )

        # Список предметов
        ids = self.current_ids
        start_y = SCREEN_HEIGHT // 2 + 40
        line_height = 32

        for idx, item_id in enumerate(ids):
            if self.category == "skins":
                item = SKINS[item_id]
                owned_list = self.save_data.get("owned_skins", [])
                selected_item = self.save_data.get("selected_skin")
            else:
                item = TRAILS[item_id]
                owned_list = self.save_data.get("owned_trails", [])
                selected_item = self.save_data.get("selected_trail")

            y = start_y - idx * line_height
            if y < 80:
                break

            is_selected_row = idx == self.selected_index
            base_color = arcade.color.WHITE
            color = arcade.color.YELLOW if is_selected_row else base_color

            owned = item_id in owned_list
            price = item.get("price", 0)

            if item_id == selected_item and owned:
                status = "Выбрано"
            elif owned:
                status = "Куплено"
            elif price > 0:
                status = f"Цена: {price}"
            else:
                status = "Бесплатно"

            text = f"{item['name']} — {status}"
            arcade.draw_text(
                text,
                SCREEN_WIDTH // 2,
                y,
                color,
                18,
                anchor_x="center",
            )

        # Подсказки
        help_text = "↑/↓ - выбор, ←/→ - категория, ENTER/SPACE - купить/выбрать, ESC - назад"
        arcade.draw_text(
            help_text,
            SCREEN_WIDTH // 2,
            40,
            arcade.color.LIGHT_GRAY,
            14,
            anchor_x="center",
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(MenuView())
        elif key in (arcade.key.UP, arcade.key.W):
            self.move_selection(-1)
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.move_selection(1)
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.toggle_category("skins")
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.toggle_category("trails")
        elif key in (arcade.key.ENTER, arcade.key.SPACE):
            self.buy_or_select()

    def move_selection(self, direction: int):
        ids = self.current_ids
        if not ids:
            return
        self.selected_index = (self.selected_index + direction) % len(ids)

    def toggle_category(self, target: str):
        if target not in ("skins", "trails"):
            return
        if self.category != target:
            self.category = target
            self.selected_index = 0

    def buy_or_select(self):
        ids = self.current_ids
        if not ids:
            return
        item_id = ids[self.selected_index]

        if self.category == "skins":
            item = SKINS[item_id]
            owned_list = self.save_data.setdefault("owned_skins", [])
            selected_key = "selected_skin"
        else:
            item = TRAILS[item_id]
            owned_list = self.save_data.setdefault("owned_trails", [])
            selected_key = "selected_trail"

        price = item.get("price", 0)
        coins = self.save_data.get("coins", 0)

        if item_id in owned_list:
            # просто выбираем
            self.save_data[selected_key] = item_id
        else:
            if price <= 0 or coins >= price:
                if price > 0:
                    self.save_data["coins"] = coins - price
                owned_list.append(item_id)
                self.save_data[selected_key] = item_id

        save_game(self.save_data)


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
