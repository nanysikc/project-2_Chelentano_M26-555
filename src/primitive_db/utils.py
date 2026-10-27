import json
from pathlib import Path

from primitive_db.constants import DATA_DIRECTORY


def save_metadata(filepath: str, data: dict):
    """Сохраняет метаданные таблиц в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def load_metadata(filepath: str):
    """Загружает метаданные таблиц из JSON-файла."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data

    except FileNotFoundError:
        return {}


def load_table_data(table_name: str) -> list:
    """Загружает записи таблицы из JSON-файла."""
    filepath = Path(DATA_DIRECTORY) / f"{table_name}.json"
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data

    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data: list):
    """Сохраняет записи таблицы в JSON-файл."""
    Path(DATA_DIRECTORY).mkdir(exist_ok=True)

    filepath = Path(DATA_DIRECTORY) / f"{table_name}.json"

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
