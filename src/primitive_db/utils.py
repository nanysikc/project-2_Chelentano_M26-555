import json


def save_metadata(filepath, data):
    """Сохраняет метаданные таблиц в JSON-файл."""
    with open(filepath, 'w', encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def load_metadata(filepath):
    """Загружает метаданные таблиц из JSON-файла."""
    try:
        with open(filepath, 'r', encoding="utf-8") as file:
            data = json.load(file)
        return data
    
    except FileNotFoundError:
        return {}


result = load_metadata("nonexistent_file.json")
print(result)