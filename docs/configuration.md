# Configuration

[← CLI Reference](api.md) · [Back to README](../README.md) · [Optimization →](optimization.md)

# Конфигурация симуляции

## Обзор

Конфигурация хранится в JSON-файлах (`config/`). Каждый файл определяет параметры маршрута, экономики и поведения симуляции.

## Структура JSON

```json
{
  "route": {
    "num_stops": 5,
    "bus_capacity": 50,
    "travel_time_between_stops": 5
  },
  "economics": {
    "ticket_price": 50,
    "bus_cost_per_route": 300
  },
  "passengers": {
    "arrival_rate": 10,
    "max_wait_time": 15,
    "ride_duration_mean": 20,
    "ride_duration_std": 5
  },
  "bus_release": {
    "release_time_mean": 60,
    "release_time_std": 10
  },
  "simulation": {
    "simulation_time": 480,
    "debug_mode": false,
    "console_logging": true,
    "optimization": {
      "min_intensity": 6,
      "max_intensity": 20,
      "step": 1,
      "num_runs": 5
    }
  }
}
```

## Параметры конфигурации

### route — параметры маршрута

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `num_stops` | integer | Количество остановок на маршруте | `5` |
| `bus_capacity` | integer | Вместимость автобуса (пассажиров) | `50` |
| `travel_time_between_stops` | float | Время между остановками (минуты) | `5.0` |

### economics — экономические параметры

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `ticket_price` | float | Стоимость одного билета (руб.) | `50.0` |
| `bus_cost_per_route` | float | Стоимость одного рейса автобуса (руб.) | `300.0` |

### passengers — параметры пассажиров

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `arrival_rate` | float | Интенсивность потока пассажиров (пасс./мин) | `10.0` |
| `max_wait_time` | float | Максимальное время ожидания (минуты) | `15.0` |
| `ride_duration_mean` | float | Среднее время поездки (минуты) | `20.0` |
| `ride_duration_std` | float | Стандартное отклонение времени поездки | `5.0` |

### bus_release — параметры выпуска автобусов

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `release_time_mean` | float | Средний интервал выпуска (секунды) | `60.0` |
| `release_time_std` | float | Стандартное отклонение интервала | `10.0` |

### simulation — параметры симуляции

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `simulation_time` | int | Длительность симуляции (минуты) | `480` |
| `debug_mode` | bool | Режим отладки (подробные логи) | `false` |
| `console_logging` | bool | Вывод логов в консоль | `true` |

### simulation.optimization — параметры оптимизации

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `min_intensity` | int | Минимальная интенсивность (автобусов/час) | `6` |
| `max_intensity` | int | Максимальная интенсивность (автобусов/час) | `20` |
| `step` | int | Шаг перебора интенсивности | `1` |
| `num_runs` | int | Количество прогонов для усреднения | `5` |

## Примеры конфигураций

### 1. Равномерный поток (простой тест)

```json
{
  "route": { "num_stops": 5, "bus_capacity": 50, "travel_time_between_stops": 5 },
  "economics": { "ticket_price": 50, "bus_cost_per_route": 300 },
  "passengers": { "arrival_rate": 10, "max_wait_time": 15, "ride_duration_mean": 20, "ride_duration_std": 5 },
  "bus_release": { "release_time_mean": 60, "release_time_std": 10 },
  "simulation": {
    "simulation_time": 480,
    "debug_mode": false,
    "console_logging": true,
    "optimization": { "min_intensity": 6, "max_intensity": 20, "step": 1, "num_runs": 1 }
  }
}
```

### 2. Утренний час пик

```json
{
  "route": { "num_stops": 10, "bus_capacity": 75, "travel_time_between_stops": 4 },
  "economics": { "ticket_price": 50, "bus_cost_per_route": 350 },
  "passengers": { "arrival_rate": 25, "max_wait_time": 10, "ride_duration_mean": 25, "ride_duration_std": 8 },
  "bus_release": { "release_time_mean": 45, "release_time_std": 5 },
  "simulation": {
    "simulation_time": 480,
    "debug_mode": false,
    "console_logging": true,
    "optimization": { "min_intensity": 10, "max_intensity": 30, "step": 2, "num_runs": 10 }
  }
}
```

### 3. Высоконагруженный маршрут

```json
{
  "route": { "num_stops": 15, "bus_capacity": 100, "travel_time_between_stops": 6 },
  "economics": { "ticket_price": 60, "bus_cost_per_route": 400 },
  "passengers": { "arrival_rate": 40, "max_wait_time": 20, "ride_duration_mean": 35, "ride_duration_std": 10 },
  "bus_release": { "release_time_mean": 30, "release_time_std": 8 },
  "simulation": {
    "simulation_time": 720,
    "debug_mode": false,
    "console_logging": true,
    "optimization": { "min_intensity": 15, "max_intensity": 40, "step": 2, "num_runs": 15 }
  }
}
```

## Валидация

Конфигурация валидируется через JSONSchema. Ошибки включают:

- Отрицательные значения
- Неверные типы данных
- Отсутствие обязательных полей

Пример ошибки:

```bash
❌ Ошибка загрузки конфигурации: schema validation failed:
  'num_stops' must be >= 1, got -5
```

## См. также

- [Getting Started](getting-started.md) — установка и запуск
- [CLI Reference](api.md) — параметры командной строки
- [Optimization](optimization.md) — как работает оптимизация
