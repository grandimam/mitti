from mitti.server import Mitti

app = Mitti()

@app.get(path="/", methods=["GET"])
async def index(request):
    return "Hello World"

@app.get(path="/users/{user_id}", methods=["GET"])
async def users(request):
    return "1234"