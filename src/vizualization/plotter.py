"""
Визуализация результатов симуляции
"""
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple, Dict, Any
import os
from datetime import datetime


def plot_profit_vs_intensity(
    results: List[Tuple[float, Dict[str, Any]]],
    optimal_intensity: float,
    save_path: str = None
):
    """
    График зависимости прибыли от интенсивности выпуска
    
    Args:
        results: результаты симуляций [(интенсивность, метрики), ...]
        optimal_intensity: оптимальная интенсивность
        save_path: путь для сохранения графика
    """
    intensities = [r[0] for r in results]
    profits = [r[1]['profit'] for r in results]
    
    plt.figure(figsize=(12, 7))
    
    # Основной график
    plt.plot(intensities, profits, 'b-', linewidth=2, label='Прибыль')
    plt.fill_between(intensities, profits, alpha=0.3, color='blue')
    
    # Оптимальная точка
    optimal_idx = intensities.index(optimal_intensity)
    plt.plot(
        optimal_intensity,
        profits[optimal_idx],
        'ro',
        markersize=12,
        label=f'Оптимум: {optimal_intensity:.2f} авт/час'
    )
    
    plt.xlabel('Интенсивность выпуска автобусов (автобусов/час)', fontsize=12, fontweight='bold')
    plt.ylabel('Прибыль (руб.)', fontsize=12, fontweight='bold')
    plt.title('Зависимость прибыли от интенсивности выпуска автобусов', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=11)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"График сохранен: {save_path}")
    else:
        plt.show()


def plot_metrics_comparison(
    results: List[Tuple[float, Dict[str, Any]]],
    optimal_intensity: float,
    save_path: str = None
):
    """
    Сравнение метрик для разных интенсивностей
    
    Args:
        results: результаты симуляций
        optimal_intensity: оптимальная интенсивность
        save_path: путь для сохранения графика
    """
    intensities = [r[0] for r in results]
    
    # Извлечение метрик
    passengers_served = [r[1]['total_passengers_served'] for r in results]
    passengers_lost = [r[1]['total_passengers_lost'] for r in results]
    buses_released = [r[1]['total_buses_released'] for r in results]
    avg_wait_times = [r[1].get('avg_wait_time', 0) for r in results]
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Сравнение метрик для разных интенсивностей выпуска', 
                 fontsize=16, fontweight='bold')
    
    # 1. Количество перевезенных пассажиров
    axes[0, 0].plot(intensities, passengers_served, 'g-', linewidth=2)
    axes[0, 0].set_xlabel('Интенсивность (автобусов/час)')
    axes[0, 0].set_ylabel('Количество пассажиров')
    axes[0, 0].set_title('Перевезено пассажиров')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Отметка оптимума
    opt_idx = intensities.index(optimal_intensity)
    axes[0, 0].plot(optimal_intensity, passengers_served[opt_idx], 'ro')
    
    # 2. Количество потерянных пассажиров
    axes[0, 1].plot(intensities, passengers_lost, 'r-', linewidth=2)
    axes[0, 1].set_xlabel('Интенсивность (автобусов/час)')
    axes[0, 1].set_ylabel('Количество пассажиров')
    axes[0, 1].set_title('Потеряно пассажиров')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].plot(optimal_intensity, passengers_lost[opt_idx], 'ro')
    
    # 3. Количество выпущенных автобусов
    axes[1, 0].plot(intensities, buses_released, 'b-', linewidth=2)
    axes[1, 0].set_xlabel('Интенсивность (автобусов/час)')
    axes[1, 0].set_ylabel('Количество автобусов')
    axes[1, 0].set_title('Выпущено автобусов')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].plot(optimal_intensity, buses_released[opt_idx], 'ro')
    
    # 4. Среднее время ожидания
    axes[1, 1].plot(intensities, avg_wait_times, 'purple', linewidth=2)
    axes[1, 1].set_xlabel('Интенсивность (автобусов/час)')
    axes[1, 1].set_ylabel('Время (минуты)')
    axes[1, 1].set_title('Среднее время ожидания')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].plot(optimal_intensity, avg_wait_times[opt_idx], 'ro')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"График сохранен: {save_path}")
    else:
        plt.show()


