"""Экран игры "Найди пару"."""

import pygame
import config
from modules import audio
from modules.ui.screen import Screen
from modules.ui.label import Label
from modules.ui.button import Button
from modules.games.match_pairs import MatchPairsGame
from modules.database.db_manager import DatabaseManager
from modules.database.models import GameSession


class MatchPairsScreen(Screen):
    def __init__(self, manager, localizer, font_normal, font_small, font_large):
        super().__init__(manager, localizer, font_normal)
        self.font_small = font_small
        self.font_large = font_large
        self.bg_color = config.COLOR_BG

        self.title = Label(
            x=manager.screen.get_width() // 2,
            y=60,
            text_key='match_pairs',
            font=self.font_large,
            color=config.COLOR_BLACK,
            center=True,
            localizer=self.loc
        )

        self.moves_label = Label(
            x=30,
            y=110,
            text_key=None,
            font=self.font,
            color=config.COLOR_BLACK,
            center=False,
            localizer=None
        )
        self.timer_label = Label(
            x=30,
            y=140,
            text_key=None,
            font=self.font,
            color=config.COLOR_BLACK,
            center=False,
            localizer=None
        )
        self.status_label = Label(
            x=manager.screen.get_width() // 2,
            y=manager.screen.get_height() - 70,
            text_key=None,
            font=self.font_small,
            color=config.COLOR_BLACK,
            center=True,
            localizer=None
        )

        self.wrong_sound = audio.load_sound(config.MATCH_PAIRS_WRONG_SOUND)
        self.victory_sound = audio.load_sound(config.MATCH_PAIRS_VICTORY_SOUND)

        self.back_button = Button(
            x=30,
            y=manager.screen.get_height() - 100,
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            font=self.font,
            text_key='back',
            click_sound_path=config.BUTTON_CLICK_SOUND,
            localizer=self.loc,
            callback=self.on_back
        )
        self.restart_button = Button(
            x=manager.screen.get_width() - config.BUTTON_WIDTH - 30,
            y=manager.screen.get_height() - 100,
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            font=self.font,
            text_key='restart',
            click_sound_path=config.BUTTON_CLICK_SOUND,
            localizer=self.loc,
            callback=self.on_restart
        )

        self.game = None
        self.saved = False

    def on_enter(self):
        self.status_label.text = ''
        self.saved = False
        self._start_new_game()

    def _start_new_game(self):
        level = int(self.manager.context.get('match_pairs_level', 1))
        self.manager.context['match_pairs_level'] = level

        board_rect = pygame.Rect(
            0,
            140,
            self.manager.screen.get_width(),
            self.manager.screen.get_height() - 260
        )

        self.game = MatchPairsGame(level=level, board_rect=board_rect)
        self.status_label.text = ''

    def on_back(self):
        self.manager.set_screen('menu')

    def on_restart(self):
        self._start_new_game()

    def handle_event(self, event):
        self.back_button.handle_event(event)
        self.restart_button.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.game and not self.game.locked and not self.game.completed:
                index = self.game.get_card_index_at(event.pos)
                if index is not None:
                    result = self.game.select_card(index, pygame.time.get_ticks())
                    if result == 'wrong' and self.wrong_sound:
                        self.wrong_sound.play()
                    elif result == 'victory' and self.victory_sound:
                        self.victory_sound.play()
                    if self.game.is_completed():
                        self._save_results()

    def update(self):
        if not self.game:
            return

        current_time = pygame.time.get_ticks()
        self.game.update(current_time)
        if self.game.is_completed() and not self.saved:
            self._save_results()

    def _save_results(self):
        current_user = self.manager.context.get('current_user')
        current_time = pygame.time.get_ticks()
        duration = self.game.get_elapsed_seconds(current_time)
        score = self.game.get_score()
        level = self.game.get_level()

        self.manager.context['last_match_pairs_stats'] = {
            'score': score,
            'moves': self.game.moves,
            'duration': duration,
            'level': level,
            'completed_at': current_time
        }

        if current_user:
            db = DatabaseManager(config.DB_PATH)
            session = GameSession(
                user_id=current_user.id,
                game_type='match_pairs',
                score=score,
                level=level,
                duration=duration
            )
            try:
                db.save_game_session(session)
                self.status_label.text = self.loc.get('results_saved')
            except Exception:
                self.status_label.text = self.loc.get('save_failed')
        else:
            self.status_label.text = self.loc.get('results_not_saved')

        self.status_label._update_surface()
        self.saved = True

    def draw(self, screen):
        screen.fill(self.bg_color)
        self.title.draw(screen)

        self.moves_label.text = f"{self.loc.get('moves')}: {self.game.moves if self.game else 0}"
        self.timer_label.text = f"{self.loc.get('time')}: {self.game.get_elapsed_seconds(pygame.time.get_ticks()) if self.game else 0}s"
        self.moves_label._update_surface()
        self.timer_label._update_surface()
        self.moves_label.draw(screen)
        self.timer_label.draw(screen)

        if self.game:
            for card in self.game.cards:
                display_rect = card.get('current_rect', card['rect'])
                if not self.game.animation_done:
                    pygame.draw.rect(screen, config.COLOR_GRAY_DARK, display_rect)
                    pygame.draw.rect(screen, config.COLOR_GRAY, display_rect, 2)
                elif self.game.previewing or card['revealed'] or card['matched']:
                    pygame.draw.rect(screen, card['color'], display_rect)
                    if card.get('sprite'):
                        sprite = card['sprite']
                        sprite_rect = sprite.get_rect(center=display_rect.center)
                        screen.blit(sprite, sprite_rect)
                    else:
                        label = self.font_small.render(str(card['pair_id']), True, config.COLOR_BLACK)
                        label_rect = label.get_rect(center=display_rect.center)
                        screen.blit(label, label_rect)
                    pygame.draw.rect(screen, config.COLOR_BLACK, display_rect, 2)
                else:
                    pygame.draw.rect(screen, config.COLOR_GRAY_DARK, display_rect)
                    pygame.draw.rect(screen, config.COLOR_GRAY, display_rect, 2)

                if card['matched']:
                    pygame.draw.rect(screen, config.COLOR_GREEN, display_rect, 4)

        if self.game and self.game.is_completed():
            over_text = self.loc.get('game_over')
            finished_label = self.font_large.render(over_text, True, config.COLOR_RED)
            finished_rect = finished_label.get_rect(center=(screen.get_width() // 2, 130))
            screen.blit(finished_label, finished_rect)

            summary_text = f"{self.loc.get('score')}: {self.game.get_score()}  {self.loc.get('moves')}: {self.game.moves}  {self.loc.get('time')}: {self.game.get_elapsed_seconds(pygame.time.get_ticks())}"
            summary_label = self.font.render(summary_text, True, config.COLOR_BLACK)
            summary_rect = summary_label.get_rect(center=(screen.get_width() // 2, 165))
            screen.blit(summary_label, summary_rect)

        if self.status_label.text:
            self.status_label._update_surface()
            self.status_label.draw(screen)

        self.back_button.draw(screen)
        self.restart_button.draw(screen)
