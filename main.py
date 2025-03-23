# main.py
import pygame
import sys
import webbrowser
import threading
import os
import json
import nbtlib
import subprocess
import tkinter as tk
from tkinter import filedialog
import shutil
from nbtlib.tag import Compound, List, String, Int
import requests
import zipfile
import platform
import tarfile

# Функція для коректного визначення шляху до ресурсів у .exe
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Функція для перевірки прав доступу до папки
def check_directory_permissions(directory):
    try:
        os.makedirs(directory, exist_ok=True)
        test_file = os.path.join(directory, "test_permissions.txt")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        print(f"Directory permissions OK: {directory}")
        return True
    except Exception as e:
        print(f"Directory permissions error: {e}")
        return False

# Функція для перевірки наявності модів у папці
def check_mods_exist():
    global status_message
    update_status("Checking mods...")
    mods_dir = os.path.join(minecraft_directory, "mods")
    if not os.path.exists(mods_dir):
        update_status("Mods folder not found")
        return False
    files = os.listdir(mods_dir)
    for file in files:
        if file.endswith(".jar"):
            update_status("Mods found")
            return True
    update_status("No mods found")
    return False

# Функція для оновлення статусу
def update_status(message):
    global status_message
    status_message = message
    print(f"Status: {message}")
    pygame.display.flip()

# Функція для завантаження модів із GitHub
def download_mods_from_github():
    global status_message, error_message
    repo_owner = "Ivanl47"
    repo_name = "WULauncher"
    branch = "season_1"
    folder_path = "mods"
    mods_dir = os.path.join(minecraft_directory, "mods")
    
    update_status("Checking mods directory...")
    if not check_directory_permissions(mods_dir):
        error_message = "No permissions to mods directory!"
        update_status("Permission error")
        return False
    
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{folder_path}?ref={branch}"
    update_status("Requesting mods from GitHub...")
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        files = response.json()
        
        if not files:
            error_message = "Mods folder empty!"
            update_status("No mods in repository")
            return False
        
        for file in files:
            if file["type"] == "file" and file["name"].endswith(".jar"):
                file_url = file["download_url"]
                file_name = file["name"]
                file_path = os.path.join(mods_dir, file_name)
                
                if not os.path.exists(file_path):
                    update_status(f"Downloading {file_name}...")
                    file_response = requests.get(file_url, stream=True)
                    file_response.raise_for_status()
                    
                    with open(file_path, "wb") as f:
                        for chunk in file_response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    update_status(f"Downloaded {file_name}")
                else:
                    update_status(f"{file_name} already exists")
        
        if check_mods_exist():
            update_status("Mods downloaded successfully")
            return True
        else:
            error_message = "No mods downloaded!"
            update_status("Mods download failed")
            return False
                
    except requests.exceptions.RequestException as e:
        error_message = "Failed to download mods!"
        update_status("Download error")
        return False
    except Exception as e:
        error_message = "Unknown error while downloading mods!"
        update_status("Unknown error")
        return False

# Ініціалізація Pygame
pygame.init()

# Ініціалізація Tkinter (для вибору файлу)
root = tk.Tk()
root.withdraw()

# Налаштування вікна (960x540)
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540
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
font_path = resource_path("source/fonts/Minecraft.ttf")
title_font = pygame.font.Font(font_path, 50)
button_font = pygame.font.Font(font_path, 20)
profile_font = pygame.font.Font(font_path, 20)
settings_title_font = pygame.font.Font(font_path, 16)
input_font = pygame.font.Font(font_path, 18)

# Функція для завантаження конфігурації
def load_config():
    global status_message
    update_status("Loading config...")
    config_file = "config.json"
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    default_config = {
        "minecraft_directory": os.path.join(base_dir, "minecraft_folder"),
        "username": "Player",
        "language": "en_us",
        "ram": 8,
        "skin_path": ""
    }
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
            if not os.path.isabs(config["minecraft_directory"]):
                config["minecraft_directory"] = os.path.join(base_dir, config["minecraft_directory"])
            update_status("Config loaded")
            return config
    update_status("Using default config")
    return default_config

# Функція для збереження конфігурації
def save_config(directory, username, language, ram, skin_path):
    global status_message
    update_status("Saving config...")
    config_file = "config.json"
    config = {
        "minecraft_directory": directory,
        "username": username,
        "language": language,
        "ram": ram,
        "skin_path": skin_path
    }
    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)
    update_status("Config saved")

