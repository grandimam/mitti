from abc import ABC
from abc import abstractmethod

from mitti.types import Scope
from mitti.types import Receive
from mitti.types import Send



class BaseMiddleware(ABC):

    @abstractmethod
    def __call__(self, scope: Scope, receive: Receive, send: Send):
        raise NotImplementedError



class RouteNotFoundMiddleware(BaseMiddleware):

    def __call__(self, scope: Scope, receive: Receive, send: Send):
        pass