from mitti.server import Mitti
from mitti.routing import APIRoute


async def index(request):
    return "Hello World"

async def get_users(request):
    return "1234"


app = Mitti(
    routes=[
        APIRoute(
            path="/",
            methods=["GET"],
            handler=index,
        ),
        APIRoute(
            path="/users/{user_id}",
            methods=["GET"],
            handler=get_users,
        )
    ]
)
