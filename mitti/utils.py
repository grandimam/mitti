import inspect

from collections.abc import Callable

from pathlib import Path

def is_str(value: object) -> bool:
    return isinstance(value, str)

def is_bytes(value: object) -> bool:
    return isinstance(value, bytes)


def final(func: object) -> object:
    def wrap(*args, **kwargs):
        pass
    return wrap


def get_func_path(func: Callable):
    _path = Path(inspect.getfile(func))
