# Optimization

[← Configuration](configuration.md) · [Back to README](../README.md)

# Алгоритмы оптимизации

## Обзор

Оптимизация находится в `src/optimization/optimizer.py`. Цель — найти интенсивность выпуска автобусов, которая максимизирует прибыль.

## Метрики оптимизации

### Доход
```
Доход = Количество обслуженных пассажиров × Цена билета
```

### Расходы
```
Расходы = Количество рейсов × Стоимость одного рейса
```

### Прибыль
```
Прибыль = Доход - Расходы
```

## Алгоритм оптимизации

### 1. Перебор значений

```python
for intensity in range(min_intensity, max_intensity + 1, step):
    result = run_simulation(config, intensity)
    all_results.append(result)
```

**Параметры:**
- `min_intensity` — минимальная интенсивность (автобусов/час)
- `max_intensity` — максимальная интенсивность
- `step` — шаг перебора

### 2. Многократные прогоны

Для статистической достоверности каждый уровень интенсивности запускается `num_runs` раз:

```python
def run_simulation(config, intensity):
    total_profit = 0
    for run in range(num_runs):
        sim = Simulation(config)
        sim.run()
        total_profit += get_profit(sim.metrics)
    
    return {
        'intensity': intensity,
        'avg_profit': total_profit / num_runs,
        # ... другие метрики
    }
```

### 3. Поиск оптимальной конфигурации

```python
def find_optimal(all_results):
    return max(all_results, key=lambda x: x['avg_profit'])
```

## Пример вывода оптимизации

```
================================================================================
ОПТИМАЛЬНЫЕ РЕЗУЛЬТАТЫ:
  Интенсивность выпуска: 12 автобусов/час
  Прибыль: 45,230 руб.
  Обслужено пассажиров: 892
  Потеряно пассажиров: 47 (5.0%)
  Среднее время ожидания: 4.2 мин
  Средняя длительность поездки: 26.1 мин
  Средняя загрузка автобусов: 72%
================================================================================

Все результаты:
  Интенсивность 8  → Прибыль: 38,450 руб.
  Интенсивность 10 → Прибыль: 42,120 руб.
  Интенсивность 12 → Прибыль: 45,230 руб. ←Оптимальная интенсивность выпуска автобусов
  Интенсивность 14 → Прибыль: 44,890 руб.
  Интенсивность 16 → Прибыль: 42,310 руб.
```

## Графики оптимизации

### 1. Зависимость прибыли от интенсивности

Показывает "кривую прибыли" с пиком на оптимальном значении.

**Как читать:**
- Левее пика — не хватает автобусов (много потерянных пассажиров)
- Правее пика — лишние рейсы (высокие расходы)

### 2. Время ожидания vs интенсивность

Показывает, как увеличение числа автобусов влияет на качество сервиса.

**Тенденция:** чем больше автобусов — тем меньше время ожидания (до определённого предела).

### 3. Загрузка автобусов vs интенсивность

Показывает среднюю загрузку автобусов для разных значений интенсивности.

**Оптимальная зона:** 60-85% загрузки (не слишком пустые, не переполненные).

## Технические детали

### Функция оптимизации

```python
def optimize_bus_intensity(config):
    min_i = config['simulation']['optimization']['min_intensity']
    max_i = config['simulation']['optimization']['max_intensity']
    step = config['simulation']['optimization']['step']
    num_runs = config['simulation']['optimization']['num_runs']
    
    all_results = []
    for intensity in range(min_i, max_i + 1, step):
        result = run_simulation(config, intensity, num_runs)
        all_results.append(result)
    
    optimal = find_optimal(all_results)
    return optimal, all_results
```

### Структура результата

```python
{
    'intensity': 12,
    'avg_profit': 45230.5,
    'total_passengers': 892,
    'lost_passengers': 47,
    'avg_wait_time': 4.2,
    'avg_ride_duration': 26.1,
    'avg_load_factor': 0.72,
    'num_rides': 384
}
```

## Рекомендации по настройке

### 1. Узкий диапазон для точной настройки

```json
{
  "optimization": {
    "min_intensity": 10,
    "max_intensity": 14,
    "step": 1,
    "num_runs": 20
  }
}
```

### 2. Широкий диапазон для первоначального поиска

```json
{
  "optimization": {
    "min_intensity": 5,
    "max_intensity": 30,
    "step": 5,
    "num_runs": 5
  }
}
```

### 3. Быстрый прогон (меньше точности, быстрее)

```json
{
  "optimization": {
    "min_intensity": 8,
    "max_intensity": 20,
    "step": 4,
    "num_runs": 1
  }
}
```

## См. также

- [Configuration](configuration.md) — параметры оптимизации в JSON
- [API Reference](api.md) — запуск через CLI
- [Architecture](architecture.md) — место optimization в структуре проекта
