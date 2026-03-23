import pygame
from modules.ui.button import Button
 


class MenuScreen:
    def __init__(self, manager, loc, font):
        self.manager = manager
        self.loc = loc
        self.font = font
        self.buttons = []

        # Создаём кнопки
        self.start_btn = Button(300, 200, 200, 50, font=font, text_key="start_game", localizer=self.loc,
                                callback=self.start_game)
        self.settings_btn = Button(300, 270, 200, 50, font=font, text_key="settings", localizer=self.loc,
                                   callback=self.open_settings)
        self.exit_btn = Button(300, 340, 200, 50, font=font, text_key="exit", localizer=self.loc,
                               callback=self.exit_game)
        self.buttons = [self.start_btn, self.settings_btn, self.exit_btn]

    def on_enter(self):
        pass

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)

    def draw(self, screen):
        # Очистка экрана (можно фон)
        screen.fill((255,255,255))
        for btn in self.buttons:
            btn.draw(screen)

    def update(self):
        pass

    def start_game(self):
        # Переключиться на экран выбора игры
        self.manager.set_screen("game_choice")

    def open_settings(self):
        self.manager.set_screen("settings")

    def exit_game(self):
        pygame.quit()
        exit()