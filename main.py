# main.py
import pygame
import sys
import webbrowser
import threading
import os
import json
import nbtlib
from nbtlib.tag import Compound, List, String, Int
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
GRAY = (200, 200, 200)
LIGHT_PURPLE = (200, 162, 255)

# Завантаження шрифту
font_path = "source/fonts/Minecraft.ttf"
title_font = pygame.font.Font(font_path, 100)
button_font = pygame.font.Font(font_path, 60)
profile_font = pygame.font.Font(font_path, 40)
settings_title_font = pygame.font.Font(font_path, 33)
input_font = pygame.font.Font(font_path, 36)

# Функція для завантаження конфігурації
def load_config():
    config_file = "config.json"
    default_config = {
        "minecraft_directory": r"minecraft_folder",
        "username": "Player",
        "language": "en_us",
        "ram": 8
    }
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            return json.load(f)
    return default_config

# Функція для збереження конфігурації
def save_config(directory, username, language, ram):
    config_file = "config.json"
    config = {
        "minecraft_directory": directory,
        "username": username,
        "language": language,
        "ram": ram
    }
    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)

# Функція для додавання сервера до servers.dat
def add_predefined_server(directory):
    # Переконаємося, що директорія існує
    os.makedirs(directory, exist_ok=True)
    servers_file = os.path.join(directory, "servers.dat")
    
    # --- ПОЛЕ ДЛЯ ВКАЗАННЯ АДРЕСИ ТА ПОРТУ СЕРВЕРА ---
    server_data = {
        "name": "WebUniverseServer",
        "ip": "ivanl47.aternos.me:42309",
        "port": 42309
    }
    # --- КІНЕЦЬ ПОЛЯ ДЛЯ ЗМІНИ ---

    try:
        # Завантажуємо існуючий файл servers.dat
        server_list = List[Compound]()
        if os.path.exists(servers_file):
            try:
                nbt_file = nbtlib.load(servers_file)
                if "servers" in nbt_file:
                    server_list = nbt_file["servers"]
                    print(f"Існуючі сервери: {server_list}")
            except Exception as e:
                print(f"Помилка при читанні servers.dat: {e}. Створюємо новий файл.")

        # Перевіряємо, чи сервер уже є в списку
        server_exists = any(
            server["ip"] == server_data["ip"] and int(server.get("port", 25565)) == server_data["port"]
            for server in server_list
        )

        if not server_exists:
            # Додаємо новий сервер
            new_server = Compound({
                "name": String(server_data["name"]),
                "ip": String(server_data["ip"]),
                "port": Int(server_data["port"])
            })
            server_list.append(new_server)
            print(f"Додано сервер: {server_data['name']} ({server_data['ip']})")

            # Створюємо або оновлюємо NBT-файл
            nbt_data = Compound({"servers": server_list})
            nbt_file = nbtlib.File(nbt_data)
            # Зберігаємо файл без стиснення
            try:
                # Спробуємо використати параметр gzipped=False
                nbt_file.save(servers_file, gzipped=False)
            except TypeError:
                # Якщо параметр gzipped не підтримується, просто зберігаємо
                nbt_file.save(servers_file)
            print(f"Файл servers.dat оновлено: {servers_file}")
        else:
            print(f"Сервер {server_data['ip']} уже є в списку")

        # Перевіряємо, чи файл створений
        if os.path.exists(servers_file):
            updated_nbt = nbtlib.load(servers_file)
            print(f"Оновлений список серверів: {updated_nbt['servers']}")
        else:
            print(f"Файл servers.dat НЕ створений у {servers_file}")

    except Exception as e:
        print(f"Помилка при додаванні сервера: {e}")

# Завантаження початкових налаштувань
config = load_config()
minecraft_directory = config["minecraft_directory"]
fake_auth = {
    "username": config["username"],
    "uuid": "",
    "access_token": ""
}
version = "1.20.1"

# Стан завантаження
is_loading = False

# Стан вікна налаштувань
settings_open = False
SETTINGS_WINDOW_WIDTH = 1000
SETTINGS_WINDOW_HEIGHT = 600
settings_window = pygame.Surface((SETTINGS_WINDOW_WIDTH, SETTINGS_WINDOW_HEIGHT))

# Стан полів вводу
input_path_active = False
input_username_active = False
input_path_text = config["minecraft_directory"]
input_username_text = config["username"]

# Стан слайдера для RAM
ram_value = config["ram"]
RAM_MIN = 1
RAM_MAX = 16

def on_launch_complete():
    global is_loading
    is_loading = False

# Функція для створення тексту
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# Функція для створення кнопки з анімацією натискання (для основного вікна)
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

