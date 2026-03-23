# modules/ui/localization.py
import json

class Localizer:
    """
    Класс для управления локализацией текста в приложении.
    Поддерживает переключение языков, загрузку строк из словаря,
    уведомление наблюдателей (UI элементов) при смене языка.
    """
    def __init__(self, lang='ru'):
        """
        Инициализация локализатора.
        
        :param lang: начальный язык ('ru' или 'en')
        """
        self.lang = lang
        self.strings = {}
        self._observers = set()  # Наблюдатели (UI элементы, подписанные на обновления)
        self.load_lang(lang)

    def register_observer(self, callback):
        """
        Регистрирует наблюдателя (функцию обратного вызова).
        
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
            except Exception:
                pass

    def load_lang(self, lang):
        """
        Загружает строки для указанного языка.
        Пока использует заглушку с словарями, в будущем можно загрузить из JSON.
        
        :param lang: язык для загрузки
        """
        # Загружаем из JSON-файла
        # Пока заглушка
        if lang == 'ru':
            self.strings = {
                "menu_title": "Тренажёр памяти",
                "start_game": "Начать игру",
                "settings": "Настройки",
                "exit": "Выход"
            }
        else:
            self.strings = {
                "menu_title": "Memory Trainer",
                "start_game": "Start Game",
                "settings": "Settings",
                "exit": "Exit"
            }

    def get(self, key):
        """
        Возвращает переведённую строку по ключу.
        Если ключ не найден, возвращает сам ключ.
        
        :param key: ключ строки
        :return: переведённая строка
        """
        return self.strings.get(key, key) #возвращает строку по ключу, если ключ не найден, возвращает сам ключ

    def switch_lang(self, lang): #метод для переключения языка, принимает новый язык, загружает строки для этого языка и обновляет текущий язык
        """
        Переключает язык, загружает новые строки и уведомляет наблюдателей.
        
        :param lang: новый язык
        """
        self.lang = lang
        self.load_lang(lang)
        self._notify_observers() #уведомляем всех наблюдателей об изменении языка, чтобы они могли обновить отображаемый текст