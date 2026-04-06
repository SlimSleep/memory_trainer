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
        self.stats_label = None  # <--- ОБЯЗАТЕЛЬНО
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
            y=140,
            text_key=None,
            font=self.font,
            color=config.COLOR_BLACK,
            center=True,
            localizer=None
        )
        
        # Метка статистики (СОЗДАЁМ)
        self.stats_label = Label(
            x=screen_width // 2,
            y=180,
            text_key=None,
            font=pygame.font.Font(None, config.FONT_SIZE_SMALL),
            color=config.COLOR_GRAY_DARK,
            center=True,
            localizer=None
        )
        
        # Кнопка "Вход / регистрация"
        login_btn = Button(
            x=screen_width // 2 - config.BUTTON_WIDTH // 2,
            y=230,
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
            y=230 + config.BUTTON_HEIGHT + config.BUTTON_SPACING,
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
            y=230 + 2 * (config.BUTTON_HEIGHT + config.BUTTON_SPACING),
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
            y=230 + 3 * (config.BUTTON_HEIGHT + config.BUTTON_SPACING),
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
            y=230 + 4 * (config.BUTTON_HEIGHT + config.BUTTON_SPACING),
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
            y=230 + 5 * (config.BUTTON_HEIGHT + config.BUTTON_SPACING),
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

    def _update_stats(self):
        """Обновляет отображение статистики пользователя."""
        current_user = self.manager.context.get('current_user')
        
        if current_user and self.stats_label:
            from modules.database.db_manager import DatabaseManager
            db = DatabaseManager(config.DB_PATH)
            
            # Получаем все игры пользователя
            conn = db._get_connection()
            cursor = conn.cursor()
            
            # Суммарное количество очков
            cursor.execute('''
                SELECT SUM(score) as total_score, COUNT(*) as total_games
                FROM game_sessions
                WHERE user_id = ?
            ''', (current_user.id,))
            
            result = cursor.fetchone()
            total_score = result['total_score'] if result['total_score'] else 0
            total_games = result['total_games'] if result['total_games'] else 0
            
            # Формируем текст статистики
            stats_text = f"Всего игр: {total_games} | Сумма очков: {total_score}"
            self.stats_label.text = stats_text
            self.stats_label._update_surface()
        elif self.stats_label:
            self.stats_label.text = self.loc.get('results_not_saved')
            self.stats_label._update_surface()

    def on_enter(self):
        """Вызывается при входе на экран."""
        print("✓ Вход на экран меню")
        
        # Обновляем информацию о пользователе
        current_user = self.manager.context.get('current_user')
        if current_user:
            self.user_label.text = f"{self.loc.get('user')}: {current_user.username}"
        else:
            self.user_label.text = self.loc.get('not_logged_in')
        self.user_label._update_surface()
        
        # Обновляем статистику
        self._update_stats()

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
        self.user_label.draw(screen)
        
        # Статистика (если создана)
        if self.stats_label:
            self.stats_label.draw(screen)

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
