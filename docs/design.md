# Next-Generation ASGI Framework — Requirements, Design & Philosophy

## 1. Vision

Build a production-grade ASGI web framework that competes directly with FastAPI on developer experience while pursuing a fundamentally different execution model.

### Core thesis

> **AsyncIO is not the only way to build high-performance Python servers.**

The framework should make **parallel execution with threads** a first-class primitive rather than forcing application developers to structure their applications around `async`/`await`.

The framework should target:

* Python 3.13+
* ASGI 3
* Free-threaded Python where available
* Traditional GIL-enabled Python as a compatibility mode
* HTTP APIs
* Web applications
* Streaming
* WebSockets
* Background work
* Middleware
* Dependency injection
* Validation
* OpenAPI

The project should initially compete with **FastAPI**, not attempt to replace every feature in the Python web ecosystem.

---

# 2. Product Philosophy

## 2.1 Simple code should be fast code

The framework should avoid requiring developers to understand:

* event loops
* coroutine scheduling
* `await`
* async generators
* async context managers
* task groups

for ordinary HTTP applications.

A basic endpoint should look like:

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return users.get(user_id)
```

The framework owns the execution machinery.

The developer describes **what the application does**, while the framework decides **how to execute it efficiently**.

---

# 3. Primary Design Principles

## Principle 1 — Synchronous by default

Application code should be ordinary Python.

```python
@app.get("/users")
def users():
    return repository.list_users()
```

No artificial:

```python
async def users():
    result = await repository.list_users()
    return result
```

unless asynchronous APIs are genuinely required.

---

## Principle 2 — Parallelism should be explicit at the framework level

The framework should internally be capable of executing independent requests concurrently and, where Python permits it, in parallel.

Conceptually:

```text
                 ┌──────────────┐
HTTP ───────────►│   Scheduler  │
                 └──────┬───────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       Worker 1      Worker 2      Worker 3
          │             │             │
          ▼             ▼             ▼
       Request A     Request B     Request C
```

On free-threaded Python:

```text
Worker 1 ── CPU ──┐
Worker 2 ── CPU ──┼── parallel execution
Worker 3 ── CPU ──┘
```

On GIL Python:

```text
Worker 1 ──┐
Worker 2 ──┼── concurrent execution
Worker 3 ──┘
```

The application programming model remains identical.

---

# 4. The Most Important Architectural Decision

Separate the framework into **three layers**.

```text
┌───────────────────────────────────────────┐
│                  API Layer                │
│                                           │
│  routing / DI / validation / OpenAPI      │
├───────────────────────────────────────────┤
│               Execution Layer             │
│                                           │
│  scheduler / workers / pools / lifecycle  │
├───────────────────────────────────────────┤
│                Protocol Layer             │
│                                           │
│             ASGI / HTTP / WS              │
└───────────────────────────────────────────┘
```

This separation is fundamental.

FastAPI's conceptual center is heavily influenced by its application/API layer.

Your framework's differentiator should be the **execution layer**.

---

# 5. Framework Architecture

Proposed internal architecture:

```text
                     Application
                         │
                         ▼
                    Router
                         │
                         ▼
                 Request Resolver
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
        Dependency Graph       Endpoint
              │                     │
              └──────────┬──────────┘
                         ▼
                    Executor
                         │
                ┌────────┴────────┐
                │                 │
                ▼                 ▼
             Worker           Worker
                │                 │
                └────────┬────────┘
                         ▼
                    Response
                         │
                         ▼
                       ASGI
```

---

# 6. Requirements

## 6.1 Routing

Must support:

* static routes
* path parameters
* typed path parameters
* query parameters
* headers
* cookies
* route groups
* route prefixes
* HTTP methods
* route naming
* route metadata

Example:

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    ...
```

The router should compile routes during application startup.

Avoid performing expensive reflection or parsing on every request.

---

# 7. Request Model

Create a lightweight request object.

```python
@app.get("/users")
def users(request: Request):
    ...
```

The request should expose:

```python
request.method
request.path
request.headers
request.query
request.cookies
request.body()
request.client
```

But accessing these properties should be cheap.

Do not build large abstractions over ASGI unless they provide measurable value.

---

# 8. Response Model

Responses should be extremely simple.

```python
return {"id": 1, "name": "Fauzan"}
```

The framework automatically serializes the object.

Explicit responses:

