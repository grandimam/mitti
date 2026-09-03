import re

from abc import ABC
from abc import abstractmethod

from mitti.request import Request

from collections.abc import Callable

from enum import Enum

from mitti.types import Receive
from mitti.types import Scope
from mitti.types import Send
from mitti.response import Response


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
    def match(self, scope: Scope, receive: Receive) -> Match:
        raise NotImplementedError

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
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
        self._methods = methods or ["GET"]
        self._path_regex = compile_path(self._path)

    def match(self, scope: Scope, receive: Receive) -> Match:
        request = Request(scope, receive)
        match = self._path_regex.match(request.path)
        if match and request.method in self._methods:
            return Match.FULL
        if match:
            return Match.PARTIAL
        return Match.NONE

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        request = Request(scope, receive)
        result = await self._handler(request)
        return await Response(content=result)(scope, receive, send)


class Router:
    def __init__(
            self,
            *,
            routes: list[BaseRoute] | None = None,
    ) -> None:
        self._routes: list[BaseRoute] = routes if routes else []

    @staticmethod
    def wrap_asgi(func: Callable | None = None):
        async def not_found(scope: Scope, receive: Receive, send: Send):
            response = Response(status_code=500, content="Route Not Found")
            return await response(scope, receive, send)

        async def found(scope: Scope, receive: Receive, send: Send):
            return await func(scope, receive, send)

        return found if func else not_found

    async def __call__(
            self,
            scope: Scope,
            receive: Receive,
            send: Send,
    ):
        for route in self._routes:
            match = route.match(scope, receive)
            if match == Match.PARTIAL:
                return await Response(status_code=405, content="Method Not Allowed")(scope, receive, send)
            if match == Match.FULL:
                return await Router.wrap_asgi(route)(scope, receive, send)
        return await Router.wrap_asgi()(scope, receive, send)
