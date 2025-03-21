from minecraft_setup import setup_minecraft_directory, install_minecraft_version
from minecraft_launcher import generate_launch_command, launch_minecraft

def main():
    # Параметри
    minecraft_directory = r"D:\Desktop\май"
    version = "1.20.1"
    fake_auth = {
        "username": "PirateMotherfucker",
        "uuid": "",
        "access_token": ""
    }

    # Виконання
    directory = setup_minecraft_directory(minecraft_directory)
    install_minecraft_version(version, directory)
    command = generate_launch_command(version, directory, fake_auth)
    launch_minecraft(command)

if __name__ == "__main__":
    main()