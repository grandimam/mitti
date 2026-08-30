from mitti.types import Scope
from mitti.types import Send

from abc import ABC
from abc import abstractmethod


class BaseResponse(ABC):
    def __init__(
        self,
        scope: Scope,
        send: Send,
    ):
        self._scope = scope
        self._send = send

    @abstractmethod
    def __call__(self, message, *args, **kwargs):
        raise NotImplementedError


class LifespanResponse(BaseResponse):
    async def __call__(self, message, *args, **kwargs):
        if message["type"] == "lifespan.startup":
            await self._send({"type": "lifespan.startup.complete"})
        elif message["type"] == "lifespan.shutdown":
            await self._send({"type": "lifespan.shutdown.complete"})
            return


class HTTPResponse(BaseResponse):
    async def __call__(self, message, *args, **kwargs):
        pass
