import json
from functools import cached_property
from typing import final
from urllib.parse import parse_qsl

from mitti.types import Receive
from mitti.types import Scope
from mitti.utils import is_str


class Headers:


    def __init__(self, headers) -> None:
        self._raw = headers

class QueryParams:

    def __init__(self, query_string: bytes = b"") -> None:
        self._query = parse_qsl(
            query_string.decode('latin-1'),
            keep_blank_values=True,
        )

@final
class Request:

    """
    Top-level class to handle the request metadata and body.
    This includes QueryParams, Headers, and Body

    request = Request(scope, receive)

    Request should process the body, and handle http.request and http.disconnect.
    It also parses the headers and query_params.
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

    @cached_property
    def headers(self) -> Headers:
        _headers = self._scope["headers"]
        if not isinstance(_headers, list):
            raise ValueError("Headers must be a list")
        return Headers(_headers)

    @cached_property
    def query(self) -> QueryParams:
        _query = self._scope["query_string"]
        if not isinstance(_query, bytes):
            raise ValueError("Query string must be bytes")
        return QueryParams(_query)

    async def body(self) -> bytes | None:
        _payload = await self._receive()
        _type = _payload["type"]

        if _type == "http.disconnect":
            raise RuntimeError("Http connection disconnected")

        if _type == "http.request":
            _body = _payload["body"]
            _chunks: list = [_body]
            if not _payload.get("more_body", False):
                return b"".join(_chunks)
            while True:
                _payload = await self._receive()
                if not isinstance(_payload["body"], bytes):
                    raise ValueError("Body must be bytes")
                _chunk: bytes = _payload["body"]
                _chunks.append(_chunk)
                if not _payload.get("more_body", False):
                    break
            return b"".join(_chunks)

    async def json(self):
        _body: bytes | None = await self.body()
        return json.loads(_body) if _body else None