# Функція для додавання сервера до servers.dat
def add_predefined_server(directory):
    global status_message, error_message
    update_status("Adding server...")
    os.makedirs(directory, exist_ok=True)
    servers_file = os.path.join(directory, "servers.dat")
    
    server_data = {
        "name": "WebUniverseServer",
        "ip": "ivanl47.aternos.me:42309",
        "port": 42309
    }

    try:
        server_list = List[Compound]()
        if os.path.exists(servers_file):
            try:
                nbt_file = nbtlib.load(servers_file)
                if "servers" in nbt_file:
                    server_list = nbt_file["servers"]
            except Exception as e:
                update_status("Creating new servers.dat")

        server_exists = any(
            server["ip"] == server_data["ip"] and int(server.get("port", 25565)) == server_data["port"]
            for server in server_list
        )

        if not server_exists:
            new_server = Compound({
                "name": String(server_data["name"]),
                "ip": String(server_data["ip"]),
                "port": Int(server_data["port"])
            })
            server_list.append(new_server)
            nbt_data = Compound({"servers": server_list})
            nbt_file = nbtlib.File(nbt_data)
            try:
                nbt_file.save(servers_file, gzipped=False)
            except TypeError:
                nbt_file.save(servers_file)
            update_status("Server added")
        else:
            update_status("Server already exists")

    except Exception as e:
        error_message = "Failed to add server!"
        update_status("Server add error")

# Завантаження початкових налаштувань
config = load_config()
minecraft_directory = config["minecraft_directory"]
fake_auth = {
    "username": config["username"],
    "uuid": "",
    "access_token": ""
}
minecraft_version = "1.20.1"
forge_version = "1.20.1-47.3.0"
skin_path = config["skin_path"]

# Імпорт із launcher.py після визначення змінних
from launcher import install_and_launch_forge

# Стан завантаження
is_loading = False
status_message = ""
error_message = None

# Стан вікна налаштувань
settings_open = False
SETTINGS_WINDOW_WIDTH = 500
SETTINGS_WINDOW_HEIGHT = 300
settings_window = pygame.Surface((SETTINGS_WINDOW_WIDTH, SETTINGS_WINDOW_HEIGHT))
settings_window_rect = pygame.Rect((WINDOW_WIDTH - SETTINGS_WINDOW_WIDTH) // 2, (WINDOW_HEIGHT - SETTINGS_WINDOW_HEIGHT) // 2, SETTINGS_WINDOW_WIDTH, SETTINGS_WINDOW_HEIGHT)

# Стан полів вводу
input_path_active = False
input_username_active = False
input_path_text = config["minecraft_directory"]
input_username_text = config["username"]

# Стан слайдера для RAM
ram_value = config["ram"]
RAM_MIN = 1
RAM_MAX = 16

# Стан для скіна
skin_image = None
if skin_path and os.path.exists(skin_path):
    try:
        skin_image = pygame.image.load(skin_path)
        skin_image = pygame.transform.scale(skin_image, (32, 32))
    except Exception as e:
        print(f"Failed to load skin: {e}")
        skin_image = None

# Функції для автоматичної установки Java
def check_java():
    global status_message
    update_status("Checking Java...")
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, text=True, check=True)
        update_status("Java found")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        update_status("Java not found")
        return False

