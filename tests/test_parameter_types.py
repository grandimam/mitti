import unittest
from datetime import date, datetime
from decimal import Decimal
from enum import Enum, IntEnum
from typing import Literal
from uuid import UUID

from mitti.inspector import Inspector
from mitti.server import Mitti
from tests.test_route_validation import make_request


class Status(str, Enum):
    pending = "pending"
    shipped = "shipped"


class Priority(IntEnum):
    low = 1
    high = 2


class ParameterTypeTests(unittest.TestCase):
    def request_value(self, annotation, query):
        app = Mitti()
        received = []

        async def handler(value):
            received.append(value)
            return "ok"

        handler.__annotations__ = {"value": annotation}
        app.get(path="/values", methods=["GET"])(handler)
        return make_request(app, "/values", query), received

    def test_supported_values_reach_handler_with_expected_types(self):
        identifier = "12345678-1234-5678-1234-567812345678"
        cases = [
            (float, b"value=1.25", 1.25),
            (UUID, f"value={identifier}".encode(), UUID(identifier)),
            (date, b"value=2026-09-25", date(2026, 9, 25)),
            (datetime, b"value=2026-09-25T12:30:00Z",
             datetime.fromisoformat("2026-09-25T12:30:00+00:00")),
            (Decimal, b"value=0.1234567890123456789", Decimal("0.1234567890123456789")),
            (Status, b"value=shipped", Status.shipped),
            (Priority, b"value=2", Priority.high),
            (Literal["price", "newest"], b"value=price", "price"),
            (Literal[1, 2], b"value=2", 2),
            (Literal[True], b"value=true", True),
            (list[int], b"value=3&value=1&value=3", [3, 1, 3]),
            (list[Status], b"value=pending&value=shipped", [Status.pending, Status.shipped]),
            (list[Literal["price", "newest"]], b"value=price", ["price"]),
            (str, b"value=", ""),
            (list[str], b"value=&value=hello", ["", "hello"]),
        ]
        for annotation, query, expected in cases:
            with self.subTest(annotation=annotation):
                messages, received = self.request_value(annotation, query)
                self.assertEqual(messages[0]["status"], 200)
                self.assertEqual(received, [expected])
                self.assertIs(type(received[0]), type(expected))

    def test_invalid_values_return_422_without_calling_handler(self):
        cases = [
            (UUID, b"value=invalid"),
            (date, b"value=2026-02-30"),
            (datetime, b"value=invalid"),
            (Decimal, b"value=invalid"),
            (float, b"value=invalid"),
            (Status, b"value=unknown"),
            (Priority, b"value=3"),
            (Literal["price", "newest"], b"value=random"),
            (Literal[1, 2], b"value=3"),
            (list[int], b"value=1&value=bad"),
            (list[int], b"value="),
            (list[int], b""),
            (int, b"value=1&value=2"),
        ]
        for annotation, query in cases:
            with self.subTest(annotation=annotation, query=query):
                messages, received = self.request_value(annotation, query)
                self.assertEqual(messages[0]["status"], 422)
                self.assertEqual(received, [])

    def test_uuid_path_and_list_default(self):
        app = Mitti()
        received = []

        @app.get(path="/values/{identifier}", methods=["GET"])
        async def handler(identifier: UUID, values: list[int] = [10]):
            received.append((identifier, values))
            return "ok"

        identifier = UUID("12345678-1234-5678-1234-567812345678")
        messages = make_request(app, f"/values/{identifier}")
        self.assertEqual(messages[0]["status"], 200)
        self.assertEqual(received, [(identifier, [10])])

    def test_unsupported_annotations_fail_at_registration(self):
        for annotation, path_names in [
            (list[int], {"value"}), (list, set()),
            (list[list[int]], set()), (dict[str, int], set()),
            (bytes, set()), (bytearray, set()), (complex, set()),
        ]:
            with self.subTest(annotation=annotation, path_names=path_names):
                def handler(value):
                    pass

                handler.__annotations__ = {"value": annotation}
                with self.assertRaises(TypeError):
                    Inspector.inspect(handler, path_names)
