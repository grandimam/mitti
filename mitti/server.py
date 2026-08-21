from __future__ import annotations

import copy

from mitti.types import Scope
from mitti.types import Receive
from mitti.types import Send

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

    async def handle_http(self, scope: Scope, receive: Receive) -> None:
        request: Request = Request(scope, receive)


    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        _scope = copy.deepcopy(scope)
        _scope_type: str = str(_scope["type"])

        if _scope_type == "http":
            await self.handle_http(_scope, receive)
        raise NotImplementedError
