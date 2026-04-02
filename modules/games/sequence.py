"""
Игра "Запомни последовательность" (Simon Says) с графическими карточками.
Логика генерации, проверки и управления последовательностью.
"""

import os
import random
import pygame
import config
from modules import audio


class SequenceGame:
    """
    Логика игры Sequence с поддержкой спрайтов.
    """
    
    # Цвета для фона карточек (50% яркости от активных)
    BUTTON_BG_COLORS = {
        0: (128, 50, 50),    # Тёмно-красный
        1: (50, 128, 50),    # Тёмно-зелёный
        2: (50, 50, 128),    # Тёмно-синий
        3: (128, 128, 50),   # Тёмно-жёлтый
    }
    
    # Активные цвета (100% яркости для подсветки)
    BUTTON_ACTIVE_COLORS = {
        0: (255, 100, 100),   # Красный
        1: (100, 255, 100),   # Зелёный
        2: (100, 100, 255),   # Синий
        3: (255, 255, 100),   # Жёлтый
    }
    
    # Цвета для наведения мыши
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
            level 1: длина 3-5, задержка 1.0 сек
            level 2: длина 4-7, задержка 0.8 сек
            level 3: длина 5-10, задержка 0.6 сек
        """
        self.level = level
        self._init_level_params()
        
        self.sequence = []           # Исходная последовательность (индексы 0-3)
        self.player_input = []       # Ввод игрока
        self.current_step = 0        # Текущий шаг демонстрации
        self.game_state = 'preview'  # preview, player_turn, game_over, completed
        self.score = 0
        self.mistakes = 0
        self.max_mistakes = 3
        
        # Тайминги
        self.preview_start_time = 0
        self.preview_step_time = 0
        self.active_button = None
        self.active_until = 0
        self.wait_until = 0
        
        # Задержка перед первым показом
        self.initial_delay = 1000  # 1 секунда
        self.initial_delay_start = 0
        
        # Спрайты для карточек
        self.sprites = self._load_sprites()
        
        self._new_round()
    
    def _load_sprites(self):
        """Загружает спрайты card1.png - card4.png из папки assets/images."""
        sprites = []
        for i in range(1, 5):
            path = os.path.join(config.IMAGES_DIR, f'card{i}.png')
            try:
                sprite = pygame.image.load(path).convert_alpha()
                sprites.append(sprite)
            except (pygame.error, FileNotFoundError) as e:
                print(f"⚠ Не удалось загрузить спрайт {path}: {e}")
                sprites.append(None)
        return sprites
    
    def _init_level_params(self):
        """Инициализирует параметры уровня сложности."""
        level_config = {
            1: {'min_length': 3, 'max_length': 5, 'preview_delay': 1000, 'button_duration': 400},
            2: {'min_length': 4, 'max_length': 7, 'preview_delay': 800, 'button_duration': 350},
            3: {'min_length': 5, 'max_length': 10, 'preview_delay': 600, 'button_duration': 300},
        }
        cfg = level_config.get(self.level, level_config[1])
        self.min_sequence_length = cfg['min_length']
        self.max_sequence_length = cfg['max_length']
        self.preview_delay = cfg['preview_delay']
        self.button_duration = cfg['button_duration']
    
    def _new_round(self):
        """Начинает новый раунд с увеличенной последовательностью."""
        current_length = len(self.sequence)
        if current_length < self.min_sequence_length:
            new_length = self.min_sequence_length
        else:
            new_length = min(current_length + 1, self.max_sequence_length)
        
        # Добавляем случайный элемент (0-3)
        self.sequence.append(random.randint(0, 3))
        
        self.player_input = []
        self.current_step = 0
        self.game_state = 'preview'
        self.preview_start_time = pygame.time.get_ticks()
        self.preview_step_time = 0
        self.initial_delay_start = pygame.time.get_ticks()  # Задержка перед показом
        
        # Увеличиваем счёт за успешное прохождение раунда
        if current_length > 0:
            self.score += 10 * self.level
    
    def set_buttons_rect(self, buttons_rect: list):
        """
        Устанавливает прямоугольники кнопок для определения нажатий.
        
        :param buttons_rect: список из 4 pygame.Rect в порядке [красный, зелёный, синий, жёлтый]
        """
        self.buttons_rect = buttons_rect
    
    def get_button_at_pos(self, pos) -> int:
        """
        Возвращает индекс кнопки по позиции мыши.
        
        :param pos: координаты (x, y)
        :return: индекс 0-3 или None
        """
        if not hasattr(self, 'buttons_rect'):
            return None
        
        for i, rect in enumerate(self.buttons_rect):
            if rect.collidepoint(pos):
                return i
        return None
    
    def _play_button_sound(self, button_index: int):
        """Воспроизводит звук нажатия кнопки."""
        sound = audio.load_sound(config.SEQUENCE_BUTTON_SOUND)
        if sound:
            sound.play()
    
    def _play_correct_sound(self):
        """Воспроизводит звук правильного ответа."""
        sound = audio.load_sound(config.SEQUENCE_CORRECT_SOUND)
        if sound:
            sound.play()
    
    def _play_wrong_sound(self):
        """Воспроизводит звук ошибки."""
        sound = audio.load_sound(config.SEQUENCE_WRONG_SOUND)
        if sound:
            sound.play()
    
    def handle_player_input(self, button_index: int, current_time: int) -> bool:
        """
        Обрабатывает нажатие игрока.
        
        :param button_index: индекс нажатой кнопки (0-3)
        :param current_time: текущее время в мс
        :return: True если ввод корректен, False если ошибка
        """
        if self.game_state != 'player_turn':
            return False
        
        # Проверяем блокировку после ошибки
        if current_time < self.wait_until:
            return False
        
        # Звук нажатия кнопки
        self._play_button_sound(button_index)
        
        expected_index = len(self.player_input)
        if expected_index >= len(self.sequence):
            return False
        
        if button_index == self.sequence[expected_index]:
            self.player_input.append(button_index)
            
            # Визуальная обратная связь
            self.active_button = button_index
            self.active_until = current_time + 150
            
            # Звук правильного ответа (после каждого правильного нажатия)
            self._play_correct_sound()
            
            # Проверяем завершение раунда
            if len(self.player_input) == len(self.sequence):
                # Раунд пройден
                self._new_round()
            return True
        else:
            # Ошибка
            self.mistakes += 1
            self.wait_until = current_time + 1000  # Блокировка на 1 сек
            
            # Звук ошибки
            self._play_wrong_sound()
            
            if self.mistakes >= self.max_mistakes:
                self.game_state = 'game_over'
            else:
                # Сбрасываем ввод, показываем последовательность заново
                self.player_input = []
                self.current_step = 0
                self.game_state = 'preview'
                self.preview_start_time = current_time
                self.preview_step_time = 0
                self.initial_delay_start = current_time  # Задержка перед повторным показом
            
            return False
    
    def update(self, current_time: int):
        """
        Обновляет состояние игры (анимации, демонстрацию последовательности).
        
        :param current_time: текущее время в мс
        """
        # Обновление активной кнопки (визуальная обратная связь)
        if self.active_until and current_time >= self.active_until:
            self.active_button = None
            self.active_until = 0
        
        # Демонстрация последовательности
        if self.game_state == 'preview':
            # Проверяем начальную задержку (только для первого показа в раунде)
            if self.current_step == 0 and len(self.player_input) == 0:
                if current_time < self.initial_delay_start + self.initial_delay:
                    return  # Ждём завершения задержки
            
            if self.preview_step_time == 0:
                # Начинаем демонстрацию
                self.preview_step_time = current_time
                self.current_step = 0
                self._show_next_preview(current_time)
            elif current_time >= self.preview_step_time + self.preview_delay:
                self._show_next_preview(current_time)
        
        # Блокировка после ошибки
        if self.game_state == 'player_turn' and current_time < self.wait_until:
            pass  # Игрок заблокирован
    
    def _show_next_preview(self, current_time: int):
        """Показывает следующий элемент последовательности."""
        if self.current_step >= len(self.sequence):
            # Демонстрация завершена
            self.game_state = 'player_turn'
            self.preview_step_time = 0
            self.active_button = None
            return
        
        # Подсвечиваем текущую кнопку
        button_index = self.sequence[self.current_step]
        self.active_button = button_index
        self.active_until = current_time + self.button_duration
        
        # Звук при показе последовательности
        self._play_button_sound(button_index)
        
        self.current_step += 1
        self.preview_step_time = current_time + self.button_duration
    
    def get_button_color(self, button_index: int, is_hovered: bool = False) -> tuple:
        """
        Возвращает цвет фона кнопки для отрисовки.
        
        :param button_index: индекс кнопки
        :param is_hovered: наведена ли мышь
        :return: RGB кортеж
        """
        if self.active_button == button_index:
            return self.BUTTON_ACTIVE_COLORS[button_index]
        elif is_hovered and self.game_state == 'player_turn' and self.wait_until == 0:
            return self.BUTTON_HOVER_COLORS[button_index]
        else:
            return self.BUTTON_BG_COLORS[button_index]
    
    def get_button_sprite(self, button_index: int):
        """
        Возвращает спрайт для кнопки.
        
        :param button_index: индекс кнопки (0-3)
        :return: Surface с изображением или None
        """
        if button_index < len(self.sprites):
            return self.sprites[button_index]
        return None
    
    def is_completed(self) -> bool:
        """Возвращает True если игра завершена (достигнут максимум длины)."""
        return len(self.sequence) >= self.max_sequence_length and self.game_state == 'player_turn'
    
    def is_game_over(self) -> bool:
        """Возвращает True если игра проиграна."""
        return self.game_state == 'game_over'
    
    def is_player_turn(self) -> bool:
        """Возвращает True если ход игрока."""
        return self.game_state == 'player_turn'
    
    def get_score(self) -> int:
        """Возвращает текущий счёт."""
        return self.score
    
    def get_level(self) -> int:
        """Возвращает уровень сложности."""
        return self.level
    
    def get_sequence_length(self) -> int:
        """Возвращает текущую длину последовательности."""
        return len(self.sequence)
    
    def get_mistakes(self) -> int:
        """Возвращает количество ошибок."""
        return self.mistakes
    
    def get_remaining_mistakes(self) -> int:
        """Возвращает количество оставшихся попыток."""
        return self.max_mistakes - self.mistakes
    
    def reset(self):
        """Полный сброс игры."""
        self.sequence = []
        self.player_input = []
        self.current_step = 0
        self.score = 0
        self.mistakes = 0
        self.game_state = 'preview'
        self.active_button = None
        self._new_round()
