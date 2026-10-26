def create_table(metadata: dict, table_name: str, columns: dict):
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