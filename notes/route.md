# Route

Route is an ASGI middleware that abstracts the route matching and handling. The handler is
called once the route is matched. So, we are sure that we are calling the correct handler, 
now, the first thing we need to do is validate the parameters, query string, etc.

Router is responsible for selecting the route by __matching__ the request path with the ones attached to the
route. The route has two primary things during registration: path; handler. 

We use the path to identify the path parameter. We use the handler to fetch the function parameters, and their 
typehints. The type hints are used for doing validation of data types of both the path params, and query params.

### Users define path and query parameter types

```bash
@app.get("/users/{user_id}")
def index(user_id: int, limit: int = 100) -> Response:
  pass
```

We need to validate whether the user_id is a valid path parameter, and if there are 
any query string parameters then we need to validate that as well.

There are two phases: registration and resolution. We do not need to identify the expected
path parameters during resolution, during registration, we already have partial info. 

During resolution, we can simply run the check whether this is true or not. Upon validate failure
we can raise the RequestValidationError. 

We can have one top-level ExceptionHandler that captures the exception and sends a Response, instead of
sending the response inside the route handler.

Route handler must do one of the two things: serve the request or raise exception. How the exception is handled
should be the concern of the exception middleware.

### Sub Routes

I want to add capability for subroutes. Like, one that can nested inside each other. 

