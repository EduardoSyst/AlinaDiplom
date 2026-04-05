"""
Текстовый вывод результатов в консоль
"""
from typing import Dict, Any, List, Tuple

def print_metrics(metrics: Dict[str, Any], prefix: str = ""):
    """
    Вывод метрик в консоль
    
    Args:
        metrics: словарь с метриками
        prefix: префикс для вывода
    """
    print(f"\n{prefix}{'='*60}")
    print(f"{prefix}МЕТРИКИ СИМУЛЯЦИИ")
    print(f"{prefix}{'='*60}")
    
    print(f"{prefix}Общие показатели:")
    print(f"{prefix}  • Время моделирования:       {metrics.get('simulation_time', 'N/A')} минут")
    print(f"{prefix}  • Выпущено автобусов:         {metrics['total_buses_released']:.1f}")
    print(f"{prefix}  • Перевезено пассажиров:      {metrics['total_passengers_served']:.1f}")
    print(f"{prefix}  • Потеряно пассажиров:         {metrics['total_passengers_lost']:.1f}")
    
    if 'lost_passenger_percentage' in metrics:
        print(f"{prefix}  • Процент потерянных:          {metrics['lost_passenger_percentage']:.2f}%")
    
    print(f"\n{prefix}Финансовые показатели:")
    print(f"{prefix}  • Выручка:                     {metrics.get('revenue', 0):,.2f} руб.")
    print(f"{prefix}  • Затраты:                     {metrics.get('costs', 0):,.2f} руб.")
    print(f"{prefix}  • Прибыль:                     {metrics['profit']:,.2f} руб.")
    
    # Если есть стандартное отклонение прибыли (несколько прогонов)
    if 'profit_std' in metrics:
        print(f"{prefix}  • Прибыль (±σ):                {metrics['profit']:,.2f} ± {metrics['profit_std']:,.2f} руб.")
    
    print(f"\n{prefix}Временные характеристики:")
    if 'avg_wait_time' in metrics:
        print(f"{prefix}  • Среднее время ожидания:      {metrics['avg_wait_time']:.2f} минут")
        print(f"{prefix}  • Стд. откл. ожидания:         {metrics.get('std_wait_time', 0):.2f} минут")
    
    if 'avg_trip_duration' in metrics:
        print(f"{prefix}  • Средняя длительность поездки: {metrics['avg_trip_duration']:.2f} минут")
        print(f"{prefix}  • Стд. откл. длительности:     {metrics.get('std_trip_duration', 0):.2f} минут")
    
    print(f"\n{prefix}Загрузка автобусов:")
    if 'avg_bus_load' in metrics:
        print(f"{prefix}  • Средняя загрузка:            {metrics['avg_bus_load']:.2f} пассажиров")
        print(f"{prefix}  • Стд. откл. загрузки:         {metrics['std_bus_load']:.2f} пассажиров")
    
    print(f"{prefix}{'='*60}\n")


