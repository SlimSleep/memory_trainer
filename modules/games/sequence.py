"""
Игра "Запомни последовательность" с генерацией мелодий на лету.
"""

import os
import random
import pygame
import config
from modules import audio


class SequenceGame:
    """
    Логика игры Sequence с мелодичной генерацией последовательностей.
    """
    
    # Цвета для фона карточек
    BUTTON_BG_COLORS = {
        0: (128, 50, 50),    # До (красный)
        1: (50, 128, 50),    # Ре (зелёный)
        2: (50, 50, 128),    # Ми (синий)
        3: (128, 128, 50),   # Фа (жёлтый)
    }
    
    BUTTON_ACTIVE_COLORS = {
        0: (255, 100, 100),
        1: (100, 255, 100),
        2: (100, 100, 255),
        3: (255, 255, 100),
    }
    
    BUTTON_HOVER_COLORS = {
        0: (200, 80, 80),
        1: (80, 200, 80),
        2: (80, 80, 200),
        3: (200, 200, 80),
    }
    
    def __init__(self, level: int = 1):
        """
        Инициализация игры Sequence.
        
        :param level: уровень сложности (1-3)
            1 - лёгкий: начало 3 ноты, макс 8 нот, медленный показ
            2 - средний: начало 4 ноты, макс 10 нот, средний показ
            3 - сложный: начало 5 нот, макс 12 нот, быстрый показ
        """
        self.level = level
        self._init_level_params()
        
        # Состояние игры
        self.sequence = []
        self.player_input = []
        self.current_step = 0
        self.game_state = 'preview'
        self.score = 0
        self.mistakes = 0
        self.max_mistakes = 3
        self.round_number = 1
        
        # Тайминги
        self.preview_start_time = 0
        self.preview_step_time = 0
        self.active_button = None
        self.active_until = 0
        self.wait_until = 0
        self.initial_delay = 800
        self.initial_delay_start = 0
        
        # Время начала игры (для статистики)
        self.game_start_time = 0
        self.game_end_time = 0
        
        # Спрайты
        self.sprites = self._load_sprites()
        self.buttons_rect = None
        
        # Генерируем первую мелодию
        self._new_melody()
        self.game_start_time = pygame.time.get_ticks()
    
    def _init_level_params(self):
        """Инициализирует параметры уровня сложности."""
        level_config = {
            1: {  # Лёгкий
                'base_length': 3,
                'max_length': 8,
                'preview_delay': 1000,
                'button_duration': 500
            },
            2: {  # Средний
                'base_length': 4,
                'max_length': 10,
                'preview_delay': 800,
                'button_duration': 400
            },
            3: {  # Сложный
                'base_length': 5,
                'max_length': 12,
                'preview_delay': 600,
                'button_duration': 300
            },
        }
        cfg = level_config.get(self.level, level_config[1])
        self.base_sequence_length = cfg['base_length']
        self.max_sequence_length = cfg['max_length']
        self.preview_delay = cfg['preview_delay']
        self.button_duration = cfg['button_duration']
    
    def _load_sprites(self):
        """Загружает спрайты для кнопок."""
        sprites = []
        for i in range(1, 5):
            path = os.path.join(config.IMAGES_DIR, f'card{i}.png')
            try:
                sprite = pygame.image.load(path).convert_alpha()
                sprites.append(sprite)
            except (pygame.error, FileNotFoundError):
                sprites.append(None)
        return sprites
    
    def _generate_melodic_sequence(self, length: int) -> list:
        """Генерирует мелодичную последовательность нот."""
        if length <= 0:
            return []
        
        sequence = [random.randint(0, 3)]
        repeat_count = 0
        last_interval = 0
        
        for i in range(1, length):
            last_note = sequence[-1]
            variety_factor = min(0.8, 0.4 + (i / length) * 0.4)
            rand = random.random()
            
            if rand < 0.6 * variety_factor:
                direction = random.choice([-1, 1])
                new_note = (last_note + direction) % 4
                interval = 1
            elif rand < 0.85 * variety_factor:
                new_note = last_note
                interval = 0
            else:
                jump = random.choice([2, 3])
                direction = random.choice([-1, 1])
                new_note = (last_note + direction * jump) % 4
                interval = jump
            
            current_interval = abs(new_note - last_note)
            
            if interval == 0:
                repeat_count += 1
                if repeat_count > 2:
                    new_note = (last_note + random.choice([-1, 1])) % 4
                    repeat_count = 0
            else:
                repeat_count = 0
            
            if current_interval == last_interval and current_interval != 0:
                if random.random() < 0.5:
                    alt_note = (last_note + random.choice([-2, 2])) % 4
                    new_note = alt_note
            
            last_interval = current_interval
            sequence.append(new_note)
        
        return sequence
    
    def _generate_rhythmic_variation(self, sequence: list) -> list:
        """Добавляет ритмические вариации."""
        if len(sequence) < 3:
            return sequence
        
        result = []
        i = 0
        
        while i < len(sequence):
            note = sequence[i]
            if random.random() < 0.2 and i < len(sequence) - 1:
                result.append(note)
                result.append(note)
                i += 1
            else:
                result.append(note)
                i += 1
        
        return result
    
    def _get_current_sequence_length(self) -> int:
        """Возвращает длину последовательности для текущего раунда."""
        increment = (self.round_number - 1) // 2
        length = self.base_sequence_length + increment
        return min(length, self.max_sequence_length)
    
    def _new_melody(self):
        """Генерирует новую мелодию для текущего раунда."""
        length = self._get_current_sequence_length()
        raw_sequence = self._generate_melodic_sequence(length)
        self.sequence = self._generate_rhythmic_variation(raw_sequence)
        
        self.player_input = []
        self.current_step = 0
        self.game_state = 'preview'
        self.preview_step_time = 0
        self.initial_delay_start = pygame.time.get_ticks()
    
    def _advance_to_next_round(self):
        """Переход к следующему раунду."""
        round_bonus = len(self.sequence) * 10 * self.level
        self.score += round_bonus
        self.round_number += 1
        
        # Проверка на победу (достигнут максимум длины И пройдено минимум 10 раундов)
        if self._get_current_sequence_length() >= self.max_sequence_length and self.round_number > 10:
            self.game_state = 'completed'
            self.game_end_time = pygame.time.get_ticks()
            return
        
        self._new_melody()
    
    def set_buttons_rect(self, buttons_rect: list):
        """Устанавливает прямоугольники кнопок."""
        self.buttons_rect = buttons_rect
    
    def get_button_at_pos(self, pos) -> int:
        """Возвращает индекс кнопки по позиции мыши."""
        if not hasattr(self, 'buttons_rect') or not self.buttons_rect:
            return None
        
        for i, rect in enumerate(self.buttons_rect):
            if rect.collidepoint(pos):
                return i
        return None
    
    def _play_button_sound(self, button_index: int):
        """Воспроизводит фортепианную ноту."""
        audio.play_piano_note(button_index)
    
    def _play_wrong_sound(self):
        """Воспроизводит звук ошибки."""
        sound = audio.load_sound(config.SEQUENCE_WRONG_SOUND)
        if sound:
            sound.play()
    
    def handle_player_input(self, button_index: int, current_time: int) -> bool:
        """Обрабатывает нажатие игрока."""
        if self.game_state != 'player_turn':
            return False
        
        if current_time < self.wait_until:
            return False
        
        self._play_button_sound(button_index)
        
        expected_index = len(self.player_input)
        if expected_index >= len(self.sequence):
            return False
        
        if button_index == self.sequence[expected_index]:
            self.player_input.append(button_index)
            
            self.active_button = button_index
            self.active_until = current_time + 150
            
            if len(self.player_input) == len(self.sequence):
                self._advance_to_next_round()
            return True
        else:
            self.mistakes += 1
            self.wait_until = current_time + 1000
            self._play_wrong_sound()
            
            if self.mistakes >= self.max_mistakes:
                self.game_state = 'game_over'
                self.game_end_time = pygame.time.get_ticks()
            else:
                self.player_input = []
                self.current_step = 0
                self.game_state = 'preview'
                self.preview_start_time = current_time
                self.initial_delay_start = current_time
            
            return False
    
    def update(self, current_time: int):
        """Обновляет состояние игры."""
        if self.active_until and current_time >= self.active_until:
            self.active_button = None
            self.active_until = 0
        
        if self.game_state == 'preview':
            if self.current_step == 0 and len(self.player_input) == 0:
                if current_time < self.initial_delay_start + self.initial_delay:
                    return
            
            if self.preview_step_time == 0:
                self.preview_step_time = current_time
                self.current_step = 0
                self._show_next_preview(current_time)
            elif current_time >= self.preview_step_time + self.preview_delay:
                self._show_next_preview(current_time)
    
    def _show_next_preview(self, current_time: int):
        """Показывает следующий элемент последовательности."""
        if self.current_step >= len(self.sequence):
            self.game_state = 'player_turn'
            self.preview_step_time = 0
            self.active_button = None
            return
        
        button_index = self.sequence[self.current_step]
        self.active_button = button_index
        self.active_until = current_time + self.button_duration
        self._play_button_sound(button_index)
        
        self.current_step += 1
        self.preview_step_time = current_time + self.button_duration
    
    def get_button_color(self, button_index: int, is_hovered: bool = False) -> tuple:
        """Возвращает цвет кнопки для отрисовки."""
        if self.active_button == button_index:
            return self.BUTTON_ACTIVE_COLORS[button_index]
        elif is_hovered and self.game_state == 'player_turn' and self.wait_until == 0:
            return self.BUTTON_HOVER_COLORS[button_index]
        else:
            return self.BUTTON_BG_COLORS[button_index]
    
    def get_button_sprite(self, button_index: int):
        """Возвращает спрайт кнопки."""
        if button_index < len(self.sprites):
            return self.sprites[button_index]
        return None
    
    def is_completed(self) -> bool:
        return self.game_state == 'completed'
    
    def is_game_over(self) -> bool:
        return self.game_state == 'game_over'
    
    def is_player_turn(self) -> bool:
        return self.game_state == 'player_turn'
    
    def get_score(self) -> int:
        return self.score
    
    def get_level(self) -> int:
        return self.level
    
    def get_sequence_length(self) -> int:
        return len(self.sequence)
    
    def get_mistakes(self) -> int:
        return self.mistakes
    
    def get_round_number(self) -> int:
        return self.round_number
    
    def get_remaining_mistakes(self) -> int:
        return self.max_mistakes - self.mistakes
    
    def get_duration_seconds(self) -> int:
        """Возвращает длительность игры в секундах."""
        if self.game_end_time == 0:
            return 0
        return max(0, (self.game_end_time - self.game_start_time) // 1000)
    
    def get_stats(self) -> dict:
        """Возвращает статистику для сохранения."""
        return {
            'score': self.score,
            'level': self.level,
            'rounds_completed': self.round_number - 1,
            'max_round_reached': self.round_number - 1,
            'mistakes': self.mistakes,
            'duration': self.get_duration_seconds(),
            'won': self.is_completed(),
            'sequence_length': self.get_sequence_length()
        }
    
    def reset(self):
        self.round_number = 1
        self.score = 0
        self.mistakes = 0
        self.game_state = 'preview'
        self.active_button = None
        self.game_start_time = pygame.time.get_ticks()
        self.game_end_time = 0
        self._new_melody()
