import inspect

from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any
from typing import get_args
from typing import get_origin
from typing import get_type_hints

from mitti.mixins import InspectorValidationMixin


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


class Inspector(InspectorValidationMixin):

    @staticmethod
    def inspect(
        func: Callable[..., Any],
        path_params: set[str],
    ) -> OrderedDict[str, _Param]:

        signature = inspect.signature(func)
        type_hints = get_type_hints(func)

        Inspector._missing(signature, path_params)

        parameters: OrderedDict[str, _Param] = OrderedDict()
        for name, parameter in signature.parameters.items():
            annotation = type_hints.get(name, parameter.annotation)
            Inspector._args_and_empty(parameter, annotation)
            is_multi = get_origin(annotation) is list
            item_annotation = annotation

            if is_multi:
                Inspector._list(name, path_params)
                Inspector._list_item_type(name, annotation)
                item_annotation = get_args(annotation)[0]   # tuple, that's why we need 0th index

            converter = Inspector._converter(name, annotation, item_annotation)

            source = (
                ParameterSource.PATH
                if name in path_params
                else ParameterSource.QUERY
            )
            parameters[name] = _Param(
                name=name,
                source=source,
                converter=converter,
                required=parameter.default is inspect.Parameter.empty,
                multiple=is_multi,
            )

        return parameters