def download_and_install_java(install_dir):
    global status_message, error_message
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    if system == "windows":
        if "64" in arch:
            java_url = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.6%2B7/OpenJDK21U-jdk_x64_windows_hotspot_21.0.6_7.zip"
            java_filename = "OpenJDK21U-jdk_x64_windows_hotspot_21.0.6_7.zip"
        else:
            error_message = "Only 64-bit Windows supported!"
            update_status("Unsupported system")
            sys.exit(1)
    elif system == "linux":
        if "64" in arch:
            java_url = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.6%2B7/OpenJDK21U-jdk_x64_linux_hotspot_21.0.6_7.tar.gz"
            java_filename = "OpenJDK21U-jdk_x64_linux_hotspot_21.0.6_7.tar.gz"
        else:
            error_message = "Only 64-bit Linux supported!"
            update_status("Unsupported system")
            sys.exit(1)
    elif system == "darwin":
        if "arm" in arch:
            java_url = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.6%2B7/OpenJDK21U-jdk_aarch64_mac_hotspot_21.0.6_7.tar.gz"
            java_filename = "OpenJDK21U-jdk_aarch64_mac_hotspot_21.0.6_7.tar.gz"
        else:
            java_url = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.6%2B7/OpenJDK21U-jdk_x64_mac_hotspot_21.0.6_7.tar.gz"
            java_filename = "OpenJDK21U-jdk_x64_mac_hotspot_21.0.6_7.tar.gz"
    else:
        error_message = "Unsupported OS!"
        update_status("Unsupported system")
        sys.exit(1)

    os.makedirs(install_dir, exist_ok=True)
    java_zip_path = os.path.join(install_dir, java_filename)

    update_status("Downloading Java...")
    response = requests.get(java_url, stream=True)
    with open(java_zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    update_status("Java downloaded")

    update_status("Extracting Java...")
    if java_filename.endswith(".zip"):
        with zipfile.ZipFile(java_zip_path, "r") as zip_ref:
            zip_ref.extractall(install_dir)
    elif java_filename.endswith(".tar.gz"):
        with tarfile.open(java_zip_path, "r:gz") as tar_ref:
            tar_ref.extractall(install_dir)
    update_status("Java extracted")

    os.remove(java_zip_path)

    java_home = None
    for item in os.listdir(install_dir):
        item_path = os.path.join(install_dir, item)
        if os.path.isdir(item_path) and "jdk" in item.lower():
            java_home = item_path
            break

    if not java_home:
        error_message = "Java folder not found!"
        update_status("Java extraction error")
        sys.exit(1)

    java_bin = os.path.join(java_home, "bin", "java")
    if system == "windows":
        java_bin += ".exe"
    try:
        result = subprocess.run([java_bin, "-version"], capture_output=True, text=True, check=True)
        update_status("Java installed")
        return java_home
    except subprocess.CalledProcessError as e:
        error_message = "Java verification failed!"
        update_status("Java error")
        sys.exit(1)

def ensure_java():
    global status_message
    if check_java():
        return None
    install_dir = os.path.join(os.path.expanduser("~"), "custom_java")
    update_status("Installing Java...")
    java_home = download_and_install_java(install_dir)
    return java_home

# Функція, яка викликається після завершення запуску Minecraft
def on_launch_complete(success, message):
    global is_loading, status_message, error_message
    is_loading = False
    if success:
        update_status("Forge installed")
        # Перевіряємо наявність модів після встановлення Forge
        if not check_mods_exist():
            update_status("Downloading mods after Forge install...")
            if not download_mods_from_github():
                update_status("Mods download failed")
                return
        update_status("Game launched")
        logs_dir = os.path.join(minecraft_directory, "logs")
        latest_log = os.path.join(logs_dir, "latest.log")
        if os.path.exists(latest_log):
            update_status("Log created")
        else:
            update_status("Log not created")
    else:
        error_message = "Game launch failed!"
        update_status("Launch error")

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
    draw_text(text, font, text_color, window, rect.x + 20, rect.y + 10)
    if icon:
        icon_width = 25
        icon_height = int(icon_width * (icon.get_height() / icon.get_width()))
        icon = pygame.transform.scale(icon, (icon_width, icon_height))
        window.blit(icon, (rect.x + rect.width - 35, rect.y + 7))

# Функція для створення кнопки у вікні налаштувань
def draw_settings_button(surface, rect, text, font, color, text_color, pressed=False):
    if pressed:
        button_color = (max(color[0] - 50, 0), max(color[1] - 50, 0), max(color[2] - 50, 0))
    else:
        button_color = color
    pygame.draw.rect(surface, button_color, rect, border_radius=15)
    draw_text(text, font, text_color, surface, rect.x + 10, rect.y + (rect.height - font.get_height()) // 2)

# Функція для створення кнопки-іконки (соцмережі)
def draw_icon_button(icon, x, y, target_width):
    icon_width = target_width
    icon_height = int(icon_width * (icon.get_height() / icon.get_width()))
    icon = pygame.transform.scale(icon, (icon_width, icon_height))
    icon_rect = pygame.Rect(x, y, icon_width, icon_height)
    window.blit(icon, (x, y))
    return icon_rect

# Функція для малювання статусу або помилки
def draw_status_message():
    if error_message:
        status_text = profile_font.render(error_message, True, (255, 0, 0))
    else:
        status_text = profile_font.render(status_message, True, DARK_PURPLE)
    text_rect = status_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 25))
    window.blit(status_text, text_rect)

