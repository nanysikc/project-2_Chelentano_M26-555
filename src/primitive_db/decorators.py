import time
from functools import wraps


def handle_db_errors(func):
    """Перехватывает ошибки при работе с базой данных."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: файл данных не найден")
        except KeyError as error:
            print(f"Ошибка: таблица или столбец {error} не найдены")
        except ValueError as error:
            print(f"Ошибка валидации: {error}")

    return wrapper


def confirm_action(action_name):
    """Запрашивает подтверждение перед опасной операцией."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            answer = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')

            if answer.lower() != "y":
                print("Операция отменена")
                return None

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Выводит время выполнения функции."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()

        try:
            return func(*args, **kwargs)
        finally:
            duration = time.monotonic() - start
            print(f"Функция {func.__name__} выполнилась за {duration:.3f} секунд.")

    return wrapper


def create_cacher():
    """Создаёт кэш для результатов запросов."""

    cache = {}

    def cached_call(key, func):
        """Возвращает сохранённый результат или выполняет запрос."""
        if key in cache:
            print("Результат получен из кэша")
            return cache[key]

        result = func()
        cache[key] = result

        return result

    def clear_cache():
        """Очищает сохранённые результаты."""
        cache.clear()

    return cached_call, clear_cache
