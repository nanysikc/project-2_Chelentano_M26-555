from prettytable import PrettyTable

from primitive_db.core import create_table, drop_table, insert, list_tables, select
from primitive_db.parser import parse_values
from primitive_db.utils import load_metadata, load_table_data, save_metadata


def run():
    """Запрашивает и обрабатывает команды пользователя."""

    # Здесь загружаем metadata
    metadata = load_metadata("db_meta.json")

    while True:
        # Здесь обрабатываем команды
        command = input("Введите команду: ")
        parts = command.split()

        if not parts:
            continue

        if command == "exit":
            break
        elif command == "help":
            print("exit — завершить программу.\nhelp — показать список команд.")

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
                    save_metadata("db_meta.json", result)

        elif command == "list_tables":
            list_tables(metadata)

        elif parts[0] == "drop_table":
            if len(parts) != 2:
                print("Использование: drop_table <название_таблицы>")
                continue

            table_name = parts[1]
            result = drop_table(metadata, table_name)

            if result is not None:
                save_metadata("db_meta.json", result)
                print(f'Таблица "{table_name}" удалена')

        elif parts[0] == "insert":
            if len(parts) < 5 or parts[1] != "into" or parts[3] != "values":
                print('Использование: insert into users values ("Maria", 25)')
                continue

            table_name = parts[2]

            values_text = command.split("values", 1)[1].strip()

            try:
                values = parse_values(values_text)
                insert(metadata, table_name, values)
            except ValueError as error:
                print(f"Ошибка: {error}")

        elif parts[0] == "select":
            if len(parts) != 3 or parts[1] != "from":
                print("Использование: select from <название_таблицы>")
                continue

            table_name = parts[2]

            if table_name not in metadata:
                print("Ошибка: таблица не существует")
                continue

            table_data = load_table_data(table_name)
            records = select(table_data)

            table = PrettyTable()
            table.field_names = list(metadata[table_name].keys())

            for record in records:
                table.add_row([record[name] for name in table.field_names])

            print(table)

        else:
            print("Неизвестная команда. Попробуйте снова.")