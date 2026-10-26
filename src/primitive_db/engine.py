from primitive_db.core import create_table
from primitive_db.utils import save_metadata, load_metadata


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
            parts = command.split()
            table_name = parts[1]
            column_definitions = parts[2:]

            columns = {}

            for column in column_definitions:
                column_parts = column.split(":")
                columns[column_parts[0]] = column_parts[1]

            print(table_name)
            print(columns)
        else:
            print("Неизвестная команда. Попробуйте снова.")