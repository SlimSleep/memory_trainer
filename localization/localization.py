# modules/ui/localization.py
import json

class Localizer:
    def __init__(self, lang='ru'):
        self.lang = lang
        self.strings = {}
        self._observers = set()
        self.load_lang(lang)

    def register_observer(self, callback):
        if callable(callback):
            self._observers.add(callback)

    def unregister_observer(self, callback):
        self._observers.discard(callback)

    def _notify_observers(self):
        for callback in list(self._observers):
            try:
                callback()
            except Exception:
                pass

    def load_lang(self, lang):
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
        return self.strings.get(key, key) #возвращает строку по ключу, если ключ не найден, возвращает сам ключ

    def switch_lang(self, lang): #метод для переключения языка, принимает новый язык, загружает строки для этого языка и обновляет текущий язык
        self.lang = lang
        self.load_lang(lang)
        self._notify_observers() #уведомляем всех наблюдателей об изменении языка, чтобы они могли обновить отображаемый текст