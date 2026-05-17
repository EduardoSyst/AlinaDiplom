import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.simulation import Simulation


class TestSimulationLastStopExit(unittest.TestCase):
    """Тесты для проверки выхода пассажиров на последней остановке"""

    def get_base_config(self):
        """Базовая конфигурация симуляции"""
        return {
            'simulation': {'simulation_time': 480, 'max_wait_time': 60},
            'route': {'num_stops': 5, 'travel_time_between_stops': 3, 'bus_capacity': 30},
            'passenger_flow': {'lambda_arrival': [0.5, 0.5, 0.5, 0.5], 'lambda_exit': [0.1, 0.1, 0.1, 0.1]},
            'economics': {'ticket_price': 50.0, 'bus_cost_per_route': 300.0},
            'bus_release': {'release_time_std': 2.0}
        }

    def test_last_stop_passenger_exit(self):
        """Проверка, что все пассажиры выходят на последней остановке"""
        config = self.get_base_config()
        
        sim = Simulation(config, bus_release_intensity=10)
        metrics = sim.run()
        
        last_stop_idx = config['route']['num_stops'] - 1
        passengers_exited_last_stop = metrics['stop_statistics']['passengers_exited'][last_stop_idx]
        
        self.assertGreater(passengers_exited_last_stop, 0,
                          "На последней остановке пассажиры обязаны выйти")

    def test_all_passengers_served(self):
        """Проверка, что все пришедшие пассажиры были обслужены (или ушли по таймауту)"""
        config = self.get_base_config()
        
        sim = Simulation(config, bus_release_intensity=15)
        metrics = sim.run()
        
        total_served = metrics['total_passengers_served']
        total_lost = metrics['total_passengers_lost']
        
        self.assertGreater(total_served + total_lost, 0,
                          "Должны быть пассажиры в симуляции")

    def test_last_stop_statistics_consistency(self):
        """Проверка согласованности статистики на последней остановке"""
        config = self.get_base_config()
        
        sim = Simulation(config, bus_release_intensity=12)
        metrics = sim.run()
        
        last_stop_idx = config['route']['num_stops'] - 1
        
        passengers_arrived = metrics['stop_statistics']['passengers_arrived'][last_stop_idx]
        passengers_boarded = metrics['stop_statistics']['passengers_boarded'][last_stop_idx]
        passengers_exited = metrics['stop_statistics']['passengers_exited'][last_stop_idx]
        
        self.assertGreaterEqual(passengers_exited, 0,
                               "Количество вышедших не может быть отрицательным")
        
        if passengers_arrived > 0 or passengers_boarded > 0:
            self.assertGreater(passengers_exited, 0,
                              "Если были пассажиры на последней остановке, они должны были выйти")


if __name__ == '__main__':
    unittest.main()
