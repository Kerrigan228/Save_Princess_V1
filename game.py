import pygame
import sys
import os
import random
import tkinter as tk
from tkinter import ttk

def assign_value():
    global SCREEN_HEIGHT, SCREEN_WIDTH
    if selected_size.get() == "1920x1080":
        SCREEN_HEIGHT = 1080
        SCREEN_WIDTH = 1920
    elif selected_size.get() == "1280x720":
        SCREEN_HEIGHT = 720
        SCREEN_WIDTH = 1280
    elif selected_size.get() == "800x600":
        SCREEN_HEIGHT = 600
        SCREEN_WIDTH = 800
    variable.set(f"Ширина: {SCREEN_WIDTH}, Высота: {SCREEN_HEIGHT}")
    root.destroy()

root = tk.Tk()
root.geometry("300x250")  # Увеличил размер, чтобы разместить элементы более равномерно

variable = tk.StringVar()
label = tk.Label(root, textvariable=variable)
label.pack(pady=10)  # Отступ сверху

# Добавляем вкладку
tab_control = ttk.Notebook(root)

tab1 = ttk.Frame(tab_control)
tab_control.add(tab1, text='Выбор размера')

selected_size = tk.StringVar(value="Выберите размер")

sizes = ["1920x1080", "1280x720", "800x600"]

for size in sizes:
    tk.Radiobutton(tab1, text=size, variable=selected_size, value=size).pack()

button = tk.Button(root, text="Начать игру", command=assign_value)


tab_control.pack(expand=1, fill="both")
button.pack(pady=40)  # Отступ снизу
root.mainloop()


# Инициализация Pygame
pygame.init()

# Размеры экрана


# Размеры карты
MAP_WIDTH = 1600
MAP_HEIGHT = 1200

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Игровой персонаж
class Player(pygame.sprite.Sprite):
    def __init__(self, image_paths, speed, animation_speed=15):
        super().__init__()
        self.image_paths = image_paths
        self.current_frame = 0
        self.animation_speed = animation_speed
        self.load_images()
        self.image = self.images["down"][0]
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.attack_range = pygame.Rect(0, 0, 50, 50)  # Зона атаки
        self.experience = 0
        self.speed = speed

    def load_images(self):
        self.images = {"up": [], "down": [], "left": [], "right": []}
        for direction in self.images.keys():
            for path in self.image_paths[direction]:
                image = pygame.image.load(path)
                image = pygame.transform.scale(image, (50, 75))
                self.images[direction].append(image)

    def update(self):
        keys = pygame.key.get_pressed()
        direction = None

        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            direction = "left"
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            direction = "right"
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
            direction = "up"
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
            direction = "down"

        if direction:
            self.animate(direction)

        # Обновление зоны атаки
        self.attack_range.center = self.rect.center

    def animate(self, direction):
        self.current_frame = (self.current_frame + 1) % (len(self.images[direction]) * self.animation_speed)
        frame_index = self.current_frame // self.animation_speed
        self.image = self.images[direction][frame_index]

