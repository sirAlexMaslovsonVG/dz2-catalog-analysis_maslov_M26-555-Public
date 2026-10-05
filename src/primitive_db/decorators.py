"""Декораторы и замыкания для primitive_db."""

import functools
import time
from typing import Any, Callable


def handle_db_errors(func: Callable) -> Callable:
    """Централизованная обработка ошибок БД."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as error:
            print(f"Ошибка: Таблица или столбец {error} не найден.")
        except ValueError as error:
            print(f"Ошибка валидации: {error}")
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")
        return None

    return wrapper


def confirm_action(action_name: str) -> Callable:
    """Декоратор с аргументом для подтверждения опасных операций."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            prompt = f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            try:
                response = input(prompt).strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nОперация отменена.")
                return None

            if response != "y":
                print("Операция отменена.")
                if args and isinstance(args[0], (dict, list)):
                    if func.__name__ == "delete":
                        return args[0], 0
                    return args[0]
                return None

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func: Callable) -> Callable:
    """Замеряет время выполнения функции и выводит результат в консоль."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        duration = time.monotonic() - start_time
        print(f"Функция {func.__name__} выполнилась за {duration:.3f} секунд.")
        return result

    return wrapper


def create_cacher() -> Callable:
    """Создаёт функцию кэширования на основе замыкания."""
    cache: dict[Any, Any] = {}

    def cache_result(key: Any, value_func: Callable[[], Any]) -> Any:
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result

    def clear() -> None:
        """Полностью очищает кэш."""
        cache.clear()

    # Прикрепляем сброс к самой функции кэширования
    cache_result.clear = clear  # type: ignore[attr-defined]
    return cache_result
