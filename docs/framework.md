# Mitti — Framework Design

Mitti is a Python-first ASGI framework built around a simple idea:

> The framework should not ask the developer to repeat information that Python already expresses.

ASGI remains underneath as the protocol boundary. Mitti provides the application model above it.

The goal is not zero configuration or maximum inference. The goal is to use Python's existing structure wherever that structure already communicates intent, while remaining explicit whenever information genuinely does not exist.

---

# 1. Core Principles

## Principle 1 — Python Structure Is Application Structure

Python already has mechanisms for expressing structure:

- packages
- modules
- functions
- function signatures
- annotations
- defaults
- imports
- dataclasses
- context managers

Mitti should use these structures instead of creating parallel framework configuration wherever possible.

For example, instead of:

```python
router = Router(prefix="/users")
app.include_router(router)
```

the Python package itself can establish the resource:

```text
routes/
└── users/
    └── __init__.py
```

The package hierarchy is not merely code organization.

It is part of the application structure.

This principle extends beyond routing.

Python structure can also communicate:

- resource hierarchy
- dependency scope
- middleware scope
- lifecycle ownership
- error-handler scope
- application organization

The general rule is:

> If Python already structurally expresses something, Mitti should not require the developer to express it again through framework configuration.

---

## Principle 2 — Explicit When Information Is Missing

Mitti should not confuse reducing redundancy with guessing.

For example:

```text
routes/
└── users/
    └── __init__.py
```

contains enough information to establish:

```text
/users
```

There is therefore no reason to write:

```python
@get("/users")
```

But Python structure does not tell Mitti that this exists:

```text
/users/{user_id}
```

The dynamic segment is genuinely new information.

Therefore it should be explicit:

```python
@get("/{user_id}")
async def one(user_id: int):
    ...
```

The decision test is:

> Does this declaration add information?

If not, remove it.

If it does, make it explicit.

Mitti should therefore:

> Eliminate redundancy, not information.

The two principles create an intentional tension:

> **Structure where Python already knows. Explicitness where Python does not.**

---

# 2. ASGI Stays Underneath

Mitti is still an ASGI framework.

Internally, the application eventually becomes:

```python
async def app(scope, receive, send):
    ...
```

ASGI concepts such as:

```text
scope
receive
send
http.request
http.response.start
http.response.body
```

remain part of the implementation boundary.

They do not need to define the normal application programming model.

Mitti translates these low-level protocol concepts into Python-level concepts such as:

```text
Request
Response
routes
dependencies
parameters
bodies
```

The framework should compile/discover application structure at startup and build normal routing/dependency machinery underneath.

Request handling should not involve filesystem traversal.

Conceptually:

```text
Python application
       ↓
discovery
       ↓
validation
       ↓
compilation
       ↓
route/dependency tables
       ↓
ASGI application
```

---

# 3. Modules Are Resources

The fundamental routing abstraction is:

> **A Python package/module represents an HTTP resource.**

For example:

```text
routes/
└── users/
    └── __init__.py
```

represents:

```text
/users
```

Mitti should reason primarily in terms of Python modules:

```text
routes.users
```

rather than merely filesystem paths:

```text
routes/users/__init__.py
```

The filesystem is the normal physical representation of Python's module hierarchy.

---

# 4. `__init__.py` Represents the Resource

There is no need for an artificial:

```text
index.py
```

convention.

Python already has a module representing the package itself:

```text
__init__.py
```

Therefore:

```text
routes/
└── users/
    └── __init__.py
```

means:

```text
routes.users
→ /users
```

Operations for `/users` live naturally inside:

```text
routes/users/__init__.py
```

---

# 5. Nested Directories Represent Nested Resources

Resources should consistently be packages rather than mixing directories and leaf `.py` modules.

Prefer:

```text
routes/
└── users/
    ├── __init__.py
    └── posts/
        ├── __init__.py
        └── comments/
            └── __init__.py
```

rather than:

