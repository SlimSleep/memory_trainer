# Конфигурационный файл для настроек приложения
# Содержит параметры окна, UI элементов, шрифтов и производительности

import os

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
COLOR_BG = (240, 242, 245)  # Светлый фон по умолчанию
MATCH_PAIRS_COLORS = [
    (255, 179, 186),
    (255, 223, 186),
    (255, 255, 186),
    (186, 255, 201),
    (186, 225, 255),
    (201, 186, 255),
    (255, 186, 255),
    (186, 255, 255),
    (255, 210, 218),
    (210, 255, 214),
]

# ============================================================================
# UI ЭЛЕМЕНТЫ - РАЗМЕРЫ
# ============================================================================
# Кнопки
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_SPACING = 20  # Расстояние между кнопками

# Текстовые поля
TEXTBOX_WIDTH = 300
TEXTBOX_HEIGHT = 40

# Слайдеры
SLIDER_WIDTH = 300
SLIDER_HEIGHT = 20

# ============================================================================
# ШРИФТЫ
# ============================================================================
FONT_SIZE_SMALL = 24
FONT_SIZE_NORMAL = 36
FONT_SIZE_LARGE = 48
FONT_SIZE_TITLE = 64

# None = использовать встроенный шрифт системы
FONT_NAME = None

# ============================================================================
# ПУТИ К РЕСУРСАМ
# ============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')
BUTTON_CLICK_SOUND = os.path.join(SOUNDS_DIR, 'Menu_buttons.wav')
MATCH_PAIRS_WRONG_SOUND = os.path.join(SOUNDS_DIR, 'Wrong.wav')
MATCH_PAIRS_VICTORY_SOUND = os.path.join(SOUNDS_DIR, 'Victory.mp3')
DEFAULT_AUDIO_VOLUME = 0.5
DEFAULT_VOLUME_PERCENT = 25
DEFAULT_SFX_VOLUME_PERCENT = 25
DEFAULT_BG_VOLUME_PERCENT = 25
BACKGROUND_MUSIC_PATH = os.path.join(SOUNDS_DIR, 'background.mp3')
AUDIO_DIR = os.path.join(BASE_DIR, 'audio')
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOCALIZATION_DIR = os.path.join(BASE_DIR, 'localization')

# ============================================================================
# ЛОКАЛИЗАЦИЯ
# ============================================================================
DEFAULT_LANGUAGE = 'ru'
SUPPORTED_LANGUAGES = ['ru', 'en']

# ============================================================================
# БД И ХРАНИЛИЩЕ
# ============================================================================
DB_PATH = os.path.join(DATA_DIR, 'users.db')
SETTINGS_PATH = os.path.join(DATA_DIR, 'settings.json')

# ============================================================================
# ИГРЫ - ПАРАМЕТРЫ СЛОЖНОСТИ
# ============================================================================
# MatchPairs
MATCH_PAIRS_LEVELS = {
    1: {'rows': 3, 'cols': 4, 'time_limit': None},
    2: {'rows': 4, 'cols': 4, 'time_limit': None},
    3: {'rows': 5, 'cols': 4, 'time_limit': None},
}

# Sequence
SEQUENCE_START_LENGTH = 3
SEQUENCE_MAX_LENGTH = 20
SEQUENCE_BUTTON_COUNT = 4