```python
return Response(
    content="hello",
    status_code=200,
    headers={"x-version": "1"}
)
```

Support:

* JSON
* text
* bytes
* streaming
* files
* redirects
* HTML
* custom content types

---

# 9. Serialization

Serialization should be treated as a first-class performance concern.

The pipeline should be:

```text
Python Object
      │
      ▼
Serializer
      │
      ▼
Bytes
      │
      ▼
ASGI send()
```

Avoid unnecessary transformations:

```text
object
 → dict
 → JSON string
 → bytes
 → ASGI
```

Prefer:

```text
object
 → optimized serializer
 → bytes
 → ASGI
```

The framework should allow pluggable serializers.

---

# 10. Dependency Injection

Keep FastAPI's strongest idea.

Example:

```python
def database():
    return Database()


@app.get("/users")
def users(db: Database = Depends(database)):
    return db.users()
```

But internally represent dependencies as a **dependency graph**.

```text
users()
 │
 ├── database()
 │
 │    └── config()
 │
 └── auth()
      └── request()
```

Resolve the graph once where possible.

Do not repeatedly inspect function signatures on every request.

---

# 11. Dependency Execution

This is where your framework can diverge significantly.

Dependencies should have execution metadata.

Conceptually:

```python
Dependency(
    function=database,
    scope="request",
    execution="worker",
)
```

Potential execution categories:

```text
inline
worker
parallel
background
```

For example:

```python
user = Depends(load_user)
permissions = Depends(load_permissions)
```

If they are independent:

```text
          Request
          /     \
         /       \
    load_user   permissions
         \       /
          \     /
         Endpoint
```

The framework could eventually execute them concurrently/parallelly.

This is much more interesting than simply replacing `async` with threads.

---

# 12. Execution Model

The core abstraction should be something like:

```text
Executor
    │
    ├── submit()
    ├── execute()
    ├── map()
    ├── parallel()
    └── shutdown()
```

The web framework should not be tightly coupled to one executor implementation.

Possible implementations:

```text
ThreadExecutor
ProcessExecutor
AsyncExecutor
FreeThreadExecutor
```

Initially:

```text
Executor
   │
   └── ThreadPoolExecutor
```

Later:

```text
Executor
   │
   ├── GILThreadExecutor
   └── FreeThreadExecutor
```

---

# 13. Free-Threaded Python

This should be an explicit project goal.

On Python builds with free-threading:

```text
                 Request Scheduler
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       Thread 1       Thread 2       Thread 3
          │             │             │
       CPU work       CPU work       CPU work
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                      Response
```

The framework should detect the runtime characteristics rather than requiring application developers to care.

Potential API:

```python
app = App(
    workers=8,
    execution="auto",
)
```

Where:

```text
execution="auto"
       │
       ├── free-threaded Python
       │       → parallel workers
       │
       └── GIL Python
               → concurrent workers
```

---

# 14. Do Not Promise "2–5x Faster"

The project should not make performance claims before establishing a rigorous benchmark suite.

Instead define measurable targets.

For example:

### Target

For simple JSON endpoints:

```text
Framework overhead ≤ X μs/request
```

For IO-bound endpoints:

```text
Throughput >= FastAPI
```

For CPU-bound workloads on free-threaded Python:

```text
Scaling should approach available CPU capacity
```

For example:

```text
1 core  → 1.0x
2 cores → ~1.8x
4 cores → ~3.2x
8 cores → ~5–6x
```

Actual targets should be determined empirically.

---

# 15. Middleware

Middleware should use ASGI directly where possible.

```python
@app.middleware
def logging(request, next):
    start = time.monotonic()

    response = next(request)

    log(time.monotonic() - start)

    return response
```

However, this API is only conceptual.

Internally, middleware must preserve ASGI compatibility.

The framework should support:

```text
ASGI middleware
+
native framework middleware
```

This prevents ecosystem fragmentation.

---

# 16. Lifecycle

Support:

```python
@app.startup
def startup():
    ...


@app.shutdown
def shutdown():
    ...
```

Or preferably a lifespan abstraction.

Startup should initialize:

* worker pools
* database pools
* caches
* application resources

Shutdown should:

1. stop accepting requests
2. finish active requests
3. drain queues
4. execute shutdown hooks
5. terminate workers

---

# 17. Error Handling

Exceptions should have a predictable pipeline.

