from __future__ import annotations

import copy

from mitti.types import Scope
from mitti.types import Receive
from mitti.types import Send

from mitti.routing import BaseRoute
from mitti.request import Request
from mitti.response import LifespanResponse
from mitti.response import HTTPResponse

from mitti.routing import Router


class Mitti:
    def __init__(
        self,
        *,
        routes: list[BaseRoute],
    ) -> None:
        self._routes = routes
        # routes are defined once, so adding new routes will automatically be injected into router
        # how? because list hold references, so we do not need to recreate the router
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
            response = LifespanResponse(scope, send)
            await response(message)

    async def _http(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        request = Request(scope, receive)
        await self._router(request)
        response = HTTPResponse(scope, send)
        await response(send)

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
            await self._http(_scope, receive, send)

        raise RuntimeError("Type is not handled by the app")
