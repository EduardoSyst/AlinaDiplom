"""
Сущности модели: пассажир, автобус, остановка
"""


class Passenger:
    """Пассажир"""
    
    def __init__(self, passenger_id, arrival_time, stop_id):
        self.id = passenger_id
        self.arrival_time = arrival_time  # время прибытия на остановку
        self.stop_id = stop_id  # остановка, на которой прибыл
        self.boarding_time = None  # время посадки в автобус
        self.boarding_stop = None  # остановка посадки
        self.exit_stop = None  # остановка выхода
        self.served = False  # успешно перевезен?
    
    def __repr__(self):
        return f"Passenger(id={self.id}, stop={self.stop_id}, served={self.served})"


class Bus:
    """Автобус"""
    
    def __init__(self, bus_id, release_time):
        self.id = bus_id
        self.release_time = release_time  # время выпуска на маршрут
        self.current_stop = 1  # текущая остановка
        self.passengers = []  # список пассажиров в автобусе
        self.total_passengers_served = 0  # всего перевезено пассажиров
        self.completed = False  # завершил маршрут?
        self.load_history = []  # история загрузки [(время, количество)]
    
    def add_passenger(self, passenger, current_time):
        """Посадить пассажира в автобус"""
        self.passengers.append(passenger)
        self.load_history.append((current_time, len(self.passengers)))
    
    def remove_passengers(self, count):
        """Высадить пассажиров из автобуса"""
        removed = self.passengers[:count]
        self.passengers = self.passengers[count:]
        return removed
    
    def get_current_load(self):
        """Текущая загрузка автобуса"""
        return len(self.passengers)
    
    def __repr__(self):
        return f"Bus(id={self.id}, stop={self.current_stop}, load={self.get_current_load()})"


class Stop:
    """Остановка"""
    
    def __init__(self, stop_id, lambda_arrival, lambda_exit):
        self.id = stop_id
        self.lambda_arrival = lambda_arrival  # интенсивность прибытия
        self.lambda_exit = lambda_exit  # интенсивность выхода
        self.passengers_waiting = []  # очередь пассажиров
        self.passengers_served = 0  # всего обслужено пассажиров
        self.passengers_lost = 0  # ушедшие пассажиры
    
    def add_passenger(self, passenger):
        """Добавить пассажира в очередь ожидания"""
        self.passengers_waiting.append(passenger)
    
    def remove_passenger(self, passenger):
        """Удалить пассажира из очереди"""
        if passenger in self.passengers_waiting:
            self.passengers_waiting.remove(passenger)
            return True
        return False
    
    def get_waiting_count(self):
        """Количество пассажиров в очереди"""
        return len(self.passengers_waiting)
    
    def __repr__(self):
        return f"Stop(id={self.id}, waiting={self.get_waiting_count()})"