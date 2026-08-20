from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import MutableMapping

Scope = MutableMapping[str, object]
Message = MutableMapping[str, object]

Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]

MittiApp = Callable[[Scope, Receive, Send], Awaitable[None]]