# Функція для малювання поля вводу у вікні налаштувань
def draw_input_field(surface, rect, text, active, label):
    color = LIGHT_PURPLE if active else GRAY
    pygame.draw.rect(surface, color, rect, border_radius=10)
    draw_text(text, input_font, DARK_PURPLE, surface, rect.x + 5, rect.y + (rect.height - input_font.get_height()) // 2)
    draw_text(label, input_font, WHITE, surface, rect.x, rect.y - 20)

# Функція для малювання слайдера RAM
def draw_ram_slider(surface, rect, value, min_val, max_val, dragging):
    pygame.draw.rect(surface, GRAY, rect, border_radius=5)
    slider_width = rect.width / (max_val - min_val)
    slider_pos = rect.x + (value - min_val) * slider_width
    slider_rect = pygame.Rect(slider_pos - 5, rect.y - 2, 10, rect.height + 4)
    pygame.draw.rect(surface, LIGHT_PURPLE if dragging else WHITE, slider_rect, border_radius=5)
    ram_text = f"RAM: {value} GB"
    draw_text(ram_text, input_font, WHITE, surface, rect.x + rect.width + 10, rect.y - 2)

# Функція для зміни налаштувань у options.txt
def set_minecraft_options(directory, language, ram):
    global status_message
    update_status("Saving options...")
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
    update_status("Options saved")

# Функція для вибору скіна
def choose_skin():
    global skin_path, skin_image, status_message
    update_status("Choosing skin...")
    skins_dir = "skins"
    os.makedirs(skins_dir, exist_ok=True)
    
    file_path = filedialog.askopenfilename(
        initialdir=skins_dir,
        title="Choose a Skin",
        filetypes=[("PNG files", "*.png")]
    )
    
    if file_path:
        skin_path = file_path
        try:
            skin_image = pygame.image.load(skin_path)
            skin_image = pygame.transform.scale(skin_image, (32, 32))
            update_status("Skin chosen")
            
            minecraft_dir = input_path_text
            target_skin_path = os.path.join(minecraft_dir, "skin.png")
            os.makedirs(minecraft_dir, exist_ok=True)
            shutil.copy(skin_path, target_skin_path)
            update_status("Skin copied")
            
            save_config(input_path_text, input_username_text, current_language, ram_value, skin_path)
        except Exception as e:
            error_message = "Failed to load skin!"
            update_status("Skin load error")
            skin_image = None

# Функція для відкриття папки з модами
def open_mods_folder():
    global minecraft_directory, status_message
    update_status("Opening mods folder...")
    mods_dir = os.path.join(minecraft_directory, "mods")
    try:
        os.makedirs(mods_dir, exist_ok=True)
        update_status("Mods folder ready")
    except Exception as e:
        error_message = "Failed to create mods folder!"
        update_status("Mods folder error")
        return

    try:
        if os.name == "nt":
            os.startfile(mods_dir)
        elif sys.platform == "darwin":
            subprocess.run(["open", mods_dir])
        else:
            subprocess.run(["xdg-open", mods_dir])
        update_status("Mods folder opened")
    except Exception as e:
        error_message = "Failed to open mods folder!"
        update_status("Folder open error")

# Функція для малювання вікна налаштувань
def draw_settings_window(mouse_pos, left_pressed, ram_dragging):
    settings_window.fill(PURPLE)
    draw_text("Settings", settings_title_font, WHITE, settings_window, 200, 15)
    
    draw_input_field(settings_window, input_path_rect, input_path_text, input_path_active, "Minecraft Directory")
    draw_input_field(settings_window, input_username_rect, input_username_text, input_username_active, "Username")

    settings_mouse_pos = (mouse_pos[0] - (WINDOW_WIDTH - SETTINGS_WINDOW_WIDTH) // 2, mouse_pos[1] - (WINDOW_HEIGHT - SETTINGS_WINDOW_HEIGHT) // 2)
    
    is_english_pressed = english_button_rect.collidepoint(settings_mouse_pos) and left_pressed
    is_ukrainian_pressed = ukrainian_button_rect.collidepoint(settings_mouse_pos) and left_pressed
    is_choose_skin_pressed = choose_skin_button_rect.collidepoint(settings_mouse_pos) and left_pressed
    draw_settings_button(settings_window, english_button_rect, "English", button_font, WHITE, DARK_PURPLE, pressed=is_english_pressed)
    draw_settings_button(settings_window, ukrainian_button_rect, "Ukrainian", button_font, WHITE, DARK_PURPLE, pressed=is_ukrainian_pressed)
    draw_settings_button(settings_window, choose_skin_button_rect, "Choose Skin", button_font, WHITE, DARK_PURPLE, pressed=is_choose_skin_pressed)
    
    draw_ram_slider(settings_window, ram_slider_rect, ram_value, RAM_MIN, RAM_MAX, ram_dragging)
    
    if skin_image:
        draw_text("Current Skin:", input_font, WHITE, settings_window, 375, 175)
        settings_window.blit(skin_image, (375, 195))
    
    window.blit(settings_window, ((WINDOW_WIDTH - SETTINGS_WINDOW_WIDTH) // 2, (WINDOW_HEIGHT - SETTINGS_WINDOW_HEIGHT) // 2))

# Завантаження зображень
cloud_image = pygame.image.load(resource_path("source/images/cloud.png"))
rocket_icon = pygame.image.load(resource_path("source/images/WU_rocket.png"))
settings_icon = pygame.image.load(resource_path("source/images/WU_space.png"))
logo_icon = pygame.image.load(resource_path("source/images/WU_logo.png"))
instagram_icon = pygame.image.load(resource_path("source/images/WU_instagram.png"))
tiktok_icon = pygame.image.load(resource_path("source/images/WU_tiktok.png"))

# Зміна розміру хмари
base_height = WINDOW_HEIGHT
scale_factor = 1.32
new_height = int(base_height * scale_factor)
new_width = int(cloud_image.get_width() * (new_height / cloud_image.get_height()))
cloud_image = pygame.transform.scale(cloud_image, (new_width, new_height))

# Визначення прямокутників для кнопок і полів вводу
play_rect = pygame.Rect(50, 150, 200, 50)
settings_rect = pygame.Rect(50, 210, 200, 50)
mods_rect = pygame.Rect(50, 270, 200, 50)
exit_rect = pygame.Rect(50, 330, 200, 50)
input_path_rect = pygame.Rect(25, 50, 450, 25)
input_username_rect = pygame.Rect(25, 100, 450, 25)
english_button_rect = pygame.Rect(25, 150, 150, 30)
ukrainian_button_rect = pygame.Rect(200, 150, 150, 30)
choose_skin_button_rect = pygame.Rect(375, 150, 100, 30)
ram_slider_rect = pygame.Rect(25, 200, 150, 10)

# Початкові налаштування
java_home = ensure_java()
current_language = config["language"]
add_predefined_server(minecraft_directory)
set_minecraft_options(minecraft_directory, current_language, ram_value)

# Основний цикл
clock = pygame.time.Clock()
running = True
left_mouse_pressed = False
ram_dragging = False
just_opened_settings = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            left_mouse_pressed = True

            if play_rect.collidepoint(mouse_pos) and not is_loading and not settings_open:
                update_status("Checking directory...")
                if not check_directory_permissions(input_path_text):
                    error_message = "No permissions to directory!"
                    update_status("Permission error")
                    continue
                if not check_mods_exist():
                    update_status("Downloading mods...")
                    if not download_mods_from_github():
                        update_status("Mods download failed")
                        continue
                else:
                    update_status("Mods already downloaded")
                error_message = None
                is_loading = True
                update_status("Launching game...")
                threading.Thread(target=install_and_launch_forge, args=(input_path_text, minecraft_version, forge_version, {"username": input_username_text, "uuid": "", "access_token": ""}, on_launch_complete, java_home)).start()

            elif settings_rect.collidepoint(mouse_pos) and not is_loading and not settings_open:
                settings_open = True
                just_opened_settings = True

            elif mods_rect.collidepoint(mouse_pos) and not is_loading and not settings_open:
                open_mods_folder()

            elif exit_rect.collidepoint(mouse_pos):
                running = False

            if settings_open and not just_opened_settings and not settings_window_rect.collidepoint(mouse_pos):
                settings_open = False

            if settings_open:
                settings_mouse_pos = (mouse_pos[0] - (WINDOW_WIDTH - SETTINGS_WINDOW_WIDTH) // 2, mouse_pos[1] - (WINDOW_HEIGHT - SETTINGS_WINDOW_HEIGHT) // 2)
                if input_path_rect.collidepoint(settings_mouse_pos):
                    input_path_active = True
                    input_username_active = False
                elif input_username_rect.collidepoint(settings_mouse_pos):
                    input_username_active = True
                    input_path_active = False
                else:
                    input_path_active = False
                    input_username_active = False

                if ram_slider_rect.collidepoint(settings_mouse_pos):
                    ram_dragging = True

                if english_button_rect.collidepoint(settings_mouse_pos):
                    current_language = "en_us"
                    set_minecraft_options(minecraft_directory, current_language, ram_value)
                    save_config(input_path_text, input_username_text, current_language, ram_value, skin_path)

                if ukrainian_button_rect.collidepoint(settings_mouse_pos):
                    current_language = "uk_ua"
                    set_minecraft_options(minecraft_directory, current_language, ram_value)
                    save_config(input_path_text, input_username_text, current_language, ram_value, skin_path)

                if choose_skin_button_rect.collidepoint(settings_mouse_pos):
                    choose_skin()

        elif event.type == pygame.MOUSEBUTTONUP:
            left_mouse_pressed = False
            ram_dragging = False
            just_opened_settings = False

        elif event.type == pygame.MOUSEMOTION and ram_dragging and settings_open:
            settings_mouse_pos = (event.pos[0] - (WINDOW_WIDTH - SETTINGS_WINDOW_WIDTH) // 2, event.pos[1] - (WINDOW_HEIGHT - SETTINGS_WINDOW_HEIGHT) // 2)
            slider_pos = min(max(settings_mouse_pos[0], ram_slider_rect.x), ram_slider_rect.x + ram_slider_rect.width)
            ram_value = int(RAM_MIN + (slider_pos - ram_slider_rect.x) / ram_slider_rect.width * (RAM_MAX - RAM_MIN))
            set_minecraft_options(minecraft_directory, current_language, ram_value)
            save_config(input_path_text, input_username_text, current_language, ram_value, skin_path)

        elif event.type == pygame.KEYDOWN and settings_open:
            if input_path_active:
                if event.key == pygame.K_BACKSPACE:
                    input_path_text = input_path_text[:-1]
                elif event.key == pygame.K_RETURN:
                    input_path_active = False
                    minecraft_directory = input_path_text
                    add_predefined_server(minecraft_directory)
                    set_minecraft_options(minecraft_directory, current_language, ram_value)
                    save_config(input_path_text, input_username_text, current_language, ram_value, skin_path)
                else:
                    input_path_text += event.unicode
            elif input_username_active:
                if event.key == pygame.K_BACKSPACE:
                    input_username_text = input_username_text[:-1]
                elif event.key == pygame.K_RETURN:
                    input_username_active = False
                    save_config(input_path_text, input_username_text, current_language, ram_value, skin_path)
                else:
                    input_username_text += event.unicode
            elif event.key == pygame.K_ESCAPE:
                settings_open = False

    window.fill(WHITE)
    window.blit(cloud_image, (0, -110))

    # Напис
    draw_text("WEB UNIVERSE", title_font, PURPLE, window, 500, 50)
    draw_text("LAUNCHER", title_font, PURPLE, window, 500, 100)

    # Логотипи
    logo_rect = draw_icon_button(logo_icon, 750, 450, 70)
    instagram_rect = draw_icon_button(instagram_icon, 830, 450, 50)
    tiktok_rect = draw_icon_button(tiktok_icon, 890, 450, 50)

    if left_mouse_pressed:
        if instagram_rect.collidepoint(pygame.mouse.get_pos()):
            webbrowser.open("https://www.instagram.com/web.universe.ua/")
        if tiktok_rect.collidepoint(pygame.mouse.get_pos()):
            webbrowser.open("https://www.tiktok.com/@web.universe.ua")
        if logo_rect.collidepoint(pygame.mouse.get_pos()):
            webbrowser.open("https://webuniverseua.com")

    is_play_pressed = play_rect.collidepoint(pygame.mouse.get_pos()) and left_mouse_pressed
    is_settings_pressed = settings_rect.collidepoint(pygame.mouse.get_pos()) and left_mouse_pressed
    is_mods_pressed = mods_rect.collidepoint(pygame.mouse.get_pos()) and left_mouse_pressed
    is_exit_pressed = exit_rect.collidepoint(pygame.mouse.get_pos()) and left_mouse_pressed

    draw_button(play_rect, "PLAY", button_font, WHITE, DARK_PURPLE, rocket_icon, is_play_pressed)
    draw_button(settings_rect, "SETTINGS", button_font, WHITE, DARK_PURPLE, settings_icon, is_settings_pressed)
    draw_button(mods_rect, "MODS", button_font, WHITE, DARK_PURPLE, pressed=is_mods_pressed)
    draw_button(exit_rect, "EXIT", button_font, WHITE, DARK_PURPLE, pressed=is_exit_pressed)

    # Відображаємо статус або помилку
    draw_status_message()

    if settings_open:
        draw_settings_window(pygame.mouse.get_pos(), left_mouse_pressed, ram_dragging)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()