from dataclasses import dataclass


@dataclass
class Router:
    path: str
    method: str