def plot_bus_load_distribution(
    metrics: Dict[str, Any],
    save_path: str = None
):
    """
    Распределение загрузки автобусов
    
    Args:
        metrics: метрики симуляции
        save_path: путь для сохранения графика
    """
    if not metrics['bus_loads']:
        print("Нет данных о загрузке автобусов")
        return
    
    loads = metrics['bus_loads']
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Анализ загрузки автобусов', fontsize=16, fontweight='bold')
    
    # Гистограмма распределения
    axes[0].hist(loads, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0].axvline(np.mean(loads), color='red', linestyle='--', 
                    linewidth=2, label=f'Среднее: {np.mean(loads):.1f}')
    axes[0].axvline(np.median(loads), color='green', linestyle='--', 
                    linewidth=2, label=f'Медиана: {np.median(loads):.1f}')
    axes[0].set_xlabel('Количество пассажиров в автобусе')
    axes[0].set_ylabel('Частота')
    axes[0].set_title('Распределение загрузки')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Box plot
    axes[1].boxplot(loads, vert=True, patch_artist=True,
                    boxprops=dict(facecolor='lightblue'))
    axes[1].set_ylabel('Количество пассажиров')
    axes[1].set_title('Box plot загрузки')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"График сохранен: {save_path}")
    else:
        plt.show()


def plot_passenger_flow_analysis(
    config: Dict[str, Any],
    save_path: str = None
):
    """
    Анализ пассажиропотока на остановках
    
    Args:
        config: конфигурация модели
        save_path: путь для сохранения графика
    """
    num_stops = config['route']['num_stops']
    lambda_arrival = config['passenger_flow']['lambda_arrival']
    lambda_exit = config['passenger_flow']['lambda_exit']
    
    stops = list(range(1, num_stops + 1))
    
    plt.figure(figsize=(14, 7))
    
    plt.bar(
        [s - 0.2 for s in stops],
        lambda_arrival,
        width=0.4,
        label='Прибытие пассажиров',
        alpha=0.7,
        color='green'
    )
    plt.bar(
        [s + 0.2 for s in stops],
        lambda_exit,
        width=0.4,
        label='Выход пассажиров',
        alpha=0.7,
        color='red'
    )
    
    plt.xlabel('Номер остановки', fontsize=12, fontweight='bold')
    plt.ylabel('Интенсивность (пассажиров/мин)', fontsize=12, fontweight='bold')
    plt.title('Анализ пассажиропотока по остановкам', fontsize=14, fontweight='bold')
    plt.xticks(stops)
    plt.grid(True, alpha=0.3, axis='y')
    plt.legend(fontsize=11)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"График сохранен: {save_path}")
    else:
        plt.show()


def save_all_plots(
    optimal_result: Tuple[float, Dict[str, Any]],
    all_results: List[Tuple[float, Dict[str, Any]]],
    config: Dict[str, Any],
    output_dir: str = "output/plots"
):
    """
    Сохранение всех графиков
    
    Args:
        optimal_result: оптимальный результат
        all_results: все результаты
        config: конфигурация
        output_dir: директория для сохранения
    """
    # Создание директории
    os.makedirs(output_dir, exist_ok=True)
    
    # Временная метка
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    optimal_intensity, optimal_metrics = optimal_result
    
    # 1. График прибыли
    profit_path = os.path.join(output_dir, f"profit_vs_intensity_{timestamp}.png")
    plot_profit_vs_intensity(all_results, optimal_intensity, profit_path)
    
    # 2. Сравнение метрик
    metrics_path = os.path.join(output_dir, f"metrics_comparison_{timestamp}.png")
    plot_metrics_comparison(all_results, optimal_intensity, metrics_path)
    
    # 3. Распределение загрузки
    load_path = os.path.join(output_dir, f"bus_load_distribution_{timestamp}.png")
    plot_bus_load_distribution(optimal_metrics, load_path)
    
    # 4. Анализ пассажиропотока
    flow_path = os.path.join(output_dir, f"passenger_flow_{timestamp}.png")
    plot_passenger_flow_analysis(config, flow_path)
    
    print(f"\n✅ Все графики сохранены в директорию: {output_dir}")