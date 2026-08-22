from __future__ import annotations

import copy

from mitti.types import Scope
from mitti.types import Receive
from mitti.types import Send

from mitti.router import _Router
from mitti.request import Request

class Mitti:
    """
    Top-level ASGI Application for handling http requests. It's a
    callable that handles the connection event.

    The connection scope is handled in the Request top-level class.
    Request parses the connection scope and provides access to path,
    method, and other metadata including body and json.

    Router is another top-level class for handling path and method.
    Then, what should it emit - ideally, the actually method that
    needs to be called.

    Like for example:
        @get('{user_id}')
        async def get_user(user_id: int):
            pass
    """

    def __init__(
        self,
        *,
        routes: list | None = None,
        services: list | None = None,
        service_dir: str = "services",
        route_dir: str = "routes",
    ) -> None:
        if not routes:
            routes = []

        if not services:
            services = []

        self._routes = routes
        self._services = services

        # metadata
        self._route_dir: str = route_dir
        self._service_dir: str = service_dir

        # router
        self._router = _Router(route_dir=self._route_dir)

    async def _lifespan(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        while True:
            message = await receive()
            if message['type'] == 'lifespan.startup':
                self._router.discover()
                await send({'type': 'lifespan.startup.complete'})
            elif message['type'] == 'lifespan.shutdown':
                await send({'type': 'lifespan.shutdown.complete'})
                return

    async def _http(
        self,
        scope: Scope,
        receive: Receive,
    ) -> None:
        request = Request(scope, receive)
        pass


    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ):
        _scope = copy.deepcopy(scope)
        if _scope["type"] == "lifespan":
            await self._lifespan(scope, receive, send)
        elif _scope["type"] == "http":
            await self._http(_scope, receive)
        raise NotImplementedError
