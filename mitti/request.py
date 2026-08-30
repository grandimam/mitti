import json
from functools import cached_property
from typing import final

from mitti.types import Receive
from mitti.types import Scope

from abc import ABC
from abc import abstractmethod


class BaseRequest(ABC):

    def __init__(
            self,
            scope: Scope,
            receive: Receive,
    ):
        self._scope = scope
        self._receive = receive

    @abstractmethod
    async def body(self):
        raise NotImplementedError("Body is not implemented")


@final
class Request(BaseRequest):
    @cached_property
    def path(self) -> str:
        return self._scope["path"]

    @cached_property
    def method(self) -> str:
        return self._scope["method"]

    async def body(self) -> bytes | None:
        _chunks: list[bytes] = []

        while True:
            _payload = await self._receive()
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
