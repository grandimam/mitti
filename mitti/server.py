from __future__ import annotations

import copy

from mitti.types import Scope
from mitti.types import Receive
from mitti.types import Send

from mitti.router import Router
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
        route_path: str
    ) -> None:
        self._route_path = route_path
        self._routes = []

    async def _lifespan(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        while True:
            message = await receive()
            if message['type'] == 'lifespan.startup':
                # we should create the routes
                await send({'type': 'lifespan.startup.complete'})
            elif message['type'] == 'lifespan.shutdown':
                # figure out what to do with this
                await send({'type': 'lifespan.shutdown.complete'})
                return

    async def _http(
        self,
        scope: Scope,
        receive: Receive,
    ) -> None:
        request: Request = Request(scope, receive)
        router = Router(routes=self._routes)
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
