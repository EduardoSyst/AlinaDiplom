# Архитектура: Layered Architecture

## Обзор

Layered Architecture (архитектура с уровнями) выбрана для этой имитационной модели на Python. Этот паттерн идеально подходит для проектов с четким разделением ответственности, где данные проходят через последовательные слои обработки.

Проект имеет естественную декомпозицию: загрузка конфигурации и UI (presentation) → оптимизация и управление симуляцией (application) → ядро симуляции и модели данных (domain). Layered Architecture обеспечивает простоту понимания, легкость тестирования и поддержки.

## Обоснование выбора

- **Тип проекта:** Научно-вычислительная имитационная модель на Python
- **Стек технологий:** Python 3.11+, NumPy, SciPy, Matplotlib
- **Ключевой фактор:** Четкое разделение между бизнес-логикой симуляции и инфраструктурными Concerns (визуализация, загрузка конфигурации)

## Структура папок

```
src/
├── presentation/       # UI layer — точка входа и обработка аргументов
│   ├── main.py        # Точка входа в программу
│   └── cli/           # CLI-интерфейс (если расширится)
├── application/        # Application layer — координация сценариев использования
│   ├── optimizer.py   # Оптимизация интенсивности выпуска автобусов
│   └── orchestrator.py # Оркестрация симуляции (если потребуется)
├── domain/             # Domain layer — ядро бизнес-логики и моделей
│   ├── simulation.py  # DES-движок и управление событиями
│   ├── entities.py    # Сущности: Passenger, Bus, Stop
│   └── event.py       # Типы событий и очередь событий
├── infrastructure/     # Infrastructure layer — внешние зависимости
│   ├── config.py      # Загрузка и валидация конфигурации
│   ├── logging.py     # Настройка логгера
│   └── visualization/ # Визуализация и отчеты
│       ├── plotter.py
│       └── console_output.py
└── utils/              # Cross-cutting utilities
    └── random_generator.py
```

**Примечание:** Структура адаптирована под текущую организацию кода в `src/core/`, `src/optimization/`, `src/visualization/`, `src/utils/`. Вместо полной реорганизации используется постепенная эволюция.

## Правила зависимостей

- ✅ **presentation → application** — CLI вызывает сценарии оптимизации
- ✅ **application → domain** — оркестрация использует DES-движок
- ✅ **domain → nothing** — чистая бизнес-логика без внешних зависимостей
- ✅ **infrastructure → application + domain** — реализация интерфейсов и доступ к данным
- ❌ **application → infrastructure** — приложение не должно знать о конкретных реализациях
- ❌ **domain → любой другой слой** — домен всегда независим

## Коммуникация между уровнями

- **Синхронные вызовы:** Основной поток выполнения проходит через последовательные слои
  - `main.py` → `optimizer.py` → `simulation.py` → `entities.py`
  
- **Обратный вызов (callback):** Для сбора метрик в реальном времени
  - DES-движок передает события в слой приложений для агрегации

- **Интерфейсы в domain:** Для внедрения зависимостей
  - Интерфейсы генераторов случайных чисел в `domain/`
  - Реализации — в `infrastructure/`

## Ключевые принципы

1. **Чистота домена (Domain Purity):** Модели данных (`Passenger`, `Bus`, `Stop`) и движок (`Simulation`) не зависят от внешних библиотек — только от стандартной библиотеки Python.

2. **Инверсия зависимостей:** Слой приложений зависит от абстракций (интерфейсов) в домене, а не от конкретных реализаций в infrastructure.

3. **Слабая связанность:** Каждый слой может быть заменен без влияния на другие слои (например, смена библиотеки визуализации).

4. **Тестируемость:** Доменные компоненты тестируются изолированно без UI или файловой системы.

## Примеры кода

### Пример 1: Поток данных через уровни

```python
# presentation/main.py (уровень представления)
def main():
    args = parse_arguments()
    config = load_config(args.config)  # infrastructure → domain
    
    optimal_result, all_results = optimize_bus_intensity(config)  # application → domain
    print_optimization_results(optimal_result, all_results)  # application → visualization
    
    save_results(optimal_result, all_results, config, results_dir)  # application → infrastructure

# application/optimizer.py (уровень приложений)
def optimize_bus_intensity(config):
    min_intensity = config['simulation']['optimization']['min_intensity']
    max_intensity = config['simulation']['optimization']['max_intensity']
    
    all_results = []
    for intensity in range(min_intensity, max_intensity + 1, step):
        result = run_simulation(config, intensity)  # application → domain
        all_results.append(result)
    
    return find_optimal(all_results), all_results

# domain/simulation.py (доменный уровень — чистая логика)
class Simulation:
    def __init__(self, config):
        self.config = config
        self.passengers = []
        self.buses = []
        self.events = PriorityQueue()  # Только стандартная библиотека
    
    def run(self):
        while not self.events.empty():
            event = self.events.get()
            self._process_event(event)  # Только внутренняя логика
```

### Пример 2: Правило зависимостей

```python
# ❌ Неправильно: application знает о конкретной реализации в infrastructure
from infrastructure.visualization import MatplotlibPlotter  # Зависимость от деталей

def optimize_bus_intensity(config):
    plotter = MatplotlibPlotter()  # Жесткая связь
    # ...

# ✅ Правильно: application зависит от абстракции в domain
from domain.interfaces import VisualizationInterface  # Зависимость от интерфейса

class OptimizationService:
    def __init__(self, visualization: VisualizationInterface):
        self.visualization = visualization
    
    def optimize(self, config):
        # ...
        self.visualization.generate_plots(results)  # Полиморфный вызов
```

## Анти-паттерны

- ❌ **Direct Database Access from UI:** Никогда не обращайтесь к `matplotlib` или файловой системе прямо из `main.py`. Всегда через слой приложений.

- ❌ **Domain Entities with Framework Dependencies:** Модели данных (`Passenger`, `Bus`) не должны импортировать NumPy или Matplotlib. Используйте только в `infrastructure/`.

- ❌ **Cyclical Dependencies:** Избегайте циклических зависимостей (например, `domain` → `application` → `domain`). Если возникает — выносите общую логику в отдельный модуль.

- ❌ **Fat Presentation Layer:** Точка входа (`main.py`) должна только оркестрировать вызовы. Вся бизнес-логика — в `domain/` и `application/`.

---

**Следующие шаги:**
- Используйте `/aif-plan` для создания планов реализации с соблюдением этих правил
- Применяйте `/aif-fix` при необходимости рефакторинга для улучшения слоистости
- Консультации с `/aif-review` перед внесением изменений, нарушающих правила зависимостей
