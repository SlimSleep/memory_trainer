"""
UI модуль для приложения Тренажёр памяти.
Содержит все визуальные элементы: Button, Label, TextBox, Slider, ScreenManager, Screen.
"""

from .button import Button
from .label import Label
from .textbox import TextBox
from .slider import Slider
from .screen_manager import ScreenManager
from .screen import Screen

__all__ = [
    'Button',
    'Label',
    'TextBox',
    'Slider',
    'ScreenManager',
    'Screen',
]
