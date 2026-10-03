"""Парсеры условий WHERE, SET и списка VALUES для CRUD-команд."""

import re

VALID_TYPES = ("int", "str", "bool")


def parse_value(raw: str):
    """Преобразует строковый токен в Python-значение нужного типа.

    "Sergei" -> str, 28 -> int, true -> bool.
    Строковые значения обязательно должны быть в кавычках.
    """
    raw = raw.strip()

    # строка в одинарных или двойных кавычках -> str
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ('"', "'"):
        return raw[1:-1]

    low = raw.lower()
    if low == "true":
        return True
    if low == "false":
        return False

    # целое число
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)

    raise ValueError(
        f"Не удалось распознать значение: {raw!r} (строки должны быть в кавычках)"
    )


def parse_where(clause: str) -> dict:
    """'age = 28' -> {'age': 28}. Пустая строка -> None."""
    clause = clause.strip()
    if not clause:
        return None
    if "=" not in clause:
        raise ValueError("Неверный формат условия WHERE (нужно 'столбец = значение').")
    col, val = clause.split("=", 1)
    return {col.strip(): parse_value(val)}


def parse_set(clause: str) -> dict:
    """'age = 29' -> {'age': 29}. (То же самое, что WHERE, но для SET.)"""
    return parse_where(clause)


def parse_values(raw: str) -> list:
    """'"Sergei", 28, true' -> ['Sergei', 28, True]."""
    return [parse_value(tok) for tok in _split_commas(raw)]


def _split_commas(raw: str) -> list:
    """Разбивает строку по запятым, НЕ разрывая содержимое кавычек."""
    parts, buf, in_quotes, quote_char = [], "", False, ""
    for ch in raw:
        if ch in ('"', "'"):
            if not in_quotes:
                in_quotes, quote_char = True, ch
            elif ch == quote_char:
                in_quotes = False
            buf += ch
        elif ch == "," and not in_quotes:
            parts.append(buf)
            buf = ""
        else:
            buf += ch
    if buf.strip():
        parts.append(buf)
    return [p.strip() for p in parts if p.strip()]
