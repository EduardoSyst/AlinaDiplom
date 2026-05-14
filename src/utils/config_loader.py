"""
Загрузка и валидация конфигурации
"""
import json
import os
from typing import Dict, Any
from jsonschema import validate, ValidationError


# Схема валидации JSON
CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "simulation": {
            "type": "object",
            "properties": {
                "simulation_time": {"type": "number", "minimum": 1},
                "max_wait_time": {"type": "number", "minimum": 1},
                "optimization": {
                    "type": "object",
                    "properties": {
                        "min_intensity": {"type": "number", "minimum": 0.1},
                        "max_intensity": {"type": "number", "minimum": 0.1},
                        "step": {"type": "number", "minimum": 0.01},
                        "num_runs": {"type": "integer", "minimum": 1},
                    },
                    "required": ["min_intensity", "max_intensity", "step"]
                },
                "debug_mode": {"type": "boolean"}
            },
            "required": ["simulation_time", "max_wait_time", "optimization"]
        },
        "route": {
            "type": "object",
            "properties": {
                "num_stops": {"type": "integer", "minimum": 2},
                "travel_time_between_stops": {"type": "number", "minimum": 0.1},
                "bus_capacity": {"type": "integer", "minimum": 1}
            },
            "required": ["num_stops", "travel_time_between_stops", "bus_capacity"]
        },
        "passenger_flow": {
            "type": "object",
            "properties": {
                "lambda_arrival": {
                    "type": "array",
                    "items": {"type": "number", "minimum": 0},
                    "minItems": 1
                },
                "lambda_exit": {
                    "type": "array",
                    "items": {"type": "number", "minimum": 0},
                    "minItems": 1
                }
            },
            "required": ["lambda_arrival", "lambda_exit"]
        },
        "economics": {
            "type": "object",
            "properties": {
                "ticket_price": {"type": "number", "minimum": 0},
                "bus_cost_per_route": {"type": "number", "minimum": 0}
            },
            "required": ["ticket_price", "bus_cost_per_route"]
        },
        "bus_release": {
            "type": "object",
            "properties": {
                "release_time_std": {"type": "number", "minimum": 0.1}
            },
            "required": ["release_time_std"]
        }
    },
    "required": [
        "simulation",
        "route",
        "passenger_flow",
        "economics",
        "bus_release"
    ]
}


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Загрузить конфигурацию из JSON файла
    
    Args:
        config_path: путь к файлу конфигурации
        
    Returns:
        Словарь с конфигурацией
        
    Raises:
        FileNotFoundError: если файл не найден
        json.JSONDecodeError: если файл не является валидным JSON
        ValidationError: если конфигурация не прошла валидацию
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Валидация конфигурации
    validate_config(config)
    
    # Дополнительные проверки
    num_stops = config['route']['num_stops']
    lambda_arrival = config['passenger_flow']['lambda_arrival']
    lambda_exit = config['passenger_flow']['lambda_exit']
    
    if len(lambda_arrival) != num_stops:
        raise ValidationError(
            f"lambda_arrival length ({len(lambda_arrival)}) "
            f"must be num_stops = {num_stops}"
        )

    if len(lambda_exit) != num_stops:
        raise ValidationError(
            f"lambda_exit length ({len(lambda_exit)}) "
            f"must be num_stops = {num_stops}"
        )
    
    return config


def validate_config(config: Dict[str, Any]) -> None:
    """
    Валидация конфигурации по схеме
    
    Args:
        config: словарь конфигурации
        
    Raises:
        ValidationError: если конфигурация не валидна
    """
    try:
        validate(instance=config, schema=CONFIG_SCHEMA)
    except ValidationError as e:
        raise ValidationError(f"Config validation error: {e.message}")