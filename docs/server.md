# Server

MittiApp is a top-level class for handling the HTTP connections. It parses the connection event using Request.
Request class provides access to path, method, and other metadata. It also parses the body and json.

```python
request = Request(scope, recieve)

# metadata
request.path
request.method

# payload
await request.body()
await request.json()
```

Now, what can we do with the body and other details. It's only required for POST requests. So, we can proceed without
body. So, once we parse the connection scope we simply need to send that detail.


Now, what's the abstraction that gives us the path to method mapping. That's a path route. It simply provides me an 
abstraction.

```python
path_route = PathRoute(path, method)

# ok, here we have the current connection scope. 
# but how can I inject all the existing routes availbale.
# ok, lets craete another abstraction Router. It should return a Route, but router itself should have 
# existing routing details. 
# So, route should be path, method, and callable.

# ok, based on the analysis, the router object should expose a method
# route, match(path, method)
```

## Router

One of the challenges is the router. I went with the approach of usign modules as routing criteria. 
For this, we can add a field `router_dir` in the top-level ASGI application.
This will be used for determining the route details

```bash
# So anything inside the routes direction will be used to determine
# the route path.
/routes/
```

So, effectively we will have the following folder structure for the project.

```bash
/routes
/services
/dependencies
/tasks
/commands
```
