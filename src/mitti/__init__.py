"""mitti — a Python ASGI framework unifying concurrent and parallel
execution behind a synchronous application model.

The framework owns the execution machinery: application code stays
ordinary, synchronous Python while mitti decides how to run it
efficiently — concurrently on GIL builds, in parallel on free-threaded
Python.
"""

from .app import App

__all__ = ["App"]
__version__ = "0.1.0"
