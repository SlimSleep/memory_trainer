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
from typing import Dict, List, Any
import config
from modules.ui.screen import Screen
from modules.ui.button import Button
from modules.ui.label import Label
from modules.database.db_manager import DatabaseManager
from modules.database.models import GameSession


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
                 level: int = 1, difficulty: int = 1, sound_manager=None):
        """
        Инициализация игры "Повтори цифры".
        
        :param manager: ScreenManager для переключения экранов
        :param localizer: Localizer для локализации текстов
        :param font_normal: нормальный шрифт (размер ~36)
        :param font_large: крупный шрифт (размер ~48)
        :param font_huge: огромный шрифт для цифр (размер ~200), создаётся если не передан
        :param level: уровень сложности (длина последовательности, 1-∞)
        :param difficulty: уровень сложности (влияет на время, паузы, ошибки, 1-3)
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
        self.level = max(1, level)  # Уровень (длина последовательности)
        self.difficulty = max(1, min(difficulty, 3))  # Сложность (1-3)
        self.sound_manager = sound_manager
        
        # Параметры, зависящие от сложности
        self._update_difficulty_params()
        
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
        
        # Флаг сохранения
        self.saved = False
        
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
        
        # Обновляем локализацию кнопок
        self._update_button_texts()
        
        # Подписываемся на изменения языка
        if self.loc:
            self.loc.register_observer(self._update_button_texts)
    
    def _update_button_texts(self):
        """Обновляет текст кнопок при смене языка."""
        self.btn_try_again.set_text('try_again')
        self.btn_change_level.set_text('change_level')
        self.btn_menu.set_text('menu')
    
    def _update_difficulty_params(self):
        """
        Обновляет параметры игры в зависимости от уровня сложности.
        
        Сложность влияет на:
        - Время показа каждой цифры (speed)
        - Максимум ошибок (max_attempts)
        """
        if self.difficulty == 1:
            # Лёгкая сложность
            self.speed = 1.5  # 1.5 секунды на цифру
            self.max_attempts = 5  # 5 ошибок
        elif self.difficulty == 2:
            # Средняя сложность
            self.speed = 1.0  # 1 секунда на цифру
            self.max_attempts = 3  # 3 ошибки
        else:  # difficulty == 3
            # Высокая сложность
            self.speed = 0.7  # 0.7 секунды на цифру
            self.max_attempts = 2  # 2 ошибки
    
    def generate_sequence(self) -> List[int]:
        """
        Генерирует случайную последовательность цифр.
        
        Длина последовательности = self.level
        
        :return: список цифр (0-9)
        """
        length = self.level
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
        self.saved = False
        
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
            
            # Enter — если всё введено, проверяем
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
                self._save_results()
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
            self._save_results()
            print(f"✓ Победа! Последовательность введена правильно. Уровень: {self.level}")
            
            # Автоматическое увеличение уровня после каждой победы
            self.level += 1
            print(f"🎉 Уровень повышен до {self.level}!")
        else:
            # Это не должно случиться, так как мы проверяем в _input_digit
            self.state = STATE_LOSE
            self.game_end_time = pygame.time.get_ticks()
            self._play_sound('lose')
            self._save_results()
            print(f"✗ Поражение.")
    
    def _play_sound(self, sound_type: str):
        """
        Воспроизводит звук через модуль audio.
        
        :param sound_type: тип звука ('correct', 'wrong', 'win', 'lose')
        """
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
                from modules import audio
                sound = audio.load_sound(sound_path)
                if sound:
                    sound.play()
            except Exception as e:
                print(f"⚠ Ошибка при воспроизведении звука {sound_type}: {e}")
    
    def _save_results(self):
        """Сохраняет результаты в БД и обновляет статистику в меню."""
        if self.saved:
            return
        
        current_user = self.manager.context.get('current_user')
        
        if not current_user:
            return
        
        # Вычисляем очки: 10 * длина последовательности за победу, 0 за поражение
        if self.state == STATE_WIN:
            score = len(self.sequence) * 10
        else:
            score = 0
        
        duration = max(0, (self.game_end_time - self.game_start_time) // 1000)
        
        # Сохраняем в контекст
        self.manager.context['last_digits_stats'] = {
            'won': self.state == STATE_WIN,
            'score': score,
            'level': self.level - 1 if self.state == STATE_WIN else self.level,
            'duration': duration,
            'sequence': self.sequence,
            'user_input': self.user_input,
            'completed_at': self.game_end_time
        }
        
        # Сохраняем в БД
        db = DatabaseManager(config.DB_PATH)
        session = GameSession(
            user_id=current_user.id,
            game_type='digits',
            score=score,
            level=self.difficulty,
            duration=duration
        )
        
        try:
            db.save_game_session(session)
            print(f"✓ Результаты сохранены: {score} очков")
            
            # Обновить статистику в главном меню
            menu_screen = self.manager.screens.get('menu')
            if menu_screen and hasattr(menu_screen, 'refresh_stats'):
                menu_screen.refresh_stats()
                
        except Exception as e:
            print(f"⚠ Ошибка сохранения: {e}")
        
        self.saved = True
    
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
        if not self.sequence:
            return
            
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.game_start_time
        
        # Общее время на одну цифру: время показа + пауза
        digit_duration = int((self.speed + DIGIT_PAUSE_MS / 1000) * 1000)
        show_duration = int(self.speed * 1000)
        
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
            digit_rect = digit_surf.get_rect()
            digit_rect.center = (screen.get_width() // 2, screen.get_height() // 2)
            screen.blit(digit_surf, digit_rect)
        
        # Показываем подсказку внизу
        hint_text = self.loc.get('demo_ready')
        hint_font = pygame.font.Font(None, 36)
        hint_surf = hint_font.render(hint_text, True, self.demo_text_color)
        hint_rect = hint_surf.get_rect()
        hint_rect.centerx = screen.get_width() // 2
        hint_rect.bottom = screen.get_height() - 30
        screen.blit(hint_surf, hint_rect)
    
    def _draw_input(self, screen):
        """
        Рисует экран ввода: прогресс, подсказка, кнопки.
        """
        screen.fill(self.bg_color)
        
        # Заголовок
        title_text = self.loc.get('digits')
        title_surf = self.font_large.render(title_text, True, config.COLOR_BLACK)
        title_rect = title_surf.get_rect()
        title_rect.centerx = screen.get_width() // 2
        title_rect.top = 50
        screen.blit(title_surf, title_rect)
        
        # Текущая длина последовательности
        length_text = f"{self.loc.get('level')}: {len(self.sequence)}"
        length_surf = self.font.render(length_text, True, config.COLOR_BLACK)
        length_rect = length_surf.get_rect()
        length_rect.centerx = screen.get_width() // 2
        length_rect.top = 120
        screen.blit(length_surf, length_rect)
        
        # Подсказка с текущим прогрессом
        prompt_text = self.loc.get('input_prompt').format(
            current=len(self.user_input) + 1,
            total=len(self.sequence)
        )
        prompt_surf = self.font.render(prompt_text, True, config.COLOR_BLACK)
        prompt_rect = prompt_surf.get_rect()
        prompt_rect.centerx = screen.get_width() // 2
        prompt_rect.top = 180
        screen.blit(prompt_surf, prompt_rect)
        
        # Крупное отображение текущей введённой цифры (если есть)
        if self.user_input:
            last_digit = str(self.user_input[-1])
            digit_surf = self.font_huge.render(last_digit, True, config.COLOR_BLUE)
            digit_rect = digit_surf.get_rect()
            digit_rect.center = (screen.get_width() // 2, 350)
            screen.blit(digit_surf, digit_rect)
        
        # Прогресс-бар
        self._draw_progress_bar(screen, len(self.user_input), len(self.sequence))
        
        # Попытки
        attempts_text = f"{self.loc.get('mistakes')}: {self.max_attempts - self.attempts_left}/{self.max_attempts}"
        attempts_surf = self.font.render(attempts_text, True, config.COLOR_RED)
        attempts_rect = attempts_surf.get_rect()
        attempts_rect.centerx = screen.get_width() // 2
        attempts_rect.top = 550
        screen.blit(attempts_surf, attempts_rect)
        
        # Подсказка внизу
        hint_text = "0-9 | Backspace | Enter"
        hint_font = pygame.font.Font(None, 24)
        hint_surf = hint_font.render(hint_text, True, config.COLOR_GRAY_DARK)
        hint_rect = hint_surf.get_rect()
        hint_rect.centerx = screen.get_width() // 2
        hint_rect.bottom = screen.get_height() - 20
        screen.blit(hint_surf, hint_rect)
    
    def _draw_progress_bar(self, screen, current: int, total: int):
        """
        Рисует простой прогресс-бар.
        
        :param screen: экран для рисования
        :param current: текущее значение
        :param total: максимальное значение
        """
        bar_width = 400
        bar_height = 40
        bar_x = screen.get_width() // 2 - bar_width // 2
        bar_y = 460
        
        # Фон бара
        pygame.draw.rect(screen, config.COLOR_GRAY_LIGHT, (bar_x, bar_y, bar_width, bar_height))
        
        # Заполненная часть
        if total > 0:
            filled_width = int((current / total) * bar_width)
            pygame.draw.rect(screen, config.COLOR_GREEN, (bar_x, bar_y, filled_width, bar_height))
        
        # Границы
        pygame.draw.rect(screen, config.COLOR_GRAY, (bar_x, bar_y, bar_width, bar_height), 3)
        
        # Текст: "2/3"
        progress_text = f"{current}/{total}"
        progress_font = pygame.font.Font(None, 28)
        progress_surf = progress_font.render(progress_text, True, config.COLOR_BLACK)
        progress_rect = progress_surf.get_rect()
        progress_rect.center = (bar_x + bar_width // 2, bar_y + bar_height // 2)
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
        difficulty_names = {1: self.loc.get('easy'), 2: self.loc.get('medium'), 3: self.loc.get('hard')}
        
        if is_win:
            score_text = f"{self.loc.get('score')}: {len(self.sequence) * 10}"
            level_up_text = " 🎉"
        else:
            score_text = f"{self.loc.get('score')}: 0"
            level_up_text = ""
        
        self.result_details.text = (
            f"{score_text} | "
            f"{self.loc.get('level')}: {len(self.sequence)}{level_up_text} | "
            f"{self.loc.get('difficulty')}: {difficulty_names.get(self.difficulty, str(self.difficulty))} | "
            f"{self.loc.get('time')}: {elapsed}с"
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
        # Загружаем сохранённый прогресс
        self.level = self.manager.context.get('digits_level', 1)
        self.difficulty = self.manager.context.get('digits_difficulty', 1)
        self._update_difficulty_params()
        
        self.start_game()
        print(f"✓ Вход на экран игры 'Повтори цифры'. Уровень: {self.level}, Сложность: {self.difficulty}")
    
    def on_try_again(self):
        """Кнопка 'Сыграть ещё': перезапуск с текущим уровнем."""
        self.start_game()
    
    def on_change_level(self):
        """Кнопка 'Сменить уровень': переход на экран настроек."""
        # Сохраняем текущий прогресс
        self.manager.context['digits_level'] = self.level
        self.manager.context['digits_difficulty'] = self.difficulty
        self.manager.set_screen('settings')
    
    def on_menu(self):
        """Кнопка 'Меню' или Escape: переход в главное меню."""
        # Сохраняем текущий прогресс
        self.manager.context['digits_level'] = self.level
        self.manager.context['digits_difficulty'] = self.difficulty
        self.manager.set_screen('menu')
    
    def on_exit(self):
        """Вызывается при выходе с экрана."""
        # Отписываемся от обновлений языка
        if self.loc:
            try:
                self.loc.unregister_observer(self._update_button_texts)
            except:
                pass
    
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
            'difficulty': self.difficulty,
            'score': len(self.sequence) * 10 if self.state == STATE_WIN else 0,
            'sequence': self.sequence,
            'user_input': self.user_input,
        }