```text
routes/
└── users/
    ├── __init__.py
    ├── posts.py
    └── comments.py
```

The Python structure now communicates the resource hierarchy:

```text
users
└── posts
    └── comments
```

Each resource has a consistent place for its operations:

```text
users/__init__.py
users/posts/__init__.py
users/posts/comments/__init__.py
```

This keeps the mental model simple:

> Package = resource.

---

# 6. HTTP Primitives

Mitti should expose familiar HTTP primitives rather than requiring router objects.

For example:

```python
from mitti import get, post, patch, delete
```

The primitive communicates the HTTP operation.

The module communicates the resource.

Therefore:

```python
# routes/users/__init__.py

from mitti import get, post


@get
async def all():
    ...


@post
async def create():
    ...
```

can represent:

```text
GET  /users
POST /users
```

There is no need for:

```python
router = Router(prefix="/users")
```

or:

```python
@app.get("/users")
```

because `/users` is already encoded by:

```text
routes.users
```

The primitive should add only information that the module does not already contain.

---

# 7. Dynamic Resources

Dynamic URL topology should not be guessed from parameter names or directory naming conventions.

Avoid conventions such as:

```text
_id.py
[user_id].py
$user_id.py
_.py
```

unless there is a compelling reason for them.

These merely move routing configuration into a filename DSL.

Instead, dynamic topology belongs explicitly in the HTTP primitive because it represents genuinely new information.

For example:

```python
# routes/users/__init__.py

from mitti import get


@get("/{user_id}")
async def one(user_id: int):
    ...
```

The module contributes:

```text
/users
```

The primitive contributes:

```text
/{user_id}
```

The function signature contributes:

```text
user_id
int
```

Together:

```text
GET /users/{user_id}
```

Every piece of information is expressed once.

---

# 8. Collection and Member Operations

A resource can expose both collection and member operations.

For example:

```python
# routes/users/__init__.py

from mitti import get, post, patch, delete


@get
async def all():
    ...


@post
async def create():
    ...


@get("/{user_id}")
async def one(user_id: int):
    ...


@patch("/{user_id}")
async def update(user_id: int):
    ...


@delete("/{user_id}")
async def remove(user_id: int):
    ...
```

This represents:

```text
GET    /users
POST   /users
GET    /users/{user_id}
PATCH  /users/{user_id}
DELETE /users/{user_id}
```

There is no requirement for Mitti to invent concepts such as:

```text
get_one
member.get
get.member
```

The distinction already exists in the primitive's local path.

---

# 9. Nested Dynamic Resources

Consider:

```text
routes/
└── users/
    ├── __init__.py
    └── posts/
        └── __init__.py
```

The package hierarchy communicates:

```text
users
└── posts
```

But it does not contain enough information to determine whether the URL should be:

```text
/users/posts
```

or:

```text
/users/{user_id}/posts
```

That information must therefore be explicit.

Inside:

```text
routes/users/posts/__init__.py
```

we can write:

```python
from mitti import get, post, delete


@get("/{user_id}/posts")
async def all(user_id: int):
    ...


@post("/{user_id}/posts")
async def create(user_id: int):
    ...


@get("/{user_id}/posts/{post_id}")
async def one(user_id: int, post_id: int):
    ...


@delete("/{user_id}/posts/{post_id}")
async def remove(user_id: int, post_id: int):
    ...
```

Combined with the parent resource:

```text
/users
```

Mitti derives:

```text
GET    /users/{user_id}/posts
POST   /users/{user_id}/posts
GET    /users/{user_id}/posts/{post_id}
DELETE /users/{user_id}/posts/{post_id}
```

There is some apparent repetition of `posts`, because it appears both in:

```text
users/posts/
```

and:

```python
@get("/{user_id}/posts")
```

That is acceptable when eliminating the repetition would require complicated hidden routing semantics.

Predictability is more important than eliminating every repeated character.

The principle is not:

> Never repeat anything.

It is:

> Do not require redundant configuration when Python already contains sufficient information.

