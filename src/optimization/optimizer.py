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
    
    # Получение количества прогонов (по умолчанию 1)
    num_runs = config['simulation']['optimization'].get('num_runs', 1)
    
    logger.info(f"Running {len(intensity_values)} simulations...")
    
    results = []
    
    for i, intensity in enumerate(intensity_values, 1):
        # Вывод прогресса через print (не через логгер)
        print(f"  [{i}/{len(intensity_values)}] Testing intensity: {intensity:.2f} buses/hour")
        
        if num_runs > 1:
            logger.debug(f"  Running {num_runs} simulations...")  # ← debug вместо info
        
        # Списки для сбора метрик по всем прогонам
        all_metrics = {
            'total_passengers_served': [],
            'total_passengers_lost': [],
            'total_buses_released': [],
            'wait_times': [],
            'trip_durations': [],
            'bus_loads': [],
            'profits': [],
            'revenues': [],
            'costs': []
        }
        
        # Запуск нескольких прогонов для одной интенсивности
        for run_num in range(num_runs):
            # Создание и запуск симуляции
            sim = Simulation(config, intensity)
            metrics = sim.run()
            
            # Сохранение метрик для усреднения
            all_metrics['total_passengers_served'].append(metrics['total_passengers_served'])
            all_metrics['total_passengers_lost'].append(metrics['total_passengers_lost'])
            all_metrics['total_buses_released'].append(metrics['total_buses_released'])
            all_metrics['profits'].append(metrics['profit'])
            all_metrics['revenues'].append(metrics['revenue'])
            all_metrics['costs'].append(metrics['costs'])
            
            # Для списков добавляем все элементы
            all_metrics['wait_times'].extend(metrics.get('wait_times', []))
            all_metrics['trip_durations'].extend(metrics.get('trip_durations', []))
            all_metrics['bus_loads'].extend(metrics.get('bus_loads', []))
        
        # УСРЕДНЕНИЕ МЕТРИК
        avg_metrics = {}
        
        if num_runs > 1:
            # Усреднение скалярных метрик
            avg_metrics['total_passengers_served'] = np.mean(all_metrics['total_passengers_served'])
            avg_metrics['total_passengers_lost'] = np.mean(all_metrics['total_passengers_lost'])
            avg_metrics['total_buses_released'] = np.mean(all_metrics['total_buses_released'])
            avg_metrics['profit'] = np.mean(all_metrics['profits'])
            avg_metrics['revenue'] = np.mean(all_metrics['revenues'])
            avg_metrics['costs'] = np.mean(all_metrics['costs'])
            
            # Расчёт статистики для списков
            avg_metrics['wait_times'] = all_metrics['wait_times']
            avg_metrics['trip_durations'] = all_metrics['trip_durations']
            avg_metrics['bus_loads'] = all_metrics['bus_loads']
            
            # Стандартные отклонения для надёжности
            avg_metrics['profit_std'] = np.std(all_metrics['profits'])
            avg_metrics['passengers_served_std'] = np.std(all_metrics['total_passengers_served'])
            avg_metrics['buses_released_std'] = np.std(all_metrics['total_buses_released'])
            
            logger.debug(
                f"  Result (avg of {num_runs} runs): "
                f"profit={avg_metrics['profit']:.0f}±{avg_metrics['profit_std']:.0f}, "
                f"buses={avg_metrics['total_buses_released']:.1f}, "
                f"served={avg_metrics['total_passengers_served']:.1f}"
            )
        else:
            # Если только один прогон - используем его метрики напрямую
            avg_metrics = {
                'total_passengers_served': all_metrics['total_passengers_served'][0],
                'total_passengers_lost': all_metrics['total_passengers_lost'][0],
                'total_buses_released': all_metrics['total_buses_released'][0],
                'profit': all_metrics['profits'][0],
                'revenue': all_metrics['revenues'][0],
                'costs': all_metrics['costs'][0],
                'wait_times': all_metrics['wait_times'],
                'trip_durations': all_metrics['trip_durations'],
                'bus_loads': all_metrics['bus_loads']
            }
            
            logger.debug(
                f"  Result: profit={avg_metrics['profit']:.0f}, "
                f"buses={avg_metrics['total_buses_released']}, "
                f"served={avg_metrics['total_passengers_served']}"
            )
        
        # Расчёт дополнительных метрик (как в _finalize_simulation)
        if avg_metrics['wait_times']:
            avg_metrics['avg_wait_time'] = np.mean(avg_metrics['wait_times'])
            avg_metrics['std_wait_time'] = np.std(avg_metrics['wait_times'])
        else:
            avg_metrics['avg_wait_time'] = 0
            avg_metrics['std_wait_time'] = 0
        
        if avg_metrics['trip_durations']:
            avg_metrics['avg_trip_duration'] = np.mean(avg_metrics['trip_durations'])
            avg_metrics['std_trip_duration'] = np.std(avg_metrics['trip_durations'])
        else:
            avg_metrics['avg_trip_duration'] = 0
            avg_metrics['std_trip_duration'] = 0
        
        if avg_metrics['bus_loads']:
            avg_metrics['avg_bus_load'] = np.mean(avg_metrics['bus_loads'])
            avg_metrics['std_bus_load'] = np.std(avg_metrics['bus_loads'])
        else:
            avg_metrics['avg_bus_load'] = 0
            avg_metrics['std_bus_load'] = 0
        
        # Процент потерянных пассажиров
        total_arrivals = avg_metrics['total_passengers_served'] + avg_metrics['total_passengers_lost']
        if total_arrivals > 0:
            avg_metrics['lost_passenger_percentage'] = (avg_metrics['total_passengers_lost'] / total_arrivals * 100)
        else:
            avg_metrics['lost_passenger_percentage'] = 0.0
        
        results.append((intensity, avg_metrics))
    
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