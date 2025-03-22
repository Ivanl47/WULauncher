# launcher.py
import minecraft_launcher_lib as mll
import subprocess
import os

def setup_minecraft_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    print(f"Директорія Minecraft: {directory_path}")
    return directory_path

def install_minecraft_version(version, directory):
    try:
        mll.install.install_minecraft_version(version, directory)
        print(f"Версія {version} успішно встановлена.")
    except Exception as e:
        print(f"Помилка при встановленні: {e}")
        raise

def generate_launch_command(version, directory, auth_data):
    return mll.command.get_minecraft_command(version, directory, auth_data)

def launch_minecraft(command):
    subprocess.Popen(command)
    print("Minecraft запущено!")

def launch_minecraft_game(directory, version, auth_data, on_complete):
    directory = setup_minecraft_directory(directory)
    install_minecraft_version(version, directory)
    command = generate_launch_command(version, directory, auth_data)
    launch_minecraft(command)
    on_complete()  # Викликаємо функцію зворотного виклику після завершення