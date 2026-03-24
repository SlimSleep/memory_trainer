# localization/localization.py
import json
import os
from pathlib import Path


# Встроенные значения по умолчанию для резервного использования
FALLBACK_STRINGS = {
    'ru': {
        "menu_title": "Тренажёр памяти",
        "start_game": "Начать игру",
        "settings": "Настройки",
        "exit": "Выход",
        "match_pairs": "Найди пару",
        "sequence": "Запомни последовательность",
        "digits": "Повтори цифры",
        "difficulty": "Сложность",
        "score": "Очки",
        "time": "Время",
        "level": "Уровень",
        "pause": "Пауза",
        "resume": "Продолжить",
        "back": "Назад",
        "language": "Язык",
        "english": "English",
        "russian": "Русский",
    },
    'en': {
        "menu_title": "Memory Trainer",
        "start_game": "Start Game",
        "settings": "Settings",
        "exit": "Exit",
        "match_pairs": "Match Pairs",
        "sequence": "Sequence",
        "digits": "Digits",
        "difficulty": "Difficulty",
        "score": "Score",
        "time": "Time",
        "level": "Level",
        "pause": "Pause",
        "resume": "Resume",
        "back": "Back",
        "language": "Language",
        "english": "English",
        "russian": "Russian",
    }
}


class Localizer:
    """
    Класс для управления локализацией текста в приложении.
    Поддерживает переключение языков, загрузку строк из JSON-файлов,
    уведомление наблюдателей (UI элементов) при смене языка,
    а также использование встроенных значений в качестве резерва.
    """
    def __init__(self, lang='ru', localization_dir=None):
        """
        Инициализация локализатора.
        
        :param lang: начальный язык ('ru' или 'en')
        :param localization_dir: путь к директории с JSON-файлами локализации
        """
        self.lang = lang
        self.strings = {}
        self._observers = set()  # Наблюдатели (UI элементы, подписанные на обновления)
        
        # Определяем директорию локализации
        if localization_dir is None:
            # По умолчанию используем директорию рядом с этим файлом
            localization_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.localization_dir = localization_dir
        self.load_lang(lang)

    def register_observer(self, callback):
        """
        Регистрирует наблюдателя (функцию обратного вызова).
        Наблюдатель будет уведомлён при смене языка.
        
        :param callback: функция, вызываемая при смене языка
        """
        if callable(callback):
            self._observers.add(callback)

    def unregister_observer(self, callback):
        """
        Удаляет наблюдателя.
        
        :param callback: функция для удаления
        """
        self._observers.discard(callback)

    def _notify_observers(self):
        """
        Уведомляет всех наблюдателей о смене языка.
        Вызывает их функции обновления.
        """
        for callback in list(self._observers):
            try:
                callback()
            except Exception as e:
                print(f"Ошибка при уведомлении наблюдателя: {e}")

    def load_lang(self, lang):
        """
        Загружает строки для указанного языка из JSON-файла.
        Если файл не найден, использует встроенные значения.
        
        :param lang: язык для загрузки ('ru' или 'en')
        """
        json_file = os.path.join(self.localization_dir, f"{lang}.json")
        
        # Сначала используем встроенные значения
        self.strings = FALLBACK_STRINGS.get(lang, FALLBACK_STRINGS['en']).copy()
        
        # Пытаемся загрузить из JSON
        try:
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    loaded_strings = json.load(f)
                    # Объединяем загруженные значения со встроенными (загруженные приоритетнее)
                    self.strings.update(loaded_strings)
                    print(f"✓ Локализация загружена: {json_file}")
            else:
                print(f"⚠ Файл локализации не найден: {json_file}, используются встроенные значения")
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠ Ошибка загрузки локализации из {json_file}: {e}")
            print(f"  Используются встроенные значения для языка: {lang}")

    def get(self, key):
        """
        Возвращает переведённую строку по ключу.
        Если ключ не найден, возвращает сам ключ.
        
        :param key: ключ строки
        :return: переведённая строка
        """
        return self.strings.get(key, key)

    def switch_lang(self, lang):
        """
        Переключает язык, загружает новые строки и уведомляет наблюдателей.
        
        :param lang: новый язык
        """
        if lang in ('ru', 'en'):
            self.lang = lang
            self.load_lang(lang)
            self._notify_observers()
        else:
            print(f"⚠ Неизвестный язык: {lang}. Поддерживаемые языки: ru, en")

    def get_lang(self):
        """Возвращает текущий выбранный язык."""
        return self.lang

    def get_available_languages(self):
        """Возвращает список доступных языков."""
        return list(FALLBACK_STRINGS.keys())