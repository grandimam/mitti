from __future__ import annotations

import copy

from mitti.types import Scope
from mitti.types import Receive
from mitti.types import Send

from mitti.routing import BaseRoute
from mitti.request import Request
from mitti.response import Response

from mitti.routing import Router


class Mitti:
    def __init__(
        self,
        *,
        routes: list[BaseRoute] | None = None,
    ) -> None:
        if not routes:
            routes: list[BaseRoute] = []
        self._routes = routes
        self._router = Router(routes=self._routes)

    def add_route(self, route: BaseRoute):
        self._routes.append(route)

    async def _lifespan(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        while True:
            message = await receive()
            response = Response(scope, send)
            await response(message)

    async def _http(
        self,
        scope: Scope,
        receive: Receive,
    ) -> None:
        request = Request(scope, receive)
        await self._router()

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ):
        _scope = copy.deepcopy(scope)

        if _scope["type"] == "lifespan":
            await self._lifespan(scope, receive, send)

        if _scope["type"] == "http":
            await self._http(_scope, receive)

        raise RuntimeError("Type is not handled by the app")
