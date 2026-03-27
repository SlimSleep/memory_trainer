"""
Экран логина/регистрации пользователя.
"""

import pygame
from modules.ui.screen import Screen
from modules.ui.label import Label
from modules.ui.textbox import TextBox
from modules.ui.button import Button
from modules.database.db_manager import DatabaseManager
from modules.session import save_session
import config


class LoginScreen(Screen):
    def __init__(self, manager, localizer, font_normal, font_small):
        super().__init__(manager, localizer, font_normal)
        self.font_small = font_small
        self.bg_color = config.COLOR_WHITE

        self.title = Label(
            x=manager.screen.get_width() // 2,
            y=80,
            text_key='login_title',
            font=self.font_small,
            color=config.COLOR_BLACK,
            center=True,
            localizer=self.loc
        )

        self.username_box = TextBox(
            x=manager.screen.get_width() // 2 - 200,
            y=180,
            width=400,
            height=50,
            font=self.font,
            placeholder=self.loc.get('name_placeholder'),
            text_key='name_placeholder',
            localizer=self.loc,
            max_length=30
        )

        self.message = ''
        self.message_label = Label(
            x=manager.screen.get_width() // 2,
            y=250,
            text_key=None,
            font=self.font_small,
            color=config.COLOR_RED,
            center=True,
            localizer=None
        )

        self.login_button = Button(
            x=manager.screen.get_width() // 2 - config.BUTTON_WIDTH // 2,
            y=300,
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            font=self.font,
            text_key='sign_in',
            localizer=self.loc,
            callback=self.try_login
        )

        self.back_button = Button(
            x=manager.screen.get_width() // 2 - config.BUTTON_WIDTH // 2,
            y=370,
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            font=self.font,
            text_key='back',
            localizer=self.loc,
            callback=self.go_back
        )

    def on_enter(self):
        self.message = ''
        self.message_label.text = ''


    def try_login(self):
        username = self.username_box.get_text().strip()
        if not username:
            self.message = self.loc.get('empty_name_error')
            return

        db = DatabaseManager(config.DB_PATH)
        user = db.get_user_by_name(username)
        if not user:
            user = db.create_user(username)
            if not user:
                self.message = self.loc.get('registration_failed')
                return

        save_session(username)
        self.manager.context['current_user'] = user
        self.message = self.loc.get('login_success').format(username=username)

        # Перейти к меню после успешного логина
        self.manager.set_screen('menu')

    def go_back(self):
        self.manager.set_screen('menu')

    def handle_event(self, event):
        self.username_box.handle_event(event)
        self.login_button.handle_event(event)
        self.back_button.handle_event(event)

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(self.bg_color)
        self.title.draw(screen)
        self.username_box.draw(screen)

        if self.message:
            self.message_label.text = self.message
            self.message_label._update_surface()
            self.message_label.draw(screen)

        self.login_button.draw(screen)
        self.back_button.draw(screen)
