import functools

from collections.abc import Callable

def get(path: str):
    """
    This is the http operation

    # suppose it's inside
    # api/
    @get("{user_id}/")
    async def get_user():
        pass

    We need to understand where the get_user function
    is location
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrap(*args, **kwargs):

            pass
        return wrap
    return decorator
