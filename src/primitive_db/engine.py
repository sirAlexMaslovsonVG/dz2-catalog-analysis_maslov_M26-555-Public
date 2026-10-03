import re
import shlex

from prettytable import PrettyTable

from primitive_db.core import (
    DB_META_FILE,
    create_table,
    delete,
    drop_table,
    insert,
    select,
    update,
)
from primitive_db.parser import parse_set, parse_values, parse_where
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help() -> None:
    """Печатает справку по командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values (<знач1>, <знач2>, ...) - создать запись"
    )
    print("<command> select from <имя_таблицы> - прочитать все записи")
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> - по условию"
    )
    print(
        "<command> update <имя_таблицы> set <столбец1> = <знач1> where <столбец> = <знач> - обновить"
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись"
    )
    print("<command> info <имя_таблицы> - информация о таблице")
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


# ---------------------------------------------------------------------------
# Обработчики CRUD-команд
# ---------------------------------------------------------------------------


def _print_select(metadata: dict, table_name: str, rows: list) -> None:
    """Вывод записей через PrettyTable."""
    columns = [c["name"] for c in metadata[table_name]["columns"]]
    table = PrettyTable()
    table.field_names = columns
    for row in rows:
        table.add_row([row.get(col) for col in columns])
    print(table)


def _handle_insert(metadata: dict, table_name: str, values_raw: str) -> None:
    values = parse_values(values_raw)
    data, new_id = insert(metadata, table_name, values)
    save_table_data(table_name, data)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')


def _handle_select(metadata: dict, table_name: str, where_raw: str | None) -> None:
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    data = load_table_data(table_name)
    where = parse_where(where_raw) if where_raw else None
    result = select(data, where)
    if not result:
        print("Записи не найдены.")
        return
    _print_select(metadata, table_name, result)


def _handle_update(
    metadata: dict, table_name: str, set_raw: str, where_raw: str
) -> None:
    data = load_table_data(table_name)
    set_clause = parse_set(set_raw)
    where = parse_where(where_raw)
    data, count = update(data, set_clause, where)
    if count:
        save_table_data(table_name, data)
        print(f'Записи в таблице "{table_name}" обновлены (затронуто: {count}).')
    else:
        print("Записи для обновления не найдены.")


def _handle_delete(metadata: dict, table_name: str, where_raw: str) -> None:
    data = load_table_data(table_name)
    where = parse_where(where_raw)
    data, count = delete(data, where)
    if count:
        save_table_data(table_name, data)
        print(f'Записи удалены из таблицы "{table_name}" (удалено: {count}).')
    else:
        print("Записи для удаления не найдены.")


def _handle_info(metadata: dict, table_name: str) -> None:
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    columns = metadata[table_name]["columns"]
    cols = ", ".join(f"{c['name']}:{c['type']}" for c in columns)
    data = load_table_data(table_name)
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {cols}")
    print(f"Количество записей: {len(data)}")


# ---------------------------------------------------------------------------
# Разбор и диспетчеризация команд
# ---------------------------------------------------------------------------


def _dispatch(user_input: str, metadata: dict) -> bool:
    """Разбирает и выполняет команду. Возвращает True, если обработано."""
    # --- простые команды без аргументов ---
    if user_input == "exit":
        raise SystemExit
    if user_input == "help":
        print_help()
        return True
    if user_input == "list_tables":
        for table_name in metadata:
            print(f"- {table_name}")
        return True

    # --- create_table / drop_table (разбор через shlex, как раньше) ---
    if user_input.startswith("create_table "):
        args = shlex.split(user_input)
        metadata = _handle_create_table(metadata, args[1:])
        save_metadata(DB_META_FILE, metadata)
        return True
    if user_input.startswith("drop_table "):
        args = shlex.split(user_input)
        metadata = _handle_drop_table(metadata, args[1:])
        save_metadata(DB_META_FILE, metadata)
        return True

    # --- insert into <table> values (...) ---
    match = re.fullmatch(r"insert\s+into\s+(\w+)\s+values\s*\((.*)\)", user_input)
    if match:
        _handle_insert(metadata, match.group(1), match.group(2))
        return True

    # --- select from <table> [where ...] ---
    match = re.fullmatch(r"select\s+from\s+(\w+)(?:\s+where\s+(.+))?", user_input)
    if match:
        _handle_select(metadata, match.group(1), match.group(2))
        return True

    # --- update <table> set ... where ... ---
    match = re.fullmatch(r"update\s+(\w+)\s+set\s+(.+?)\s+where\s+(.+)", user_input)
    if match:
        _handle_update(metadata, match.group(1), match.group(2), match.group(3))
        return True

    # --- delete from <table> where ... ---
    match = re.fullmatch(r"delete\s+from\s+(\w+)\s+where\s+(.+)", user_input)
    if match:
        _handle_delete(metadata, match.group(1), match.group(2))
        return True

    # --- info <table> ---
    match = re.fullmatch(r"info\s+(\w+)", user_input)
    if match:
        _handle_info(metadata, match.group(1))
        return True

    print(f"Функции {user_input.split()[0]} нет. Попробуйте снова.")
    return True


def run() -> None:
    """Основной цикл программы."""
    while True:
        metadata = load_metadata(DB_META_FILE)

        try:
            user_input = input(">>>Введите команду: ").strip()
        except EOFError:
            break

        if not user_input:
            continue

        try:
            _dispatch(user_input, metadata)
        except SystemExit:
            break
        except ValueError as error:
            print(f"Ошибка: {error}")
