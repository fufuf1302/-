import arcade
import math
import enum
import random
from PIL import Image

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "drunobirint"


class FaceDirection(enum.Enum):
    LEFT = 0
    RIGHT = 1


class GameMenu(arcade.View):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.DARK_BLUE_GRAY

    def on_show(self):
        arcade.set_background_color(self.background_color)

    def on_draw(self):
        self.clear()
        arcade.draw_text("ГЛАВНОЕ МЕНЮ", self.window.width / 2, self.window.height * 0.7,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("1. НАЧАТЬ ИГРУ", self.window.width / 2, self.window.height * 0.5,
                         arcade.color.GREEN, font_size=30, anchor_x="center")
        arcade.draw_text("2. НАСТРОЙКИ", self.window.width / 2, self.window.height * 0.4,
                         arcade.color.YELLOW, font_size=30, anchor_x="center")
        arcade.draw_text("3. ВЫХОД", self.window.width / 2, self.window.height * 0.3,
                         arcade.color.RED, font_size=30, anchor_x="center")
        arcade.draw_text("Нажмите соответствующую цифру",
                         self.window.width / 2, self.window.height * 0.1,
                         arcade.color.LIGHT_GRAY, font_size=16, anchor_x="center")

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.KEY_1 or symbol == arcade.key.NUM_1:
            game_view = GameView()
            self.window.show_view(game_view)
        elif symbol == arcade.key.KEY_2 or symbol == arcade.key.NUM_2:
            settings_view = SettingsView()
            self.window.show_view(settings_view)
        elif symbol == arcade.key.KEY_3 or symbol == arcade.key.NUM_3:
            arcade.close_window()


class SettingsView(arcade.View):
    def __init__(self):
        super().__init__()

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        arcade.draw_text("НАСТРОЙКИ", self.window.width / 2, self.window.height * 0.7,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Здесь можно добавить настройки игры",
                         self.window.width / 2, self.window.height * 0.5,
                         arcade.color.YELLOW, font_size=20, anchor_x="center")
        arcade.draw_text("Нажмите ESC для возврата в меню",
                         self.window.width / 2, self.window.height * 0.3,
                         arcade.color.GREEN, font_size=20, anchor_x="center")

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            menu_view = GameMenu()
            self.window.show_view(menu_view)


def create_simple_texture(color, width, height):
    image = Image.new('RGBA', (width, height), color)

    import io
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    return arcade.load_texture(img_bytes)


def arcade_color_to_tuple(color):
    if hasattr(color, 'r'):
        return (color.r, color.g, color.b, 255)
    elif isinstance(color, tuple):
        if len(color) == 3:
            return (color[0], color[1], color[2], 255)
        else:
            return color
    else:
        try:
            color_obj = getattr(arcade.color, color.upper())
            return (color_obj.r, color_obj.g, color_obj.b, 255)
        except:
            return (255, 255, 255, 255)  # Белый по умолчанию


class Igra(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.scale = 0.05
        self.speed = 300
        self.health = 100
        self.max_health = 100
        # Создаем текстуру для игрока
        try:
            self.texture = arcade.load_texture("fog1.png")
            print("Текстура игрока загружена из файла")
        except Exception as e:
            print(f"Не удалось загрузить текстуру игрока: {e}")
            color_tuple = arcade_color_to_tuple(arcade.color.BLUE)
            self.texture = create_simple_texture(color_tuple, 50, 50)
            print("Создана простая текстура для игрока")

        self.walk_textures = []
        for i in range(1, 5):
            try:
                texture = arcade.load_texture(f"fog{i}.png")
                self.walk_textures.append(texture)
            except:
                if self.texture:
                    self.walk_textures.append(self.texture)

        if not self.walk_textures and self.texture:
            self.walk_textures.append(self.texture)

        self.current_texture = 0
        self.texture_change_time = 0
        self.texture_change_delay = 0.15

        self.is_walking = False
        self.face_direction = FaceDirection.RIGHT

        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2

    def update_animation(self, delta_time: float):
        if self.is_walking and self.walk_textures:
            self.texture_change_time += delta_time
            if self.texture_change_time >= self.texture_change_delay:
                self.texture_change_time = 0
                self.current_texture += 1
                if self.current_texture >= len(self.walk_textures):
                    self.current_texture = 0
                self.texture = self.walk_textures[self.current_texture]

    def update_movement(self, delta_time, keys_pressed):
        dx, dy = 0, 0
        if arcade.key.LEFT in keys_pressed or arcade.key.A in keys_pressed:
            dx -= self.speed * delta_time
        if arcade.key.RIGHT in keys_pressed or arcade.key.D in keys_pressed:
            dx += self.speed * delta_time
        if arcade.key.UP in keys_pressed or arcade.key.W in keys_pressed:
            dy += self.speed * delta_time
        if arcade.key.DOWN in keys_pressed or arcade.key.S in keys_pressed:
            dy -= self.speed * delta_time

        if dx != 0 and dy != 0:
            factor = 0.7071
            dx *= factor
            dy *= factor

        self.center_x += dx
        self.center_y += dy

        if dx < 0:
            self.face_direction = FaceDirection.LEFT
        elif dx > 0:
            self.face_direction = FaceDirection.RIGHT

        self.center_x = max(50, min(SCREEN_WIDTH - 50, self.center_x))
        self.center_y = max(50, min(SCREEN_HEIGHT - 50, self.center_y))

        self.is_walking = dx != 0 or dy != 0


class Bullet(arcade.Sprite):
    def __init__(self, start_x, start_y, target_x, target_y, speed=800, damage=10):
        super().__init__()
        color_tuple = arcade_color_to_tuple(arcade.color.RED)
        self.texture = create_simple_texture(color_tuple, 8, 8)
        self.center_x = start_x
        self.center_y = start_y
        self.speed = speed
        self.damage = damage

        x_diff = target_x - start_x
        y_diff = target_y - start_y
        angle = math.atan2(y_diff, x_diff)

        self.change_x = math.cos(angle) * speed
        self.change_y = math.sin(angle) * speed
        self.angle = math.degrees(angle)

        self.life_time = 3.0

    def update(self, delta_time=None):
        if delta_time is not None:
            self.life_time -= delta_time
            if self.life_time <= 0:
                self.remove_from_sprite_lists()
                return

        self.center_x += self.change_x * (1 / 60 if delta_time is None else delta_time)
        self.center_y += self.change_y * (1 / 60 if delta_time is None else delta_time)

        if (self.center_x < -100 or self.center_x > SCREEN_WIDTH + 100 or
                self.center_y < -100 or self.center_y > SCREEN_HEIGHT + 100):
            self.remove_from_sprite_lists()


class Enemy(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.scale = 0.5
        self.speed = 100
        self.health = 50
        self.damage = 10
        self.attack_range = 100
        self.attack_cooldown = 1.0
        self.attack_timer = 0

        try:
            self.texture = arcade.load_texture("enemy.png")
            print("Текстура врага загружена из файла")
        except Exception as e:
            print(f"Не удалось загрузить текстуру врага: {e}")
            color_tuple = arcade_color_to_tuple(arcade.color.RED)
            self.texture = create_simple_texture(color_tuple, 40, 40)
            print("Создана простая текстура для врага")

        self.center_x = x
        self.center_y = y

    def update(self, delta_time, player):
        if player is None:
            return

        if self.attack_timer > 0:
            self.attack_timer -= delta_time

        dx = player.center_x - self.center_x
        dy = player.center_y - self.center_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0 and distance > 20:
            dx_norm = dx / distance
            dy_norm = dy / distance

            self.center_x += dx_norm * self.speed * delta_time
            self.center_y += dy_norm * self.speed * delta_time

            if distance < self.attack_range and self.attack_timer <= 0:
                self.attack_timer = self.attack_cooldown
                return True

        return False

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0


# КЛАСС СТЕНЫ
class Wall(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.texture = arcade.load_texture(":resources:images/tiles/boxCrate_double.png")
            print("Текстура стены загружена из ресурсов")
        except Exception as e:
            print(f"Не удалось загрузить текстуру стены: {e}")
            color_tuple = arcade_color_to_tuple(arcade.color.BROWN)
            self.texture = create_simple_texture(color_tuple, 64, 64)
            print("Создана простая текстура для стены")
        self.center_x = x
        self.center_y = y
        self.scale = 1.0


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.player = None
        self.keys_pressed = set()
        self.shoot_sound = None
        self.hit_sound = None
        self.game_over = False
        self.score = 0
        self.time_elapsed = 0
        self.wave = 1
        self.enemies_killed = 0

        self.setup()

    def setup(self):
        print("Создание игры...")

        self.player_list.clear()
        self.wall_list.clear()
        self.bullet_list.clear()
        self.enemy_list.clear()

        self.player = Igra()
        self.player_list.append(self.player)

        self.create_simple_map()
        self.spawn_enemies()

        try:
            self.shoot_sound = arcade.load_sound(":resources:sounds/laser1.wav")
            self.hit_sound = arcade.load_sound(":resources:sounds/hit2.wav")
            print("Звуки загружены")
        except Exception as e:
            print(f"Не удалось загрузить звуки: {e}")
            self.shoot_sound = None
            self.hit_sound = None

        self.keys_pressed = set()
        self.game_over = False
        self.score = 0
        self.time_elapsed = 0
        self.wave = 1
        self.enemies_killed = 0

        print("Игра настроена!")

    def create_simple_map(self):
        wall_positions = [
            (200, 150), (300, 150), (400, 150), (500, 150), (600, 150),
            (200, 450), (300, 450), (400, 450), (500, 450), (600, 450),
            (100, 300), (700, 300),
            (150, 200), (150, 400), (650, 200), (650, 400)
        ]

        for x, y in wall_positions:
            wall = Wall(x, y)
            self.wall_list.append(wall)
        print(f"Создано стен: {len(self.wall_list)}")

    def spawn_enemies(self):
        num_enemies = 3 + self.wave

        for _ in range(num_enemies):
            placed = False
            attempts = 0

            while not placed and attempts < 50:
                x = random.randint(100, SCREEN_WIDTH - 100)
                y = random.randint(100, SCREEN_HEIGHT - 100)

                distance = math.sqrt((x - self.player.center_x) ** 2 + (y - self.player.center_y) ** 2)

                if distance > 300:
                    wall_collision = False
                    for wall in self.wall_list:
                        if abs(wall.center_x - x) < 64 and abs(wall.center_y - y) < 64:
                            wall_collision = True
                            break

                    if not wall_collision:
                        enemy = Enemy(x, y)
                        self.enemy_list.append(enemy)
                        placed = True

                attempts += 1

        print(f"Создано врагов: {len(self.enemy_list)}")

    def draw_rectangle_simple(self, center_x, center_y, width, height, color):
        points = [
            (center_x - width / 2, center_y - height / 2),
            (center_x + width / 2, center_y - height / 2),
            (center_x + width / 2, center_y + height / 2),
            (center_x - width / 2, center_y + height / 2)
        ]
        arcade.draw_polygon_filled(points, color)

    def on_draw(self):
        self.clear()

        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        self.wall_list.draw()
        self.enemy_list.draw()
        self.player_list.draw()
        self.bullet_list.draw()

        arcade.draw_text(f"Очки: {self.score}", 10, SCREEN_HEIGHT - 30, arcade.color.WHITE, 16)

        if self.player:
            health_width = 200
            health_percent = self.player.health / self.player.max_health

            self.draw_rectangle_simple(110, SCREEN_HEIGHT - 50, health_width, 20, arcade.color.DARK_GRAY)
            if health_percent > 0:
                current_width = health_width * health_percent
                self.draw_rectangle_simple(110 - health_width / 2 + current_width / 2,
                                           SCREEN_HEIGHT - 50,
                                           current_width,
                                           20,
                                           arcade.color.GREEN)

            arcade.draw_text(f"Здоровье: {self.player.health}/{self.player.max_health}",
                             10, SCREEN_HEIGHT - 60, arcade.color.WHITE, 14)

        arcade.draw_text(f"Волна: {self.wave}", 10, SCREEN_HEIGHT - 90, arcade.color.WHITE, 16)
        arcade.draw_text(f"Убито врагов: {self.enemies_killed}", 10, SCREEN_HEIGHT - 120, arcade.color.WHITE, 16)

        arcade.draw_text("Управление: WASD - движение, ЛКМ - выстрел, ESC - меню",
                         SCREEN_WIDTH // 2, 30, arcade.color.LIGHT_GRAY, 14, anchor_x="center")

        if self.game_over:
            self.draw_rectangle_simple(
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                SCREEN_WIDTH, SCREEN_HEIGHT,
                arcade.color.BLACK
            )
            arcade.draw_text("ИГРА ОКОНЧЕНА",
                             SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
                             arcade.color.RED, 40, anchor_x="center")
            arcade.draw_text(f"Ваш счет: {self.score}",
                             SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                             arcade.color.WHITE, 30, anchor_x="center")
            arcade.draw_text(f"Убито врагов: {self.enemies_killed}",
                             SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40,
                             arcade.color.YELLOW, 24, anchor_x="center")
            arcade.draw_text("Нажмите ESC для выхода в меню",
                             SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 90,
                             arcade.color.YELLOW, 20, anchor_x="center")

    def on_update(self, delta_time):
        if self.game_over:
            return

        self.time_elapsed += delta_time

        if self.player is None:
            return

        self.player.update_movement(delta_time, self.keys_pressed)

        for bullet in self.bullet_list:
            bullet.update(delta_time)

        if hasattr(self.player, 'update_animation'):
            self.player.update_animation(delta_time)

        for enemy in self.enemy_list:
            attacked = enemy.update(delta_time, self.player)
            if attacked:
                self.player.health -= enemy.damage
                if self.hit_sound:
                    arcade.play_sound(self.hit_sound, volume=0.3)

        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.wall_list)
            if hit_list:
                bullet.remove_from_sprite_lists()
                continue

            hit_enemies = arcade.check_for_collision_with_list(bullet, self.enemy_list)
            for enemy in hit_enemies:
                bullet.remove_from_sprite_lists()
                if enemy.take_damage(bullet.damage):
                    enemy.remove_from_sprite_lists()
                    self.score += 50
                    self.enemies_killed += 1
                else:
                    self.score += 10
                break

        if self.player.health <= 0:
            self.game_over = True

        if len(self.enemy_list) == 0:
            self.wave += 1
            self.spawn_enemies()
            print(f"Волна {self.wave} началась!")

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT and not self.game_over and self.player:
            bullet = Bullet(
                self.player.center_x,
                self.player.center_y,
                x,
                y
            )
            self.bullet_list.append(bullet)
            if self.shoot_sound:
                arcade.play_sound(self.shoot_sound, volume=0.3)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            menu_view = GameMenu()
            self.window.show_view(menu_view)
            return

        if key == arcade.key.Z:
            print("=== ДЕБАГ ИНФО ===")
            if self.player:
                print(f"Игрок: ({self.player.center_x:.1f}, {self.player.center_y:.1f})")
                print(f"Здоровье: {self.player.health}/{self.player.max_health}")
            print(f"Стен: {len(self.wall_list)}")
            print(f"Пули: {len(self.bullet_list)}")
            print(f"Врагов: {len(self.enemy_list)}")
            print(f"Счет: {self.score}")
            print(f"Волна: {self.wave}")

        if key == arcade.key.P and self.player:
            self.player.health = min(self.player.max_health, self.player.health + 20)
            print(f"Здоровье увеличено: {self.player.health}/{self.player.max_health}")

        if key == arcade.key.K and self.enemy_list:
            for enemy in self.enemy_list:
                enemy.remove_from_sprite_lists()
            self.enemies_killed += len(self.enemy_list)
            self.score += len(self.enemy_list) * 50
            print("Все враги убиты!")

        if key in [arcade.key.W, arcade.key.A, arcade.key.S, arcade.key.D,
                   arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT]:
            self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu_view = GameMenu()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()