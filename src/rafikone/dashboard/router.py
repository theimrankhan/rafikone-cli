from __future__ import annotations

from typing import Any


class Router:
    def __init__(self) -> None:
        self._stack: list[str] = ["home"]
        self._data: dict[str, Any] = {}

    @property
    def current(self) -> str:
        return self._stack[-1]

    def push(self, screen: str, data: dict[str, Any] | None = None) -> None:
        self._stack.append(screen)
        if data:
            self._data[screen] = data

    def pop(self) -> str:
        if len(self._stack) > 1:
            self._stack.pop()
        return self.current

    def get_data(self, screen: str) -> dict[str, Any] | None:
        return self._data.get(screen)

    def clear_data(self, screen: str) -> None:
        self._data.pop(screen, None)
