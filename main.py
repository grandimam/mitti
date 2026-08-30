from mitti.server import Mitti
from mitti.routing import APIRoute


async def get_users(request):
    print("it is coming in the handler")
    return 1234


app = Mitti(
    routes=[
        APIRoute(
            path="/users/{user_id}",
            methods=["GET"],
            handler=get_users,
        )
    ]
)