Dynamic placement between resource segments is information Python's module hierarchy does not contain.

Therefore explicitness is justified.

---

# 10. Routing Model

The routing model can therefore be summarized as:

```text
Python package hierarchy
        ↓
resource organization

HTTP primitive
        ↓
HTTP operation + missing topology

function signature
        ↓
parameter names + Python types
```

For example:

```text
routes.users.posts
```

combined with:

```python
@get("/{user_id}/posts/{post_id}")
async def one(user_id: int, post_id: int):
    ...
```

contains everything Mitti needs to construct the endpoint.

There is:

- no router object
- no router prefix
- no `include_router`
- no central route registry
- no duplicated `/users` prefix inside the users resource

---

# 11. Route Discovery

Mitti should discover resource modules at startup.

Conceptually:

```text
routes/
└── users/
    ├── __init__.py
    └── posts/
        └── __init__.py
```

becomes:

```text
routes.users
routes.users.posts
```

Mitti imports/discovers these modules, finds HTTP primitives, validates them, and compiles them into an internal routing table.

For example:

```text
GET     /users
POST    /users
GET     /users/{user_id}
PATCH   /users/{user_id}
DELETE  /users/{user_id}

GET     /users/{user_id}/posts
POST    /users/{user_id}/posts
GET     /users/{user_id}/posts/{post_id}
DELETE  /users/{user_id}/posts/{post_id}
```

The filesystem/module system is used during application construction.

It is not consulted on every HTTP request.

---

# 12. Route Introspection Is Important

Because routes are partially derived from module structure, Mitti should provide excellent introspection.

For example:

```bash
mitti routes
```

could output:

```text
GET     /users
        routes.users:all

POST    /users
        routes.users:create

GET     /users/{user_id}
        routes.users:one

PATCH   /users/{user_id}
        routes.users:update

GET     /users/{user_id}/posts
        routes.users.posts:all

GET     /users/{user_id}/posts/{post_id}
        routes.users.posts:one
```

Implicit structure should never mean invisible structure.

Mitti should make the compiled application easy to inspect.

---

# 13. Dependencies Follow the Same Structural Principle

The package hierarchy should also communicate dependency scope.

Instead of configuring:

```python
router.add_dependency(...)
app.add_dependency(...)
```

Mitti can use conventional Python modules:

```text
app/
├── dependencies.py
└── routes/
    └── users/
        ├── dependencies.py
        ├── __init__.py
        └── posts/
            ├── dependencies.py
            └── __init__.py
```

Placement communicates dependency ownership and lifetime.

---

# 14. Global Dependencies Are Application-Scoped

The root dependency module:

```text
app/dependencies.py
```

contains application-scoped dependencies.

For example:

```python
# app/dependencies.py

from mitti import dependency


@dependency
async def database():
    return Database(...)
```

The database is initialized/resolved for the application lifetime and reused.

Conceptually:

```text
application
└── database
```

There is no need to write:

```python
@dependency(scope="app")
```

because placement already communicates the scope.

This follows Principle 1:

> Use Python structure when it already expresses the application's structure.

---

# 15. Resource Dependencies Are Request-Scoped

Dependencies inside the resource hierarchy:

```text
routes/**/dependencies.py
```

are request-scoped.

For example:

```text
routes/
└── users/
    ├── dependencies.py
    └── __init__.py
```

```python
# routes/users/dependencies.py

from mitti import dependency


@dependency
async def current_user(request):
    ...
```

This dependency is created/resolved for the current request.

Conceptually:

```text
application
│
├── database
│
├── request A
│   └── current_user
│
└── request B
    └── current_user
```

The rule is therefore:

> **Root dependencies are application-scoped. Resource dependencies are request-scoped.**

No explicit `scope=` argument is needed for the normal case.

---

# 16. Dependency Visibility Follows Resource Hierarchy

Dependencies can also follow lexical-like resource visibility.

For example:

```text
routes/
├── dependencies.py
└── users/
    ├── dependencies.py
    └── posts/
        ├── dependencies.py
        └── __init__.py
```

