import minecraft_launcher_lib as mll
import subprocess

def generate_launch_command(version, directory, auth_data):
    """Генерує команду для запуску Minecraft."""
    return mll.command.get_minecraft_command(version, directory, auth_data)

def launch_minecraft(command):
    """Запускає Minecraft за допомогою згенерованої команди."""
    subprocess.run(command)
    print("Minecraft запущено!")