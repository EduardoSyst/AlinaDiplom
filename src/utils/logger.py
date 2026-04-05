"""
Настройка логирования
"""
import logging
import sys
from typing import Optional


def setup_logger(name: str, debug_mode: bool = False, log_file: Optional[str] = None) -> logging.Logger:
    """
    Настройка логгера
    
    Args:
        name: имя логгера
        debug_mode: если True, выводить отладочную информацию
        log_file: путь к файлу лога (опционально)
        
    Returns:
        Настроенный логгер
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)
    
    # Очистка существующих обработчиков
    logger.handlers = []
    
    # Форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if debug_mode else logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Файловый обработчик (опционально)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Получить логгер по имени
    
    Args:
        name: имя логгера
        
    Returns:
        Логгер
    """
    return logging.getLogger(name)