import re

from abc import ABC
from abc import abstractmethod

from mitti.request import BaseRequest
from mitti.request import Request

from collections.abc import Callable

from enum import Enum


class Match(Enum):
    NONE = 0
    PARTIAL = 1
    FULL = 2

PARAM_RE = re.compile(r"{([a-zA-Z_][a-zA-Z0-9_]*)}")


def compile_path(path: str) -> re.Pattern:
    pattern = PARAM_RE.sub(
        lambda match: f"(?P<{match.group(1)}>[^/]+)",
        path,
    )

    return re.compile(f"^{pattern}$")


class BaseRoute(ABC):
    @abstractmethod
    def match(self, request: BaseRequest) -> tuple[Match, dict]:
        raise NotImplementedError

    @abstractmethod
    async def handle(self, request: BaseRequest):
        raise NotImplementedError


class APIRoute(BaseRoute):
    def __init__(
        self,
        path: str,
        *,
        methods: list[str] | None,
        handler: Callable | None,
    ):
        self._path = path
        self._handler = handler
        self._methods = methods
        self._path_regex = compile_path(self._path)

    def match(self, request: BaseRequest) -> tuple[Match, dict]:
        if not isinstance(request, Request):
            raise RuntimeError("Invalid route instance")
        match_obj = self._path_regex.match(request.path)
        if match_obj:
            matched_params = match_obj.groupdict()
            if self._methods and request.method not in self._methods:
                return Match.PARTIAL, {}
            else:
                return Match.FULL, {}
        return Match.NONE, {}

    async def handle(self, request: BaseRequest):
        return await self._handler(request)


class Router:
    def __init__(
        self,
        *,
        routes: list[BaseRoute] | None = None,
    ) -> None:
        self._routes: list[BaseRoute] = routes if routes else []

    async def __call__(
        self,
        request: BaseRequest,
        *args,
        **kwargs,
    ):
        for route in self._routes:
            match, child_scope = route.match(request)
            if match.FULL:
                return await route.handle(request)
        return "Not found"
