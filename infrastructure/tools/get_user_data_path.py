from sys import platform as sys_platform
from os import environ as os_env
from pathlib import Path


def get_user_data_path(app_name: str) -> Path:
    """
    Получаем путь к пользовательской папке для данных приложения.
    Гарантированно возвращает существующую директорию или создаёт её.
    """
    # Определяем базовую директорию в зависимости от ОС
    if sys_platform == "win32" or sys_platform == "win64":
        app_data = os_env.get("APPDATA")
        if not app_data:
            # Резервный вариант для Windows
            base = Path.home() / "AppData" / "Roaming"
        else:
            base = Path(app_data)
    elif sys_platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:  # Linux и другие Unix-системы
        # Используем XDG_DATA_HOME, если задан, иначе ~/.local/share
        xdg_data_home = os_env.get("XDG_DATA_HOME")
        if xdg_data_home:
            base = Path(xdg_data_home)
        else:
            base = Path.home() / ".local" / "share"

    # Формируем полный путь
    data_path = base / app_name

    # Создаём директорию с родительскими папками, если нужно
    data_path.mkdir(parents=True, exist_ok=True)
    return data_path