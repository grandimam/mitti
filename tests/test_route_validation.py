import asyncio
import unittest

from mitti.server import Mitti


def make_request(app, path: str, query_string: bytes = b""):
    messages = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        messages.append(message)

    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "query_string": query_string,
    }
    asyncio.run(app(scope, receive, send))
    return messages


class RouteValidationTests(unittest.TestCase):
    def test_path_contract_is_checked_during_registration(self):
        app = Mitti()

        with self.assertRaisesRegex(
            ValueError,
            "Path parameters missing from handler signature: user_id",
        ):

            @app.get(path="/users/{user_id}", methods=["GET"])
            async def user():
                return "unreachable"

    def test_path_and_query_parameters_are_converted(self):
        app = Mitti()

        @app.get(path="/users/{user_id}", methods=["GET"])
        async def user(user_id: int, active: bool):
            return f"{user_id}:{active}"

        messages = make_request(app, "/users/42", b"active=true")

        self.assertEqual(messages[0]["status"], 200)
        self.assertEqual(messages[1]["body"], b"42:True")

    def test_default_is_used_for_missing_optional_query_parameter(self):
        app = Mitti()

        @app.get(path="/users/{user_id}", methods=["GET"])
        async def user(user_id: int, page: int = 1):
            return f"{user_id}:{page}"

        messages = make_request(app, "/users/42")

        self.assertEqual(messages[0]["status"], 200)
        self.assertEqual(messages[1]["body"], b"42:1")

    def test_invalid_path_parameter_becomes_validation_response(self):
        app = Mitti()

        @app.get(path="/users/{user_id}", methods=["GET"])
        async def user(user_id: int):
            return str(user_id)

        messages = make_request(app, "/users/not-an-int")

        self.assertEqual(messages[0]["status"], 422)
        self.assertIn(b"Invalid path parameter 'user_id'", messages[1]["body"])

    def test_missing_query_parameter_becomes_validation_response(self):
        app = Mitti()

        @app.get(path="/users", methods=["GET"])
        async def users(limit: int):
            return str(limit)

        messages = make_request(app, "/users")

        self.assertEqual(messages[0]["status"], 422)
        self.assertIn(b"Invalid query parameter 'limit'", messages[1]["body"])

    def test_unhandled_handler_exception_becomes_internal_error(self):
        app = Mitti()

        @app.get(path="/users", methods=["GET"])
        async def users():
            raise RuntimeError("database unavailable")

        with self.assertLogs("mitti.errors", level="ERROR"):
            messages = make_request(app, "/users")

        self.assertEqual(messages[0]["status"], 500)
        self.assertEqual(messages[1]["body"], b"Internal Server Error")


if __name__ == "__main__":
    unittest.main()
