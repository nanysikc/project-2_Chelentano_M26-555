from primitive_db.utils import load_table_data, save_table_data


def create_table(metadata: dict, table_name: str, columns: dict) -> dict | None:
    """Создаёт описание новой таблицы в метаданных."""

    if table_name in metadata:
        print("Таблица уже существует")
        return

    valid_types = ("int", "str", "bool")

    for column_type in columns.values():
        if column_type not in valid_types:
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


def drop_table(metadata: dict, table_name: str) -> dict | None:
    """Удаляет описание таблицы из метаданных."""

    if table_name not in metadata:
        print("Ошибка: таблица не существует")
        return None

    del metadata[table_name]

    return metadata


def insert(metadata: dict, table_name: str, values: list):
    """Добавляет новую запись в таблицу."""
    if table_name not in metadata:
        print("Ошибка: таблица не существует")
        return

    table_data = load_table_data(table_name)

    new_id = max(
        (record["ID"] for record in table_data),
        default=0,
    ) + 1

    column_names = list(metadata[table_name].keys())[1:]

    if len(column_names) != len(values):
        print("Ошибка: неверное количество значений")
        return

    python_types = {
        "int": int,
        "str": str,
        "bool": bool,
    }

    for column_name, value in zip(column_names, values):
        type_name = metadata[table_name][column_name]
        expected_type = python_types[type_name]

        if type(value) is not expected_type:
            print(f"Ошибка: неверный тип данных для столбца {column_name}")
            return

    new_record = {"ID": new_id}

    for column_name, value in zip(column_names, values):
        new_record[column_name] = value

    table_data.append(new_record)
    save_table_data(table_name, table_data)

    print(f'Запись с ID {new_id} добавлена в таблицу "{table_name}"')


def select(table_data: list, where_clause=None):
    """Возвращает записи таблицы с учётом условия отбора."""
    if where_clause is None:
        return table_data