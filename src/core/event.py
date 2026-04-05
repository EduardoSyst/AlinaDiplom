from enum import Enum

class EventType(Enum):
    PASSENGER_ARRIVAL = 1
    PASSENGER_LEAVE = 2
    BUS_RELEASE = 3
    BUS_ARRIVAL = 4

class Event:
    # Атрибуты: time, type, data