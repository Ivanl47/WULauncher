import minecraft_launcher_lib as mll
import os

def setup_minecraft_directory(directory_path):
    """Налаштовує директорію Minecraft і створює її, якщо не існує."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    print(f"Директорія Minecraft: {directory_path}")
    return directory_path

def install_minecraft_version(version, directory, retry_on_error=True):
    """Встановлює задану версію Minecraft з обробкою помилок."""
    try:
        mll.install.install_minecraft_version(version, directory)
        print(f"Версія {version} успішно встановлена.")
    except mll.exceptions.InvalidChecksum as e:
        print(f"Помилка контрольної суми: {e}")
        if os.path.exists(e.path):
            os.remove(e.path)
            print(f"Видалено пошкоджений файл: {e.path}")
        if retry_on_error:
            print("Повторна спроба завантаження...")
            mll.install.install_minecraft_version(version, directory)
    except Exception as e:
        print(f"Інша помилка: {e}")
        raise