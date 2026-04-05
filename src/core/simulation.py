"""
Дискретно-событийная симуляция движения автобусов
"""
import heapq
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime

from .entities import Passenger, Bus, Stop
from .event import Event, EventType
from ..utils import (
    truncated_normal,
    poisson,
    exponential,
    get_logger
)


class Simulation:
    """Дискретно-событийная симуляция"""
    
    def __init__(self, config: Dict[str, Any], bus_release_intensity: float):
        """
        Инициализация симуляции
        
        Args:
            config: конфигурация модели
            bus_release_intensity: интенсивность выпуска автобусов (автобусов в час)
        """
        self.config = config
        self.bus_release_intensity = bus_release_intensity
        
        # Параметры симуляции
        self.simulation_time = config['simulation']['simulation_time']
        self.max_wait_time = config['simulation']['max_wait_time']
        self.debug_mode = config['simulation'].get('debug_mode', False)
        self.travel_time = config['route']['travel_time_between_stops']
        self.bus_capacity = config['route']['bus_capacity']
        self.num_stops = config['route']['num_stops']
        self.ticket_price = config['economics']['ticket_price']
        self.bus_cost = config['economics']['bus_cost_per_route']
        self.release_std = config['bus_release']['release_time_std']
        
        # Среднее время между выпусками (в минутах)
        self.release_mean = 60.0 / bus_release_intensity
        
        # Остановки
        self.stops: List[Stop] = []
        for i in range(self.num_stops):
            stop = Stop(
                stop_id=i + 1,
                lambda_arrival=config['passenger_flow']['lambda_arrival'][i],
                lambda_exit=config['passenger_flow']['lambda_exit'][i]
            )
            self.stops.append(stop)
        
        # Автобусы
        self.buses: Dict[int, Bus] = {}
        self.next_bus_id = 1
        
        # События
        self.event_queue = []
        self.current_time = 0.0
        
        # Метрики
        self.metrics = {
            'total_passengers_served': 0,
            'total_passengers_lost': 0,
            'total_buses_released': 0,
            'wait_times': [],  # время ожидания каждого пассажира
            'trip_durations': [],  # длительность поездки каждого пассажира
            'bus_loads': [],  # загрузка автобусов в моменты времени
            'passenger_events': []  # для детального лога
        }
        
        # Счетчики
        self.passenger_counter = 1
        
        # Логгер
        self.logger = get_logger(__name__)
        
        # Инициализация событий
        self._initialize_events()
    
    def _initialize_events(self):
        """Инициализация начальных событий"""
        # Запланировать первый выпуск автобуса
        first_release_time = truncated_normal(self.release_mean, self.release_std)
        if first_release_time <= self.simulation_time:
            event = Event(
                time=first_release_time,
                type=EventType.BUS_RELEASE,
                data={}
            )
            heapq.heappush(self.event_queue, event)
            if self.debug_mode:
                self.logger.debug(f"Scheduled first bus release at t={first_release_time:.2f}")
        
        # Запланировать прибытия пассажиров на все остановки
        for stop in self.stops:
            if stop.lambda_arrival > 0:
                next_arrival = exponential(stop.lambda_arrival)
                if next_arrival <= self.simulation_time:
                    event = Event(
                        time=next_arrival,
                        type=EventType.PASSENGER_ARRIVAL,
                        data={'stop_id': stop.id}
                    )
                    heapq.heappush(self.event_queue, event)
                    if self.debug_mode:
                        self.logger.debug(
                            f"Scheduled first passenger arrival at stop {stop.id} "
                            f"at t={next_arrival:.2f}"
                        )
    
    def run(self) -> Dict[str, Any]:
        """
        Запуск симуляции
        
        Returns:
            Словарь с метриками
        """
        self.logger.info(
            f"Starting simulation with bus release intensity = "
            f"{self.bus_release_intensity:.2f} buses/hour"
        )
        
        # Основной цикл обработки событий
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.time
            
            # Если превышено время симуляции, завершаем
            if self.current_time > self.simulation_time:
                break
            
            # Обработка события в зависимости от типа
            if event.type == EventType.PASSENGER_ARRIVAL:
                self._process_passenger_arrival(event)
            elif event.type == EventType.PASSENGER_LEAVE:
                self._process_passenger_leave(event)
            elif event.type == EventType.BUS_RELEASE:
                self._process_bus_release(event)
            elif event.type == EventType.BUS_ARRIVAL:
                self._process_bus_arrival(event)
        
        # Завершение симуляции
        self._finalize_simulation()
        
        return self.metrics
    
    def _process_passenger_arrival(self, event: Event):
        """Обработка прибытия пассажира на остановку"""
        stop_id = event.data['stop_id']
        stop = self.stops[stop_id - 1]
        
        # Создание нового пассажира
        passenger = Passenger(
            passenger_id=self.passenger_counter,
            arrival_time=self.current_time,
            stop_id=stop_id
        )
        self.passenger_counter += 1
        
        # Добавление пассажира в очередь остановки
        stop.add_passenger(passenger)
        
        # Запланировать следующее прибытие пассажира на эту остановку
        if stop.lambda_arrival > 0:
            next_arrival_time = self.current_time + exponential(stop.lambda_arrival)
            if next_arrival_time <= self.simulation_time:
                next_event = Event(
                    time=next_arrival_time,
                    type=EventType.PASSENGER_ARRIVAL,
                    data={'stop_id': stop_id}
                )
                heapq.heappush(self.event_queue, next_event)
        
        # Запланировать уход пассажира, если он долго ждет
        leave_time = self.current_time + self.max_wait_time
        if leave_time <= self.simulation_time:
            leave_event = Event(
                time=leave_time,
                type=EventType.PASSENGER_LEAVE,
                data={
                    'stop_id': stop_id,
                    'passenger_id': passenger.id
                }
            )
            heapq.heappush(self.event_queue, leave_event)
        
        if self.debug_mode:
            self.logger.debug(
                f"Passenger {passenger.id} arrived at stop {stop_id} at t={self.current_time:.2f}. "
                f"Queue size: {stop.get_waiting_count()}"
            )
    
    def _process_passenger_leave(self, event: Event):
        """Обработка ухода пассажира из-за долгого ожидания"""
        stop_id = event.data['stop_id']
        passenger_id = event.data['passenger_id']
        stop = self.stops[stop_id - 1]
        
        # Найти пассажира в очереди
        passenger = None
        for p in stop.passengers_waiting:
            if p.id == passenger_id:
                passenger = p
                break
        
        if passenger:
            # Удалить пассажира из очереди
            stop.remove_passenger(passenger)
            stop.passengers_lost += 1
            self.metrics['total_passengers_lost'] += 1
            
            if self.debug_mode:
                wait_time = self.current_time - passenger.arrival_time
                self.logger.debug(
                    f"Passenger {passenger_id} left stop {stop_id} after waiting "
                    f"{wait_time:.2f} minutes"
                )
    
    def _process_bus_release(self, event: Event):
        """Обработка выпуска автобуса на маршрут"""
        # Создание нового автобуса
        bus = Bus(
            bus_id=self.next_bus_id,
            release_time=self.current_time
        )
        self.buses[self.next_bus_id] = bus
        self.next_bus_id += 1
        self.metrics['total_buses_released'] += 1
        
        # Запланировать прибытие автобуса на первую остановку (мгновенно)
        arrival_event = Event(
            time=self.current_time,
            type=EventType.BUS_ARRIVAL,
            data={
                'bus_id': bus.id,
                'stop_id': 1
            }
        )
        heapq.heappush(self.event_queue, arrival_event)
        
        # Запланировать следующий выпуск автобуса
        next_release_time = self.current_time + truncated_normal(
            self.release_mean,
            self.release_std
        )
        if next_release_time <= self.simulation_time:
            next_event = Event(
                time=next_release_time,
                type=EventType.BUS_RELEASE,
                data={}
            )
            heapq.heappush(self.event_queue, next_event)
        
        if self.debug_mode:
            self.logger.debug(
                f"Bus {bus.id} released at t={self.current_time:.2f}. "
                f"Next release at t={next_release_time:.2f}"
            )
    
    def _process_bus_arrival(self, event: Event):
        """Обработка прибытия автобуса на остановку"""
        bus_id = event.data['bus_id']
        stop_id = event.data['stop_id']
        bus = self.buses[bus_id]
        stop = self.stops[stop_id - 1]
        
        if self.debug_mode:
            self.logger.debug(
                f"Bus {bus_id} arrived at stop {stop_id} at t={self.current_time:.2f}. "
                f"Load: {bus.get_current_load()}/{self.bus_capacity}, "
                f"Waiting: {stop.get_waiting_count()}"
            )
        
        # 1. ВЫХОД ПАССАЖИРОВ: случайное количество по пуассону
        exiting_count = 0
        if stop.lambda_exit > 0 and bus.get_current_load() > 0:
            exiting_count = min(
                poisson(stop.lambda_exit),
                bus.get_current_load()
            )
            
            if exiting_count > 0:
                exited_passengers = bus.remove_passengers(exiting_count)
                for passenger in exited_passengers:
                    passenger.served = True
                    passenger.exit_stop = stop_id
                    
                    if passenger.boarding_time is not None:
                        trip_duration = self.current_time - passenger.boarding_time
                        self.metrics['trip_durations'].append(trip_duration)
                        self.metrics['total_passengers_served'] += 1
        
        # 2. ПОСАДКА ПАССАЖИРОВ: ВСЕ из очереди (ограничено вместимостью)
        available_seats = self.bus_capacity - bus.get_current_load()
        boarding_count = min(available_seats, stop.get_waiting_count())
        
        if boarding_count > 0:
            boarded_passengers = stop.passengers_waiting[:boarding_count]
            
            for passenger in boarded_passengers:
                passenger.boarding_time = self.current_time
                passenger.boarding_stop = stop_id
                bus.add_passenger(passenger, self.current_time)
                
                # Расчет времени ожидания
                wait_time = self.current_time - passenger.arrival_time
                self.metrics['wait_times'].append(wait_time)
            
            # Удаление посаженных из очереди
            stop.passengers_waiting = stop.passengers_waiting[boarding_count:]
            stop.passengers_served += boarding_count
        
        # Сохранение загрузки для метрик
        self.metrics['bus_loads'].append(bus.get_current_load())
        
        if self.debug_mode:
            self.logger.debug(
                f"Bus {bus_id} at stop {stop_id}: "
                f"{exiting_count} exited, {boarding_count} boarded. "
                f"New load: {bus.get_current_load()}/{self.bus_capacity}, "
                f"Remaining queue: {stop.get_waiting_count()}"
            )
        
        # 3. Движение к следующей остановке
        if stop_id < self.num_stops:
            next_stop_id = stop_id + 1
            arrival_time = self.current_time + self.travel_time
            
            if arrival_time <= self.simulation_time:
                next_event = Event(
                    time=arrival_time,
                    type=EventType.BUS_ARRIVAL,
                    data={'bus_id': bus_id, 'stop_id': next_stop_id}
                )
                heapq.heappush(self.event_queue, next_event)
        else:
            bus.completed = True
            if self.debug_mode:
                self.logger.debug(f"Bus {bus_id} completed route at t={self.current_time:.2f}")
            """Обработка прибытия автобуса на остановку"""
            bus_id = event.data['bus_id']
            stop_id = event.data['stop_id']
            bus = self.buses[bus_id]
            stop = self.stops[stop_id - 1]
            
            if self.debug_mode:
                self.logger.debug(
                    f"Bus {bus_id} arrived at stop {stop_id} at t={self.current_time:.2f}. "
                    f"Load: {bus.get_current_load()}/{self.bus_capacity}"
                )
            
            # 1. Выход пассажиров из автобуса
            exiting_count = 0
            if stop.lambda_exit > 0 and bus.get_current_load() > 0:
                exiting_count = min(
                    poisson(stop.lambda_exit),
                    bus.get_current_load()
                )
                
                if exiting_count > 0:
                    exited_passengers = bus.remove_passengers(exiting_count)
                    for passenger in exited_passengers:
                        passenger.served = True
                        passenger.exit_stop = stop_id
                        
                        # Расчет длительности поездки
                        if passenger.boarding_time is not None:
                            trip_duration = self.current_time - passenger.boarding_time
                            self.metrics['trip_durations'].append(trip_duration)
                            self.metrics['total_passengers_served'] += 1
            
            # 2. Посадка пассажиров в автобус
            boarding_count = 0
            available_seats = self.bus_capacity - bus.get_current_load()
            
            if available_seats > 0 and stop.get_waiting_count() > 0:
                # Определяем, сколько пассажиров хочет войти
                desired_boarding = poisson(stop.lambda_arrival)
                
                # Ограничиваем доступными местами и количеством ожидающих
                actual_boarding = min(
                    desired_boarding,
                    available_seats,
                    stop.get_waiting_count()
                )
                
                # Посадка пассажиров
                boarded_passengers = stop.passengers_waiting[:actual_boarding]
                for passenger in boarded_passengers:
                    passenger.boarding_time = self.current_time
                    passenger.boarding_stop = stop_id
                    bus.add_passenger(passenger, self.current_time)
                    
                    # Расчет времени ожидания
                    wait_time = self.current_time - passenger.arrival_time
                    self.metrics['wait_times'].append(wait_time)
                    
                    boarding_count += 1
                
                # Удаление посаженных пассажиров из очереди остановки
                stop.passengers_waiting = stop.passengers_waiting[actual_boarding:]
                stop.passengers_served += boarding_count
            
            # Сохранение загрузки автобуса для метрик
            self.metrics['bus_loads'].append(bus.get_current_load())
            
            if self.debug_mode:
                self.logger.debug(
                    f"Bus {bus_id} at stop {stop_id}: "
                    f"{exiting_count} exited, {boarding_count} boarded. "
                    f"New load: {bus.get_current_load()}/{self.bus_capacity}"
                )
            
            # 3. Планирование движения к следующей остановке
            if stop_id < self.num_stops:
                next_stop_id = stop_id + 1
                arrival_time = self.current_time + self.travel_time
                
                # Автобус продолжает движение только если не превышено время симуляции
                if arrival_time <= self.simulation_time:
                    next_event = Event(
                        time=arrival_time,
                        type=EventType.BUS_ARRIVAL,
                        data={
                            'bus_id': bus_id,
                            'stop_id': next_stop_id
                        }
                    )
                    heapq.heappush(self.event_queue, next_event)
            else:
                # Автобус достиг конечной остановки
                bus.completed = True
                if self.debug_mode:
                    self.logger.debug(
                        f"Bus {bus_id} completed route at t={self.current_time:.2f}"
                    )
    
    def _finalize_simulation(self):
        """Финализация симуляции и расчет итоговых метрик"""
        logger = get_logger(__name__)

        logger.debug("Simulation completed")
        
        # Расчет дополнительных метрик
        if self.metrics['wait_times']:
            self.metrics['avg_wait_time'] = np.mean(self.metrics['wait_times'])
            self.metrics['std_wait_time'] = np.std(self.metrics['wait_times'])
        else:
            self.metrics['avg_wait_time'] = 0
            self.metrics['std_wait_time'] = 0
        
        if self.metrics['trip_durations']:
            self.metrics['avg_trip_duration'] = np.mean(self.metrics['trip_durations'])
            self.metrics['std_trip_duration'] = np.std(self.metrics['trip_durations'])
        else:
            self.metrics['avg_trip_duration'] = 0
            self.metrics['std_trip_duration'] = 0
        
        if self.metrics['bus_loads']:
            self.metrics['avg_bus_load'] = np.mean(self.metrics['bus_loads'])
            self.metrics['std_bus_load'] = np.std(self.metrics['bus_loads'])
        else:
            self.metrics['avg_bus_load'] = 0
            self.metrics['std_bus_load'] = 0
        
        # Расчет прибыли
        revenue = self.metrics['total_passengers_served'] * self.ticket_price
        costs = self.metrics['total_buses_released'] * self.bus_cost
        self.metrics['profit'] = revenue - costs
        self.metrics['revenue'] = revenue
        self.metrics['costs'] = costs
        
        # Процент потерянных пассажиров
        total_arrivals = (
            self.metrics['total_passengers_served'] +
            self.metrics['total_passengers_lost']
        )
        if total_arrivals > 0:
            self.metrics['lost_passenger_percentage'] = (
                self.metrics['total_passengers_lost'] / total_arrivals * 100
            )
        else:
            self.metrics['lost_passenger_percentage'] = 0.0
        
        # Вывод итоговых метрик
        self.logger.debug(f"Total buses released: {self.metrics['total_buses_released']}")
        self.logger.debug(f"Total passengers served: {self.metrics['total_passengers_served']}")
        self.logger.debug(f"Total passengers lost: {self.metrics['total_passengers_lost']}")
        self.logger.debug(f"Average wait time: {self.metrics['avg_wait_time']:.2f} minutes")
        self.logger.debug(f"Average trip duration: {self.metrics['avg_trip_duration']:.2f} minutes")
        self.logger.debug(f"Average bus load: {self.metrics['avg_bus_load']:.2f}")
        self.logger.debug(f"Profit: {self.metrics['profit']:.2f}")