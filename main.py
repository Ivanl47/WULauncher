# main.py
import pygame
import sys
import webbrowser
import threading
import os
from launcher import launch_minecraft_game

# Ініціалізація Pygame
pygame.init()

# Налаштування вікна
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("WEB UNIVERSE LAUNCHER")

# Кольори
WHITE = (255, 255, 255)
PURPLE = (147, 112, 219)
PINK = (255, 182, 193)
DARK_PURPLE = (75, 0, 130)

# Завантаження шрифту
font_path = "source/fonts/Minecraft.ttf"
title_font = pygame.font.Font(font_path, 100)
button_font = pygame.font.Font(font_path, 60)
profile_font = pygame.font.Font(font_path, 40)

# Налаштування Minecraft
minecraft_directory = r"D:\Desktop\май"  # Зміни на свій шлях
version = "1.20.1"
fake_auth = {
    "username": "PirateMotherfucker",
    "uuid": "",
    "access_token": ""
}

# Стан завантаження та закриття
is_loading = False
should_close = False

# Функція для створення тексту
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# Функція для створення кнопки з анімацією натискання
def draw_button(rect, text, font, color, text_color, icon=None, pressed=False):
    if pressed:
        button_color = (max(color[0] - 50, 0), max(color[1] - 50, 0), max(color[2] - 50, 0))
    else:
        button_color = color
    pygame.draw.rect(window, button_color, rect, border_radius=15)
    draw_text(text, font, text_color, window, rect.x + 40, rect.y + 20)
    if icon:
        icon_width = 50
        icon_height = int(icon_width * (icon.get_height() / icon.get_width()))
        icon = pygame.transform.scale(icon, (icon_width, icon_height))
        window.blit(icon, (rect.x + rect.width - 70, rect.y + 15))

# Функція для створення кнопки-іконки (соцмережі)
def draw_icon_button(icon, x, y, target_width):
    icon_width = target_width
    icon_height = int(icon_width * (icon.get_height() / icon.get_width()))
    icon = pygame.transform.scale(icon, (icon_width, icon_height))
    icon_rect = pygame.Rect(x, y, icon_width, icon_height)
    window.blit(icon, (x, y))
    return icon_rect

# Функція для малювання "loading..."
def draw_loading_text():
    loading_text = profile_font.render("loading...", True, DARK_PURPLE)
    text_rect = loading_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
    window.blit(loading_text, text_rect)

# Завантаження зображень
cloud_image = pygame.image.load("source/images/cloud.png")
rocket_icon = pygame.image.load("source/images/WU_rocket.png")
settings_icon = pygame.image.load("source/images/WU_space.png")
logo_icon = pygame.image.load("source/images/WU_logo.png")
instagram_icon = pygame.image.load("source/images/WU_instagram.png")
tiktok_icon = pygame.image.load("source/images/WU_tiktok.png")
profile_icon = pygame.image.load("source/images/WU_planet.png")

# Зміна розміру хмари
base_height = WINDOW_HEIGHT
scale_factor = 1.2
new_height = int(base_height * scale_factor)
new_width = int(cloud_image.get_width() * (new_height / cloud_image.get_height()))
cloud_image = pygame.transform.scale(cloud_image, (new_width, new_height))

# Зміна розміру іконки профілю
profile_icon_width = 40
profile_icon_height = int(profile_icon_width * (profile_icon.get_height() / profile_icon.get_width()))
profile_icon = pygame.transform.scale(profile_icon, (profile_icon_width, profile_icon_height))

# Визначення прямокутників для кнопок
play_rect = pygame.Rect(100, 300, 400, 100)
settings_rect = pygame.Rect(100, 420, 400, 100)
mods_rect = pygame.Rect(100, 540, 400, 100)
exit_rect = pygame.Rect(100, 660, 400, 100)
profile_rect = pygame.Rect(WINDOW_WIDTH - 280, 30, 250, 60)

# Функція для завершення встановлення та закриття лаунчера
def on_install_complete():
    global should_close
    pygame.time.delay(2000)  # Затримка 2 секунди для відображення "loading..."
    should_close = True

# Функція для перезапуску лаунчера
def restart_launcher():
    python = sys.executable  # Шлях до інтерпретатора Python
    os.execl(python, python, *sys.argv)  # Перезапуск main.py

# Функція для запуску Minecraft
def on_play_button_clicked():
    global is_loading
    is_loading = True
    thread = threading.Thread(target=launch_minecraft_game, args=(minecraft_directory, version, fake_auth, on_install_complete, restart_launcher))
    thread.start()

# Основний цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if play_rect.collidepoint(mouse_pos):
                on_play_button_clicked()
            elif settings_rect.collidepoint(mouse_pos):
                print("settings button clicked!")
            elif mods_rect.collidepoint(mouse_pos):
                print("mods button clicked!")
            elif exit_rect.collidepoint(mouse_pos):
                running = False
            elif profile_rect.collidepoint(mouse_pos):
                print("Profile button clicked!")
            elif logo_button.collidepoint(mouse_pos):
                webbrowser.open("https://webuniverseua.com/showend")
            elif instagram_button.collidepoint(mouse_pos):
                webbrowser.open("https://www.instagram.com/web.universe.ua/")
            elif tiktok_button.collidepoint(mouse_pos):
                webbrowser.open("https://www.tiktok.com/@web.universe.ua")

    # Перевірка, чи потрібно закрити лаунчер
    if should_close:
        running = False

    # Отримуємо поточний стан миші
    mouse_pos = pygame.mouse.get_pos()
    left_pressed = pygame.mouse.get_pressed()[0]

    # Визначаємо, чи натиснуті кнопки
    is_play_pressed = play_rect.collidepoint(mouse_pos) and left_pressed
    is_settings_pressed = settings_rect.collidepoint(mouse_pos) and left_pressed
    is_mods_pressed = mods_rect.collidepoint(mouse_pos) and left_pressed
    is_exit_pressed = exit_rect.collidepoint(mouse_pos) and left_pressed

    # Очистка екрану
    window.fill(WHITE)

    # Малювання елементів
    window.blit(cloud_image, (0, 0))
    draw_text("WEB UNIVERSE", title_font, PURPLE, window, 800, 150)
    draw_text("LAUNCHER", title_font, PURPLE, window, 800, 260)

    draw_button(play_rect, "PLAY", button_font, PURPLE, WHITE, rocket_icon, pressed=is_play_pressed)
    draw_button(settings_rect, "settings", button_font, PURPLE, WHITE, settings_icon, pressed=is_settings_pressed)
    draw_button(mods_rect, "mods", button_font, PURPLE, WHITE, pressed=is_mods_pressed)
    draw_button(exit_rect, "exit", button_font, PURPLE, WHITE, pressed=is_exit_pressed)

    pygame.draw.rect(window, PURPLE, profile_rect, border_radius=10)
    draw_text("profile", profile_font, DARK_PURPLE, window, profile_rect.x + 10, profile_rect.y + 10)
    window.blit(profile_icon, (profile_rect.x + profile_rect.width - 50, profile_rect.y + 5))

    logo_button = draw_icon_button(logo_icon, WINDOW_WIDTH - 475, WINDOW_HEIGHT - 150, 125)
    instagram_button = draw_icon_button(instagram_icon, WINDOW_WIDTH - 300, WINDOW_HEIGHT - 150, 80)
    tiktok_button = draw_icon_button(tiktok_icon, WINDOW_WIDTH - 190, WINDOW_HEIGHT - 150, 80)

    # Малювання "loading...", якщо триває завантаження
    if is_loading:
        draw_loading_text()

    pygame.display.flip()

pygame.quit()
sys.exit()