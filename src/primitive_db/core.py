"""Основная логика работы с таблицами."""

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
