"""Вспомогательные функции для работы с файлами."""

import json
import os

DATA_DIR = "data"


def load_metadata(filepath: str) -> dict:
    """Загружает метаданные из JSON-файла.

    Если файл не найден — возвращает пустой словарь.
    """
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath: str, data: dict) -> None:
    """Сохраняет метаданные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def _table_path(table_name: str) -> str:
    """Путь к файлу данных таблицы: data/<table_name>.json."""
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{table_name}.json")


def load_table_data(table_name: str) -> list:
    """Загружает список записей таблицы.

    Если файла нет — возвращает пустой список.
    """
    try:
        with open(_table_path(table_name), encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data: list) -> None:
    """Сохраняет список записей таблицы в data/<table_name>.json."""
    with open(_table_path(table_name), "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
