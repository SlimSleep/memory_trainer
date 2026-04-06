"""
Модуль логирования для приложения Memory Trainer.
Логирует события в оба источника: консоль и файл.
"""

import logging
import os
from datetime import datetime


class Logger:
    """Синглтон для управления логированием приложения."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._setup_logging()
        self._initialized = True
    
    def _setup_logging(self):
        """Инициализирует систему логирования."""
        # Создаём папку для логов, если её нет
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Путь к файлу лога с датой и временем
        log_filename = os.path.join(
            log_dir, 
            f"memory_trainer_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
        )
        
        # Конфигурация логирования
        self.logger = logging.getLogger('memory_trainer')
        self.logger.setLevel(logging.DEBUG)  # Ловим все сообщения от DEBUG и выше
        
        # Формат логов
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Хендлер для файла
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Хендлер для консоли
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # В консоль только INFO и выше
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        self.log_filename = log_filename
    
    def debug(self, message, *args):
        """Логирует отладочную информацию."""
        self.logger.debug(message, *args)
    
    def info(self, message, *args):
        """Логирует информационное сообщение."""
        self.logger.info(message, *args)
    
    def warning(self, message, *args):
        """Логирует предупреждение."""
        self.logger.warning(message, *args)
    
    def error(self, message, *args):
        """Логирует ошибку."""
        self.logger.error(message, *args)
    
    def critical(self, message, *args):
        """Логирует критическую ошибку."""
        self.logger.critical(message, *args)
    
    def exception(self, message, *args):
        """Логирует исключение с трассировкой стека."""
        self.logger.exception(message, *args)


# Глобальный объект логгера для удобного использования
logger = Logger()


def get_logger():
    """Возвращает логгер приложения."""
    return logger
