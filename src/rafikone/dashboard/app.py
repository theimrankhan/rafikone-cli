from __future__ import annotations

import io
import shutil
import subprocess
from typing import Any

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, Window, FormattedTextControl
from prompt_toolkit.formatted_text import ANSI
from rich.console import Console

from rafikone.dashboard.router import Router

SCREEN_REGISTRY: dict[str, type] = {}


def register_screen(name: str) -> callable:
    def wrapper(cls: type) -> type:
        SCREEN_REGISTRY[name] = cls
        return cls

    return wrapper


class DashboardApp:
    def __init__(self) -> None:
        self.router = Router()
        self._screens: dict[str, Any] = {}
        self._console = Console()
        self._init_screens()
        self._pt_app = self._build_app()

    def _init_screens(self) -> None:
        from rafikone.dashboard.screens.home import HomeScreen
        from rafikone.dashboard.screens.search import SearchScreen
        from rafikone.dashboard.screens.list import ListScreen
        from rafikone.dashboard.screens.detail import DetailScreen
        from rafikone.dashboard.screens.stats import StatsScreen
        from rafikone.dashboard.screens.settings import SettingsScreen
        from rafikone.dashboard.screens.help import HelpScreen

        self._screens["home"] = HomeScreen(self.router)
        self._screens["search"] = SearchScreen(self.router)
        self._screens["list"] = ListScreen(self.router)
        self._screens["detail"] = DetailScreen(self.router)
        self._screens["stats"] = StatsScreen(self.router)
        self._screens["settings"] = SettingsScreen(self.router)
        self._screens["help"] = HelpScreen(self.router)

    @property
    def _current(self) -> Any:
        return self._screens[self.router.current]

    def _get_formatted_text(self) -> ANSI:
        try:
            renderable = self._current.render()
            buf = io.StringIO()
            w, h = shutil.get_terminal_size()
            c = Console(file=buf, width=w, height=h, force_terminal=True)
            c.print(renderable)
            return ANSI(buf.getvalue())
        except Exception:
            from rich.panel import Panel
            from rich.text import Text
            buf = io.StringIO()
            w, h = shutil.get_terminal_size()
            c = Console(file=buf, width=w, height=h, force_terminal=True)
            c.print(
                Panel(
                    Text("An error occurred while rendering this screen.\nPress Esc to go back.", style="red"),
                    title="Render Error",
                    border_style="red",
                )
            )
            return ANSI(buf.getvalue())

    def _build_app(self) -> Application:
        kb = KeyBindings()

        @kb.add("up")
        def _(event: Any) -> None:
            self._current.handle_key("up")
            event.app.invalidate()

        @kb.add("down")
        def _(event: Any) -> None:
            self._current.handle_key("down")
            event.app.invalidate()

        @kb.add("enter")
        def _(event: Any) -> None:
            action = self._current.handle_key("enter")
            self._dispatch(action, event)

        @kb.add("escape")
        def _(event: Any) -> None:
            if self.router.current != "home":
                prev = self.router.current
                self._screens[prev].on_exit()
                self.router.pop()
                self._current.on_enter()
            event.app.invalidate()

        @kb.add("c-c")
        def _(event: Any) -> None:
            event.app.exit()

        @kb.add("c-l")
        def _(event: Any) -> None:
            self._current.on_enter()
            event.app.invalidate()

        @kb.add("q")
        def _(event: Any) -> None:
            if self.router.current != "home":
                prev = self.router.current
                self._screens[prev].on_exit()
                self.router.pop()
                self._current.on_enter()
                event.app.invalidate()

        @kb.add("backspace")
        def _(event: Any) -> None:
            self._current.handle_key("backspace")
            event.app.invalidate()

        return Application(
            layout=Layout(
                Window(
                    FormattedTextControl(self._get_formatted_text),
                    dont_extend_height=False,
                )
            ),
            key_bindings=kb,
            full_screen=True,
            mouse_support=False,
        )

    def _dispatch(self, action: str | None, event: Any) -> None:
        if action is None:
            return
        if action == "exit":
            event.app.exit()
        elif action == "back":
            if self.router.current != "home":
                prev = self.router.current
                self._screens[prev].on_exit()
                self.router.pop()
                self._current.on_enter()
        elif action.startswith("go:"):
            target = action[3:]
            data = None
            if "|" in target:
                target, data_raw = target.split("|", 1)
                import json as _json
                try:
                    data = _json.loads(data_raw)
                except _json.JSONDecodeError:
                    data = None
            self.router.push(target, data)
            self._current.on_enter(data)
        elif action.startswith("cmd:"):
            cmd = action[4:]
            subprocess.Popen(["xdg-open", cmd], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        elif action.startswith("shell:"):
            cmd = action[6:]
            subprocess.run(cmd, shell=True)
        event.app.invalidate()

    def run(self) -> None:
        self._current.on_enter()
        self._pt_app.run()
