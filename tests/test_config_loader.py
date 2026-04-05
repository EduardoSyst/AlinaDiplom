"""
Тесты для загрузчика конфигурации
"""
import unittest
import tempfile
import json
import os
from src.utils.config_loader import load_config, validate_config


class TestConfigLoader(unittest.TestCase):
    """Тесты для загрузчика конфигурации"""
    
    def setUp(self):
        """Создание временного файла конфигурации"""
        self.valid_config = {
            "simulation": {
                "simulation_time": 480,
                "max_wait_time": 60,
                "optimization": {
                    "min_intensity": 2,
                    "max_intensity": 20,
                    "step": 0.5
                },
                "debug_mode": False
            },
            "route": {
                "num_stops": 10,
                "travel_time_between_stops": 3,
                "bus_capacity": 16
            },
            "passenger_flow": {
                "lambda_arrival": [2.0] * 10,
                "lambda_exit": [0.5] * 9 + [8.0]
            },
            "economics": {
                "ticket_price": 30.0,
                "bus_cost_per_route": 500.0
            },
            "bus_release": {
                "release_time_std": 5.0
            }
        }
        
        # Создание временного файла
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(self.valid_config, self.temp_file)
        self.temp_file.close()
    
    def tearDown(self):
        """Удаление временного файла"""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
    
    def test_load_valid_config(self):
        """Тест загрузки валидной конфигурации"""
        config = load_config(self.temp_file.name)
        
        self.assertEqual(config['simulation']['simulation_time'], 480)
        self.assertEqual(config['route']['num_stops'], 10)
        self.assertEqual(len(config['passenger_flow']['lambda_arrival']), 10)
    
    def test_validate_valid_config(self):
        """Тест валидации валидной конфигурации"""
        try:
            validate_config(self.valid_config)
            valid = True
        except Exception:
            valid = False
        
        self.assertTrue(valid)
    
    def test_invalid_num_stops(self):
        """Тест невалидного количества остановок"""
        invalid_config = self.valid_config.copy()
        invalid_config['route']['num_stops'] = 1  # Должно быть минимум 2
        
        with self.assertRaises(Exception):
            validate_config(invalid_config)
    
    def test_mismatched_lambda_lengths(self):
        """Тест несоответствия длин массивов интенсивностей"""
        invalid_config = self.valid_config.copy()
        invalid_config['passenger_flow']['lambda_arrival'] = [2.0] * 5  # Должно быть 10
        
        with self.assertRaises(Exception):
            validate_config(invalid_config)


if __name__ == '__main__':
    unittest.main()