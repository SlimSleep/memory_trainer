# Конфигурационный файл для настроек приложения
# Содержит параметры окна, UI элементов, шрифтов и производительности

import os
import sys

# ============================================================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С ПУТЯМИ (поддержка exe)
# ============================================================================

def resource_path(relative_path):
    """
    Путь к ресурсам внутри exe (только для чтения).
    Для разработки - из папки проекта.
    Для exe - из временной папки _MEIPASS.
    """
    try:
        # PyInstaller создаёт временную папку _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Запущено как скрипт - берём из папки проекта
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)


def data_path(relative_path):
    """
    Путь к данным, которые нужно сохранять (БД, настройки).
    Всегда сохраняет рядом с exe файлом или в папке проекта.
    """
    if getattr(sys, 'frozen', False):
        # Запущено как exe - сохраняем рядом с exe
        base_path = os.path.dirname(sys.executable)
    else:
        # Запущено как скрипт - сохраняем в папке проекта
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)


# ============================================================================
# ОКНО ПРИЛОЖЕНИЯ
# ============================================================================
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
WINDOW_TITLE = "Тренажёр памяти"
FPS = 60

# ============================================================================
# ЦВЕТА (RGB)
# ============================================================================
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY_LIGHT = (220, 220, 220)
COLOR_GRAY = (200, 200, 200)
COLOR_GRAY_DARK = (180, 180, 180)
COLOR_BLUE_LIGHT = (200, 200, 255)
COLOR_BLUE = (100, 150, 255)
COLOR_RED = (255, 100, 100)
COLOR_GREEN = (100, 255, 100)
COLOR_YELLOW = (255, 255, 100)
COLOR_BG = (240, 242, 245)
MATCH_PAIRS_COLORS = [
    (255, 179, 186), (255, 223, 186), (255, 255, 186),
    (186, 255, 201), (186, 225, 255), (201, 186, 255),
    (255, 186, 255), (186, 255, 255), (255, 210, 218), (210, 255, 214),
]

# ============================================================================
# UI ЭЛЕМЕНТЫ - РАЗМЕРЫ
# ============================================================================
BUTTON_WIDTH = 260
BUTTON_HEIGHT = 50
BUTTON_SPACING = 20
TEXTBOX_WIDTH = 300
TEXTBOX_HEIGHT = 40
SLIDER_WIDTH = 300
SLIDER_HEIGHT = 20

# ============================================================================
# ШРИФТЫ
# ============================================================================
FONT_SIZE_SMALL = 24
FONT_SIZE_NORMAL = 36
FONT_SIZE_LARGE = 48
FONT_SIZE_TITLE = 64
FONT_NAME = None

# ============================================================================
# ПУТИ К РЕСУРСАМ
# ============================================================================
# Определяем базовую папку проекта для разработки
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Для exe используем resource_path, для разработки - BASE_DIR
if getattr(sys, 'frozen', False):
    ASSETS_DIR = resource_path('assets')
    LOCALIZATION_DIR = resource_path('localization')
else:
    ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
    LOCALIZATION_DIR = os.path.join(BASE_DIR, 'localization')

FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')

# Звуки
BUTTON_CLICK_SOUND = os.path.join(SOUNDS_DIR, 'Menu_buttons.wav')
MATCH_PAIRS_WRONG_SOUND = os.path.join(SOUNDS_DIR, 'Wrong.wav')
MATCH_PAIRS_VICTORY_SOUND = os.path.join(SOUNDS_DIR, 'Victory.mp3')
BACKGROUND_MUSIC_PATH = os.path.join(SOUNDS_DIR, 'background.mp3')
SEQUENCE_CORRECT_SOUND = os.path.join(SOUNDS_DIR, 'Correct.wav')
SEQUENCE_WRONG_SOUND = os.path.join(SOUNDS_DIR, 'Wrong.wav')
SEQUENCE_BUTTON_SOUND = os.path.join(SOUNDS_DIR, 'cards_Match_pairs.mp3')

# ============================================================================
# ПУТИ К ДАННЫМ (рядом с exe - для сохранения)
# ============================================================================
DATA_DIR = data_path('data')
DB_PATH = data_path('data/users.db')
SETTINGS_PATH = data_path('data/settings.json')

# ============================================================================
# ЗВУКИ - ГРОМКОСТЬ
# ============================================================================
DEFAULT_AUDIO_VOLUME = 0.5
DEFAULT_VOLUME_PERCENT = 25
DEFAULT_SFX_VOLUME_PERCENT = 25
DEFAULT_BG_VOLUME_PERCENT = 10

# ============================================================================
# ЛОКАЛИЗАЦИЯ
# ============================================================================
DEFAULT_LANGUAGE = 'ru'
SUPPORTED_LANGUAGES = ['ru', 'en']

# ============================================================================
# ИГРЫ - ПАРАМЕТРЫ СЛОЖНОСТИ
# ============================================================================
MATCH_PAIRS_LEVELS = {
    1: {'rows': 3, 'cols': 4, 'time_limit': None},
    2: {'rows': 4, 'cols': 4, 'time_limit': None},
    3: {'rows': 5, 'cols': 4, 'time_limit': None},
}

SEQUENCE_START_LENGTH = 3
SEQUENCE_MAX_LENGTH = 20
SEQUENCE_BUTTON_COUNT = 4

# Для отладки - выводим пути при запуске (можно удалить после проверки)
if __name__ == "__main__":
    print(f"frozen: {getattr(sys, 'frozen', False)}")
    print(f"ASSETS_DIR: {ASSETS_DIR}")
    print(f"LOCALIZATION_DIR: {LOCALIZATION_DIR}")
    print(f"SOUNDS_DIR: {SOUNDS_DIR}")
    print(f"DATA_DIR: {DATA_DIR}")
