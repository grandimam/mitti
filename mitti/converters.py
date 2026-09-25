from collections.abc import Callable
from datetime import date
from datetime import datetime
from decimal import Decimal
from decimal import InvalidOperation
from enum import Enum
from typing import Any
from typing import Literal
from typing import get_args
from typing import get_origin
from uuid import UUID


def _convert_bool(value: str) -> bool:
    normalized = value.lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError("expected a boolean value")


def _convert_decimal(value: str) -> Decimal:
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("expected a decimal value") from exc


CONVERTERS: dict[type[Any], Callable[[str], Any]] = {
    str: str,
    int: int,
    float: float,
    bool: _convert_bool,
    UUID: UUID,
    date: date.fromisoformat,
    datetime: datetime.fromisoformat,
    Decimal: _convert_decimal,
}


def _get_converter(annotation: Any) -> Callable[[str], Any]:
    converter = CONVERTERS.get(annotation)
    if converter:
        return converter

    if isinstance(annotation, type) and issubclass(annotation, Enum):
        choices = [(member.value, member) for member in annotation]
    elif get_origin(annotation) is Literal:
        choices = [(value, value) for value in get_args(annotation)]
    else:
        raise TypeError(f"Unsupported annotation: {annotation!r}")

    converters = [(_get_converter(type(value)), value, result)
                  for value, result in choices]

    def convert_choice(raw: str) -> Any:
        for convert, value, result in converters:
            try:
                converted = convert(raw)
            except (TypeError, ValueError):
                continue
            if type(converted) is type(value) and converted == value:
                return result
        allowed = ", ".join(repr(value) for value, _ in choices)
        raise ValueError(f"expected one of: {allowed}")

    return convert_choice


