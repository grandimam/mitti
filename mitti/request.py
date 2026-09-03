from dataclasses import dataclass

import json
from functools import cached_property

from mitti.types import Receive
from mitti.types import Scope

@dataclass
class Request:
    scope: Scope
    receive: Receive

    @cached_property
    def path(self) -> str:
        return self.scope["path"]

    @cached_property
    def method(self) -> str:
        return self.scope["method"]

    async def body(self) -> bytes | None:
        _chunks: list[bytes] = []

        while True:
            _payload = await self.receive()
            _type = _payload["type"]

            if _type == "http.disconnect":
                raise RuntimeError("Http connection disconnected")

            if _type == "http.request":
                _body = _payload["body"]
                _chunks.append(_body)
                if not _payload.get("more_body", False):
                    break

        return b"".join(_chunks)

    async def json(self):
        _body: bytes | None = await self.body()
        return json.loads(_body) if _body else None
