"""
Экран игры "Запомни последовательность".
"""

import pygame
import config
from modules import audio
from modules.ui.screen import Screen
from modules.ui.label import Label
from modules.ui.button import Button
from modules.games.sequence import SequenceGame
from modules.database.db_manager import DatabaseManager
from modules.database.models import GameSession


class SequenceScreen(Screen):
    """Экран игры Sequence."""
    
    def __init__(self, manager, localizer, font_normal, font_small, font_large):
        super().__init__(manager, localizer, font_normal)
        self.font_small = font_small
        self.font_large = font_large
        self.bg_color = config.COLOR_BG
        
        screen_width = manager.screen.get_width()
        screen_height = manager.screen.get_height()
        
        # Заголовок
        self.title = Label(
            x=screen_width // 2,
            y=50,
            text_key='sequence',
            font=self.font_large,
            color=config.COLOR_BLACK,
            center=True,
            localizer=self.loc
        )
        
        # Информационные панели
        self.score_label = Label(
            x=30,
            y=120,
            text_key=None,
            font=self.font,
            color=config.COLOR_BLACK,
            center=False,
            localizer=None
        )
        
        self.level_label = Label(
            x=30,
            y=160,
            text_key=None,
            font=self.font,
            color=config.COLOR_BLACK,
            center=False,
            localizer=None
        )
        
        self.mistakes_label = Label(
            x=30,
            y=200,
            text_key=None,
            font=self.font,
            color=config.COLOR_BLACK,
            center=False,
            localizer=None
        )
        
        self.round_label = Label(
            x=30,
            y=240,
            text_key=None,
            font=self.font,
            color=config.COLOR_BLACK,
            center=False,
            localizer=None
        )
        
        self.status_label = Label(
            x=screen_width // 2,
            y=screen_height - 260,
            text_key=None,
            font=self.font,
            color=config.COLOR_BLACK,
            center=True,
            localizer=None
        )
        
        # Кнопки управления
        self.back_button = Button(
            x=30,
            y=screen_height - 100,
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            font=self.font,
            text_key='back',
            localizer=self.loc,
            callback=self.on_back
        )
        
        self.restart_button = Button(
            x=screen_width - config.BUTTON_WIDTH - 30,
            y=screen_height - 100,
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            font=self.font,
            text_key='restart',
            localizer=self.loc,
            callback=self.on_restart
        )
        
        # Кнопки игры
        self.button_rects = []
        self.button_hover = [False, False, False, False]
        
        self._init_button_rects()
        
        self.game = None
        self.saved = False
        self.previous_bg_volume = 0.0
    
    def _init_button_rects(self):
        """Создаёт прямоугольники для 4 кнопок игры."""
        screen_width = self.manager.screen.get_width()
        screen_height = self.manager.screen.get_height()
        
        button_size = 150
        spacing = 50
        
        total_width = button_size * 4 + spacing * 3
        start_x = (screen_width - total_width) // 2
        start_y = screen_height // 2 - button_size // 2 - 50
        
        self.button_rects = []
        for i in range(4):
            rect = pygame.Rect(
                start_x + i * (button_size + spacing),
                start_y,
                button_size,
                button_size
            )
            self.button_rects.append(rect)
    
    def on_enter(self):
        """Вызывается при входе на экран."""
        self.previous_bg_volume = audio.get_bg_volume()
        audio.set_bg_volume(0.0)
        
        self.status_label.text = ''
        self.saved = False
        self._start_new_game()
    
    def on_exit(self):
        """Вызывается при выходе с экрана."""
        audio.set_bg_volume(self.previous_bg_volume)
    
    def _start_new_game(self):
        """Начинает новую игру."""
        level = int(self.manager.context.get('sequence_level', 1))
        self.manager.context['sequence_level'] = level
        
        self.game = SequenceGame(level=level)
        self.game.set_buttons_rect(self.button_rects)
        self.status_label.text = ''
        self.button_hover = [False, False, False, False]
        self.saved = False
    
    def on_back(self):
        self.manager.set_screen('menu')
    
    def on_restart(self):
        self._start_new_game()
    
    def handle_event(self, event):
        self.back_button.handle_event(event)
        self.restart_button.handle_event(event)
        
        if event.type == pygame.MOUSEMOTION:
            if self.game and self.game.is_player_turn():
                for i, rect in enumerate(self.button_rects):
                    self.button_hover[i] = rect.collidepoint(event.pos)
            else:
                self.button_hover = [False, False, False, False]
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.game and not self.game.is_completed() and not self.game.is_game_over():
                button_index = self.game.get_button_at_pos(event.pos)
                if button_index is not None:
                    current_time = pygame.time.get_ticks()
                    self.game.handle_player_input(button_index, current_time)
                    
                    if self.game.is_game_over() or self.game.is_completed():
                        self._save_results()
    
    def update(self):
        if not self.game:
            return
        
        current_time = pygame.time.get_ticks()
        self.game.update(current_time)
        
        if self.game.game_state == 'preview' and any(self.button_hover):
            self.button_hover = [False, False, False, False]
        
        self.score_label.text = f"{self.loc.get('score')}: {self.game.get_score()}"
        self.level_label.text = f"{self.loc.get('level')}: {self.game.get_level()}"
        self.mistakes_label.text = f"{self.loc.get('mistakes')}: {self.game.get_mistakes()}/{self.game.max_mistakes}"
        self.round_label.text = f"{self.loc.get('round')}: {self.game.get_round_number()}"
        
        self.score_label._update_surface()
        self.level_label._update_surface()
        self.mistakes_label._update_surface()
        self.round_label._update_surface()
        
        if self.game.is_player_turn():
            if self.status_label.text != self.loc.get('your_turn'):
                self.status_label.text = self.loc.get('your_turn')
                self.status_label._update_surface()
        elif self.game.game_state == 'preview':
            if self.status_label.text != self.loc.get('watch_sequence'):
                self.status_label.text = self.loc.get('watch_sequence')
                self.status_label._update_surface()
        
        if not self.saved and (self.game.is_completed() or self.game.is_game_over()):
            self._save_results()
    
    def _save_results(self):
        """Сохраняет результаты в БД и контекст."""
        if self.saved:
            return
        
        current_user = self.manager.context.get('current_user')
        stats = self.game.get_stats()
        
        self.manager.context['last_sequence_stats'] = {
            'score': stats['score'],
            'rounds': stats['rounds_completed'],
            'duration': stats['duration'],
            'level': self.game.get_level(),
            'mistakes': stats['mistakes'],
            'won': self.game.is_completed()
        }
        
        if current_user:
            db = DatabaseManager(config.DB_PATH)
            session = GameSession(
                user_id=current_user.id,
                game_type='sequence',
                score=stats['score'],
                level=self.game.get_level(),
                duration=stats['duration']
            )
            try:
                db.save_game_session(session)
                self.status_label.text = self.loc.get('results_saved')
                
                # Обновить статистику в главном меню
                menu_screen = self.manager.screens.get('menu')
                if menu_screen and hasattr(menu_screen, '_update_stats'):
                    menu_screen._update_stats()
                    
            except Exception as e:
                print(f"⚠ Ошибка сохранения: {e}")
                self.status_label.text = self.loc.get('save_failed')
        else:
            self.status_label.text = self.loc.get('results_not_saved')
        
        self.status_label._update_surface()
        self.saved = True
    
    def draw(self, screen):
        screen.fill(self.bg_color)
        self.title.draw(screen)
        
        self.score_label.draw(screen)
        self.level_label.draw(screen)
        self.mistakes_label.draw(screen)
        self.round_label.draw(screen)
        
        if self.game:
            for i, rect in enumerate(self.button_rects):
                bg_color = self.game.get_button_color(i, self.button_hover[i])
                pygame.draw.rect(screen, bg_color, rect)
                
                sprite = self.game.get_button_sprite(i)
                if sprite:
                    padding = 10
                    sprite_size = min(rect.width - padding * 2, rect.height - padding * 2)
                    if sprite_size > 0:
                        scaled_sprite = pygame.transform.smoothscale(sprite, (sprite_size, sprite_size))
                        sprite_rect = scaled_sprite.get_rect(center=rect.center)
                        screen.blit(scaled_sprite, sprite_rect)
                
                pygame.draw.rect(screen, config.COLOR_BLACK, rect, 3)
        
        # Окно результатов
        if self.game and self.game.is_completed():
            # Рисуем прямоугольник с результатами для победы
            results_rect = pygame.Rect(
                screen.get_width() // 2 - 250,
                100,
                500,
                120
            )
            pygame.draw.rect(screen, config.COLOR_WHITE, results_rect)
            pygame.draw.rect(screen, config.COLOR_BLACK, results_rect, 3)
            
            over_text = self.loc.get('win_message')
            finished_label = self.font_large.render(over_text, True, config.COLOR_GREEN)
            finished_rect = finished_label.get_rect(center=(screen.get_width() // 2, 120))
            screen.blit(finished_label, finished_rect)

            summary_text = f"{self.loc.get('score')}: {self.game.get_score()}  {self.loc.get('round')}: {self.game.get_round_number() - 1}  {self.loc.get('mistakes')}: {self.game.get_mistakes()}"
            summary_label = self.font.render(summary_text, True, config.COLOR_BLACK)
            summary_rect = summary_label.get_rect(center=(screen.get_width() // 2, 155))
            screen.blit(summary_label, summary_rect)
        
        elif self.game and self.game.is_game_over():
            # Рисуем прямоугольник с результатами для поражения
            results_rect = pygame.Rect(
                screen.get_width() // 2 - 250,
                screen.get_height() // 2 - 120,
                500,
                100
            )
            pygame.draw.rect(screen, config.COLOR_WHITE, results_rect)
            pygame.draw.rect(screen, config.COLOR_BLACK, results_rect, 3)
            
            over_text = self.loc.get('game_over')
            over_label = self.font_large.render(over_text, True, config.COLOR_RED)
            over_rect = over_label.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 100))
            screen.blit(over_label, over_rect)
            
            # Добавляем результаты
            results_text = f"{self.loc.get('score')}: {self.game.get_score()}  {self.loc.get('level')}: {self.game.get_sequence_length()}  {self.loc.get('mistakes')}: {self.game.get_mistakes()}"
            results_label = self.font.render(results_text, True, config.COLOR_BLACK)
            results_rect_center = results_label.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 70))
            screen.blit(results_label, results_rect_center)
        
        if self.status_label.text:
            self.status_label._update_surface()
            self.status_label.draw(screen)
        
        self.back_button.draw(screen)
        self.restart_button.draw(screen)
