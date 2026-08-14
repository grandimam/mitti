"""Application construction and lifecycle."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class App:
    """Top-level ASGI application.

    Routes, middleware and lifecycle hooks are registered here and
    compiled into an ASGI callable at startup.

    Example:

        from mitti import App

        app = App()


        @app.get("/hello")
        def hello():
            return {"message": "hello"}
    """

    debug: bool = False
    docs: bool = True
    workers: int = 8
    _routes: list = field(default_factory=list)

    def get(self, path: str):
        def decorator(func):
            self._routes.append(("GET", path, func))
            return func

        return decorator

    async def __call__(self, scope, receive, send):
        raise NotImplementedError
