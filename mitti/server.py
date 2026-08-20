from __future__ import annotations

import copy

from mitti.types import Scope
from mitti.types import Receive
from mitti.types import Send

from mitti.request import Request

class MittiApp:

    async def handle_http(self, scope: Scope, receive: Receive) -> None:
        request: Request = Request(scope, receive)
        pass

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        _scope = copy.deepcopy(scope)
        _scope_type: str = str(_scope["type"])

        if _scope_type == "http":
            await self.handle_http(_scope, receive)
        raise NotImplementedError
