import inspect

from collections import OrderedDict

from typing import Callable
from typing import Any

from abc import abstractmethod
from abc import ABC


class BaseConverter(ABC):

    def __init__(self, value: Any) -> None:
        self._value = value

    @abstractmethod
    def convert(self) -> Any:
        raise NotImplementedError


class IntConverter(BaseConverter):

    def convert(self) -> int:
        return int(self._value)

class StrConverter(BaseConverter):

    def convert(self) -> str:
        return str(self._value)

CONVERTERS = {
    "str": StrConverter,
    "int": IntConverter,
}

def inspect_handler(func: Callable[..., Any]) -> dict[str, Any]:
    sig = inspect.signature(func)
    params = OrderedDict()

    for name, param in sig.parameters.items():
        params[name] = CONVERTERS[param.annotation.__name__]

    return params
