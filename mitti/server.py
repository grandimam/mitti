from __future__ import annotations

import copy

from mitti.types import Scope
from mitti.types import Receive
from mitti.types import Send

from mitti.routing import BaseRoute
from mitti.request import Request

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

    async def _lifespan(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return

    async def _http(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        request = Request(scope, receive)
        result = await self._router(request)
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": str(result).encode("utf-8")})


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