def print_optimization_results(
    optimal_result: Tuple[float, Dict[str, Any]],
    all_results: List[Tuple[float, Dict[str, Any]]]
):
    """
    Вывод результатов оптимизации в консоль
    
    Args:
        optimal_result: оптимальный результат (интенсивность, метрики)
        all_results: все результаты симуляций
    """
    optimal_intensity, optimal_metrics = optimal_result
    
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "РЕЗУЛЬТАТЫ ОПТИМИЗАЦИИ" + " " * 24 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    print("🎯 ОПТИМАЛЬНЫЕ ПАРАМЕТРЫ:")
    print(f"   • Интенсивность выпуска: {optimal_intensity:.2f} автобусов/час")
    print(f"   • Интервал между автобусами: {60.0 / optimal_intensity:.2f} минут")
    print()
    
    print_metrics(optimal_metrics, prefix="   ")
    
    # Вывод топ-5 результатов
    print("\n📊 ТОП-5 ЛУЧШИХ ВАРИАНТОВ:")
    print("   " + "-" * 80)
    
    # Проверяем, есть ли стандартные отклонения
    has_std = 'profit_std' in optimal_metrics
    
    if has_std:
        print("   {:>8} {:>15} {:>12} {:>10} {:>12}".format(
            "Интенс.", "Прибыль (±σ)", "Автобусы", "Пассажиры", "Потери (%)"
        ))
    else:
        print("   {:>8} {:>12} {:>10} {:>10} {:>12}".format(
            "Интенс.", "Прибыль", "Автобусы", "Пассажиры", "Потери (%)"
        ))
    
    print("   " + "-" * 80)
    
    # Сортировка по прибыли
    sorted_results = sorted(all_results, key=lambda x: x[1]['profit'], reverse=True)[:5]
    
    for intensity, metrics in sorted_results:
        losses_pct = metrics.get('lost_passenger_percentage', 0)
        
        if has_std:
            profit_str = f"{metrics['profit']:,.0f}±{metrics['profit_std']:,.0f}"
            print("   {:>7.2f} {:>15} {:>12.1f} {:>10.1f} {:>11.2f}%".format(
                intensity,
                profit_str,
                metrics['total_buses_released'],
                metrics['total_passengers_served'],
                losses_pct
            ))
        else:
            print("   {:>7.2f} {:>12,.0f} {:>10.1f} {:>10.1f} {:>11.2f}%".format(
                intensity,
                metrics['profit'],
                metrics['total_buses_released'],
                metrics['total_passengers_served'],
                losses_pct
            ))
    
    print("   " + "-" * 80)
    
    # Анализ тенденций
    print("\n📈 АНАЛИЗ ТЕНДЕНЦИЙ:")
    
    # Минимальная и максимальная прибыль
    min_profit_result = min(all_results, key=lambda x: x[1]['profit'])
    max_profit_result = max(all_results, key=lambda x: x[1]['profit'])
    
    print(f"   • Максимальная прибыль: {max_profit_result[1]['profit']:,.0f} руб. "
          f"(интенсивность: {max_profit_result[0]:.2f})")
    print(f"   • Минимальная прибыль: {min_profit_result[1]['profit']:,.0f} руб. "
          f"(интенсивность: {min_profit_result[0]:.2f})")
    
    # Средние значения
    avg_profit = sum(m['profit'] for _, m in all_results) / len(all_results)
    print(f"   • Средняя прибыль: {avg_profit:,.0f} руб.")
    
    # Если есть несколько прогонов, показываем стабильность
    if has_std:
        avg_profit_std = sum(m.get('profit_std', 0) for _, m in all_results) / len(all_results)
        print(f"   • Среднее отклонение прибыли: {avg_profit_std:,.0f} руб.")
        print(f"   • Стабильность результатов: {'Высокая' if avg_profit_std < avg_profit * 0.1 else 'Средняя' if avg_profit_std < avg_profit * 0.25 else 'Низкая'}")
    
    print()


def print_stop_analysis(metrics: Dict[str, Any], config: Dict[str, Any], prefix: str = ""):
    """
    Вывод анализа по остановкам
    
    Args:
        metrics: метрики симуляции
        config: конфигурация
        prefix: префикс для вывода
    """
    num_stops = config['route']['num_stops']
    stop_stats = metrics['stop_statistics']
    
    print(f"\n{prefix}{'='*60}")
    print(f"{prefix}АНАЛИЗ ПО ОСТАНОВКАМ")
    print(f"{prefix}{'='*60}")
    print(f"{prefix}{'Ост.':<6} {'Прибыло':<10} {'Вошло':<10} {'Вышло':<10} {'Ушло':<10} {'Потери %':<10} {'Ожидание':<10}")
    print(f"{prefix}{'-'*60}")

    print_stop_analysis(optimal_metrics, config, prefix="   ")
    
    total_arrived = 0
    total_boarded = 0
    total_exited = 0
    total_lost = 0
    
    for i in range(num_stops):
        arrived = stop_stats['passengers_arrived'][i]
        boarded = stop_stats['passengers_boarded'][i]
        exited = stop_stats['passengers_exited'][i]
        lost = stop_stats['passengers_lost'][i]
        wait = stop_stats['avg_wait_time'][i]
        
        total_arrived += arrived
        total_boarded += boarded
        total_exited += exited
        total_lost += lost
        
        loss_pct = (lost / arrived * 100) if arrived > 0 else 0.0
        
        print(f"{prefix}{i+1:<6} {arrived:<10} {boarded:<10} {exited:<10} {lost:<10} {loss_pct:<9.1f}% {wait:<10.1f}")
    
    print(f"{prefix}{'-'*60}")
    print(f"{prefix}{'ИТОГО':<6} {total_arrived:<10} {total_boarded:<10} {total_exited:<10} {total_lost:<10}")
    print(f"{prefix}{'='*60}\n")