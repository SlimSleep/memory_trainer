"""
Экран настроек приложения.
"""

import pygame
from modules import audio
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

        self.sfx_label = Label(
            x=150,
            y=160,
            text_key='sound_effects',
            font=self.font,
            color=config.COLOR_BLACK,
            center=False,
            localizer=self.loc
        )

        self.sfx_slider = Slider(
            x=380,
            y=165,
            width=520,
            height=25,
            min_val=0,
            max_val=100,
            initial_val=self.manager.context.get('sfx_volume', config.DEFAULT_SFX_VOLUME_PERCENT),
            callback=self.on_sfx_volume_change
        )

        self.bg_label = Label(
            x=150,
            y=235,
            text_key='background_volume',
            font=self.font,
            color=config.COLOR_BLACK,
            center=False,
            localizer=self.loc
        )

        self.bg_slider = Slider(
            x=380,
            y=240,
            width=520,
            height=25,
            min_val=0,
            max_val=100,
            initial_val=self.manager.context.get('bg_volume', config.DEFAULT_BG_VOLUME_PERCENT),
            callback=self.on_bg_volume_change
        )

        self.difficulty_label = Label(
            x=150,
            y=310,
            text_key='difficulty',
            font=self.font,
            color=config.COLOR_BLACK,
            center=False,
            localizer=self.loc
        )

        self.difficulty_slider = Slider(
            x=380,
            y=315,
            width=520,
            height=25,
            min_val=1,
            max_val=3,
            initial_val=self.manager.context.get('match_pairs_level', 1),
            callback=self.on_difficulty_change
        )

        self.difficulty_value = Label(
            x=920,
            y=310,
            text_key=None,
            font=self.font,
            color=config.COLOR_BLACK,
            center=False,
            localizer=None
        )

        self.language_slider = Slider(
            x=380,
            y=385,
            width=150,
            height=30,
            min_val=0,
            max_val=1,
            initial_val=0 if self.loc.get_lang() == 'ru' else 1,
            callback=self.on_language_change
        )

        self.language_label = Label(
            x=150,
            y=380,
            text_key='language',
            font=self.font,
            color=config.COLOR_BLACK,
            center=False,
            localizer=self.loc
        )

        self.back_button = Button(
            x=manager.screen.get_width() // 2 - config.BUTTON_WIDTH // 2,
            y=470,
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            font=self.font,
            text_key='back',
            click_sound_path=config.BUTTON_CLICK_SOUND,
            localizer=self.loc,
            callback=self.go_back
        )

        self.status_label = Label(
            x=manager.screen.get_width() // 2,
            y=430,
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

    def on_sfx_volume_change(self, value):
        volume_percent = int(round(value))
        self.manager.context['sfx_volume'] = volume_percent
        audio.set_sfx_volume(volume_percent / 100)
        self.status_label.text = self.loc.get('sound_effects').upper() + f": {volume_percent}%"

    def on_bg_volume_change(self, value):
        volume_percent = int(round(value))
        self.manager.context['bg_volume'] = volume_percent
        audio.set_bg_volume(volume_percent / 100)
        self.status_label.text = self.loc.get('background_volume').upper() + f": {volume_percent}%"

    def on_difficulty_change(self, value):
        level = int(round(value))
        self.manager.context['match_pairs_level'] = level
        self.manager.context['sequence_level'] = level
        self.difficulty_value.text = str(level)
        self.difficulty_value._update_surface()
        self.status_label.text = self.loc.get('difficulty') + f": {level}"

    def on_enter(self):
        self.status_label.text = ''
        selected_level = int(self.manager.context.get('match_pairs_level', 1))
        self.difficulty_slider.set_value(selected_level)
        self.difficulty_value.text = str(selected_level)
        self.difficulty_value._update_surface()
        current_sfx = int(self.manager.context.get('sfx_volume', config.DEFAULT_SFX_VOLUME_PERCENT))
        current_bg = int(self.manager.context.get('bg_volume', config.DEFAULT_BG_VOLUME_PERCENT))
        self.sfx_slider.set_value(current_sfx)
        self.bg_slider.set_value(current_bg)
        audio.set_sfx_volume(current_sfx / 100)
        audio.set_bg_volume(current_bg / 100)
        self.status_label.text = self.loc.get('sound_effects').upper() + f": {current_sfx}%"

    def go_back(self):
        self.manager.set_screen('menu')

    def handle_event(self, event):
        self.sfx_slider.handle_event(event)
        self.bg_slider.handle_event(event)
        self.difficulty_slider.handle_event(event)
        self.back_button.handle_event(event)
        self.language_slider.handle_event(event)

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(self.bg_color)
        self.title.draw(screen)
        self.sfx_label.draw(screen)
        self.sfx_slider.draw(screen)
        self.bg_label.draw(screen)
        self.bg_slider.draw(screen)
        self.difficulty_label.draw(screen)
        self.difficulty_slider.draw(screen)
        if self.difficulty_value.text:
            self.difficulty_value._update_surface()
            self.difficulty_value.draw(screen)
        self.language_label.draw(screen)
        self.language_slider.draw(screen)

        if self.status_label.text:
            self.status_label._update_surface()
            self.status_label.draw(screen)

        self.back_button.draw(screen)
