from mitti.types import Scope
from mitti.types import Receive
from mitti.types import Send

class Response:
    charset = "utf-8"

    def __init__(
            self,
            status_code: int = 200,
            content: str | None = None,
    ):
        self._content = content
        self._status_code = status_code


    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if self._content and not isinstance(self._content, bytes):
            self._content = self._content.encode(self.charset)

        await send({"type": "http.response.start", "status": self._status_code})
        await send({"type": "http.response.body", "body": self._content})


