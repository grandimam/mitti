from abc import ABC
from abc import abstractmethod

from mitti.types import Scope
from collections.abc import Callable


class BaseRoute(ABC):
    @abstractmethod
    def match(self, scope: Scope) -> bool:
        raise NotImplementedError

    @abstractmethod
    def handle(self):
        raise NotImplementedError


class APIRoute(BaseRoute):
    def __init__(
        self,
        path: str,
        *,
        methods: list[str] | None,
        handle: Callable | None,
    ):
        self._path = path
        self._handle = handle
        self._methods = methods

    def match(self, scope: Scope) -> bool:
        pass

    def handle(self):
        pass


class Router:
    def __init__(
        self,
        *,
        routes: list[BaseRoute] | None = None,
    ) -> None:
        self._routes: list[BaseRoute] = routes if routes else []

    async def __call__(
        self,
        path: str,
        methods: list[str],
        *args,
        **kwargs,
    ):
        for route in self._routes:
            pass
