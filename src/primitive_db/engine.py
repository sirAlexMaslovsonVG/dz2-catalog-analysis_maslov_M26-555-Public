import shlex

from primitive_db.core import DB_META_FILE, create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata


def print_help() -> None:
    """Печатает справку по командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def _handle_create_table(metadata: dict, params: list[str]) -> dict:
    """Обрабатывает команду create_table с проверкой аргументов."""
    if len(params) < 2:
        value = " ".join(params) if params else "create_table"
        print(f"Некорректное значение: {value}. Попробуйте снова.")
        return metadata
    table_name, columns = params[0], params[1:]
    return create_table(metadata, table_name, columns)


def _handle_drop_table(metadata: dict, params: list[str]) -> dict:
    """Обрабатывает команду drop_table с проверкой аргументов."""
    if not params:
        print("Некорректное значение: drop_table. Попробуйте снова.")
        return metadata
    return drop_table(metadata, params[0])


def run() -> None:
    """Основной цикл программы."""
    while True:
        metadata = load_metadata(DB_META_FILE)

        try:
            user_input = input(">>>Введите команду: ")
        except EOFError:
            break

        args = shlex.split(user_input)
        if not args:
            continue

        command, *params = args

        if command == "exit":
            break
        elif command == "help":
            print_help()
        elif command == "create_table":
            metadata = _handle_create_table(metadata, params)
            save_metadata(DB_META_FILE, metadata)
        elif command == "drop_table":
            metadata = _handle_drop_table(metadata, params)
            save_metadata(DB_META_FILE, metadata)
        elif command == "list_tables":
            for table_name in metadata:
                print(f"- {table_name}")
        else:
            print(f"Функции {command} нет. Попробуйте снова.")
