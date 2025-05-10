import pygame
import sys
import webbrowser

# Ініціалізація Pygame
pygame.init()

# Налаштування вікна
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("WEB UNIVERSE LAUNCHER")

# Кольори
WHITE = (255, 255, 255)
PURPLE = (147, 112, 219)  # Фіолетовий для кнопок, хмари і центрального тексту
PINK = (255, 182, 193)    # Рожевий (більше не використовується для тексту)
DARK_PURPLE = (75, 0, 130)  # Темно-фіолетовий для тексту профілю

# Завантаження шрифту
font_path = "source/fonts/Minecraft.ttf"  # Шлях до вашого шрифту
title_font = pygame.font.Font(font_path, 100)  # Розмір для заголовка
button_font = pygame.font.Font(font_path, 60)  # Збільшений розмір для кнопок
profile_font = pygame.font.Font(font_path, 40)  # Збільшений розмір для тексту профілю

# Функція для створення тексту
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# Функція для створення кнопки
def draw_button(text, font, x, y, width, height, color, text_color, icon=None):
    button_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(window, color, button_rect, border_radius=15)
    draw_text(text, font, text_color, window, x + 40, y + 20)  # Зміщені координати тексту для більших кнопок
    if icon:
        # Зберігаємо пропорції іконки
        icon_width = 50
        icon_height = int(icon_width * (icon.get_height() / icon.get_width()))  # Зберігаємо співвідношення
        icon = pygame.transform.scale(icon, (icon_width, icon_height))
        window.blit(icon, (x + width - 70, y + 15))  # Іконка праворуч
    return button_rect

# Функція для створення кнопки-іконки (для соцмереж)
def draw_icon_button(icon, x, y, target_width):
    # Зберігаємо пропорції іконки
    icon_width = target_width
    icon_height = int(icon_width * (icon.get_height() / icon.get_width()))  # Зберігаємо співвідношення
    icon = pygame.transform.scale(icon, (icon_width, icon_height))
    icon_rect = pygame.Rect(x, y, icon_width, icon_height)
    window.blit(icon, (x, y))
    return icon_rect

# Завантаження зображень
cloud_image = pygame.image.load("source/images/cloud.png")
rocket_icon = pygame.image.load("source/images/WU_rocket.png")
settings_icon = pygame.image.load("source/images/WU_space.png")
logo_icon = pygame.image.load("source/images/WU_logo.png")
instagram_icon = pygame.image.load("source/images/WU_instagram.png")
tiktok_icon = pygame.image.load("source/images/WU_tiktok.png")
profile_icon = pygame.image.load("source/images/WU_planet.png")

# Зміна розміру хмари (збільшення на 20%)
base_height = WINDOW_HEIGHT  # Базова висота
scale_factor = 1.2  # Збільшення на 20%
new_height = int(base_height * scale_factor)
new_width = int(cloud_image.get_width() * (new_height / cloud_image.get_height()))
cloud_image = pygame.transform.scale(cloud_image, (new_width, new_height))

# Зберігаємо пропорції іконки профілю
profile_icon_width = 40
profile_icon_height = int(profile_icon_width * (profile_icon.get_height() / profile_icon.get_width()))
profile_icon = pygame.transform.scale(profile_icon, (profile_icon_width, profile_icon_height))

# Основний цикл програми
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            # Перевірка натискання на кнопки
            if play_button.collidepoint(mouse_pos):
                print("PLAY button clicked!")
            elif settings_button.collidepoint(mouse_pos):
                print("settings button clicked!")
            elif mods_button.collidepoint(mouse_pos):
                print("mods button clicked!")
            elif exit_button.collidepoint(mouse_pos):
                running = False
            elif profile_button.collidepoint(mouse_pos):  # Обробка натискання на профіль
                print("Profile button clicked!")
            # Перевірка натискання на іконки соцмереж
            elif logo_button.collidepoint(mouse_pos):
                webbrowser.open("https://webuniverseua.com/showend")
            elif instagram_button.collidepoint(mouse_pos):
                webbrowser.open("https://www.instagram.com/web.universe.ua/")
            elif tiktok_button.collidepoint(mouse_pos):
                webbrowser.open("https://www.tiktok.com/@web.universe.ua")

    # Очистка екрану
    window.fill(WHITE)

    # Малювання хмари
    window.blit(cloud_image, (0, 0))  # Хмара на всю висоту (збільшена)

    # Малювання заголовка (колір змінено на PURPLE)
    draw_text("WEB UNIVERSE", title_font, PURPLE, window, 800, 150)
    draw_text("LAUNCHER", title_font, PURPLE, window, 800, 260)

    # Малювання кнопок (змінили колір тексту на білий)
    play_button = draw_button("PLAY", button_font, 100, 300, 400, 100, PURPLE, WHITE, rocket_icon)
    settings_button = draw_button("settings", button_font, 100, 420, 400, 100, PURPLE, WHITE, settings_icon)
    mods_button = draw_button("mods", button_font, 100, 540, 400, 100, PURPLE, WHITE)
    exit_button = draw_button("exit", button_font, 100, 660, 400, 100, PURPLE, WHITE)

    # Малювання профілю у правому верхньому куті (збільшена кнопка)
    profile_button = pygame.Rect(WINDOW_WIDTH - 280, 30, 250, 60)  # Збільшена плашка
    pygame.draw.rect(window, PURPLE, profile_button, border_radius=10)
    draw_text("profile", profile_font, DARK_PURPLE, window, WINDOW_WIDTH - 270, 40)  # Зміщений текст
    window.blit(profile_icon, (WINDOW_WIDTH - 110, 40))  # Іконка планети лівіше, ближче до тексту

    # Малювання логотипу та іконок соцмереж у правому нижньому куті (збалансовані відступи)
    logo_button = draw_icon_button(logo_icon, WINDOW_WIDTH - 475, WINDOW_HEIGHT - 150, 125)  # Логотип
    instagram_button = draw_icon_button(instagram_icon, WINDOW_WIDTH - 300, WINDOW_HEIGHT - 150, 80)  # Іконка Instagram
    tiktok_button = draw_icon_button(tiktok_icon, WINDOW_WIDTH - 190, WINDOW_HEIGHT - 150, 80)  # Іконка TikTok

    # Оновлення екрану
    pygame.display.flip()

# Завершення програми
pygame.quit()
sys.exit()