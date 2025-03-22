# java_installer.py
import os
import subprocess
import requests
import zipfile
import platform
import shutil
import sys

def check_java():
    """Перевіряє, чи встановлена Java на комп'ютері."""
    try:
        # Спробуємо виконати команду java -version
        result = subprocess.run(["java", "-version"], capture_output=True, text=True, check=True)
        # Якщо команда успішна, Java встановлена
        print("Java вже встановлена:")
        print(result.stderr)  # java -version виводить інформацію у stderr
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Java не знайдена на комп'ютері.")
        return False

def download_and_install_java(install_dir):
    """
    Завантажує і встановлює Java (Adoptium Temurin) у вказану директорію.
    Повертає шлях до папки з Java (де знаходиться bin/java).
    """
    # Визначаємо архітектуру і ОС
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    if system == "windows":
        if "64" in arch:
            # Для Windows 64-bit
            java_url = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.6%2B7/OpenJDK21U-jdk_x64_windows_hotspot_21.0.6_7.zip"
            java_filename = "OpenJDK21U-jdk_x64_windows_hotspot_21.0.6_7.zip"
        else:
            print("Цей код підтримує лише 64-бітні версії Windows.")
            sys.exit(1)
    elif system == "linux":
        if "64" in arch:
            java_url = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.6%2B7/OpenJDK21U-jdk_x64_linux_hotspot_21.0.6_7.tar.gz"
            java_filename = "OpenJDK21U-jdk_x64_linux_hotspot_21.0.6_7.tar.gz"
        else:
            print("Цей код підтримує лише 64-бітні версії Linux.")
            sys.exit(1)
    elif system == "darwin":  # macOS
        if "arm" in arch:
            java_url = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.6%2B7/OpenJDK21U-jdk_aarch64_mac_hotspot_21.0.6_7.tar.gz"
            java_filename = "OpenJDK21U-jdk_aarch64_mac_hotspot_21.0.6_7.tar.gz"
        else:
            java_url = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.6%2B7/OpenJDK21U-jdk_x64_mac_hotspot_21.0.6_7.tar.gz"
            java_filename = "OpenJDK21U-jdk_x64_mac_hotspot_21.0.6_7.tar.gz"
    else:
        print(f"Операційна система {system} не підтримується.")
        sys.exit(1)

    # Створюємо директорію для Java, якщо її немає
    os.makedirs(install_dir, exist_ok=True)
    java_zip_path = os.path.join(install_dir, java_filename)

    # Завантажуємо Java
    print(f"Завантажуємо Java з {java_url}...")
    response = requests.get(java_url, stream=True)
    with open(java_zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print(f"Java завантажено: {java_zip_path}")

    # Розпаковуємо архів
    print("Розпаковуємо Java...")
    if java_filename.endswith(".zip"):
        with zipfile.ZipFile(java_zip_path, "r") as zip_ref:
            zip_ref.extractall(install_dir)
    elif java_filename.endswith(".tar.gz"):
        import tarfile
        with tarfile.open(java_zip_path, "r:gz") as tar_ref:
            tar_ref.extractall(install_dir)
    print("Java розпаковано.")

    # Видаляємо завантажений архів
    os.remove(java_zip_path)

    # Знаходимо папку з Java (наприклад, jdk-21.0.6+7)
    java_home = None
    for item in os.listdir(install_dir):
        item_path = os.path.join(install_dir, item)
        if os.path.isdir(item_path) and "jdk" in item.lower():
            java_home = item_path
            break

    if not java_home:
        print("Не вдалося знайти папку з Java після розпакування.")
        sys.exit(1)

    # Перевіряємо, чи працює Java
    java_bin = os.path.join(java_home, "bin", "java")
    if system == "windows":
        java_bin += ".exe"
    try:
        result = subprocess.run([java_bin, "-version"], capture_output=True, text=True, check=True)
        print("Java успішно встановлена:")
        print(result.stderr)
        return java_home
    except subprocess.CalledProcessError as e:
        print(f"Помилка при перевірці Java: {e}")
        sys.exit(1)

def ensure_java():
    """
    Перевіряє наявність Java і встановлює її, якщо вона відсутня.
    Повертає шлях до Java (JAVA_HOME) або None, якщо використовується системна Java.
    """
    # Перевіряємо, чи Java вже встановлена
    if check_java():
        return None  # Використовуємо системну Java

    # Визначаємо директорію для встановлення Java
    install_dir = os.path.join(os.path.expanduser("~"), "custom_java")
    print(f"Java буде встановлена в {install_dir}")

    # Завантажуємо і встановлюємо Java
    java_home = download_and_install_java(install_dir)
    return java_home

if __name__ == "__main__":
    java_home = ensure_java()
    if java_home:
        print(f"Java встановлена в: {java_home}")
    else:
        print("Використовується системна Java.")