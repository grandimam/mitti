# mitti

mitti is a Python ASGI framework designed to unify concurrent and parallel
execution behind a synchronous application model.

Application code stays ordinary, synchronous Python. mitti owns the execution
machinery and decides *how* to run it — concurrently on GIL builds, and in
true parallel on free-threaded Python.

```python
from mitti import App

app = App()


@app.get("/users/{user_id}")
def get_user(user_id: int):
    return users.get(user_id)
```

## Status

Early alpha. The design is documented in [`docs/design.md`](docs/design.md);
the MVP covers ASGI, routing, path/query parameters, JSON responses, the
request object, dependency injection, basic validation, middleware,
lifespan, and a thread-based executor.

## Requirements

* Python 3.13+
* ASGI 3
* Free-threaded Python where available (GIL-enabled Python supported as a
  compatibility mode)

## Development

```bash
uv sync
uv run pytest
```
