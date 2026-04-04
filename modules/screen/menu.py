"""
Экран главного меню приложения.
"""

import pygame
from modules.ui.screen import Screen
from modules.ui.button import Button
from modules.ui.label import Label
import config


class MenuScreen(Screen):
    """Главное меню с кнопками для запуска игр, настроек и выхода."""
    
    def __init__(self, manager, localizer, font_normal, font_large):
        super().__init__(manager, localizer, font_normal)
        self.font_large = font_large
        self.bg_color = config.COLOR_BG
        
        self.title = None
        self.user_label = None
        self.buttons = []
        
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

        # Метка пользователя
        self.user_label = Label(
            x=screen_width // 2,
            y=150,
            text_key=None,
            font=self.font,
            color=config.COLOR_BLACK,
            center=True,
            localizer=None
        )
        
        # Кнопка "Вход / регистрация"
        login_btn = Button(
            x=screen_width // 2 - config.BUTTON_WIDTH // 2,
            y=220,
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            font=self.font,
            text_color=config.COLOR_BLACK,
            text_key="sign_in",
            click_sound_path=config.BUTTON_CLICK_SOUND,
            callback=self.on_login,
            localizer=self.loc
        )
        self.buttons.append(login_btn)
        
        # Кнопка "Найди пару"
        match_pairs_btn = Button(
            x=screen_width // 2 - config.BUTTON_WIDTH // 2,
            y=220 + config.BUTTON_HEIGHT + config.BUTTON_SPACING,
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            font=self.font,
            text_color=config.COLOR_BLACK,
            text_key="match_pairs",
            click_sound_path=config.BUTTON_CLICK_SOUND,
            callback=self.on_match_pairs,
            localizer=self.loc
        )
        self.buttons.append(match_pairs_btn)
        
        # Кнопка "Запомни последовательность"
        sequence_btn = Button(
            x=screen_width // 2 - config.BUTTON_WIDTH // 2,
            y=220 + 2 * (config.BUTTON_HEIGHT + config.BUTTON_SPACING),
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            font=self.font,
            text_color=config.COLOR_BLACK,
            text_key="sequence",
            callback=self.on_sequence,
            localizer=self.loc
        )
        self.buttons.append(sequence_btn)
        
        # Кнопка "Повтори цифры"
        digits_btn = Button(
            x=screen_width // 2 - config.BUTTON_WIDTH // 2,
            y=220 + 3 * (config.BUTTON_HEIGHT + config.BUTTON_SPACING),
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            font=self.font,
            text_color=config.COLOR_BLACK,
            text_key="digits",
            callback=self.on_digits,
            localizer=self.loc
        )
        self.buttons.append(digits_btn)
        
        # Кнопка "Настройки"
        settings_btn = Button(
            x=screen_width // 2 - config.BUTTON_WIDTH // 2,
            y=220 + 4 * (config.BUTTON_HEIGHT + config.BUTTON_SPACING),
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            font=self.font,
            text_color=config.COLOR_BLACK,
            text_key="settings",
            click_sound_path=config.BUTTON_CLICK_SOUND,
            callback=self.on_settings,
            localizer=self.loc
        )
        self.buttons.append(settings_btn)
        
        # Кнопка "Выход"
        exit_btn = Button(
            x=screen_width // 2 - config.BUTTON_WIDTH // 2,
            y=220 + 5 * (config.BUTTON_HEIGHT + config.BUTTON_SPACING),
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            font=self.font,
            text_color=config.COLOR_BLACK,
            text_key="exit",
            click_sound_path=config.BUTTON_CLICK_SOUND,
            callback=self.on_exit,
            localizer=self.loc
        )
        self.buttons.append(exit_btn)

    def on_login(self):
        """Обработчик кнопки 'Вход / регистрация'."""
        print("➜ Нажата кнопка 'Вход / регистрация'")
        self.manager.set_screen("login")

    def on_match_pairs(self):
        """Обработчик кнопки 'Найди пару'."""
        print("➜ Нажата кнопка 'Найди пару'")
        self.manager.set_screen("match_pairs")

    def on_sequence(self):
        """Обработчик кнопки 'Запомни последовательность'."""
        print("➜ Нажата кнопка 'Запомни последовательность'")
        self.manager.set_screen("sequence")

    def on_digits(self):
        """Обработчик кнопки 'Повтори цифры'."""
        print("➜ Нажата кнопка 'Повтори цифры'")
        self.manager.set_screen("digits")

    def on_settings(self):
        """Обработчик кнопки 'Настройки'."""
        print("➜ Нажата кнопка 'Настройки'")
        self.manager.set_screen("settings")

    def on_exit(self):
        """Обработчик кнопки 'Выход'."""
        print("➜ Нажата кнопка 'Выход'")
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def on_enter(self):
        """Вызывается при входе на экран."""
        print("✓ Вход на экран меню")

    def handle_event(self, event):
        """Обрабатывает события."""
        for btn in self.buttons:
            btn.handle_event(event)

    def update(self):
        """Обновляет логику экрана каждый кадр."""
        pass

    def draw(self, screen):
        """Отрисовывает содержимое экрана."""
        screen.fill(self.bg_color)
        
        # Заголовок
        self.title.draw(screen)

        # Информация о пользователе
        current_user = self.manager.context.get('current_user')
        if current_user:
            self.user_label.text = f"{self.loc.get('user')}: {current_user.username}"
        else:
            self.user_label.text = self.loc.get('not_logged_in')
        
        self.user_label._update_surface()
        self.user_label.draw(screen)

        # Кнопки
        for btn in self.buttons:
            btn.draw(screen)
        
        # Подсказка внизу экрана
        help_text = "Memory Trainer v1.0 • Use menu buttons to play"
        help_font = pygame.font.Font(None, 20)
        help_color = (150, 150, 150)
        help_surf = help_font.render(help_text, True, help_color)
        help_rect = help_surf.get_rect(bottomright=(screen.get_width() - 10, screen.get_height() - 10))
        screen.blit(help_surf, help_rect)