```text
Endpoint
   │
   ▼
Exception
   │
   ▼
Exception Resolver
   │
   ├── HTTPException
   ├── ValidationError
   ├── ApplicationError
   └── UnknownError
   │
   ▼
Response
```

Development:

```text
rich traceback
```

Production:

```json
{
    "detail": "Internal Server Error"
}
```

Never leak internal exception information by default.

---

# 18. Validation

Use Python typing as the primary interface.

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    ...
```

The framework should understand:

```text
int
str
float
bool
list[T]
dict[K, V]
Optional[T]
Union
Literal
Enum
dataclasses
```

Pydantic compatibility should be considered important because it is part of the FastAPI ecosystem.

But do not make the entire framework architecturally dependent on Pydantic.

---

# 19. OpenAPI

OpenAPI should be generated from the same internal representation used by routing and validation.

Do not build OpenAPI as a separate reflection system.

Use:

```text
Route Definition
       │
       ├── Runtime Resolver
       │
       ├── Validation
       │
       └── OpenAPI Generator
```

This gives you a single source of truth.

---

# 20. WebSockets

WebSockets should be supported, but not allowed to distort the HTTP execution architecture.

```python
@app.websocket("/chat")
def chat(socket):
    while True:
        message = socket.receive()
        socket.send(...)
```

Internally, WebSockets may use a different execution strategy because they are long-lived connections.

---

# 21. Streaming

Streaming must be first-class.

Example:

```python
@app.get("/stream")
def stream():
    return Stream(generator())
```

The framework must avoid buffering the entire response.

Pipeline:

```text
Generator
   │
   ▼
Chunk
   │
   ▼
ASGI send()
   │
   ▼
Network
```

---

# 22. Background Tasks

Background tasks should not be confused with parallel request execution.

```python
@app.post("/users")
def create_user(background: Background):
    background.submit(send_email)
    return {"created": True}
```

Initially:

```text
Background
    ↓
Thread pool
```

Eventually:

```text
Background Executor
    ├── thread
    ├── process
    └── distributed executor
```

---

# 23. Configuration

Configuration should be explicit and boring.

Example:

```python
app = App(
    workers=8,
    debug=False,
    docs=True,
)
```

Server configuration should remain separate:

```bash
mitti app:app --workers 8
```

Do not mix application configuration with deployment configuration.

---

# 24. ASGI Compatibility

This is non-negotiable.

The framework must expose:

```python
app(scope, receive, send)
```

and work with existing ASGI servers.

The framework should be usable with:

* Uvicorn
* Hypercorn
* Daphne
* other ASGI servers

Eventually, a dedicated server may be developed, but **do not start there**.

The framework should first prove that its execution model works independently of the network server.

---

# 25. Package Architecture

A possible package structure:

```text
mitti/
│
├── app.py
├── routing/
│   ├── router.py
│   ├── route.py
│   └── matcher.py
│
├── request/
│   ├── request.py
│   └── headers.py
│
├── response/
│   ├── response.py
│   ├── json.py
│   └── streaming.py
│
├── dependencies/
│   ├── graph.py
│   ├── resolver.py
│   └── dependency.py
│
├── execution/
│   ├── executor.py
│   ├── scheduler.py
│   ├── worker.py
│   └── pool.py
│
├── middleware/
│
├── validation/
│
├── serialization/
│
├── websocket/
│
├── lifespan/
│
└── openapi/
```

---

# 26. Internal Request Pipeline

The complete request lifecycle should look approximately like:

```text
             ASGI
               │
               ▼
        ┌──────────────┐
        │ HTTP Parser  │
        └──────┬───────┘
               │
               ▼
            Router
               │
               ▼
        Route Resolution
               │
               ▼
       Parameter Binding
               │
               ▼
      Dependency Resolution
               │
               ▼
          Executor
               │
               ▼
           Endpoint
               │
               ▼
         Serialization
               │
               ▼
          Response
               │
               ▼
             ASGI
```

The critical optimization principle:

> **Everything that can be moved from request time to startup time should be moved to startup time.**

---

# 27. Startup Compilation

When:

```python
app = App()
```

is created, the framework should eventually compile the application.

Conceptually:

```text
Python Functions
       │
       ▼
Application Graph
       │
       ▼
Compiled Routes
       │
       ▼
Compiled Dependency Graphs
       │
       ▼
Compiled Parameter Resolvers
       │
       ▼
