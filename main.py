from mitti.server import Mitti
from mitti.routing import APIRoute


async def get_users(request):
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
