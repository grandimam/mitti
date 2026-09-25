import logging

from mitti.exceptions import RequestValidationError
from mitti.response import Response
from mitti.types import MittiApp
from mitti.types import Receive
from mitti.types import Scope
from mitti.types import Send


logger = logging.getLogger("mitti.errors")


class ExceptionHandler:

    def __init__(self, app: MittiApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        try:
            await self._app(scope, receive, send)
        except RequestValidationError as exc:
            await Response(status_code=422, content=str(exc))(scope, receive, send)
        except Exception:
            logger.exception(
                "Unhandled exception while serving %s %s",
                scope.get("method", ""),
                scope.get("path", ""),
            )
            await Response(status_code=500, content="Internal Server Error")(scope, receive, send)
