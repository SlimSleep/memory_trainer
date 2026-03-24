"""
Экран главного меню приложения.
Демонстрирует использование UI элементов (Button, Label, Slider).
"""

import pygame
from modules.ui.screen import Screen
from modules.ui.button import Button
from modules.ui.label import Label
from modules.ui.slider import Slider
import config


class MenuScreen(Screen):
    """
    Главное меню с кнопками для запуска игр, настроек и выхода.
    """
    
    def __init__(self, manager, localizer, font_normal, font_large):
        """
        Инициализация экрана меню.
        
        :param manager: ScreenManager
        :param localizer: Localizer для локализации
        :param font_normal: шрифт для обычного текста
        :param font_large: шрифт для заголовка
        """
        super().__init__(manager, localizer, font_normal)
        self.font_large = font_large
        self.bg_color = config.COLOR_BG
        
        # Создаём элементы UI
        self.title = None
        self.buttons = []
        self.language_slider = None
        self.language_label = None
        
        self.create_ui()

    def create_ui(self):
        """Создаёт все UI элементы меню."""
        screen_width = self.manager.screen.get_width()
        screen_height = self.manager.screen.get_height()
        
        # Заголовок
        self.title = Label(
            x=screen_width // 2,
            y=80,
            text_key="menu_title",
            font=self.font_large,
            color=config.COLOR_BLACK,
            center=True,
            localizer=self.loc
        )
        
        # Кнопка "Начать игру"
        start_btn = Button(
            x=screen_width // 2 - config.BUTTON_WIDTH // 2,
            y=200,
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            font=self.font,
            text_color=config.COLOR_BLACK,
            text_key="start_game",
            callback=self.on_start_game,
            localizer=self.loc
        )
        self.buttons.append(start_btn)
        
        # Кнопка "Настройки"
        settings_btn = Button(
            x=screen_width // 2 - config.BUTTON_WIDTH // 2,
            y=200 + config.BUTTON_HEIGHT + config.BUTTON_SPACING,
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            font=self.font,
            text_color=config.COLOR_BLACK,
            text_key="settings",
            callback=self.on_settings,
            localizer=self.loc
        )
        self.buttons.append(settings_btn)
        
        # Кнопка "Выход"
        exit_btn = Button(
            x=screen_width // 2 - config.BUTTON_WIDTH // 2,
            y=200 + 2 * (config.BUTTON_HEIGHT + config.BUTTON_SPACING),
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            font=self.font,
            text_color=config.COLOR_BLACK,
            text_key="exit",
            callback=self.on_exit,
            localizer=self.loc
        )
        self.buttons.append(exit_btn)
        
        # Слайдер для выбора языка (в нижней части)
        lang_y = screen_height - 100
        self.language_label = Label(
            x=50,
            y=lang_y,
            text_key="language",
            font=self.font,
            color=config.COLOR_BLACK,
            center=False,
            localizer=self.loc
        )
        
        # Слайдер для переключения языка (0 = русский, 1 = английский)
        self.language_slider = Slider(
            x=200,
            y=lang_y + 5,
            width=150,
            height=30,
            min_val=0,
            max_val=1,
            initial_val=0 if self.loc.get_lang() == 'ru' else 1,
            callback=self.on_language_change
        )

    def on_start_game(self):
        """Обработчик кнопки 'Начать игру'"""
        print("➜ Нажата кнопка 'Начать игру'")
        # В будущем здесь будет переход на экран выбора игры
        # self.manager.set_screen("game_choice")

    def on_settings(self):
        """Обработчик кнопки 'Настройки'"""
        print("➜ Нажата кнопка 'Настройки'")
        # В будущем здесь будет экран настроек
        # self.manager.set_screen("settings")

    def on_exit(self):
        """Обработчик кнопки 'Выход'"""
        print("➜ Нажата кнопка 'Выход'")
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def on_language_change(self, value):
        """
        Обработчик изменения языка через слайдер.
        
        :param value: значение слайдера (0 или 1)
        """
        lang = 'ru' if value < 0.5 else 'en'
        self.loc.switch_lang(lang)
        print(f"➜ Язык изменён на: {lang}")

    def on_enter(self):
        """Вызывается при входе на экран."""
        print("✓ Вход на экран меню")

    def on_exit_screen(self):
        """Вызывается при выходе с экрана."""
        print("✓ Выход с экрана меню")

    def handle_event(self, event):
        """Обрабатывает события."""
        for btn in self.buttons:
            btn.handle_event(event)
        self.language_slider.handle_event(event)

    def update(self):
        """Обновляет логику экрана каждый кадр."""
        pass

    def draw(self, screen):
        """Отрисовывает содержимое экрана."""
        # Фон
        screen.fill(self.bg_color)
        
        # Заголовок
        self.title.draw(screen)
        
        # Кнопки
        for btn in self.buttons:
            btn.draw(screen)
        
        # Слайдер языка
        self.language_label.draw(screen)
        self.language_slider.draw(screen)
        
        # Текст справки внизу экрана
        help_text = "Demo UI System • Try clicking buttons or adjusting language slider"
        help_font = pygame.font.Font(None, 20)
        help_color = (150, 150, 150)
        help_surf = help_font.render(help_text, True, help_color)
        help_rect = help_surf.get_rect(bottomright=(screen.get_width() - 10, screen.get_height() - 10))
        screen.blit(help_surf, help_rect)
