"""
Тесты для классов сущностей
"""
import unittest
from src.core.entities import Passenger, Bus, Stop


class TestPassenger(unittest.TestCase):
    """Тесты для класса Passenger"""
    
    def test_passenger_creation(self):
        """Тест создания пассажира"""
        passenger = Passenger(passenger_id=1, arrival_time=10.5, stop_id=3)
        
        self.assertEqual(passenger.id, 1)
        self.assertEqual(passenger.arrival_time, 10.5)
        self.assertEqual(passenger.stop_id, 3)
        self.assertIsNone(passenger.boarding_time)
        self.assertIsNone(passenger.exit_stop)
        self.assertFalse(passenger.served)
    
    def test_passenger_string_representation(self):
        """Тест строкового представления пассажира"""
        passenger = Passenger(passenger_id=1, arrival_time=10.5, stop_id=3)
        repr_str = repr(passenger)
        
        self.assertIn("Passenger", repr_str)
        self.assertIn("id=1", repr_str)


class TestBus(unittest.TestCase):
    """Тесты для класса Bus"""
    
    def test_bus_creation(self):
        """Тест создания автобуса"""
        bus = Bus(bus_id=1, release_time=0.0)
        
        self.assertEqual(bus.id, 1)
        self.assertEqual(bus.release_time, 0.0)
        self.assertEqual(bus.current_stop, 1)
        self.assertEqual(len(bus.passengers), 0)
        self.assertEqual(bus.total_passengers_served, 0)
        self.assertFalse(bus.completed)
    
    def test_bus_add_passenger(self):
        """Тест посадки пассажира"""
        bus = Bus(bus_id=1, release_time=0.0)
        passenger = Passenger(passenger_id=1, arrival_time=10.0, stop_id=1)
        
        bus.add_passenger(passenger, current_time=15.0)
        
        self.assertEqual(len(bus.passengers), 1)
        self.assertEqual(bus.passengers[0], passenger)
        self.assertEqual(len(bus.load_history), 1)
    
    def test_bus_remove_passengers(self):
        """Тест высадки пассажиров"""
        bus = Bus(bus_id=1, release_time=0.0)
        
        # Добавляем 3 пассажиров
        for i in range(3):
            passenger = Passenger(passenger_id=i+1, arrival_time=10.0, stop_id=1)
            bus.add_passenger(passenger, current_time=15.0)
        
        # Высаживаем 2 пассажиров
        removed = bus.remove_passengers(2)
        
        self.assertEqual(len(removed), 2)
        self.assertEqual(len(bus.passengers), 1)
    
    def test_bus_get_current_load(self):
        """Тест получения текущей загрузки"""
        bus = Bus(bus_id=1, release_time=0.0)
        
        self.assertEqual(bus.get_current_load(), 0)
        
        for i in range(5):
            passenger = Passenger(passenger_id=i+1, arrival_time=10.0, stop_id=1)
            bus.add_passenger(passenger, current_time=15.0)
        
        self.assertEqual(bus.get_current_load(), 5)


class TestStop(unittest.TestCase):
    """Тесты для класса Stop"""
    
    def test_stop_creation(self):
        """Тест создания остановки"""
        stop = Stop(stop_id=1, lambda_arrival=2.0, lambda_exit=1.0)
        
        self.assertEqual(stop.id, 1)
        self.assertEqual(stop.lambda_arrival, 2.0)
        self.assertEqual(stop.lambda_exit, 1.0)
        self.assertEqual(len(stop.passengers_waiting), 0)
        self.assertEqual(stop.passengers_served, 0)
        self.assertEqual(stop.passengers_lost, 0)
    
    def test_stop_add_passenger(self):
        """Тест добавления пассажира на остановку"""
        stop = Stop(stop_id=1, lambda_arrival=2.0, lambda_exit=1.0)
        passenger = Passenger(passenger_id=1, arrival_time=10.0, stop_id=1)
        
        stop.add_passenger(passenger)
        
        self.assertEqual(len(stop.passengers_waiting), 1)
        self.assertEqual(stop.passengers_waiting[0], passenger)
    
    def test_stop_remove_passenger(self):
        """Тест удаления пассажира с остановки"""
        stop = Stop(stop_id=1, lambda_arrival=2.0, lambda_exit=1.0)
        passenger = Passenger(passenger_id=1, arrival_time=10.0, stop_id=1)
        
        stop.add_passenger(passenger)
        removed = stop.remove_passenger(passenger)
        
        self.assertTrue(removed)
        self.assertEqual(len(stop.passengers_waiting), 0)
    
    def test_stop_get_waiting_count(self):
        """Тест получения количества ожидающих пассажиров"""
        stop = Stop(stop_id=1, lambda_arrival=2.0, lambda_exit=1.0)
        
        self.assertEqual(stop.get_waiting_count(), 0)
        
        for i in range(3):
            passenger = Passenger(passenger_id=i+1, arrival_time=10.0, stop_id=1)
            stop.add_passenger(passenger)
        
        self.assertEqual(stop.get_waiting_count(), 3)


if __name__ == '__main__':
    unittest.main()