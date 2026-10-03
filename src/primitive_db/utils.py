"""Вспомогательные функции для работы с файлами."""

import json


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