A handler in:

```text
routes.users.posts
```

can resolve dependencies from its structural context:

```text
routes.users.posts.dependencies
        ↓
routes.users.dependencies
        ↓
routes.dependencies
```

Conceptually:

```text
current resource
      ↓
parent resource
      ↓
...
      ↓
route root
```

This mirrors the idea of lexical resolution without requiring a dependency container configuration tree.

---

# 17. Long-Lived Infrastructure Belongs at Application Scope

Suppose search has an expensive client that should exist for the lifetime of the application.

Do not put the long-lived client in:

```text
routes/search/dependencies.py
```

just because search uses it.

Instead:

```python
# app/dependencies.py

@dependency
async def search_client():
    return SearchClient(...)
```

Then request-specific search composition can live in:

```python
# routes/search/dependencies.py

@dependency
async def search(
    client: SearchClient = use(search_client),
):
    ...
```

This creates a useful architectural distinction:

```text
app/dependencies.py
        ↓
long-lived infrastructure

routes/**/dependencies.py
        ↓
request-specific composition
```

---

# 18. Dependencies Are Explicitly Consumed With `use`

Mitti should not automatically inject arbitrary function parameters based purely on their type or name.

For example:

```python
async def handler(db: Database):
    ...
```

does not inherently tell Python or Mitti whether `db` is:

- request input
- body input
- query input
- dependency
- manually supplied value

Therefore dependency consumption should remain explicit.

Mitti provides:

```python
use(...)
```

For example:

```python
from mitti import use
from .dependencies import current_user


@get("/{user_id}")
async def one(
    user_id: int,
    user: User = use(current_user),
):
    ...
```

The pieces are now unambiguous:

```text
user_id: int
    → ordinary request parameter

user: User
    → resulting Python value

use(current_user)
    → dependency provider
```

Dependency relationships are ordinary Python references.

There is no need for a global dependency lookup by type or parameter name.

---

# 19. Dependencies Can Depend on Dependencies

Because dependency relationships use ordinary Python references, dependency graphs remain explicit.

For example:

```python
# app/dependencies.py

@dependency
async def database():
    return Database(...)
```

Then:

```python
# routes/users/dependencies.py

from mitti import dependency, use
from app.dependencies import database


@dependency
async def current_user(
    db: Database = use(database),
):
    ...
```

And:

```python
# routes/users/__init__.py

from mitti import get, use
from .dependencies import current_user


@get("/{user_id}")
async def one(
    user_id: int,
    user: User = use(current_user),
):
    ...
```

The dependency graph is:

```text
handler
   ↓
current_user
   ↓
database
```

Mitti manages execution, caching, lifetime, and cleanup underneath.

The graph itself remains visible in ordinary Python.

---

# 20. Dependency Lifetime and Dependency Visibility Are Different Concepts

It is important to separate:

```text
where dependency is visible
```

from:

```text
how long dependency lives
```

The Python resource hierarchy controls visibility.

The structural location controls the normal lifetime:

```text
app/dependencies.py
→ application lifetime

routes/**/dependencies.py
→ request lifetime
```

ASGI itself does not require all dependencies to be request-scoped.

ASGI's `scope` object is protocol metadata.

Mitti's dependency scope is a separate lifecycle abstraction implemented above ASGI.

Mitti may internally associate a request dependency cache with the current ASGI request, but application developers do not need to work with raw ASGI `scope` to use dependencies.

---

# 21. Request Input Binding

After routing and dependencies, the next concern is function parameter binding.

Consider:

```python
@get("/{user_id}")
async def one(
    user_id: int,
    expand: str | None = None,
    user: User = use(current_user),
):
    ...
```

Mitti needs to determine:

```text
user_id → path
expand  → query
user    → dependency
```

The same two principles apply.

---

# 22. Path Parameters

Path parameters are already explicitly present in the HTTP primitive.

For example:

```python
@get("/{user_id}")
async def one(user_id: int):
    ...
```

