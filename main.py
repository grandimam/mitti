from mitti.server import Mitti

app = Mitti()

"""
This is the next feature that I am building. 

async def index(user_id: str) -> str:
    return user_id
    
Our app should be able to handle this. So, I need to infer the following things, one is the path parameters, 
query parameters, and return parameters.

So, I need to use the endpoint (or handler).
Then, I want to build the dependency injection component.

---

Let's see how we should do this. Let's hypothesize/predict this.
I should infer from the handler, and then what should I do.
At the end, the response object needs to send bytes so we need to convert it
On top of this, we need to add response validation.

But wait why do I need to infer anything from the handler.
One is the to infer from the path params, and query string.
Those are the primary. Also the POST request payload.

---

Ok, let's build that feature first.

- user passes the path param, developer needs to specify it on the function parameter. 
- name must match, and the datatype needs to be infered from the type parameter.
- what about query_string, it should be visible on the parameters.
- then use the parameters for the query_string datatype

- what about extra params and fields, how should we handle them?
- We should simplify this. User can define the parameter with type, then it's going to be automatically
- infered and validation, otherwise, they can always fetch is using request.get() and parse it oneself.

- why is the user defining the params in the handler?
- because they do not want to use the request.get()
- instead they can infer it from the function parameters itself
---

Let's build the basic stuff.

@app.get("/users/{user_id}")
async def users(user_id: int) -> str:
    print(user_id)
    print(isinstance(user_id, int))
    return str(user_id)
    
Now, my challenge is how do I know while passing the parameters to the handler
which position I need to pass them into.

Let's predict a few things. While storing the details, I won't be able to get that info, because
it's a dict? Good, inspect.parameters is an ordered mapping. So, I can store the order in which 
I need to pass them.

Ok, once I am able to infer the types, what should I do, I think I can have a converter of some
sorts to handle the converstion. 

Ok, what about the extra or missing issue? 
I think I can store the mapping if it's not there I can simply pass the requests, if the request is not present,
then I will avoid it, otherwise, I can pass it in the requests.

For the missing ones, I can check if it has a default value, otherwise it should be considered mandatory.
"""

@app.get(path="/", methods=["GET"])
async def index():
    return "Hello World"

@app.get(path="/users/{user_id}", methods=["GET"])
async def users(user_id: int) -> str:
    return "1234"