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
    
    # Pad arrays to match num_stops if needed
    arrival_padded = list(lambda_arrival) + [0.0] * (num_stops - len(lambda_arrival))
    exit_padded = list(lambda_exit) + [0.0] * (num_stops - len(lambda_exit))
    
    plt.bar(
        [s - 0.2 for s in stops],
        arrival_padded,
        width=0.4,
        label='Прибытие пассажиров',
        alpha=0.7,
        color='green'
    )
    plt.bar(
        [s + 0.2 for s in stops],
        exit_padded,
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


def plot_actual_passenger_flow(
    metrics: Dict[str, Any],
    config: Dict[str, Any],
    save_path: str = None
):
    """
    График ФАКТИЧЕСКОГО пассажиропотока на основе данных симуляции
    
    Args:
        metrics: метрики симуляции с статистикой по остановкам
        config: конфигурация модели
        save_path: путь для сохранения графика
    """
    num_stops = config['route']['num_stops']
    stops = list(range(1, num_stops + 1))
    
    # Извлечение статистики
    stop_stats = metrics['stop_statistics']
    passengers_arrived = stop_stats['passengers_arrived']
    passengers_boarded = stop_stats['passengers_boarded']
    passengers_exited = stop_stats['passengers_exited']
    passengers_lost = stop_stats['passengers_lost']
    avg_wait_times = stop_stats['avg_wait_time']
    
    # Создание фигуры с двумя подграфиками
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    fig.suptitle('Фактический пассажиропоток по остановкам', 
                 fontsize=16, fontweight='bold')
    
    # Подграфик 1: Потоки пассажиров
    width = 0.2
    x = np.arange(len(stops))
    
    ax1.bar(x - 1.5*width, passengers_arrived, width, label='Прибыло на остановку', 
            alpha=0.8, color='skyblue')
    ax1.bar(x - 0.5*width, passengers_boarded, width, label='Вошло в автобус', 
            alpha=0.8, color='green')
    ax1.bar(x + 0.5*width, passengers_exited, width, label='Вышло из автобуса', 
            alpha=0.8, color='orange')
    ax1.bar(x + 1.5*width, passengers_lost, width, label='Ушло (таймаут)', 
            alpha=0.8, color='red')
    
    ax1.set_xlabel('Номер остановки', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Количество пассажиров', fontsize=12, fontweight='bold')
    ax1.set_title('Фактические потоки пассажиров', fontsize=14)
    ax1.set_xticks(x)
    ax1.set_xticklabels(stops)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Добавление аннотаций с процентом потерь
    for i, (arrived, lost) in enumerate(zip(passengers_arrived, passengers_lost)):
        if arrived > 0:
            loss_pct = lost / arrived * 100
            ax1.text(i, max(arrived, 10) + 5, f'{loss_pct:.1f}%', 
                    ha='center', fontsize=8, color='red', fontweight='bold')
    
    # Подграфик 2: Среднее время ожидания
    ax2.plot(stops, avg_wait_times, 'b-o', linewidth=2, markersize=8, label='Среднее ожидание')
    ax2.axhline(y=config['simulation']['max_wait_time'], color='r', linestyle='--', 
                linewidth=1.5, label=f'Макс. ожидание ({config["simulation"]["max_wait_time"]} мин)')
    
    ax2.set_xlabel('Номер остановки', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Время ожидания (минуты)', fontsize=12, fontweight='bold')
    ax2.set_title('Среднее время ожидания автобуса по остановкам', fontsize=14)
    ax2.set_xticks(stops)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # Добавление аннотаций с временем ожидания
    for i, (stop, wait) in enumerate(zip(stops, avg_wait_times)):
        if wait > 0:
            ax2.text(stop, wait + 0.5, f'{wait:.1f}', 
                    ha='center', fontsize=8, color='blue')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"График сохранен: {save_path}")
    else:
        plt.show()


def plot_planned_vs_actual_flow(
    metrics: Dict[str, Any],
    config: Dict[str, Any],
    save_path: str = None
):
    """
    ФАКТИЧЕСКИЙ пассажиропоток (плановый выход удален - некорректен)
    
    Args:
        metrics: метрики симуляции
        config: конфигурация модели
        save_path: путь для сохранения графика
    """
    num_stops = config['route']['num_stops']
    stops = list(range(1, num_stops + 1))
    
    # Плановые значения (из конфигурации) - только прибытие
    planned_arrival = config['passenger_flow']['lambda_arrival']
    
    # Фактические значения (из симуляции)
    stop_stats = metrics['stop_statistics']
    actual_arrival = stop_stats['passengers_arrived'][:-1]
    actual_exit = stop_stats['passengers_exited'][:-1]
    
    simulation_time = config['simulation']['simulation_time']
    
    # Нормализация для визуализации
    planned_arrival_norm = [lam * simulation_time for lam in planned_arrival]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Фактический пассажиропоток', 
                 fontsize=16, fontweight='bold')
    
    # График 1: Прибытие пассажиров
    x = np.arange(len(planned_arrival))
    width = 0.35
    
    ax1.bar(x - width/2, planned_arrival_norm, width, label='Плановое прибытие', 
            alpha=0.7, color='lightblue')
    ax1.bar(x + width/2, actual_arrival, width, label='Фактическое прибытие', 
            alpha=0.7, color='darkblue')
    
    ax1.set_xlabel('Номер остановки', fontsize=11)
    ax1.set_ylabel('Количество пассажиров', fontsize=11)
    ax1.set_title('Прибытие пассажиров', fontsize=13, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(stops[:-1])
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # График 2: Выход пассажиров
    ax2.bar(x + width/2, actual_exit, width, label='Фактический выход', 
            alpha=0.7, color='darkred')
    
    ax2.set_xlabel('Номер остановки', fontsize=11)
    ax2.set_ylabel('Количество пассажиров', fontsize=11)
    ax2.set_title('Выход пассажиров', fontsize=13, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(stops[:-1])
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
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

    # 5. Фактический пассажиропоток (НОВЫЙ ГРАФИК)
    actual_flow_path = os.path.join(output_dir, f"passenger_flow_actual_{timestamp}.png")
    plot_actual_passenger_flow(optimal_metrics, config, actual_flow_path)
    
    # 6. Сравнение планового и фактического (НОВЫЙ ГРАФИК)
    comparison_path = os.path.join(output_dir, f"passenger_flow_comparison_{timestamp}.png")
    plot_planned_vs_actual_flow(optimal_metrics, config, comparison_path)
    
    print(f"\n✅ Все графики сохранены в директорию: {output_dir}")