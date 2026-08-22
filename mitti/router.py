import copy

from pathlib import Path

from importlib import import_module
from mitti.schema import Route


class _Router:
    """
    Router class handles a path and method

    router = Router(routes)

    We need to either statically or dynamically pass the routes.
    """

    def __init__(self,
        *,
        routes: list | None = None,
        route_dir: str | None = None,
    ) -> None:
        self._route_dir = route_dir

        if not routes:
            routes = []

        self._routes: list[Route] = copy.deepcopy(routes)


    def discover(self) -> None:
        if not self._route_dir:
            return
        root = Path(self._route_dir)
        nodes = [root]
        while nodes:
            curr_node = nodes.pop()
            if not curr_node.is_dir():
                continue
            if (curr_node / "__init__.py").is_file():
                module_name = ".".join(curr_node.parts)
                module = import_module(module_name)
                endpoints = getattr(module, "__mitti_routes__", [])
                self._routes.extend(endpoints)
            nodes.append(
                child
                for child in curr_node.iterdir()
                if child.is_dir()
            )


    def match(self, path: str, method: str) -> Route | None:
        for route in self._routes:
            if route.endpoint == path and route.method == method:
                return route
        return
