from pathlib import Path

from primitive_db.constants import DATA_DIRECTORY, PYTHON_TYPES, VALID_TYPES
from primitive_db.decorators import (
    confirm_action,
    handle_db_errors,
    log_time,
)
from primitive_db.utils import load_table_data, save_table_data


@handle_db_errors
def create_table(metadata: dict, table_name: str, columns: dict) -> dict | None:
    """Создаёт описание новой таблицы в метаданных."""

    if table_name in metadata:
        print("Таблица уже существует")
        return

    for column_type in columns.values():
        if column_type not in VALID_TYPES:
            print("Недопустимый тип данных")
            return

    if "ID" in columns and columns["ID"] != "int":
        print("Ошибка: столбец ID должен иметь тип int")
        return

    id_columns = {"ID": "int"}
    id_columns.update(columns)

    metadata[table_name] = id_columns
    return metadata


def list_tables(metadata: dict):
    """Выводит названия всех существующих таблиц."""

    if metadata == {}:
        print("Таблиц пока нет")

    else:
        for table_name in metadata:
            print(table_name)


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: dict, table_name: str) -> dict | None:
    """Удаляет таблицу и связанный с ней JSON-файл."""

    if table_name not in metadata:
        print("Ошибка: таблица не существует")
        return None

    filepath = Path(DATA_DIRECTORY) / f"{table_name}.json"
    filepath.unlink(missing_ok=True)

    del metadata[table_name]

    return metadata


@handle_db_errors
@log_time
def insert(metadata: dict, table_name: str, values: list):
    """Добавляет новую запись в таблицу."""
    if table_name not in metadata:
        print("Ошибка: таблица не существует")
        return

    table_data = load_table_data(table_name)

    new_id = (
        max(
            (record["ID"] for record in table_data),
            default=0,
        )
        + 1
    )

    column_names = list(metadata[table_name].keys())[1:]

    if len(column_names) != len(values):
        print("Ошибка: неверное количество значений")
        return

    for column_name, value in zip(column_names, values):
        type_name = metadata[table_name][column_name]
        expected_type = PYTHON_TYPES[type_name]

        if type(value) is not expected_type:
            print(f"Ошибка: неверный тип данных для столбца {column_name}")
            return

    new_record = {"ID": new_id}

    for column_name, value in zip(column_names, values):
        new_record[column_name] = value

    table_data.append(new_record)
    save_table_data(table_name, table_data)

    print(f'Запись с ID {new_id} добавлена в таблицу "{table_name}"')
    return new_id


@handle_db_errors
@log_time
def select(table_data: list, where_clause=None):
    """Возвращает записи таблицы с учётом условия отбора."""
    if where_clause is None:
        return table_data

    column_name, value = where_clause

    return [record for record in table_data if record.get(column_name) == value]


@handle_db_errors
def update(
    table_data: list,
    column_name: str,
    new_value,
    where_column: str,
    where_value,
) -> int:
    """Изменяет записи, соответствующие условию."""
    updated_count = 0

    for record in table_data:
        if record[where_column] == where_value:
            record[column_name] = new_value
            updated_count += 1

    return updated_count


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data: list, where_column: str, where_value) -> int:
    """Удаляет записи, соответствующие условию."""
    original_count = len(table_data)

    table_data[:] = [
        record for record in table_data if record[where_column] != where_value
    ]

    return original_count - len(table_data)


@handle_db_errors
def info(metadata: dict, table_name: str):
    """Выводит информацию о структуре и записях таблицы."""
    if table_name not in metadata:
        print("Ошибка: таблица не существует")
        return

    print(f"Таблица: {table_name}")
    print("Столбцы:")

    for column_name, column_type in metadata[table_name].items():
        print(f"  {column_name}: {column_type}")

    table_data = load_table_data(table_name)
    print(f"Количество записей: {len(table_data)}")
