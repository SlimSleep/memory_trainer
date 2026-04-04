"""
Модуль игры "Повтори цифры" (Digits).

Игрок смотрит на последовательность цифр, которые быстро показываются одна за другой,
а затем вводит эту последовательность в том же порядке. Игра имеет уровни сложности
и ограничение на количество ошибок.

Состояния игры:
- STATE_DEMO: показ последовательности цифр (каждая на отдельном экране)
- STATE_INPUT: пользователь вводит цифры с клавиатуры или мыши
- STATE_WIN: последовательность введена правильно
- STATE_LOSE: ошибка, попытки кончились
"""

import pygame
import random
from typing import Optional, Dict, List, Any
import config
from modules.ui.screen import Screen
from modules.ui.button import Button
from modules.ui.label import Label


# Состояния игры
STATE_DEMO = "demo"       # Показ последовательности
STATE_INPUT = "input"     # Ввод пользователя
STATE_WIN = "win"         # Победа
STATE_LOSE = "lose"       # Поражение

# Время показа цифры и паузы между ними (в миллисекундах)
DIGIT_PAUSE_MS = 300     # Пауза между цифрами (чёрный экран)


class DigitsGame(Screen):
    """
    Класс игры "Повтори цифры".
    
    Наследуется от Screen для интеграции с ScreenManager.
    Игрок видит последовательность цифр и должен её повторить.
    """
    
    def __init__(self, manager, localizer, font_normal, font_large, font_huge=None, 
                 level: int = 3, speed: float = 1.0, max_attempts: int = 3,
                 sound_manager=None):
        """
        Инициализация игры "Повтори цифры".
        
        :param manager: ScreenManager для переключения экранов
        :param localizer: Localizer для локализации текстов
        :param font_normal: нормальный шрифт (размер ~36)
        :param font_large: крупный шрифт (размер ~48)
        :param font_huge: огромный шрифт для цифр (размер ~200), создаётся если не передан
        :param level: уровень сложности (длина последовательности, 1-3)
        :param speed: время показа каждой цифры в секундах (по умолчанию 1.0)
        :param max_attempts: максимум ошибок перед поражением (по умолчанию 3)
        :param sound_manager: менеджер звука (audio модуль)
        """
        super().__init__(manager, localizer, font_normal)
        self.font_large = font_large
        
        # Если огромный шрифт не передан, создаём его
        if font_huge is None:
            self.font_huge = pygame.font.Font(None, 200)
        else:
            self.font_huge = font_huge
        
        # Параметры игры
        self.level = max(1, min(level, 3))  # Уровень 1-3
        self.speed = max(0.3, speed)        # Скорость показа цифры (мин 0.3 сек)
        self.max_attempts = max(1, max_attempts)  # Максимум ошибок
        self.sound_manager = sound_manager
        
        # Состояние игры
        self.state = STATE_DEMO
        self.sequence: List[int] = []       # Последовательность цифр для повтора
        self.user_input: List[int] = []    # Введённые цифры
        self.attempts_left = self.max_attempts  # Оставшиеся попытки
        
        # Таймеры для демонстрации
        self.demo_start_time = 0            # Время начала демонстрации
        self.current_digit_index = 0        # Текущая цифра в демонстрации
        self.digit_shown_time = 0           # Время показа текущей цифры
        
        # Время игры
        self.game_start_time = 0            # Время начала демонстрации
        self.game_end_time = 0              # Время окончания игры
        
        # Визуальные элементы для экрана результатов
        self.result_title = Label(
            x=manager.screen.get_width() // 2,
            y=100,
            text_key=None,
            font=self.font_large,
            color=config.COLOR_BLACK,
            center=True,
            localizer=None
        )
        
        self.result_message = Label(
            x=manager.screen.get_width() // 2,
            y=200,
            text_key=None,
            font=self.font,
            color=config.COLOR_BLACK,
            center=True,
            localizer=None
        )
        
        self.result_details = Label(
            x=manager.screen.get_width() // 2,
            y=280,
            text_key=None,
            font=self.font,
            color=config.COLOR_GRAY_DARK,
            center=True,
            localizer=None
        )
        
        # Кнопки для экрана результатов
        button_y = 380
        button_spacing = 120
        
        self.btn_try_again = Button(
            x=manager.screen.get_width() // 2 - config.BUTTON_WIDTH // 2,
            y=button_y,
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            font=self.font,
            text_key='try_again',
            click_sound_path=config.BUTTON_CLICK_SOUND,
            localizer=self.loc,
            callback=self.on_try_again
        )
        
        self.btn_change_level = Button(
            x=manager.screen.get_width() // 2 - config.BUTTON_WIDTH // 2,
            y=button_y + button_spacing,
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            font=self.font,
            text_key='change_level',
            click_sound_path=config.BUTTON_CLICK_SOUND,
            localizer=self.loc,
            callback=self.on_change_level
        )
        
        self.btn_menu = Button(
            x=manager.screen.get_width() // 2 - config.BUTTON_WIDTH // 2,
            y=button_y + button_spacing * 2,
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            font=self.font,
            text_key='menu',
            click_sound_path=config.BUTTON_CLICK_SOUND,
            localizer=self.loc,
            callback=self.on_menu
        )
        
        # Фоновый цвет
        self.bg_color = config.COLOR_BG
        
        # Цвет для демонстрации (белый текст на тёмном фоне)
        self.demo_bg_color = config.COLOR_BLACK
        self.demo_text_color = config.COLOR_WHITE
    
    def generate_sequence(self) -> List[int]:
        """
        Генерирует случайную последовательность цифр.
        
        Для уровня 1 (лёгкий) — цифры уникальны.
        Для уровня 2 (средний) — цифры могут повторяться.
        Для уровня 3 (сложный) — цифры обязательно повторяются.
        
        Длина последовательности = self.level
        
        :return: список цифр (0-9)
        """
        length = self.level
        
        if self.level == 1:
            # Лёгкий: уникальные цифры
            return random.sample(range(10), length)
        elif self.level == 2:
            # Средний: могут повторяться
            return [random.randint(0, 9) for _ in range(length)]
        else:  # level == 3
            # Сложный: повторяющиеся цифры более вероятны
            return [random.randint(0, 9) for _ in range(length)]
    
    def start_game(self):
        """
        Запускает новую игру: сбрасывает состояние и генерирует последовательность.
        
        Переводит игру в состояние STATE_DEMO.
        """
        self.sequence = self.generate_sequence()
        self.user_input = []
        self.attempts_left = self.max_attempts
        self.state = STATE_DEMO
        self.current_digit_index = 0
        self.digit_shown_time = 0
        self.game_start_time = pygame.time.get_ticks()
        self.game_end_time = 0
        
        print(f"✓ Игра начата. Последовательность: {self.sequence}, уровень: {self.level}")
    
    def handle_event(self, event):
        """
        Обрабатывает события: нажатия клавиш и мыши.
        
        В STATE_DEMO и STATE_INPUT: нажатие Escape возвращает в меню.
        В STATE_INPUT: цифры 0-9, Enter (далее), Backspace (удалить).
        В STATE_WIN/STATE_LOSE: клики по кнопкам.
        """
        # Выход из игры на любом экране по Escape
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.on_menu()
            return
        
        if self.state == STATE_INPUT:
            self._handle_input_event(event)
        elif self.state == STATE_WIN or self.state == STATE_LOSE:
            # Обработка кнопок на экране результатов
            self.btn_try_again.handle_event(event)
            self.btn_change_level.handle_event(event)
            self.btn_menu.handle_event(event)
    
    def _handle_input_event(self, event):
        """
        Обрабатывает события ввода: цифры, Enter, Backspace.
        """
        if event.type == pygame.KEYDOWN:
            # Цифры 0-9 (основная клавиатура)
            if pygame.K_0 <= event.key <= pygame.K_9:
                digit = event.key - pygame.K_0
                self._input_digit(digit)
            
            # Цифры 0-9 (цифровая клавиатура)
            elif pygame.K_KP0 <= event.key <= pygame.K_KP9:
                digit = event.key - pygame.K_KP0
                self._input_digit(digit)
            
            # Backspace — удалить последнюю введённую цифру
            elif event.key == pygame.K_BACKSPACE:
                if self.user_input:
                    self.user_input.pop()
                    print(f"◄ Удалена цифра. Текущий ввод: {self.user_input}")
            
            # Enter — если всё введено, переходим на следующий этап или проверяем
            elif event.key == pygame.K_RETURN:
                if len(self.user_input) == len(self.sequence):
                    self._check_input()
    
    def _input_digit(self, digit: int):
        """
        Обрабатывает ввод одной цифры.
        
        :param digit: цифра 0-9
        """
        if len(self.user_input) >= len(self.sequence):
            return  # Уже введена вся последовательность
        
        self.user_input.append(digit)
        
        # Проверяем, правильна ли цифра
        expected_digit = self.sequence[len(self.user_input) - 1]
        
        if digit == expected_digit:
            # Правильная цифра
            self._play_sound('correct')
            print(f"✓ Правильно: {digit}")
            
            # Если введена вся последовательность — победа!
            if len(self.user_input) == len(self.sequence):
                self._check_input()
        else:
            # Ошибка
            self._play_sound('wrong')
            self.attempts_left -= 1
            print(f"✗ Ошибка: ожидали {expected_digit}, получили {digit}. Попыток осталось: {self.attempts_left}")
            
            if self.attempts_left <= 0:
                # Конец игры
                self.state = STATE_LOSE
                self.game_end_time = pygame.time.get_ticks()
                self._play_sound('lose')
                print(f"✗ Игра завершена. Конец попыток.")
            else:
                # Очищаем ввод и начинаем заново
                self.user_input = []
    
    def _check_input(self):
        """
        Проверяет, совпадает ли введённая последовательность с ожидаемой.
        """
        if self.user_input == self.sequence:
            self.state = STATE_WIN
            self.game_end_time = pygame.time.get_ticks()
            self._play_sound('win')
            print(f"✓ Победа! Последовательность введена правильно.")
        else:
            # Это не должно случиться, так как мы проверяем в _input_digit
            self.state = STATE_LOSE
            self.game_end_time = pygame.time.get_ticks()
            self._play_sound('lose')
            print(f"✗ Поражение.")
    
    def _play_sound(self, sound_type: str):
        """
        Воспроизводит звук через sound_manager (если доступен).
        
        :param sound_type: тип звука ('correct', 'wrong', 'win', 'lose')
        """
        if not self.sound_manager:
            return
        
        sound_path = None
        if sound_type == 'correct':
            sound_path = config.SEQUENCE_CORRECT_SOUND
        elif sound_type == 'wrong':
            sound_path = config.SEQUENCE_WRONG_SOUND
        elif sound_type == 'win':
            sound_path = config.MATCH_PAIRS_VICTORY_SOUND
        elif sound_type == 'lose':
            sound_path = config.MATCH_PAIRS_WRONG_SOUND
        
        if sound_path:
            try:
                self.sound_manager.load_sound(sound_path).play()
            except Exception as e:
                print(f"⚠ Ошибка при попытке воспроизвести звук {sound_type}: {e}")
    
    def update(self):
        """
        Обновляет все таймеры и логику игры на каждый кадр.
        """
        if self.state == STATE_DEMO:
            self._update_demo()
    
    def _update_demo(self):
        """
        Обновляет демонстрацию последовательности.
        
        Показывает каждую цифру в течение self.speed секунд,
        между ними — пауза (чёрный экран) в течение DIGIT_PAUSE_MS мс.
        """
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.game_start_time
        
        # Проверяем, если это первый вызов демонстрации
        if self.demo_start_time == 0:
            self.demo_start_time = self.game_start_time
        
        # Общее время на одну цифру: время показа + пауза
        digit_duration = int((self.speed + DIGIT_PAUSE_MS / 1000) * 1000)  # в миллисекундах
        show_duration = int(self.speed * 1000)  # время показа в миллисекундах
        
        # Текущая цифра для показа
        digit_index = elapsed // digit_duration
        
        if digit_index >= len(self.sequence):
            # Демонстрация завершена, переходим к вводу
            self.state = STATE_INPUT
            self.user_input = []
            print("➜ Демонстрация завершена. Ожидание ввода пользователя...")
        else:
            # Находимся в демонстрации
            time_in_current_digit = elapsed % digit_duration
            
            # Если первая часть времени — показываем цифру
            if time_in_current_digit < show_duration:
                self.current_digit_index = digit_index
            else:
                # Иначе — чёрный экран
                self.current_digit_index = -1
    
    def draw(self, screen):
        """
        Отрисовывает содержимое игры в зависимости от состояния.
        """
        if self.state == STATE_DEMO:
            self._draw_demo(screen)
        elif self.state == STATE_INPUT:
            self._draw_input(screen)
        elif self.state == STATE_WIN:
            self._draw_result(screen, is_win=True)
        elif self.state == STATE_LOSE:
            self._draw_result(screen, is_win=False)
    
    def _draw_demo(self, screen):
        """
        Рисует экран демонстрации: крупная цифра или чёрный экран.
        """
        screen.fill(self.demo_bg_color)
        
        if self.current_digit_index >= 0 and self.current_digit_index < len(self.sequence):
            digit = self.sequence[self.current_digit_index]
            digit_text = str(digit)
            digit_surf = self.font_huge.render(digit_text, True, self.demo_text_color)
            digit_rect = digit_surf.get_rect(center=screen.get_rect().center)
            screen.blit(digit_surf, digit_rect)
        
        # Показываем подсказку внизу
        hint_text = self.loc.get('demo_ready')
        hint_font = pygame.font.Font(None, 36)
        hint_surf = hint_font.render(hint_text, True, self.demo_text_color)
        hint_rect = hint_surf.get_rect(bottomcenter=(screen.get_width() // 2, screen.get_height() - 30))
        screen.blit(hint_surf, hint_rect)
    
    def _draw_input(self, screen):
        """
        Рисует экран ввода: прогресс, подсказка, кнопки.
        """
        screen.fill(self.bg_color)
        
        # Заголовок
        title_text = self.loc.get('digits')
        title_surf = self.font_large.render(title_text, True, config.COLOR_BLACK)
        title_rect = title_surf.get_rect(midtop=(screen.get_width() // 2, 50))
        screen.blit(title_surf, title_rect)
        
        # Подсказка с текущим прогрессом
        prompt_text = self.loc.get('input_prompt').format(
            current=len(self.user_input) + 1,
            total=len(self.sequence)
        )
        prompt_surf = self.font.render(prompt_text, True, config.COLOR_BLACK)
        prompt_rect = prompt_surf.get_rect(midtop=(screen.get_width() // 2, 150))
        screen.blit(prompt_surf, prompt_rect)
        
        # Крупное отображение текущей введённой цифры (если есть)
        if self.user_input:
            last_digit = str(self.user_input[-1])
            digit_surf = self.font_huge.render(last_digit, True, config.COLOR_BLUE)
            digit_rect = digit_surf.get_rect(center=(screen.get_width() // 2, 350))
            screen.blit(digit_surf, digit_rect)
        
        # Прогресс-бар
        self._draw_progress_bar(screen, len(self.user_input), len(self.sequence))
        
        # Попытки
        attempts_text = f"{self.loc.get('mistakes')}: {self.max_attempts - self.attempts_left}/{self.max_attempts}"
        attempts_surf = self.font.render(attempts_text, True, config.COLOR_RED)
        attempts_rect = attempts_surf.get_rect(midtop=(screen.get_width() // 2, 550))
        screen.blit(attempts_surf, attempts_rect)
        
        # Подсказка внизу
        hint_text = f"Нажимайте цифры 0-9, Enter для подтверждения, Backspace для удаления, Escape для выхода"
        hint_font = pygame.font.Font(None, 18)
        hint_surf = hint_font.render(hint_text, True, config.COLOR_GRAY_DARK)
        hint_rect = hint_surf.get_rect(bottomcenter=(screen.get_width() // 2, screen.get_height() - 10))
        screen.blit(hint_surf, hint_rect)
    
    def _draw_progress_bar(self, screen, current: int, total: int):
        """
        Рисует простой прогресс-бар.
        
        :param screen: экран для рисования
        :param current: текущее значение
        :param total: максимальное значение
        """
        bar_width = 300
        bar_height = 30
        bar_x = screen.get_width() // 2 - bar_width // 2
        bar_y = 480
        
        # Фон бара
        pygame.draw.rect(screen, config.COLOR_GRAY_LIGHT, (bar_x, bar_y, bar_width, bar_height))
        
        # Заполненная часть
        if total > 0:
            filled_width = int((current / total) * bar_width)
            pygame.draw.rect(screen, config.COLOR_GREEN, (bar_x, bar_y, filled_width, bar_height))
        
        # Границы
        pygame.draw.rect(screen, config.COLOR_GRAY, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Текст: "2/3"
        progress_text = f"{current}/{total}"
        progress_font = pygame.font.Font(None, 20)
        progress_surf = progress_font.render(progress_text, True, config.COLOR_BLACK)
        progress_rect = progress_surf.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
        screen.blit(progress_surf, progress_rect)
    
    def _draw_result(self, screen, is_win: bool):
        """
        Рисует экран результата (победа или поражение).
        
        :param screen: экран для рисования
        :param is_win: True если победа, False если поражение
        """
        screen.fill(self.bg_color)
        
        # Заголовок
        if is_win:
            self.result_title.text = self.loc.get('win_message')
            self.result_title.color = config.COLOR_GREEN
        else:
            self.result_title.text = self.loc.get('lose_message').format(
                sequence=', '.join(map(str, self.sequence))
            )
            self.result_title.color = config.COLOR_RED
        
        self.result_title._update_surface()
        self.result_title.draw(screen)
        
        # Детали результата
        elapsed = max(0, (self.game_end_time - self.game_start_time) // 1000)
        self.result_details.text = (
            f"{self.loc.get('level')}: {self.level} | "
            f"{self.loc.get('time')}: {elapsed}с | "
            f"{self.loc.get('score')}: {len(self.sequence) * 10}"
        )
        self.result_details._update_surface()
        self.result_details.draw(screen)
        
        # Кнопки
        self.btn_try_again.draw(screen)
        self.btn_change_level.draw(screen)
        self.btn_menu.draw(screen)
    
    def on_enter(self):
        """
        Вызывается при входе на этот экран.
        Начинает новую игру.
        """
        self.start_game()
        print("✓ Вход на экран игры 'Повтори цифры'")
    
    def on_try_again(self):
        """Кнопка 'Сыграть ещё': перезапуск с тем же уровнем."""
        self.start_game()
    
    def on_change_level(self):
        """Кнопка 'Сменить уровень': переход на экран настроек."""
        self.manager.set_screen('settings')
    
    def on_menu(self):
        """Кнопка 'Меню' или Escape: переход в главное меню."""
        self.manager.set_screen('menu')
    
    def get_result(self) -> Dict[str, Any]:
        """
        Возвращает результаты текущей игры.
        
        :return: словарь с результатами
        """
        if self.game_end_time == 0:
            elapsed = 0
        else:
            elapsed = max(0, (self.game_end_time - self.game_start_time) // 1000)
        
        return {
            'won': self.state == STATE_WIN,
            'correct_inputs': len(self.user_input) if self.state == STATE_WIN else len(self.user_input),
            'total_digits': len(self.sequence),
            'time_seconds': elapsed,
            'level': self.level,
            'score': len(self.sequence) * 10 if self.state == STATE_WIN else 0,
            'sequence': self.sequence,
            'user_input': self.user_input,
        }
