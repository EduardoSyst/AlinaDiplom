# Architecture

[← Getting Started](getting-started.md) · [Back to README](../README.md) · [CLI Reference →](api.md)

# Архитектура проекта

## Обзор

Проект использует **Layered Architecture** (архитектуру с уровнями) для обеспечения чёткого разделения ответственности между компонентами. Этот паттерн идеально подходит для научно-вычислительных моделей, где важно разделить бизнес-логику от инфраструктурных задач.

## Структура папок

```
src/
├── core/              # Ядро симуляции (Domain layer)
│   ├── simulation.py  # DES-движок и управление событиями
│   ├── entities.py    # Модели данных: Passenger, Bus, Stop
│   └── event.py       # Типы событий и очередь событий
├── optimization/      # Алгоритмы оптимизации (Application layer)
│   └── optimizer.py   # Поиск最佳 интенсивности выпуска
├── visualization/     # Визуализация результатов (Infrastructure layer)
│   ├── plotter.py            # Построение графиков
│   └── console_output.py     # Вывод в консоль
└── utils/             # Утилиты и хелперы
    ├── config_loader.py      # Загрузка и валидация конфигурации
    ├── logger.py             # Настройка логгера
    └── random_generator.py   # Генераторы случайных чисел

tests/                 # Модульные тесты
config/                # Примеры конфигураций JSON
output/                # Результаты симуляции
```

## Слои архитектуры

### Domain Layer (core/)

Чистая бизнес-логика без внешних зависимостей:

- **simulation.py** — DES-движок, управление очередью событий
- **entities.py** — модели: `Passenger`, `Bus`, `Stop`
- **event.py** — типы событий и приоритетная очередь

### Application Layer (optimization/)

Координирует сценарии использования:

- **optimizer.py** — перебор значений интенсивности, поиск оптимального результата

### Infrastructure Layer (visualization/, utils/)

Внешние зависимости и инструменты:

- **plotter.py** — Matplotlib для визуализации
- **config_loader.py** — загрузка JSON с валидацией через JSONSchema
- **logger.py** — настройка логгера
- **random_generator.py** — обёртки над NumPy/SciPy

### Presentation Layer (main.py)

Точка входа и CLI:

- `main.py` — парсинг аргументов, оркестрация вызовов

## Поток данных

```
1. Загрузка конфигурации
   config/*.json → config_loader.py → dict с параметрами

2. Инициализация
   dict → Simulation() → Создание остановок, планирование событий

3. Цикл симуляции
   PriorityQueue обработка событий:
   - Прибытие пассажира
   - Уход пассажира (таймаут ожидания)
   - Выпуск автобуса
   - Прибытие автобуса

4. Сбор метрик
   Метрики накапливаются в реальном времени:

5. Оптимизация
   Запуск multiple runs для разных значений интенсивности

6. Визуализация
   Генерация графиков Matplotlib → output/plots/
```

## Основные принципы

1. **Чистота домена** — модели данных (`Passenger`, `Bus`, `Stop`) не зависят от NumPy/Matplotlib
2. **Инверсия зависимостей** — application зависит от абстракций в domain, а не от реализаций
3. **Слабая связанность** — каждый слой может быть заменён без влияния на другие
4. **Тестируемость** — доменные компоненты тестируются изолированно

## Примеры кода

### Создание симуляции

```python
from src.core import Simulation, Passenger, Bus, Stop

# Загрузка конфигурации (infrastructure → domain)
config = load_config('config/example_uniform.json')

# Инициализация (domain)
simulation = Simulation(config)

# Запуск
simulation.run()

# Получение метрик
metrics = simulation.get_metrics()
```

### Добавление кастомного события

```python
from src.core.event import EventType, Event

# Создание пользовательского события
custom_event = Event(
    time=120.0,
    event_type=EventType.CUSTOM_EVENT,
    data={'message': 'Special event'}
)

# Добавление в очередь событий
simulation.events.put(custom_event)
```

## Анти-паттерны (избегать)

- ❌ Прямой доступ к `matplotlib` из `main.py`
- ❌ Зависимость `Passenger` от NumPy или Matplotlib
- ❌ Циклические зависимости (domain → application → domain)
- ❌ Жёсткая связь с конкретными реализациями визуализации

---

## См. также

- [Getting Started](getting-started.md) — установка и первый запуск
- [CLI Reference](api.md) — параметры командной строки
- [Configuration](configuration.md) — структура JSON конфигов