Mitti knows:

```text
{user_id}
```

comes from the route because the primitive explicitly says so.

The function signature contributes its Python representation:

```text
name: user_id
type: int
```

Therefore:

```text
URL value
   ↓
"user_id"
   ↓
int conversion/validation
   ↓
handler
```

There is no need for:

```python
Path(...)
```

because the route already contains the necessary information.

---

# 23. Query Parameters

For ordinary GET-style inputs, Python defaults can naturally describe optional query parameters.

For example:

```python
@get
async def all(
    page: int = 1,
    limit: int = 20,
    search: str | None = None,
):
    ...
```

can naturally represent:

```text
GET /users?page=1&limit=20&search=...
```

The Python signature already communicates:

```text
page
    int
    default = 1

limit
    int
    default = 20

search
    str | None
    default = None
```

Mitti should avoid requiring:

```python
Query(...)
```

when the function signature already contains the required information.

However, Mitti should not assume that every required scalar parameter is a path parameter.

For example:

```python
async def search(term: str):
    ...
```

could represent a required query parameter.

Required-vs-optional is not equivalent to path-vs-query.

Path identity comes from the route primitive itself.

---

# 24. Request Bodies Should Be Structured Python Objects

For structured request bodies, Mitti should prefer structured Python types instead of inferring body fields from arbitrary function parameters.

For example:

```python
from dataclasses import dataclass


@dataclass
class CreateUser:
    name: str
    email: str
```

Then:

```python
@post
async def create(user: CreateUser):
    ...
```

The structured type communicates the expected body shape.

Conceptually:

```text
JSON request body
       ↓
CreateUser
       ↓
handler
```

This avoids APIs such as:

```python
Body(...)
```

when the Python type already communicates that the input is structured.

The exact supported structured types remain a design decision.

Candidates include:

```text
dataclass
TypedDict
Pydantic model
attrs class
arbitrary annotated class
```

Mitti should decide whether it owns validation itself or integrates with existing Python modeling systems.

---

# 25. Parameter Classification

A handler could eventually look like:

```python
@post("/{user_id}")
async def update(
    user_id: int,
    body: UpdateUser,
    notify: bool = False,
    user: User = use(current_user),
):
    ...
```

Mitti can classify the parameters based on information already available:

```text
user_id
    route contains {user_id}
    → path

body: UpdateUser
    structured body type
    → request body

notify: bool = False
    ordinary defaulted scalar
    → query

user: User = use(current_user)
    explicit use(...)
    → dependency
```

The classification should be deterministic.

Mitti should never need to guess based on vague naming conventions.

---

# 26. Current Application Shape

A realistic application might look like:

```text
app/
├── __init__.py
├── dependencies.py
│
└── routes/
    ├── dependencies.py
    │
    └── users/
        ├── __init__.py
        ├── dependencies.py
        │
        └── posts/
            ├── __init__.py
            ├── dependencies.py
            │
            └── comments/
                └── __init__.py
```

The structure communicates:

```text
app/dependencies.py
    application-scoped dependencies

routes/
    HTTP resource tree

routes/**/dependencies.py
    request-scoped dependencies

resource/__init__.py
    operations on that resource

nested package
    nested resource
```

---

# 27. Example

## Application Dependency

```python
# app/dependencies.py

from mitti import dependency


@dependency
async def database():
    return Database(...)
```

---

## User Dependency

```python
# app/routes/users/dependencies.py

from mitti import dependency, use
from app.dependencies import database


@dependency
async def current_user(
    db: Database = use(database),
) -> User:
    ...
```

---

## Users Resource

