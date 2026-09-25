# Coding style

- Prefer negation checks (`if not value:`) over explicit `None` checks (`if value is None:`).
- Put each imported name on its own line. For example, use separate `from datetime import date` and `from datetime import datetime` statements instead of `from datetime import date, datetime`.
