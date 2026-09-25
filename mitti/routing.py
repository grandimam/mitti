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

from mitti.inspector import Inspector
from mitti.inspector import ParameterSource
from mitti.exceptions import RequestValidationError


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
        self._path_parameter_names = set(PARAM_RE.findall(self._path))
        self._handler_params = Inspector.inspect(
            self._handler,
            self._path_parameter_names,
        )


    def match(self, scope: Scope, receive: Receive) -> Match:
        match = self._path_regex.match(scope["path"])
        if not match:
            return Match.NONE
        scope["path_params"] = match.groupdict()
        return Match.FULL if scope["method"] in self._methods else Match.PARTIAL

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        request = Request(scope, receive)
        path_params = scope.get("path_params", {})
        query_params = request.params
        handler_arguments = {}

        for name, parameter in self._handler_params.items():
            if parameter.source is ParameterSource.PATH:
                raw_value = path_params.get(name)
            else:
                values = query_params.get(name)
                if values and len(values) > 1 and not parameter.multiple:
                    raise RequestValidationError(
                        parameter.source.value,
                        name,
                        "expected one value",
                    )
                # query params returns an array always.
                raw_value = values[0] if values else None

            if not raw_value:
                if parameter.required:
                    raise RequestValidationError(
                        parameter.source.value,
                        name,
                        "field required",
                    )
                continue

            try:
                if parameter.multiple:
                    handler_arguments[name] = [parameter.converter(value) for value in values]
                else:
                    handler_arguments[name] = parameter.converter(raw_value)
            except (TypeError, ValueError) as exc:
                raise RequestValidationError(
                    parameter.source.value,
                    name,
                    str(exc),
                ) from exc

        result = await self._handler(**handler_arguments)
        if isinstance(result, Response):
            return await result(scope, receive, send)
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
