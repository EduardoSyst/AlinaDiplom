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
    
    return parser.parse_args()


def print_welcome():
    """Вывод приветственного сообщения"""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + " " * 15 + "BUS SIMULATION MODEL" + " " * 35 + "█")
    print("█" + " " * 12 + "Имитационная модель движения автобусов" + " " * 20 + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70 + "\n")


def print_config_summary(config: dict):
    """Вывод краткой информации о конфигурации"""
    print("📋 ИНФОРМАЦИЯ О КОНФИГУРАЦИИ:")
    print(f"   • Количество остановок: {config['route']['num_stops']}")
    print(f"   • Вместимость автобуса: {config['route']['bus_capacity']} пассажиров")
    print(f"   • Время между остановками: {config['route']['travel_time_between_stops']} минут")
    print(f"   • Время моделирования: {config['simulation']['simulation_time']} минут")
    print(f"   • Макс. время ожидания: {config['simulation']['max_wait_time']} минут")
    print(f"   • Стоимость билета: {config['economics']['ticket_price']} руб.")
    print(f"   • Стоимость рейса: {config['economics']['bus_cost_per_route']} руб.")
    print(f"   • Стд. откл. интервала выпуска: {config['bus_release']['release_time_std']} минут")
    print(f"   • Диапазон оптимизации: {config['simulation']['optimization']['min_intensity']} - "
          f"{config['simulation']['optimization']['max_intensity']} автобусов/час")
    print(f"   • Шаг оптимизации: {config['simulation']['optimization']['step']} автобусов/час")
    print()


def main():
    """Основная функция программы"""
    # Парсинг аргументов
    args = parse_arguments()
    
    # Приветственное сообщение
    print_welcome()
    
    # Загрузка конфигурации
    print("⏳ Загрузка конфигурации...")
    try:
        config = load_config(args.config)
        print(f"✅ Конфигурация загружена: {args.config}\n")
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        return
    
    # Настройка логгера
    debug_mode = config['simulation'].get('debug_mode', False)
    log_dir = os.path.join(args.output, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(
        log_dir,
        f"simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    setup_logger(None, debug_mode=debug_mode, log_file=log_file)
    
    # Вывод информации о конфигурации
    print_config_summary(config)
    
    # Запуск оптимизации
    print("🚀 ЗАПУСК ОПТИМИЗАЦИИ\n")
    
    try:
        optimal_result, all_results = optimize_bus_intensity(config)
    except Exception as e:
        print(f"❌ Ошибка во время оптимизации: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Вывод результатов в консоль
    print("\n" + "=" * 70)
    print_optimization_results(optimal_result, all_results)
    print("=" * 70)
    
    # Сохранение результатов
    if not args.no_save:
        print("\n💾 Сохранение результатов...")
        results_dir = os.path.join(args.output, 'results')
        save_optimization_results(optimal_result, all_results, config, results_dir)
    
    # Создание графиков
    if not args.no_plots:
        print("\n📊 Создание графиков...")
        plots_dir = os.path.join(args.output, 'plots')
        save_all_plots(optimal_result, all_results, config, plots_dir)
    
    # Финальное сообщение
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + " " * 20 + "ОПТИМИЗАЦИЯ ЗАВЕРШЕНА" + " " * 27 + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70 + "\n")
    
    print(f"📁 Результаты сохранены в: {args.output}")
    print(f"📄 Логи сохранены в: {log_file}\n")


if __name__ == "__main__":
    main()