import inspect

from collections.abc import Callable
from typing import Any
from typing import get_args

from mitti.converters import _get_converter


VARS_AND_KWARGS = {
    inspect.Parameter.VAR_POSITIONAL,
    inspect.Parameter.VAR_KEYWORD,
}


class InspectorValidationMixin:
    @staticmethod
    def _missing(
        signature: inspect.Signature,
        path_parameter_names: set[str],
    ) -> None:
        missing = path_parameter_names - signature.parameters.keys()
        if missing:
            names = ", ".join(sorted(missing))
            raise ValueError(f"Path parameters missing from handler signature: {names}")

    @staticmethod
    def _args_and_empty(parameter: inspect.Parameter, annotation: Any) -> None:
        if parameter.kind in VARS_AND_KWARGS:
            raise TypeError(f"Variadic handler parameter '{parameter.name}' is not supported")
        if annotation is inspect.Parameter.empty:
            raise TypeError(f"Handler parameter '{parameter.name}' requires a type annotation")

    @staticmethod
    def _list(
        name: str,
        path_parameter_names: set[str],
    ) -> None:
        if name in path_parameter_names:
            raise TypeError(f"List handler parameter '{name}' must be a query parameter")

    @staticmethod
    def _list_item_type(name: str, annotation: Any) -> None:
        if len(get_args(annotation)) != 1:
            raise TypeError(f"List handler parameter '{name}' requires an item type")

    @staticmethod
    def _converter(
        name: str,
        annotation: Any,
        item_annotation: Any,
    ) -> Callable[[str], Any]:
        try:
            return _get_converter(item_annotation)
        except TypeError as exc:
            raise TypeError(
                f"Unsupported annotation for handler parameter '{name}': {annotation!r}"
            ) from exc

