from mitti.schema import _Route


class _Router:
    """
    Router class handles a path and method

    router = Router(routes)

    We need to either statically or dynamically pass the routes.
    """

    def __init__(self,
                 *,
                 routes: list[_Route] | None = None,
                 ) -> None:
        self._routes: list[_Route] = routes if routes else []


    def match(self, path: str, method: str) -> _Route | None:
        """
        Method allows for matching the input path to the callable.
        We need to handle cases where there are multiple matches for
        top-level routes. For example:

        @app.get('/user/{user_id}/')
        @app.get('/user/{user_id}/posts')
        @app.get('/user/{user_id}/comments')
        """
        for route in self._routes:
            if route.endpoint == path and route.method == method:
                return route
        return None