Compiled Serialization Metadata
```

Then request execution becomes mostly:

```text
lookup
→ bind
→ execute
→ serialize
→ send
```

rather than repeatedly doing:

```text
inspect
→ introspect
→ build
→ resolve
→ execute
```

---

# 28. Philosophy Around Python Introspection

Python's introspection capabilities are powerful, but they should be used primarily at **application construction time**.

For example:

```python
inspect.signature(endpoint)
```

is perfectly reasonable during startup.

Doing it for every request is not.

The framework should aggressively separate:

```text
cold path
```

from:

```text
hot path
```

---

# 29. Hot Path Philosophy

The hot path should be brutally small.

Ideal conceptual pipeline:

```text
request
  ↓
route lookup
  ↓
argument extraction
  ↓
dependency execution
  ↓
endpoint
  ↓
serialization
  ↓
send
```

Avoid:

* repeated reflection
* unnecessary allocations
* unnecessary dictionaries
* repeated string parsing
* repeated validation metadata construction
* unnecessary object wrapping

---

# 30. Memory Philosophy

Performance is not only CPU.

Measure:

* allocations/request
* memory/request
* GC pressure
* object lifetime
* queue depth
* context switching

A framework that is 5% faster but allocates 3× more objects is not necessarily better.

---

# 31. Concurrency Philosophy

Do not advertise:

> "Threads are faster than async."

That is too simplistic.

Instead:

> **Concurrency and parallelism are execution strategies. The framework should choose the appropriate strategy without forcing application code to encode it.**

For IO-heavy workloads:

```text
Concurrency
```

For CPU-heavy workloads on free-threaded Python:

```text
Parallelism
```

The framework should provide one application model over both.

---

# 32. Explicit Escape Hatch

Advanced users should be able to control execution.

For example:

```python
@app.get("/cpu-intensive")
@parallel
def compute():
    ...
```

or:

```python
@app.get("/io-intensive")
@concurrent
def fetch():
    ...
```

But these should be **advanced features**, not requirements for normal applications.

---

# 33. Thread Safety

This becomes one of the most important areas of the project.

Free-threaded Python changes assumptions around shared mutable state.

The framework must clearly document:

```text
request-local state
application-global state
worker-local state
shared state
```

Potential primitives:

```python
RequestState
ApplicationState
WorkerState
```

Avoid implicit global mutable state.

---

# 34. Context Propagation

Request context must propagate correctly across worker boundaries.

For example:

```python
request_id
trace_id
user
locale
```

should remain available to:

```text
endpoint
→ dependency
→ middleware
→ logger
→ background task
```

Use `contextvars` where appropriate, but carefully test behavior under thread execution.

---

# 35. Observability

Build instrumentation hooks into the core.

Expose:

```text
request duration
route
status
worker
queue time
execution time
serialization time
```

Eventually:

```text
OpenTelemetry
Prometheus
structured logging
```

A framework should make performance debugging possible rather than merely claiming performance.

---

# 36. Testing Requirements

The framework needs several test layers.

### Unit tests

```text
router
dependency graph
validation
serialization
executor
middleware
```

### Integration tests

```text
ASGI
HTTP
WebSocket
lifespan
streaming
```

### Compatibility tests

Run the framework against:

```text
Uvicorn
Hypercorn
```

### Stress tests

Measure:

```text
RPS
latency
p50
p95
p99
CPU
memory
allocations
```

### Parallelism tests

Especially:

```text
1 worker
2 workers
4 workers
8 workers
16 workers
```

on free-threaded Python.

---

# 37. Benchmark Suite

Create a separate benchmark repository/directory.

At minimum:

```text
/plaintext
/json
/path-param
/query-param
/validation
/dependency
/database
/cpu
/streaming
```

Compare against:

```text
FastAPI
Starlette
Flask
Litestar
```

The goal is not to win every benchmark.

The goal is to understand:

> **Where does the framework spend its time?**

---

# 38. Compatibility Goal

The first major milestone should be:

```text
FastAPI-like developer experience
+
ASGI compatibility
+
competitive performance
```

Not:

```text
completely new web programming paradigm
```

You need adoption before radicalism becomes useful.

---

# 39. API Design

The public API should feel familiar.

Example:

```python
from mitti import App

app = App()


@app.get("/hello")
def hello():
    return {"message": "hello"}
```

Typed parameters:

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return repository.get(user_id)
```