# Функція для створення кнопки у вікні налаштувань
def draw_settings_button(surface, rect, text, font, color, text_color, pressed=False):
    if pressed:
        button_color = (max(color[0] - 50, 0), max(color[1] - 50, 0), max(color[2] - 50, 0))
    else:
        button_color = color
    pygame.draw.rect(surface, button_color, rect, border_radius=15)
    draw_text(text, font, text_color, surface, rect.x + 20, rect.y + 10)

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

# Функція для малювання поля вводу у вікні налаштувань
def draw_input_field(surface, rect, text, active, label):
    color = LIGHT_PURPLE if active else GRAY
    pygame.draw.rect(surface, color, rect, border_radius=10)
    draw_text(text, input_font, DARK_PURPLE, surface, rect.x + 10, rect.y + 10)
    draw_text(label, input_font, WHITE, surface, rect.x, rect.y - 40)

# Функція для малювання слайдера RAM
def draw_ram_slider(surface, rect, value, min_val, max_val, dragging):
    pygame.draw.rect(surface, GRAY, rect, border_radius=5)
    slider_width = rect.width / (max_val - min_val)
    slider_pos = rect.x + (value - min_val) * slider_width
    slider_rect = pygame.Rect(slider_pos - 10, rect.y - 5, 20, rect.height + 10)
    pygame.draw.rect(surface, LIGHT_PURPLE if dragging else WHITE, slider_rect, border_radius=5)
    ram_text = f"RAM: {value} GB"
    draw_text(ram_text, input_font, WHITE, surface, rect.x + rect.width + 20, rect.y - 5)

# Функція для зміни налаштувань у options.txt
def set_minecraft_options(directory, language, ram):
    options_path = os.path.join(directory, "options.txt")
    os.makedirs(directory, exist_ok=True)
    lines = []
    if os.path.exists(options_path):
        with open(options_path, "r") as f:
            lines = f.readlines()

    lang_found = False
    ram_found = False
    for i, line in enumerate(lines):
        if line.startswith("lang:"):
            lines[i] = f"lang:{language}\n"
            lang_found = True
        if line.startswith("jvm_args:"):
            lines[i] = f"jvm_args:-Xmx{ram}G\n"
            ram_found = True
    if not lang_found:
        lines.append(f"lang:{language}\n")
    if not ram_found:
        lines.append(f"jvm_args:-Xmx{ram}G\n")

    with open(options_path, "w") as f:
        f.writelines(lines)
    print(f"Налаштування збережено: мова={language}, RAM={ram}G у {options_path}")

