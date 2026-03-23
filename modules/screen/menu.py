import pygame
from modules.ui.button import Button
 

class MenuScreen:
    """
    Класс для экрана главного меню.
    Отображает кнопки для начала игры, настроек и выхода.
    Управляет переходами между экранами.
    """
    def __init__(self, manager, loc, font):
        """
        Инициализация меню.
        
        :param manager: ScreenManager для управления экранами
        :param loc: Localizer для перевода
        :param font: шрифт для кнопок
        """
        self.manager = manager
        self.loc = loc
        self.font = font
        self.buttons = []

        # Создаём кнопки с локализованным текстом
        self.start_btn = Button(300, 200, 200, 50, font=font, text_key="start_game", localizer=self.loc,
                                callback=self.start_game)
        self.settings_btn = Button(300, 270, 200, 50, font=font, text_key="settings", localizer=self.loc,
                                   callback=self.open_settings)
        self.exit_btn = Button(300, 340, 200, 50, font=font, text_key="exit", localizer=self.loc,
                               callback=self.exit_game)
        self.buttons = [self.start_btn, self.settings_btn, self.exit_btn]

    def on_enter(self):
        """Вызывается при входе на экран (пока пусто)."""
        pass

    def handle_event(self, event):
        """
        Обрабатывает события для всех кнопок.
        
        :param event: событие Pygame
        """
        for btn in self.buttons:
            btn.handle_event(event)

    def draw(self, screen):
        """
        Отрисовывает экран: фон и кнопки.
        
        :param screen: поверхность для рисования
        """
        # Очистка экрана (можно фон)
        screen.fill((255,255,255))
        for btn in self.buttons:
            btn.draw(screen)

    def update(self):
        """Обновляет логику экрана (пока пусто)."""
        pass

    def start_game(self):
        """Переход к выбору игры."""
        # Переключиться на экран выбора игры
        self.manager.set_screen("game_choice")

    def open_settings(self):
        """Переход к настройкам."""
        self.manager.set_screen("settings")

    def exit_game(self):
        """Выход из приложения."""
        pygame.quit()
        exit()