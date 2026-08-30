from mitti.types import Scope
from mitti.types import Send


class Response:
    def __init__(self, scope: Scope, send: Send):
        self._scope = scope
        self._send = send

    async def __call__(self, message, *args, **kwargs):
        if message["type"] == "lifespan.startup":
            await self._send({"type": "lifespan.startup.complete"})
        elif message["type"] == "lifespan.shutdown":
            await self._send({"type": "lifespan.shutdown.complete"})
            return
