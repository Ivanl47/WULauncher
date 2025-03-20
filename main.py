 import minecraft_launcher_lib as mll
import subprocess
import os

# Minecraft directory
minecraft_directory = r"D:\Desktop\майкнрафт"
print(f"Директорія Minecraft: {minecraft_directory}")

# Game version
version = "1.20.1"

# Install the game files with error handling
try:
    mll.install.install_minecraft_version(version, minecraft_directory)
except mll.exceptions.InvalidChecksum as e:
    print(f"Помилка контрольної суми: {e}")
    # Remove the corrupted file
    if os.path.exists(e.path):
        os.remove(e.path)
        print(f"Видалено пошкоджений файл: {e.path}")
    # Retry installation
    print("Повторна спроба завантаження...")
    mll.install.install_minecraft_version(version, minecraft_directory)
except Exception as e:
    print(f"Інша помилка: {e}")

# Fake auth data for offline mode
fake_auth = {
    "username": "PirateMotherfucker",  # Your pirate username
    "uuid": "",  # Empty UUID for offline mode
    "access_token": ""  # Empty token for offline mode
}

# Get the command to launch Minecraft
command = mll.command.get_minecraft_command(version, minecraft_directory, fake_auth)

# Launch the game using subprocess
subprocess.run(command)
