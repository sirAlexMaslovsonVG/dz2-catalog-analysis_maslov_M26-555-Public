"""Основная логика работы с таблицами и данными."""

# Путь к файлу с метаданными таблиц
DB_META_FILE = "db_meta.json"

# Поддерживаемые типы данных
VALID_TYPES = ("int", "str", "bool")


def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
    """Создаёт таблицу в метаданных.

    Args:
        metadata: текущие метаданные (словарь таблиц).
        table_name: имя создаваемой таблицы.
        columns: список столбцов в формате "имя:тип".

    Returns:
        Обновлённый словарь metadata.
    """
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    parsed_columns = []
    for column in columns:
        name, _, col_type = column.partition(":")
        if col_type not in VALID_TYPES:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata
        parsed_columns.append({"name": name, "type": col_type})

    # ID добавляется автоматически в начало списка столбцов
    parsed_columns.insert(0, {"name": "ID", "type": "int"})

    metadata[table_name] = {"columns": parsed_columns}

    columns_view = ", ".join(f"{col['name']}:{col['type']}" for col in parsed_columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_view}')
    return metadata


def drop_table(metadata: dict, table_name: str) -> dict:
    """Удаляет таблицу из метаданных.

    Args:
        metadata: текущие метаданные.
        table_name: имя удаляемой таблицы.

    Returns:
        Обновлённый словарь metadata.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


# ---------------------------------------------------------------------------
# CRUD-операции с данными
# ---------------------------------------------------------------------------


def _get_columns(metadata: dict, table_name: str) -> list:
    """Возвращает список столбцов [{'name':..., 'type':...}, ...]."""
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    return metadata[table_name]["columns"]


def _validate_value(field_type: str, value):
    """Проверяет соответствие значения объявленному типу."""
    if field_type == "int":
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"Ожидалось значение типа int, получено: {value!r}")
    elif field_type == "str":
        if not isinstance(value, str):
            raise ValueError(f"Ожидалось значение типа str, получено: {value!r}")
    elif field_type == "bool":
        if not isinstance(value, bool):
            raise ValueError(f"Ожидалось значение типа bool, получено: {value!r}")
    else:
        raise ValueError(f"Неизвестный тип: {field_type}")
    return value


def insert(metadata: dict, table_name: str, values: list):
    """Создаёт запись. Возвращает (data, new_id)."""
    from primitive_db.utils import load_table_data

    columns = _get_columns(metadata, table_name)
    # столбцы БЕЗ ID — их количество должно совпасть с values
    field_columns = [c for c in columns if c["name"] != "ID"]

    if len(values) != len(field_columns):
        raise ValueError(
            f"Ожидалось {len(field_columns)} значений (без учёта ID), "
            f"получено {len(values)}."
        )

    record = {}
    for col, val in zip(field_columns, values):
        record[col["name"]] = _validate_value(col["type"], val)

    data = load_table_data(table_name)
    new_id = max((row.get("ID", 0) for row in data), default=0) + 1

    ordered = {"ID": new_id}
    for col in field_columns:
        ordered[col["name"]] = record[col["name"]]

    data.append(ordered)
    return data, new_id


def select(table_data: list, where_clause: dict | None = None) -> list:
    """Возвращает все записи или отфильтрованные по where_clause."""
    if not where_clause:
        return table_data
    return [
        row
        for row in table_data
        if all(row.get(k) == v for k, v in where_clause.items())
    ]


def update(table_data: list, set_clause: dict, where_clause: dict):
    """Обновляет поля подходящих записей. Возвращает (data, count)."""
    count = 0
    for row in table_data:
        if all(row.get(k) == v for k, v in where_clause.items()):
            for k, v in set_clause.items():
                row[k] = v
            count += 1
    return table_data, count


def delete(table_data: list, where_clause: dict):
    """Удаляет подходящие записи. Возвращает (data, count)."""
    kept, count = [], 0
    for row in table_data:
        if all(row.get(k) == v for k, v in where_clause.items()):
            count += 1
        else:
            kept.append(row)
    return kept, count
