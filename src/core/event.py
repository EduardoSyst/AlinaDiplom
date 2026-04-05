"""
События для дискретно-событийной симуляции
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict


class EventType(Enum):
    """Типы событий"""
    PASSENGER_ARRIVAL = 1  # Прибытие пассажира на остановку
    PASSENGER_LEAVE = 2    # Уход пассажира из-за долгого ожидания
    BUS_RELEASE = 3        # Выпуск автобуса на маршрут
    BUS_ARRIVAL = 4        # Прибытие автобуса на остановку


@dataclass(order=True)
class Event:
    """Событие симуляции"""
    time: float  # время события
    type: EventType = field(compare=False)  # тип события
    data: Dict[str, Any] = field(default_factory=dict, compare=False)  # данные события
    
    def __post_init__(self):
        # Для сортировки в heapq: сначала по времени, затем по типу
        pass
    
    def __repr__(self):
        return f"Event(time={self.time:.2f}, type={self.type.name}, data={self.data})"