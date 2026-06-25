from __future__ import annotations

from typing import Any

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from rafikone.config import CONFIG_FILE, get_config
from rafikone.dashboard.router import Router
from rafikone.dashboard.screens import Screen


class SettingsScreen(Screen):
    def __init__(self, router: Router) -> None:
        super().__init__(router)

    def on_enter(self, data: dict[str, Any] | None = None) -> None:
        try:
            self._cfg = get_config()
        except Exception:
            self._cfg = {}

    def handle_key(self, key: str) -> str | None:
        return None

    def render(self) -> Panel:
        title = Text("Settings", style="bold cyan")

        info = Table.grid(padding=(0, 2))
        info.add_column(style="bold", width=22)
        info.add_column()

        root = self._cfg.get("project_root", "Not set")
        root_text = Text(root)
        root_text.stylize("dim")
        info.add_row(Text("Root Directory"), root_text)

        config_text = Text(str(CONFIG_FILE))
        config_text.stylize("dim")
        info.add_row(Text("Config File"), config_text)
        info.add_row(Text(""))

        tip_label = Text("Tip:")
        tip_label.stylize("yellow")
        tip_text = Text("Run rafikone config from terminal to update the root directory path.")
        info.add_row(tip_label, tip_text)

        hint = Text("Esc Back")
        hint.stylize("dim")

        content = Table.grid(padding=(0, 1))
        content.add_column()
        content.add_row(title)
        content.add_row(Text(""))
        content.add_row(info)
        content.add_row(Text(""))
        content.add_row(hint)

        return Panel(content, title="Settings", border_style="yellow")
