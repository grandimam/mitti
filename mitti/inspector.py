import inspect

from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from datetime import datetime
from decimal import Decimal
from decimal import InvalidOperation
from enum import Enum
from typing import Any
from typing import Literal
from typing import get_args
from typing import get_origin
from typing import get_type_hints
from uuid import UUID

VARS_AND_KWARGS = {
    inspect.Parameter.VAR_POSITIONAL,
    inspect.Parameter.VAR_KEYWORD,
}


class ParameterSource(Enum):
    PATH = "path"
    QUERY = "query"


@dataclass(frozen=True)
class _Param:
    name: str
    source: ParameterSource
    converter: Callable[[str], Any]
    required: bool
    multiple: bool = False


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
    if converter is not None:
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


class HandlerInspector:
    @staticmethod
    def inspect(
        func: Callable[..., Any],
        path_parameter_names: set[str],
    ) -> OrderedDict[str, _Param]:

        signature = inspect.signature(func)
        type_hints = get_type_hints(func)

        missing_path_parameters = path_parameter_names - signature.parameters.keys()
        if missing_path_parameters:
            names = ", ".join(sorted(missing_path_parameters))
            raise ValueError(f"Path parameters missing from handler signature: {names}")

        parameters: OrderedDict[str, _Param] = OrderedDict()
        for name, parameter in signature.parameters.items():
            if parameter.kind in VARS_AND_KWARGS:
                raise TypeError(f"Variadic handler parameter '{name}' is not supported")

            annotation = type_hints.get(name, parameter.annotation)
            if annotation is inspect.Parameter.empty:
                raise TypeError(f"Handler parameter '{name}' requires a type annotation")

            multiple = get_origin(annotation) is list
            if multiple and name in path_parameter_names:
                raise TypeError(f"List handler parameter '{name}' must be a query parameter")
            item_annotation = annotation
            if multiple:
                args = get_args(annotation)
                if len(args) != 1:
                    raise TypeError(f"List handler parameter '{name}' requires an item type")
                item_annotation = args[0]
            try:
                converter = _get_converter(item_annotation)
            except TypeError as exc:
                raise TypeError(
                    f"Unsupported annotation for handler parameter '{name}': {annotation!r}"
                ) from exc

            source = (
                ParameterSource.PATH
                if name in path_parameter_names
                else ParameterSource.QUERY
            )
            parameters[name] = _Param(
                name=name,
                source=source,
                converter=converter,
                required=parameter.default is inspect.Parameter.empty,
                multiple=multiple,
            )

        return parameters