Request:

```python
@app.post("/users")
def create_user(user: User):
    return repository.create(user)
```

Dependency:

```python
@app.get("/users")
def users(db: Database = Depends(get_database)):
    return db.users()
```

The developer should immediately understand the framework if they know FastAPI.

---

# 40. What NOT to Build Initially

Do not initially build:

* custom HTTP server
* custom HTTP parser
* ORM
* authentication framework
* task queue
* distributed scheduler
* frontend framework
* template engine
* CLI deployment platform
* cloud platform
* custom JSON implementation
* custom database layer

These are distractions.

Build the **execution engine**.

---

# 41. MVP

The first version should contain only:

```text
1. ASGI application
2. Router
3. Path parameters
4. Query parameters
5. JSON responses
6. Request object
7. Dependency injection
8. Basic validation
9. Middleware
10. Lifespan
11. Thread-based executor
12. Benchmark suite
```

That is enough to establish whether the core thesis works.

---

# 42. Version 0.1

The first release should answer one question:

> **Can we build an ergonomic synchronous ASGI framework whose execution model provides excellent concurrency and a credible path to true parallelism?**

Do not attempt to answer anything else.

---

# 43. Version 0.2

Add:

```text
OpenAPI
Pydantic integration
streaming
WebSockets
background tasks
structured errors
observability
```

---

# 44. Version 0.3

Focus heavily on:

```text
free-threaded Python
```

Measure:

```text
CPU scaling
request scaling
dependency scaling
serialization scaling
```

This is where the framework begins to become technically distinctive.

---

# 45. Version 1.0

The framework should only call itself production-ready when:

```text
ASGI compatible
Stable API
Excellent test coverage
Predictable lifecycle
Production observability
OpenAPI
WebSockets
Streaming
Validation
Security primitives
Graceful shutdown
Performance benchmarks
Free-threaded support
GIL compatibility
```

---

# 46. The Strategic Positioning

Do not position it as:

> FastAPI but faster.

Position it as:

> **A Python web framework designed for the transition from concurrent Python to parallel Python.**

That is a much stronger technical thesis.

The ecosystem is moving toward:

```text
Python
   │
   ├── GIL today
   │
   └── Free-threaded Python
           │
           ▼
      true parallelism
```

Most web frameworks were designed around the first world.

Your framework can be designed for both.

---

# 47. The Deeper Idea

The really interesting abstraction is not:

```text
async vs sync
```

It is:

```text
WHAT
 │
 ▼
Application semantics
 │
 ▼
WHERE
 │
 ▼
Execution strategy
```

The developer writes:

```python
def process_order(order):
    ...
```

The framework decides whether the work should execute:

```text
inline
thread
parallel thread
process
async task
```

depending on the execution environment and workload.

That is the long-term architectural bet.

---

# 48. Project North Star

The project should ultimately aim for this:

```text
                    Python Application
                           │
                           ▼
                     Framework API
                           │
                           ▼
                   Execution Planner
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
       Concurrent       Parallel        Background
          │                │                │
          ▼                ▼                ▼
        Threads       Free Threads       Workers
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                          ASGI
```

The framework becomes an **execution engine for Python web applications**, not merely a routing library.

---

# 49. First Engineering Milestone

Before writing the router, validation system, or OpenAPI generator, prove this:

```python
@app.get("/compute")
def compute():
    return expensive_cpu_work()
```

Run:

```text
1 worker
2 workers
4 workers
8 workers
```

on free-threaded Python.

Then compare:

```text
throughput
latency
CPU utilization
scaling efficiency
```

If the execution model does not scale, everything else is secondary.

If it does scale, you have the foundation for a genuinely differentiated framework.

---

# 50. Recommended Development Order

```text
Phase 1
ASGI fundamentals
       ↓
Phase 2
Execution engine
       ↓
Phase 3
Router
       ↓
Phase 4
Request/Response
       ↓
Phase 5
Dependency injection
       ↓
Phase 6
Validation
       ↓
Phase 7
Serialization
       ↓
Phase 8
Middleware + lifespan
       ↓
Phase 9
OpenAPI
       ↓
Phase 10
Free-threaded optimization
       ↓
Phase 11
Benchmarking
       ↓
Phase 12
Production hardening
```

The important part is that **the execution engine comes before the framework features**.

That is where the project's intellectual property and architectural differentiation should live.
