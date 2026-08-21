class Route:

    def __init__(self, path: str, method: str) -> None:
        self._path = path
        self._method = method

class Router:
    """
    Router class handles a path and method

    router = Router(routes)

    We need to either statically or dynamically pass the routes.
    """


    def __init__(self,
        *,
        routes: list | None = None,
    ) -> None:
        self._routes = routes


    def match(self, path: str, method: str) -> Route:
        return
