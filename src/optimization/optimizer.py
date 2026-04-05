"""
Оптимизация интенсивности выпуска автобусов
"""
import numpy as np
from typing import Dict, Any, List, Tuple
from datetime import datetime
import os
import json

from ..core.simulation import Simulation
from ..utils import setup_logger, get_logger


def run_multiple_simulations(
    config: Dict[str, Any],
    intensity_values: List[float]
) -> List[Tuple[float, Dict[str, Any]]]:
    """
    Запуск множества симуляций для разных значений интенсивности
    
    Args:
        config: конфигурация модели
        intensity_values: список значений интенсивности для тестирования
        
    Returns:
        Список кортежей (интенсивность, метрики)
    """
    logger = get_logger(__name__)
    logger.info(f"Running {len(intensity_values)} simulations...")
    
    results = []
    
    for i, intensity in enumerate(intensity_values, 1):
        logger.info(f"Simulation {i}/{len(intensity_values)}: intensity = {intensity:.2f}")
        
        # Создание и запуск симуляции
        sim = Simulation(config, intensity)
        metrics = sim.run()
        
        results.append((intensity, metrics))
        
        logger.info(
            f"Result: intensity={intensity:.2f}, "
            f"profit={metrics['profit']:.2f}, "
            f"buses={metrics['total_buses_released']}, "
            f"served={metrics['total_passengers_served']}"
        )
    
    return results


def optimize_bus_intensity(config: Dict[str, Any]) -> Tuple[
    Tuple[float, Dict[str, Any]],
    List[Tuple[float, Dict[str, Any]]]
]:
    """
    Поиск оптимальной интенсивности выпуска автобусов
    
    Args:
        config: конфигурация модели
        
    Returns:
        (оптимальный результат, все результаты)
        где оптимальный результат = (интенсивность, метрики)
    """
    logger = get_logger(__name__)
    logger.info("Starting optimization...")
    
    # Получение параметров оптимизации из конфигурации
    opt_config = config['simulation']['optimization']
    min_intensity = opt_config['min_intensity']
    max_intensity = opt_config['max_intensity']
    step = opt_config['step']
    
    # Генерация значений интенсивности
    intensity_values = np.arange(min_intensity, max_intensity + step, step)
    intensity_values = intensity_values.tolist()
    
    # Запуск симуляций
    results = run_multiple_simulations(config, intensity_values)
    
    # Поиск оптимального результата (максимальная прибыль)
    optimal_result = max(results, key=lambda x: x[1]['profit'])
    
    logger.info(
        f"Optimization completed. Optimal intensity: "
        f"{optimal_result[0]:.2f} buses/hour, "
        f"Profit: {optimal_result[1]['profit']:.2f}"
    )
    
    return optimal_result, results


def save_optimization_results(
    optimal_result: Tuple[float, Dict[str, Any]],
    all_results: List[Tuple[float, Dict[str, Any]]],
    config: Dict[str, Any],
    output_dir: str = "output/results"
):
    """
    Сохранение результатов оптимизации в JSON файл
    
    Args:
        optimal_result: оптимальный результат (интенсивность, метрики)
        all_results: все результаты симуляций
        config: конфигурация модели
        output_dir: директория для сохранения результатов
    """
    # Создание директории, если не существует
    os.makedirs(output_dir, exist_ok=True)
    
    # Формирование имени файла с временной меткой
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"optimization_results_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Подготовка данных для сохранения
    data = {
        "optimization_config": config['simulation']['optimization'],
        "optimal_result": {
            "intensity": optimal_result[0],
            "metrics": optimal_result[1]
        },
        "all_results": [
            {
                "intensity": intensity,
                "metrics": metrics
            }
            for intensity, metrics in all_results
        ],
        "timestamp": timestamp
    }
    
    # Сохранение в JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to: {filepath}")