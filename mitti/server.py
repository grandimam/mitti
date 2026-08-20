from __future__ import annotations

from mitti.types import Scope
from mitti.types import Receive
from mitti.types import Send

class MittiApp:

    async def handle_http(self, scope: Scope, receive: Receive) -> None:
        path = scope["path"]
        if not isinstance(path, str):
            raise ValueError("Path is invalid")

        method = scope["method"]
        if not isinstance(method, str):
            raise ValueError("Method is invalid")

        query_string = scope["query_string"]
        if not isinstance(query_string, bytes):
            raise ValueError("Query string is invalid")

        body = await receive()

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        scope_type: str = str(scope["type"])
        if scope_type == "http":
            await self.handle_http(scope, receive)
        raise NotImplementedError
