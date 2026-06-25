from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from rich.console import RenderableType

from rafikone.dashboard.router import Router


class Screen(ABC):
    def __init__(self, router: Router) -> None:
        self.router = router
        self._selected_index = 0

    @abstractmethod
    def render(self) -> RenderableType: ...

    def handle_key(self, key: str) -> str | None:
        if key == "up":
            self._cursor_up()
        elif key == "down":
            self._cursor_down()
        return None

    def on_enter(self, data: dict[str, Any] | None = None) -> None:
        self._selected_index = 0

    def on_exit(self) -> None:
        pass

    def _cursor_up(self) -> None:
        pass

    def _cursor_down(self) -> None:
        pass
