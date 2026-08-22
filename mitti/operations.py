import sys

from mitti.schema import EndpointMethod
from mitti.schema import Route

def _endpoint(method: str):
    def wrapper(func):
        module = sys.modules[func.__module__]
        routes = getattr(module, "__mitti_routes__", None)
        if routes is None:
            routes = []
            setattr(module, "__mitti_routes__", routes)
        routes.append(Route(method=method, handler=func))
        return func
    return wrapper


get = _endpoint(EndpointMethod.GET.value)
post = _endpoint(EndpointMethod.POST.value)
put = _endpoint(EndpointMethod.PUT.value)
patch = _endpoint(EndpointMethod.PATCH.value)
delete = _endpoint(EndpointMethod.DELETE.value)
