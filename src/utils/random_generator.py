"""
Генерация случайных величин для симуляции
"""
import numpy as np
from scipy.stats import truncnorm


def truncated_normal(mean: float, std: float, lower: float = 0, upper: float = np.inf) -> float:
    """
    Генерация случайной величины из усеченного нормального распределения
    
    Args:
        mean: математическое ожидание
        std: стандартное отклонение
        lower: нижняя граница (по умолчанию 0)
        upper: верхняя граница (по умолчанию бесконечность)
        
    Returns:
        Случайное значение из усеченного нормального распределения
    """
    a = (lower - mean) / std
    b = (upper - mean) / std
    return truncnorm.rvs(a, b, loc=mean, scale=std)


def poisson(lam: float) -> int:
    """
    Генерация случайной величины из распределения Пуассона
    
    Args:
        lam: параметр распределения (интенсивность)
        
    Returns:
        Случайное целое число из распределения Пуассона
    """
    return np.random.poisson(lam)


def exponential(rate: float) -> float:
    """
    Генерация случайной величины из экспоненциального распределения
    
    Args:
        rate: интенсивность (1/среднее)
        
    Returns:
        Случайное значение из экспоненциального распределения
    """
    return np.random.exponential(1.0 / rate)