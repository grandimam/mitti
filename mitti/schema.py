from dataclasses import dataclass
from collections.abc import Callable

from enum import Enum


class EndpointMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


@dataclass
class _Route:
    method: str
    handler: Callable | None = None
    endpoint: str | None = None
