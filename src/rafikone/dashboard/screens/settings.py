from __future__ import annotations

from pathlib import Path
from typing import Any

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from rafikone.config import CONFIG_FILE, get_config, get_project_root, set_project_root
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
        info.add_row("Root Directory", f"[dim]{root}[/]")
        info.add_row("Config File", f"[dim]{CONFIG_FILE}[/]")
        info.add_row("")
        info.add_row("[yellow]Tip:[/]", "Run [bold]rafikone config[/] from terminal")
        info.add_row("", "to update the root directory path.")

        content = Table.grid(padding=(0, 1))
        content.add_column()
        content.add_row(title)
        content.add_row("")
        content.add_row(info)
        content.add_row("")
        content.add_row("[dim]Esc Back[/]")

        return Panel(content, title="Settings", border_style="yellow")
