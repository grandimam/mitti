from functools import cached_property
from typing import final

from mitti.types import Scope
from mitti.types import Receive

from mitti.utils import is_str

@final
class Request:

    """
    Top-level class to handle the request metadata and body.
    This includes QueryParams, Headers, and Body

    request = Request(scope, receive)

    Request should process the body, and handle http.request and http.disconnect.
    """

    def __init__(self, scope: Scope, receive: Receive) -> None:
        self._scope = scope
        self._receive = receive

    @cached_property
    def path(self) -> str | None:
        _path = self._scope["path"]
        if not is_str(_path):
            raise ValueError("Path must be a str")
        return str(_path)

    @cached_property
    def method(self) -> str | None:
        _method = self._scope["method"]
        if not is_str(_method):
            raise ValueError("Path must be a str")
        return str(_method)

    def headers(self):
        pass

    def query(self):
        pass

    async def body(self) -> bytes | None:
        _payload = await self._receive()

        if not isinstance(_payload["type"], str):
            raise ValueError("Type must be str")

        if not isinstance(_payload["more_body"], bool):
            raise ValueError("More body must be bool")

        _type = _payload["type"]

        if _type == "http.disconnect":
            raise RuntimeError("Http connection disconnected")

        if _type == "http.request":
            _body: bytes = _payload["body"]
            _chunks: list[bytes] = [_body]

            if not _payload.get("more_body", False):
                return b"".join(_chunks)

            while True:
                _payload = await self._receive()
                _chunk: bytes = _payload["body"]
                _chunks.append(_chunk)
                if not _payload.get("more_body", False):
                    break
            return b"".join(_chunks)

    async def json(self):
        _body: bytes = await self.body()
        return json.loads(_body)
