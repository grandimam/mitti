from __future__ import annotations

from typing import Callable

from mitti.types import Scope
from mitti.types import Receive
from mitti.types import Send

from mitti.routing import BaseRoute
from mitti.routing import Router


class Mitti:
    def __init__(
        self,
        *,
        routes: list[BaseRoute] | None = None
    ) -> None:
        if not routes:
            routes = []
        self._router = Router(routes=routes)
        self._app = self._router


    def get(
            self,
            *,
            path: str,
            methods: list[str]
    ):
        def wrap(func: Callable):
            self._router.add_route(path=path, methods=methods, handler=func)
            return func
        return wrap

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
        await self._app(scope, receive, send)


    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ):
        if scope["type"] == "lifespan":
            await self._lifespan(scope, receive, send)

        if scope["type"] == "http":
            await self._http(scope, receive, send)
