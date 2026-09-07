import re

from abc import ABC
from abc import abstractmethod
from typing import Any

from mitti.request import Request

from collections.abc import Callable

from enum import Enum

from mitti.types import Receive
from mitti.types import Scope
from mitti.types import Send
from mitti.response import Response

from mitti.inspector import inspect_handler


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


class Route(BaseRoute):
    def __init__(
            self,
            path: str,
            *,
            methods: list[str] | None,
            handler: Callable[..., Any],
    ):
        self._path = path
        self._handler = handler
        self._methods = methods or ["GET"]
        self._path_regex = compile_path(self._path)

        # Now, it's easy.
        # I need to store the handler parameters in ordered map.
        # Then, set the parameter values, and send the unpacked values

        self._path_params = {}
        self._func_params = inspect_handler(self._handler)


    def match(self, scope: Scope, receive: Receive) -> Match:
        match = self._path_regex.match(scope["path"])
        if not match:
            return Match.NONE
        self._path_params = match.groupdict() # path params values
        return Match.FULL if scope["method"] in self._methods else Match.PARTIAL

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        result = None
        status_code = 500
        try:
            # request = Request(scope, receive)
            _all_func_params = {}

            for param, param_conv in self._func_params.items():
                path_param_val = self._path_params.get(param, None)
                _all_func_params[param] = param_conv(path_param_val).convert()

            result = await self._handler(**_all_func_params)
        except Exception as e:
            print(e)
        return await Response(content=result, status_code=status_code)(scope, receive, send)


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


    def add_route(
            self,
            *,
            path: str,
            methods: list[str],
            handler: Callable,
    ):
        self._routes.append(Route(path, methods=methods, handler=handler))


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
