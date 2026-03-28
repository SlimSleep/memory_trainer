"""
Тренажёр памяти - Главная точка входа приложения.

Инициализирует Pygame, создаёт менеджер экранов, и запускает главный игровой цикл.
"""

import pygame
import sys
import config
from localization.localization import Localizer
from modules.ui.screen_manager import ScreenManager
from modules.screen.menu import MenuScreen
from modules.screen.login import LoginScreen
from modules.screen.settings import SettingsScreen
from modules.screen.match_pairs import MatchPairsScreen
from modules.database.db_manager import DatabaseManager


def main():
    """Главная функция приложения."""
    
    # Инициализация Pygame
    pygame.init()
    print("✓ Pygame инициализирован")
    
    # Создание окна
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption(config.WINDOW_TITLE)
    print(f"✓ Окно создано: {config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
    
    # Инициализация локализации
    localizer = Localizer(lang=config.DEFAULT_LANGUAGE, localization_dir=config.LOCALIZATION_DIR)
    print(f"✓ Локализатор инициализирован, язык: {config.DEFAULT_LANGUAGE}")

    # Инициализация БД
    db = DatabaseManager(config.DB_PATH)
    print(f"✓ База данных инициализирована: {config.DB_PATH}")

    # Создание шрифтов
    font_small = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_SMALL)
    font_normal = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_NORMAL)
    font_large = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_LARGE)
    font_title = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_TITLE)
    print("✓ Шрифты инициализированы")
    
    # Создание менеджера экранов
    screen_manager = ScreenManager(screen)
    print("✓ ScreenManager инициализирован")
    
    # Создание экранов и добавление в менеджер
    menu_screen = MenuScreen(screen_manager, localizer, font_normal, font_large)
    login_screen = LoginScreen(screen_manager, localizer, font_normal, font_small)
    match_pairs_screen = MatchPairsScreen(screen_manager, localizer, font_normal, font_small, font_large)
    settings_screen = SettingsScreen(screen_manager, localizer, font_normal, font_small)
    
    screen_manager.add_screen("menu", menu_screen)
    screen_manager.add_screen("login", login_screen)
    screen_manager.add_screen("match_pairs", match_pairs_screen)
    screen_manager.add_screen("settings", settings_screen)

    # Попытка загрузить сессию из файла
    from modules.session import load_session
    remembered_username = load_session()
    if remembered_username:
        user = db.get_user_by_name(remembered_username)
        if user:
            screen_manager.context['current_user'] = user
            print(f"✓ Сессия загружена: {remembered_username}")
        else:
            print(f"⚠ Сессия содержит неизвестного пользователя: {remembered_username}")

    screen_manager.set_screen("login")
    print("✓ Меню создано и активировано")
    
    # Главный цикл приложения
    clock = pygame.time.Clock()
    running = True
    
    print("\n" + "="*60)
    print("🎮 ТРЕНАЖЁР ПАМЯТИ - ДЕМО UI СИСТЕМЫ")
    print("="*60)
    print("• Нажимайте на кнопки для тестирования")
    print("• Используйте слайдер внизу для смены языка (РУ/EN)")
    print("• Нажмите 'Выход' или закройте окно для завершения")
    print("="*60 + "\n")
    
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                print("\n✓ Приложение закрывается...")
            else:
                screen_manager.handle_event(event)
        
        # Обновление логики
        screen_manager.update()
        
        # Отрисовка
        screen_manager.draw()
        
        # Ограничение FPS
        clock.tick(config.FPS)
    
    # Завершение
    pygame.quit()
    print("✓ Pygame завершен")
    sys.exit()


if __name__ == "__main__":
    main()

