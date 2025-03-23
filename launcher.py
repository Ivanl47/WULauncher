# launcher.py
import minecraft_launcher_lib as mll
import subprocess
import os

def setup_minecraft_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    print(f"Директорія Minecraft: {directory_path}")
    return directory_path

def install_minecraft_version(version, directory, java_home=None):
    try:
        # Перевіряємо, чи Minecraft уже встановлено
        installed_versions = mll.utils.get_installed_versions(directory)
        if not any(v["id"] == version for v in installed_versions):
            mll.install.install_minecraft_version(version, directory)
            print(f"Версія Minecraft {version} успішно встановлена.")
        else:
            print(f"Версія Minecraft {version} уже встановлена.")
    except Exception as e:
        print(f"Помилка при встановленні Minecraft: {e}")
        raise

def install_forge_version(forge_version, directory, minecraft_version, java_home=None):
    try:
        # Перевіряємо, чи Forge уже встановлено
        installed_versions = mll.utils.get_installed_versions(directory)
        forge_full_version = f"{minecraft_version}-forge-{forge_version.split('-')[1]}"  # Наприклад, "1.20.1-forge-47.3.0"
        if not any(v["id"] == forge_full_version for v in installed_versions):
            # Перевіряємо доступні версії Forge
            available_forge_versions = mll.forge.list_forge_versions()
            if forge_version not in available_forge_versions:
                raise ValueError(f"Forge версія {forge_version} недоступна. Доступні версії: {available_forge_versions[:10]} (перші 10)")
            print(f"Починаємо встановлення Forge {forge_version}...")
            mll.forge.install_forge_version(forge_version, directory)
            print(f"Forge {forge_version} успішно встановлено.")
        else:
            print(f"Forge {forge_version} уже встановлено.")
        # Перевіряємо, чи з’явився профіль
        installed_versions = mll.utils.get_installed_versions(directory)
        print(f"Встановлені версії після перевірки Forge: {installed_versions}")
    except Exception as e:
        print(f"Помилка при встановленні Forge: {e}")
        raise

def generate_launch_command(forge_version, directory, auth_data, java_home=None):
    # Визначаємо шлях до Java
    java_bin = "java"
    if java_home:
        java_bin = os.path.join(java_home, "bin", "java")
        if os.name == "nt":  # Для Windows
            java_bin += ".exe"

    # Спробуємо знайти повну назву Forge-версії
    forge_full_version = mll.forge.find_forge_version(forge_version)
    if forge_full_version is None:
        # Якщо find_forge_version не спрацював, шукаємо вручну за номером версії Forge
        installed_versions = mll.utils.get_installed_versions(directory)
        forge_short_version = forge_version.split('-')[1]  # Отримуємо "47.3.0" із "1.20.1-47.3.0"
        forge_full_version = next((v["id"] for v in installed_versions if "forge" in v["id"] and forge_short_version in v["id"]), None)
        if forge_full_version is None:
            print(f"Встановлені версії в {directory}: {installed_versions}")
            raise ValueError(f"Forge версія {forge_version} не знайдена після встановлення")
    print(f"Використовується Forge версія: {forge_full_version}")

    # Об’єднуємо auth_data і java_binary в один словник options
    options = {
        "username": auth_data["username"],
        "uuid": auth_data["uuid"],
        "access_token": auth_data["access_token"],
        "java_binary": java_bin
    }
    return mll.command.get_minecraft_command(forge_full_version, directory, options)

def launch_minecraft(command):
    try:
        subprocess.Popen(command)
        print("Minecraft запущено!")
    except Exception as e:
        print(f"Помилка при запуску Minecraft: {e}")
        raise

def install_and_launch_forge(directory, minecraft_version, forge_version, auth_data, on_complete_callback=None, java_home=None):
    directory = setup_minecraft_directory(directory)
    install_minecraft_version(minecraft_version, directory, java_home)
    install_forge_version(forge_version, directory, minecraft_version, java_home)
    command = generate_launch_command(forge_version, directory, auth_data, java_home)
    launch_minecraft(command)
    if on_complete_callback:
        on_complete_callback(True, "Minecraft запущено успішно.")