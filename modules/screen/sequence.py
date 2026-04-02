"""
Экран игры "Запомни последовательность".
"""

import pygame
import config
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
        
        self.status_label = Label(
            x=screen_width // 2,
            y=screen_height - 80,
            text_key=None,
            font=self.font_small,
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
        
        # Кнопки игры (прямоугольники для кликов)
        self.button_rects = []
        self.button_hover = [False, False, False, False]
        
        self._init_button_rects()
        
        self.game = None
        self.saved = False
    
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
        self.status_label.text = ''
        self.saved = False
        self._start_new_game()
    
    def _start_new_game(self):
        """Начинает новую игру."""
        level = int(self.manager.context.get('sequence_level', 1))
        self.manager.context['sequence_level'] = level
        
        self.game = SequenceGame(level=level)
        self.game.set_buttons_rect(self.button_rects)
        self.status_label.text = self.loc.get('watch_sequence')
        self.status_label._update_surface()
        self.button_hover = [False, False, False, False]
    
    def on_back(self):
        """Возврат в меню."""
        self.manager.set_screen('menu')
    
    def on_restart(self):
        """Перезапуск игры."""
        self._start_new_game()
    
    def handle_event(self, event):
        """Обрабатывает события."""
        self.back_button.handle_event(event)
        self.restart_button.handle_event(event)
        
        # Обновление hover состояний (только если ход игрока)
        if event.type == pygame.MOUSEMOTION:
            if self.game and self.game.is_player_turn():
                for i, rect in enumerate(self.button_rects):
                    self.button_hover[i] = rect.collidepoint(event.pos)
            else:
                # Сбрасываем подсветку во время показа последовательности
                self.button_hover = [False, False, False, False]
        
        # Обработка кликов по игровым кнопкам
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.game and self.game.is_player_turn():
                button_index = self.game.get_button_at_pos(event.pos)
                if button_index is not None:
                    current_time = pygame.time.get_ticks()
                    self.game.handle_player_input(button_index, current_time)
                    
                    # Обновляем статус
                    if self.game.is_game_over():
                        self.status_label.text = self.loc.get('game_over')
                        self._save_results()
    
    def update(self):
        """Обновляет логику игры."""
        if not self.game:
            return
        
        current_time = pygame.time.get_ticks()
        self.game.update(current_time)
        
        # Сброс hover при начале нового раунда (когда игра переключается на preview)
        if self.game.game_state == 'preview' and any(self.button_hover):
            self.button_hover = [False, False, False, False]
        
        # Обновление информационных меток
        self.score_label.text = f"{self.loc.get('score')}: {self.game.get_score()}"
        self.level_label.text = f"{self.loc.get('level')}: {self.game.get_sequence_length()}"
        self.mistakes_label.text = f"{self.loc.get('mistakes')}: {self.game.get_mistakes()}/{self.game.max_mistakes}"
        
        self.score_label._update_surface()
        self.level_label._update_surface()
        self.mistakes_label._update_surface()
        
        # Обновление статуса хода (ИСПРАВЛЕНО)
        if self.game.is_player_turn():
            if self.status_label.text != self.loc.get('your_turn'):
                self.status_label.text = self.loc.get('your_turn')
                self.status_label._update_surface()
        elif self.game.game_state == 'preview':
            if self.status_label.text != self.loc.get('watch_sequence'):
                self.status_label.text = self.loc.get('watch_sequence')
                self.status_label._update_surface()
        
        # Сохранение результатов при победе
        if not self.saved and self.game.is_completed():
            self._save_results()
    
    def _save_results(self):
        """Сохраняет результаты в БД."""
        current_user = self.manager.context.get('current_user')
        current_time = pygame.time.get_ticks()
        
        score = self.game.get_score()
        level = self.game.get_level()
        sequence_length = self.game.get_sequence_length()
        
        self.manager.context['last_sequence_stats'] = {
            'score': score,
            'level': level,
            'sequence_length': sequence_length,
            'mistakes': self.game.get_mistakes(),
            'completed_at': current_time
        }
        
        if current_user:
            db = DatabaseManager(config.DB_PATH)
            session = GameSession(
                user_id=current_user.id,
                game_type='sequence',
                score=score,
                level=level,
                duration=sequence_length * 2
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
        """Отрисовывает экран с карточками и спрайтами."""
        screen.fill(self.bg_color)
        
        # Заголовок
        self.title.draw(screen)
        
        # Информационные панели
        self.score_label.draw(screen)
        self.level_label.draw(screen)
        self.mistakes_label.draw(screen)
        
        # Игровые кнопки с картинками и цветным фоном
        if self.game:
            for i, rect in enumerate(self.button_rects):
                # Получаем цвет фона (активный/неактивный/наведение)
                bg_color = self.game.get_button_color(i, self.button_hover[i])
                
                # Рисуем цветной фон
                pygame.draw.rect(screen, bg_color, rect)
                
                # Рисуем спрайт поверх фона
                sprite = self.game.get_button_sprite(i)
                if sprite:
                    # Масштабируем спрайт под размер кнопки с отступом 10px
                    padding = 10
                    sprite_size = min(rect.width - padding * 2, rect.height - padding * 2)
                    if sprite_size > 0:
                        scaled_sprite = pygame.transform.smoothscale(sprite, (sprite_size, sprite_size))
                        sprite_rect = scaled_sprite.get_rect(center=rect.center)
                        screen.blit(scaled_sprite, sprite_rect)
                
                # Рисуем рамку
                pygame.draw.rect(screen, config.COLOR_BLACK, rect, 3)
        
        # Сообщение о завершении
        if self.game and self.game.is_game_over():
            over_text = self.loc.get('game_over')
            over_label = self.font_large.render(over_text, True, config.COLOR_RED)
            over_rect = over_label.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 100))
            screen.blit(over_label, over_rect)
        
        # Статус
        if self.status_label.text:
            self.status_label._update_surface()
            self.status_label.draw(screen)
        
        # Кнопки управления
        self.back_button.draw(screen)
        self.restart_button.draw(screen)
