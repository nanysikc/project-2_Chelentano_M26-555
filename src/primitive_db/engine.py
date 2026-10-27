from prettytable import PrettyTable
from prompt import string

from primitive_db.constants import METADATA_FILE, PYTHON_TYPES
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.decorators import create_cacher
from primitive_db.parser import parse_values, parse_where
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def run():
    """Запрашивает и обрабатывает команды пользователя."""

    # Здесь загружаем metadata
    metadata = load_metadata(METADATA_FILE)
    cached_call, clear_cache = create_cacher()

    while True:
        # Здесь обрабатываем команды
        command = string("Введите команду: ")
        parts = command.split()

        if not parts:
            continue

        if command == "exit":
            break
        elif command == "help":
            print(
                "Доступные команды:\n"
                "  help — показать справку\n"
                "  exit — завершить программу\n"
                "  create_table <name> <column:type> ... — создать таблицу\n"
                "  drop_table <name> — удалить таблицу\n"
                "  list_tables — показать таблицы\n"
                "  info <name> — информация о таблице\n"
                '  insert into <name> values ("Anna", 23) — добавить запись\n'
                "  select from <name> [where age = 23] — найти записи\n"
                "  update <name> set age = 24 where ID = 1 — изменить записи\n"
                "  delete from <name> where ID = 1 — удалить записи"
            )

        elif parts[0] == "create_table":
            if len(parts) < 2:
                print("Ошибка: укажите название таблицы")
                continue
            table_name = parts[1]
            column_definitions = parts[2:]

            columns = {}

            for column in column_definitions:
                column_parts = column.split(":")

                if len(column_parts) != 2:
                    print("Ошибка: столбец должен быть записан в формате name:type")
                    break

                if not column_parts[0] or not column_parts[1]:
                    print("Пустое название или пустой тип")
                    break

                columns[column_parts[0]] = column_parts[1]

            else:
                result = create_table(metadata, table_name, columns)

                if result is not None:
                    save_metadata(METADATA_FILE, result)
                    clear_cache()

        elif command == "list_tables":
            list_tables(metadata)

        elif parts[0] == "drop_table":
            if len(parts) != 2:
                print("Использование: drop_table <название_таблицы>")
                continue

            table_name = parts[1]
            result = drop_table(metadata, table_name)

            if result is not None:
                save_metadata(METADATA_FILE, result)
                clear_cache()
                print(f'Таблица "{table_name}" удалена')

        elif parts[0] == "insert":
            if len(parts) < 5 or parts[1] != "into" or parts[3] != "values":
                print('Использование: insert into users values ("Maria", 25)')
                continue

            table_name = parts[2]

            values_text = command.split("values", 1)[1].strip()

            try:
                values = parse_values(values_text)
                new_id = insert(metadata, table_name, values)

                if new_id is not None:
                    clear_cache()

            except ValueError as error:
                print(f"Ошибка: {error}")

        elif parts[0] == "select":
            if len(parts) < 3 or parts[1] != "from":
                print("Использование: select from users [where age = 25]")
                continue

            table_name = parts[2]

            if table_name not in metadata:
                print("Ошибка: таблица не существует")
                continue

            where_clause = None

            if len(parts) > 3:
                if parts[3] != "where":
                    print("Ошибка: неверный формат WHERE")
                    continue

                where_text = command.split("where", 1)[1]

                try:
                    where_clause = parse_where(where_text)
                except ValueError as error:
                    print(f"Ошибка: {error}")
                    continue

                if where_clause[0] not in metadata[table_name]:
                    print("Ошибка: такого столбца не существует")
                    continue

                column_name, value = where_clause
                expected_type = PYTHON_TYPES[metadata[table_name][column_name]]

                if type(value) is not expected_type:
                    print(f"Ошибка: неверный тип данных для столбца {column_name}")
                    continue

            cache_key = (table_name, where_clause)

            def execute_select():
                table_data = load_table_data(table_name)
                return select(table_data, where_clause)

            records = cached_call(cache_key, execute_select)

            table = PrettyTable()
            table.field_names = list(metadata[table_name].keys())

            for record in records:
                table.add_row([record[name] for name in table.field_names])

            print(table)

        elif parts[0] == "update":
            if len(parts) < 5 or parts[2] != "set" or "where" not in parts:
                print('Использование: update users set age = 29 where name = "Max"')
                continue

            table_name = parts[1]

            if table_name not in metadata:
                print("Ошибка: таблица не существует")
                continue

            set_text, where_text = command.split(" set ", 1)[1].split(" where ", 1)

            try:
                set_column, new_value = parse_where(set_text)
                where_column, where_value = parse_where(where_text)
            except ValueError as error:
                print(f"Ошибка: {error}")
                continue

            columns = metadata[table_name]

            if set_column not in columns or where_column not in columns:
                print("Ошибка: такого столбца не существует")
                continue

            if set_column == "ID":
                print("Ошибка: изменение ID запрещено")
                continue

            if type(new_value) is not PYTHON_TYPES[columns[set_column]]:
                print(f"Ошибка: неверный тип данных для столбца {set_column}")
                continue

            if type(where_value) is not PYTHON_TYPES[columns[where_column]]:
                print(f"Ошибка: неверный тип данных для столбца {where_column}")
                continue

            table_data = load_table_data(table_name)

            updated_count = update(
                table_data,
                set_column,
                new_value,
                where_column,
                where_value,
            )

            if updated_count is not None:
                save_table_data(table_name, table_data)

                if updated_count > 0:
                    clear_cache()

                print(f"Изменено записей: {updated_count}")

        elif parts[0] == "delete":
            if len(parts) < 7 or parts[1] != "from" or parts[3] != "where":
                print("Использование: delete from users where ID = 4")
                continue

            table_name = parts[2]

            if table_name not in metadata:
                print("Ошибка: таблица не существует")
                continue

            where_text = command.split(" where ", 1)[1]

            try:
                where_column, where_value = parse_where(where_text)
            except ValueError as error:
                print(f"Ошибка: {error}")
                continue

            columns = metadata[table_name]

            if where_column not in columns:
                print("Ошибка: такого столбца не существует")
                continue

            if type(where_value) is not PYTHON_TYPES[columns[where_column]]:
                print(f"Ошибка: неверный тип данных для столбца {where_column}")
                continue

            table_data = load_table_data(table_name)

            deleted_count = delete(table_data, where_column, where_value)

            if deleted_count is None:
                continue

            save_table_data(table_name, table_data)

            if deleted_count > 0:
                clear_cache()

            print(f"Удалено записей: {deleted_count}")

        elif parts[0] == "info":
            if len(parts) != 2:
                print("Использование: info <название_таблицы>")
                continue

            info(metadata, parts[1])

        else:
            print("Неизвестная команда. Попробуйте снова.")
