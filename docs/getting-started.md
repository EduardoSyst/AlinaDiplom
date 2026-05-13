# Getting Started

[Back to README](../README.md) · [Architecture →](architecture.md)

# Установка и запуск

## Предварительные требования

- Python 3.11 или выше
- pip (менеджер пакетов Python)
- Операционная система: Windows, Linux, macOS

## Установка

### 1. Клонирование репозитория

```bash
git clone <репозиторий>
cd AlinaDiplom
```

### 2. Создание виртуального окружения (рекомендуется)

```bash
python -m venv venv
venv\Scripts\activate    # Windows
# или
source venv/bin/activate  # Linux/macOS
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

## Первый запуск

### Базовый запуск с примером конфигурации

```bash
python main.py --config config/example_uniform.json
```

### Просмотр справки

```bash
python main.py --help
```

**Доступные параметры:**

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `--config` | Путь к JSON-файлу конфигурации | `config/example_uniform.json` |
| `--output` | Директория для результатов | `output` |
| `--no-plots` | Не создавать графики | — |
| `--no-save` | Не сохранять результаты | — |
| `--no-console-logs` | Отключить логи в консоль | — |

## Структура вывода

После запуска результаты сохраняются в директорию `output/`:

```
output/
├── logs/              # Логи выполнения
│   └── simulation_YYYYMMDD_HHMMSS.log
└── plots/             # Визуализации
    ├── profit_chart.png
    ├── wait_time_chart.png
    ├── load_chart.png
    └── ...
```

## Проверка установки

Успешный запуск с примером `example_uniform.json` должен показать:

```
✅ Конфигурация загружена: config/example_uniform.json
🚀 ЗАПУСК ОПТИМИЗАЦИИ
...
ОПТИМАЛЬНЫЕ РЕЗУЛЬТАТЫ:
  Интенсивность выпуска: X автобусов/час
  Прибыль: Y руб.
  Обслужено пассажиров: Z
...
```

## Следующие шаги

- 📖 [Architecture](architecture.md) — понимание структуры проекта
- 📊 [Configuration](configuration.md) — настройка параметров симуляции
- 🎯 [Optimization](optimization.md) — детали алгоритмов оптимизации
