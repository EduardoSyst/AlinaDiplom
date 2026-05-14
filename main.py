"""
Точка входа в программу (должен находиться в КОРНЕ проекта)
"""
import sys
import os
from pathlib import Path

# Добавляем корневую директорию в путь поиска модулей
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import argparse
from datetime import datetime

from src.utils import load_config, setup_logger
from src.optimization import optimize_bus_intensity, save_optimization_results
from src.visualization import (
    print_optimization_results,
    save_all_plots
)


def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description="Bus Simulation Model - оптимизация интенсивности выпуска автобусов"
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/example_uniform.json',
        help='Путь к файлу конфигурации (по умолчанию: config/example_uniform.json)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='output',
        help='Директория для сохранения результатов (по умолчанию: output)'
    )
    
    parser.add_argument(
        '--no-plots',
        action='store_true',
        help='Не создавать графики'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Не сохранять результаты в файлы'
    )

    parser.add_argument(
        '--no-console-logs',
        action='store_true',
        help='Отключить вывод логов от логгера в консоль (логи только в файл)'
    )
    
    return parser.parse_args()


def print_welcome():
    """Вывод приветственного сообщения"""
    border = "#" * 70
    print("\n" + border)
    print("#" + " " * 68 + "#")
    print("#" + " " * 15 + "BUS SIMULATION MODEL" + " " * 35 + "#")
    print("#" + " " * 12 + "Имитационная модель движения автобусов" + " " * 20 + "#")
    print("#" + " " * 68 + "#")
    print(border + "\n")


def print_config_summary(config: dict):
    """Вывод краткой информации о конфигурации"""
    print("[INFO] CONFIGURATION SUMMARY:")
    print(f"   * Number of stops: {config['route']['num_stops']}")
    print(f"   * Bus capacity: {config['route']['bus_capacity']} passengers")
    print(f"   * Travel time between stops: {config['route']['travel_time_between_stops']} minutes")
    print(f"   * Simulation time: {config['simulation']['simulation_time']} minutes")
    print(f"   * Max wait time: {config['simulation']['max_wait_time']} minutes")
    print(f"   * Ticket price: {config['economics']['ticket_price']} RUB")
    print(f"   * Route cost: {config['economics']['bus_cost_per_route']} RUB")
    print(f"   * Release interval std: {config['bus_release']['release_time_std']} minutes")
    print(f"   * Optimization range: {config['simulation']['optimization']['min_intensity']} - "
          f"{config['simulation']['optimization']['max_intensity']} buses/hour")
    print(f"   * Optimization step: {config['simulation']['optimization']['step']} buses/hour")
    
    # Новый параметр
    num_runs = config['simulation']['optimization'].get('num_runs', 1)
    if num_runs > 1:
        print(f"   • Количество прогонов на интенсивность: {num_runs}")
        print(f"   • Всего симуляций: {int((config['simulation']['optimization']['max_intensity'] - config['simulation']['optimization']['min_intensity']) / config['simulation']['optimization']['step'] + 1) * num_runs}")
    
    print()


def main():
    """Основная функция программы"""
    # Парсинг аргументов
    args = parse_arguments()
    
    # Приветственное сообщение
    print_welcome()
    
    # Загрузка конфигурации
    print("[START] Loading configuration...")
    try:
        config = load_config(args.config)
        print(f"[OK] Configuration loaded: {args.config}\n")
    except Exception as e:
        print(f"[ERROR] Configuration loading error: {e}")
        return
    
    # Настройка логгера
    debug_mode = config['simulation'].get('debug_mode', False)
    log_dir = os.path.join(args.output, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(
        log_dir,
        f"simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

    # Логи в консоль: по умолчанию включено, можно отключить через аргумент или конфиг
    console_logging = not args.no_console_logs
    if 'console_logging' in config['simulation']:
        console_logging = config['simulation']['console_logging']

    setup_logger(None, debug_mode=debug_mode, log_file=log_file, console_logging=console_logging)
    
    # Вывод информации о конфигурации
    print_config_summary(config)
    
    # Запуск оптимизации
    print("[START] STARTING OPTIMIZATION\n")
    
    try:
        optimal_result, all_results = optimize_bus_intensity(config)
    except Exception as e:
        print(f"[ERROR] Optimization error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Вывод результатов в консоль
    print("\n" + "=" * 70)
    print_optimization_results(optimal_result, all_results)
    print("=" * 70)
    
    # Сохранение результатов
    if not args.no_save:
        print("\n[SAVE] Saving results...")
        results_dir = os.path.join(args.output, 'results')
        save_optimization_results(optimal_result, all_results, config, results_dir)
    
    # Создание графиков
    if not args.no_plots:
        print("\n[PLOTS] Creating plots...")
        plots_dir = os.path.join(args.output, 'plots')
        save_all_plots(optimal_result, all_results, config, plots_dir)
    
    # Финальное сообщение
    print("\n" + "#" * 70)
    print("#" + " " * 68 + "#")
    print("#" + " " * 20 + "OPTIMIZATION COMPLETED" + " " * 24 + "#")
    print("#" + " " * 68 + "#")
    print("#" * 70 + "\n")
    
    print(f"[INFO] Results saved to: {args.output}")
    print(f"[LOGS] Logs saved to: {log_file}\n")


if __name__ == "__main__":
    main()