# Функція для малювання вікна налаштувань
def draw_settings_window(mouse_pos, left_pressed, ram_dragging):
    settings_window.fill(PURPLE)
    draw_text("Settings", settings_title_font, WHITE, settings_window, 400, 50)
    draw_input_field(settings_window, input_path_rect, input_path_text, input_path_active, "Minecraft Directory")
    draw_input_field(settings_window, input_username_rect, input_username_text, input_username_active, "Username")

    settings_mouse_pos = (mouse_pos[0] - (WINDOW_WIDTH - SETTINGS_WINDOW_WIDTH) // 2, mouse_pos[1] - (WINDOW_HEIGHT - SETTINGS_WINDOW_HEIGHT) // 2)
    
    is_english_pressed = english_button_rect.collidepoint(settings_mouse_pos) and left_pressed
    is_ukrainian_pressed = ukrainian_button_rect.collidepoint(settings_mouse_pos) and left_pressed
    draw_settings_button(settings_window, english_button_rect, "English", button_font, WHITE, DARK_PURPLE, pressed=is_english_pressed)
    draw_settings_button(settings_window, ukrainian_button_rect, "Українська", button_font, WHITE, DARK_PURPLE, pressed=is_ukrainian_pressed)
    
    draw_ram_slider(settings_window, ram_slider_rect, ram_value, RAM_MIN, RAM_MAX, ram_dragging)
    
    window.blit(settings_window, ((WINDOW_WIDTH - SETTINGS_WINDOW_WIDTH) // 2, (WINDOW_HEIGHT - SETTINGS_WINDOW_HEIGHT) // 2))

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

# Визначення прямокутників для кнопок і полів вводу
play_rect = pygame.Rect(100, 300, 400, 100)
settings_rect = pygame.Rect(100, 420, 400, 100)
mods_rect = pygame.Rect(100, 540, 400, 100)
exit_rect = pygame.Rect(100, 660, 400, 100)
profile_rect = pygame.Rect(WINDOW_WIDTH - 280, 30, 250, 60)
input_path_rect = pygame.Rect(50, 150, 900, 50)
input_username_rect = pygame.Rect(50, 230, 900, 50)
english_button_rect = pygame.Rect(50, 310, 400, 100)
ukrainian_button_rect = pygame.Rect(550, 310, 400, 100)
ram_slider_rect = pygame.Rect(50, 460, 700, 20)

# Функція для запуску Minecraft при натисканні кнопки
def on_play_button_clicked():
    global is_loading, minecraft_directory, fake_auth
    minecraft_directory = input_path_text
    fake_auth["username"] = input_username_text
    set_minecraft_options(minecraft_directory, current_language, ram_value)
    add_predefined_server(minecraft_directory)
    is_loading = True
    thread = threading.Thread(target=launch_minecraft_game, args=(minecraft_directory, version, fake_auth, on_launch_complete))
    thread.start()

# Основний цикл
running = True
ram_dragging = False
current_language = config["language"]

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            save_config(input_path_text, input_username_text, current_language, ram_value)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if play_rect.collidepoint(mouse_pos):
                on_play_button_clicked()
            elif settings_rect.collidepoint(mouse_pos):
                settings_open = True
            elif mods_rect.collidepoint(mouse_pos):
                print("mods button clicked!")
            elif exit_rect.collidepoint(mouse_pos):
                running = False
                save_config(input_path_text, input_username_text, current_language, ram_value)
            elif profile_rect.collidepoint(mouse_pos):
                print("Profile button clicked!")
            elif logo_button.collidepoint(mouse_pos):
                webbrowser.open("https://webuniverseua.com/showend")
            elif instagram_button.collidepoint(mouse_pos):
                webbrowser.open("https://www.instagram.com/web.universe.ua/")
            elif tiktok_button.collidepoint(mouse_pos):
                webbrowser.open("https://www.tiktok.com/@web.universe.ua")
            elif settings_open:
                settings_pos = (mouse_pos[0] - (WINDOW_WIDTH - SETTINGS_WINDOW_WIDTH) // 2, mouse_pos[1] - (WINDOW_HEIGHT - SETTINGS_WINDOW_HEIGHT) // 2)
                if input_path_rect.collidepoint(settings_pos):
                    input_path_active = True
                    input_username_active = False
                elif input_username_rect.collidepoint(settings_pos):
                    input_username_active = True
                    input_path_active = False
                elif english_button_rect.collidepoint(settings_pos):
                    current_language = "en_us"
                    set_minecraft_options(input_path_text, current_language, ram_value)
                    save_config(input_path_text, input_username_text, current_language, ram_value)
                elif ukrainian_button_rect.collidepoint(settings_pos):
                    current_language = "uk_ua"
                    set_minecraft_options(input_path_text, current_language, ram_value)
                    save_config(input_path_text, input_username_text, current_language, ram_value)
                elif ram_slider_rect.collidepoint(settings_pos):
                    ram_dragging = True
                elif not pygame.Rect(0, 0, SETTINGS_WINDOW_WIDTH, SETTINGS_WINDOW_HEIGHT).collidepoint(settings_pos):
                    settings_open = False
                    input_path_active = False
                    input_username_active = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if ram_dragging:
                ram_dragging = False
                save_config(input_path_text, input_username_text, current_language, ram_value)
        elif event.type == pygame.MOUSEMOTION and ram_dragging:
            settings_pos = (event.pos[0] - (WINDOW_WIDTH - SETTINGS_WINDOW_WIDTH) // 2, event.pos[1] - (WINDOW_HEIGHT - SETTINGS_WINDOW_HEIGHT) // 2)
            slider_pos = max(ram_slider_rect.x, min(settings_pos[0], ram_slider_rect.x + ram_slider_rect.width))
            ram_value = int(RAM_MIN + (slider_pos - ram_slider_rect.x) / ram_slider_rect.width * (RAM_MAX - RAM_MIN))
            set_minecraft_options(input_path_text, current_language, ram_value)
        elif event.type == pygame.KEYDOWN and settings_open:
            if input_path_active:
                if event.key == pygame.K_RETURN:
                    input_path_active = False
                    save_config(input_path_text, input_username_text, current_language, ram_value)
                elif event.key == pygame.K_BACKSPACE:
                    input_path_text = input_path_text[:-1]
                else:
                    input_path_text += event.unicode
            elif input_username_active:
                if event.key == pygame.K_RETURN:
                    input_username_active = False
                    save_config(input_path_text, input_username_text, current_language, ram_value)
                elif event.key == pygame.K_BACKSPACE:
                    input_username_text = input_username_text[:-1]
                else:
                    input_username_text += event.unicode

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

    # Малювання вікна налаштувань, якщо воно відкрите
    if settings_open:
        draw_settings_window(mouse_pos, left_pressed, ram_dragging)

    pygame.display.flip()

pygame.quit()
sys.exit()