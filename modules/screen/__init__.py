"""
Модуль экранов приложения Тренажёр памяти.
"""

from .menu import MenuScreen
from .login import LoginScreen
from .settings import SettingsScreen
from .match_pairs import MatchPairsScreen
from .sequence import SequenceScreen

__all__ = [
    'MenuScreen',
    'LoginScreen',
    'SettingsScreen',
    'MatchPairsScreen',
    'SequenceScreen',
]