# Класс для отображения полосы здоровья
class HealthBar(pygame.sprite.Sprite):
    def __init__(self, max_health):
        super().__init__()
        self.max_health = max_health
        self.current_health = max_health
        self.width = 30
        self.height = 5

    def update(self, x, y, health):
        self.current_health = health
        self.rect = pygame.Rect(x - self.width // 2, y - 10, self.width, self.height)
        pygame.draw.rect(screen, RED, self.rect)
        current_width = int((self.current_health / self.max_health) * self.width)
        remaining_rect = pygame.Rect(x - self.width // 2, y - 10, current_width, self.height)
        pygame.draw.rect(screen, GREEN, remaining_rect)

# Класс для кнопки атаки
class AttackButton(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.topleft = (10, SCREEN_HEIGHT - 60)

# Враг
class Enemy(pygame.sprite.Sprite):
    def __init__(self, image_path, x, y):
        super().__init__()
        original_image = pygame.image.load(image_path)
        # Уменьшаем размер изображения до 30x30 пикселей
        self.image = pygame.transform.scale(original_image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = random.choice(["left", "right", "up", "down"])
        self.max_health = 100
        self.current_health = self.max_health
        self.health_bar = HealthBar(self.max_health)

    def update(self):
        if self.direction == "left":
            self.rect.x -= 2
        elif self.direction == "right":
            self.rect.x += 2
        elif self.direction == "up":
            self.rect.y -= 2
        elif self.direction == "down":
            self.rect.y += 2

        # Простая логика изменения направления
        if random.randint(0, 100) < 2:  # Шанс изменения направления: 2%
            self.direction = random.choice(["left", "right", "up", "down"])

        # Обновление полосы здоровья
        self.health_bar.update(self.rect.x, self.rect.y, self.current_health)

# Создание экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RPG с выбором текстуры, фоном и врагами")

# Загрузка изображения для фона и текстур врагов
background_image = pygame.image.load("background.jpg")
enemy_texture = pygame.image.load("enemy_texture.png")

# Группы спрайтов
all_sprites = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()

# Функция для создания игрового персонажа
def create_player(speed, texture_folder):
    image_paths = {
        "up": [os.path.join(texture_folder, "up_1.png"), os.path.join(texture_folder, "up_2.png"), os.path.join(texture_folder, "up_3.png")],
        "down": [os.path.join(texture_folder, "down_1.png"), os.path.join(texture_folder, "down_2.png"), os.path.join(texture_folder, "down_3.png")],
        "left": [os.path.join(texture_folder, "left_1.png"), os.path.join(texture_folder, "left_2.png"), os.path.join(texture_folder, "left_3.png")],
        "right": [os.path.join(texture_folder, "right_1.png"), os.path.join(texture_folder, "right_2.png"), os.path.join(texture_folder, "right_3.png")]
    }
    player = Player(image_paths, speed)
    all_sprites.add(player)
    return player

# Создание игрового персонажа
player = create_player(speed=1, texture_folder="textures")

# Создание врагов
for _ in range(5):
    enemy = Enemy("enemy_texture.png", random.randint(0, MAP_WIDTH), random.randint(0, MAP_HEIGHT))
    all_sprites.add(enemy)
    enemies_group.add(enemy)

# Загрузка звуковых файлов
attack_sound = pygame.mixer.Sound("attack_sound.wav")
enemy_hit_sound = pygame.mixer.Sound("enemy_hit_sound.wav")

# Создание кнопки атаки
attack_button = AttackButton()
ui_sprites = pygame.sprite.Group(attack_button)

# Начальные координаты камеры
camera_x = 0
camera_y = 0

# Основной цикл игры
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Левая кнопка мыши
            # При нажатии на кнопку атаки или левой кнопки мыши атакуем ближайшего врага
            if attack_button.rect.collidepoint(event.pos):
                attack_sound.play()  # Проигрываем звук атаки
                for enemy in pygame.sprite.spritecollide(player, enemies_group, False):
                    # Уменьшаем здоровье врага
                    enemy.current_health -= 20
                    enemy_hit_sound.play()  # Проигрываем звук попадания по врагу
                    if enemy.current_health <= 0:
                        # Увеличиваем опыт игрока за победу
                        player.experience += 50
                        # Убираем врага из группы спрайтов
                        enemy.kill()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.rect.x -= player.speed
    if keys[pygame.K_RIGHT]:
        player.rect.x += player.speed
    if keys[pygame.K_UP]:
        player.rect.y -= player.speed
    if keys[pygame.K_DOWN]:
        player.rect.y += player.speed

    # Обновление координат камеры в зависимости от положения персонажа
    camera_x = player.rect.x - SCREEN_WIDTH // 2
    camera_y = player.rect.y - SCREEN_HEIGHT // 2

    # Отрисовка фона
    screen.blit(background_image, (-camera_x, -camera_y))

    # Обновление спрайтов
    all_sprites.update()

    # Отрисовка спрайтов
    all_sprites.draw(screen)

    # Вывод опыта на экран
    font = pygame.font.Font(None, 36)
    text = font.render(f"Опыт: {player.experience}", True, WHITE)
    screen.blit(text, (10, 10))

    # Отрисовка кнопки атаки
    ui_sprites.draw(screen)

    # Обновление дисплея
    pygame.display.flip()

    # Установка FPS
    clock.tick(60)

# Завершение Pygame
pygame.quit()
sys.exit()
