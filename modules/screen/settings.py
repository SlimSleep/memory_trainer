"""
Экран настроек приложения.
"""

import pygame
from modules.ui.screen import Screen
from modules.ui.label import Label
from modules.ui.button import Button
from modules.ui.slider import Slider
import config


class SettingsScreen(Screen):
    def __init__(self, manager, localizer, font_normal, font_small):
        super().__init__(manager, localizer, font_normal)
        self.font_small = font_small
        self.bg_color = config.COLOR_WHITE

        self.title = Label(
            x=manager.screen.get_width() // 2,
            y=80,
            text_key='settings',
            font=self.font_small,
            color=config.COLOR_BLACK,
            center=True,
            localizer=self.loc
        )

        self.volume_label = Label(
            x=150,
            y=160,
            text_key='volume',
            font=self.font,
            color=config.COLOR_BLACK,
            center=False,
            localizer=self.loc
        )

        self.volume_slider = Slider(
            x=280,
            y=165,
            width=400,
            height=25,
            min_val=0,
            max_val=100,
            initial_val=50,
            callback=self.on_volume_change
        )
        
        self.language_slider = Slider(
            x=280,
            y=220,
            width=150,
            height=30,
            min_val=0,
            max_val=1,
            initial_val=0 if self.loc.get_lang() == 'ru' else 1,
            callback=self.on_language_change
        )

        self.language_label = Label(
            x=150,
            y=220,
            text_key='language',
            font=self.font,
            color=config.COLOR_BLACK,
            center=False,
            localizer=self.loc
        )

        self.back_button = Button(
            x=manager.screen.get_width() // 2 - config.BUTTON_WIDTH // 2,
            y=330,
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            font=self.font,
            text_key='back',
            localizer=self.loc,
            callback=self.go_back
        )

        self.status_label = Label(
            x=manager.screen.get_width() // 2,
            y=280,
            text_key=None,
            font=self.font_small,
            color=config.COLOR_BLACK,
            center=True,
            localizer=None
        )

    def on_language_change(self, value):
        """
        Обработчик изменения языка через слайдер.

        :param value: значение слайдера (0 или 1)
        """
        lang = 'ru' if value < 0.5 else 'en'
        self.loc.switch_lang(lang)
        print(f"➜ Язык изменён на: {lang}")

    def on_volume_change(self, value):
        self.status_label.text = self.loc.get('volume').upper() + f": {int(value)}%"

    def on_enter(self):
        self.status_label.text = ''

    def go_back(self):
        self.manager.set_screen('menu')

    def handle_event(self, event):
        self.volume_slider.handle_event(event)
        self.back_button.handle_event(event)
        self.language_slider.handle_event(event)

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(self.bg_color)
        self.title.draw(screen)
        self.volume_label.draw(screen)
        self.volume_slider.draw(screen)
        self.language_slider.draw(screen)
        self.language_label.draw(screen)

        if self.status_label.text:
            self.status_label._update_surface()
            self.status_label.draw(screen)

        self.back_button.draw(screen)
