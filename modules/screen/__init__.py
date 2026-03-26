"""
Модуль экранов приложения Тренажёр памяти.
Содержит различные экраны: главное меню, игры, настройки и т.д.
"""

from .menu import MenuScreen
from .login import LoginScreen
from .settings import SettingsScreen

__all__ = [
    'MenuScreen',
    'LoginScreen',
    'SettingsScreen',
]
