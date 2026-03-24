# Конфигурационный файл для настроек приложения
# Содержит параметры окна, UI элементов, шрифтов и производительности

import os
import pygame

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

# При возможности использовать шрифты из assets/fonts/
# Если нет — используются системные шрифты
FONT_NAME = None  # None = использовать встроенный шрифт система

# ============================================================================
# ПУТИ К РЕСУРСАМ
# ============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')
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
DATABASE_PATH = os.path.join(DATA_DIR, 'users.db')
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

# Sequence (Simon Says)
SEQUENCE_START_LENGTH = 3
SEQUENCE_MAX_LENGTH = 20
SEQUENCE_BUTTON_COUNT = 4

# Digits
DIGITS_LEVELS = {
    1: {'length': 5, 'time_limit': 10},
    2: {'length': 7, 'time_limit': 15},
    3: {'length': 9, 'time_limit': 20},
}