```python
# app/routes/users/__init__.py

from dataclasses import dataclass

from mitti import get, post, patch, delete, use

from .dependencies import current_user


@dataclass
class CreateUser:
    name: str
    email: str


@dataclass
class UpdateUser:
    name: str | None = None
    email: str | None = None


@get
async def all(
    page: int = 1,
    limit: int = 20,
):
    ...


@get("/{user_id}")
async def one(
    user_id: int,
    user: User = use(current_user),
):
    ...


@post
async def create(
    body: CreateUser,
):
    ...


@patch("/{user_id}")
async def update(
    user_id: int,
    body: UpdateUser,
    user: User = use(current_user),
):
    ...


@delete("/{user_id}")
async def remove(
    user_id: int,
    user: User = use(current_user),
):
    ...
```

This produces:

```text
GET    /users
GET    /users/{user_id}
POST   /users
PATCH  /users/{user_id}
DELETE /users/{user_id}
```

---

## Posts Resource

```python
# app/routes/users/posts/__init__.py

from dataclasses import dataclass

from mitti import get, post, delete, use

from ..dependencies import current_user


@dataclass
class CreatePost:
    title: str
    content: str


@get("/{user_id}/posts")
async def all(
    user_id: int,
    page: int = 1,
    limit: int = 20,
):
    ...


@get("/{user_id}/posts/{post_id}")
async def one(
    user_id: int,
    post_id: int,
):
    ...


@post("/{user_id}/posts")
async def create(
    user_id: int,
    body: CreatePost,
    user: User = use(current_user),
):
    ...


@delete("/{user_id}/posts/{post_id}")
async def remove(
    user_id: int,
    post_id: int,
    user: User = use(current_user),
):
    ...
```

This produces:

```text
GET    /users/{user_id}/posts
GET    /users/{user_id}/posts/{post_id}
POST   /users/{user_id}/posts
DELETE /users/{user_id}/posts/{post_id}
```

---

# 28. What Mitti Deliberately Avoids

The design currently avoids requiring concepts such as:

```python
app.include_router(...)
Router(prefix=...)
APIRouter(...)
Depends(...)
Path(...)
Query(...)
Body(...)
scope="request"
scope="app"
```

Not because these abstractions are inherently bad, but because in the normal case Mitti can obtain the same information from:

```text
Python package structure
HTTP primitives
function signatures
structured Python types
dependency module placement
explicit use(...)
```

Every additional framework abstraction should therefore justify itself by answering:

> What information does this add that the Python program does not already contain?

If the answer is "none," Mitti should probably not have that abstraction.

---

# 29. Design Invariants So Far

The current design can be reduced to several invariants.

### Resource

```text
Python package = HTTP resource
```

### Resource hierarchy

```text
package hierarchy = resource hierarchy
```

### Resource implementation

```text
resource/__init__.py = resource operations
```

### HTTP operation

```text
get / post / patch / delete = HTTP semantics
```

### Dynamic topology

```text
primitive path = explicit missing route information
```

### Path input

```text
{name} in route + matching function parameter = path input
```

### Query input

```text
ordinary scalar parameters/defaults = query input
```

subject to deterministic binding rules.

### Body input

```text
structured Python object = structured request body
```

### Dependency declaration

```text
dependency callable = provider
```

### Dependency consumption

```text
use(provider) = explicit dependency edge
```

### Application dependency lifetime

```text
app/dependencies.py = application scope
```

### Request dependency lifetime

```text
routes/**/dependencies.py = request scope
```

### Dependency visibility

```text
resource hierarchy = dependency visibility hierarchy
```

### ASGI

```text
ASGI = implementation boundary underneath Mitti
```

---

# 30. The Central Design Question

For every future feature—middleware, responses, exceptions, WebSockets, lifecycle, serialization, validation, background work, authentication, OpenAPI—the framework should ask two questions in order.

### Question 1

> Does Python's existing structure already communicate this information?

If yes, use it.

Do not introduce configuration that repeats it.

### Question 2

> If Python does not contain this information, can Mitti infer it without ambiguity?

If no, require the developer to express it explicitly.

Do not replace explicit information with hidden framework magic.

This gives Mitti its central philosophy:

> **Use Python as the application language, not merely as the language in which framework configuration is written.**

And the practical rule underneath it:

> **Say each thing once.**
