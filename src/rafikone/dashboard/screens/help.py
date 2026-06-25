from __future__ import annotations

from typing import Any

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from rafikone.dashboard.router import Router
from rafikone.dashboard.screens import Screen


class HelpScreen(Screen):
    def __init__(self, router: Router) -> None:
        super().__init__(router)

    def on_enter(self, data: dict[str, Any] | None = None) -> None:
        pass

    def handle_key(self, key: str) -> str | None:
        return None

    def render(self) -> Panel:
        title = Text("Help", style="bold cyan")

        shortcuts = Table.grid(padding=(0, 2))
        shortcuts.add_column(style="bold", width=16)
        shortcuts.add_column()

        shortcuts.add_row("↑ ↓", "Navigate")
        shortcuts.add_row("Enter", "Select / Confirm")
        shortcuts.add_row("Esc / q", "Go back")
        shortcuts.add_row("Ctrl+C", "Exit application")
        shortcuts.add_row("Ctrl+L", "Refresh screen")
        shortcuts.add_row("", "")

        cmd_table = Table.grid(padding=(0, 2))
        cmd_table.add_column(style="bold", width=22)
        cmd_table.add_column()

        cmd_table.add_row("rafikone", "Open interactive dashboard")
        cmd_table.add_row("rafikone new", "Create a new quotation")
        cmd_table.add_row("rafikone list", "List all quotations")
        cmd_table.add_row("rafikone list --detailed", "List with status columns")
        cmd_table.add_row("rafikone list --site akash", "Filter by site")
        cmd_table.add_row("rafikone search akash", "Search quotations")
        cmd_table.add_row("rafikone info 0034", "Quotation details")
        cmd_table.add_row("rafikone open 0034", "Open folder")
        cmd_table.add_row("rafikone stats", "Show statistics")
        cmd_table.add_row("rafikone doctor", "Check for issues")
        cmd_table.add_row("rafikone init", "Set up project root")
        cmd_table.add_row("rafikone config", "View/update config")
        cmd_table.add_row("", "")

        about = Table.grid(padding=(0, 2))
        about.add_column(style="bold", width=16)
        about.add_column()

        about.add_row("Name", "RafikOne CLI")
        about.add_row("Version", "1.1.0")
        about.add_row("License", "MIT")
        about.add_row("Author", "Rafikone")
        about.add_row("", "")
        about.add_row("[dim]Keyboard-friendly terminal[/]", "")
        about.add_row("[dim]quotation manager.[/]", "")

        layout = Table.grid(padding=(0, 4))
        layout.add_column(no_wrap=True)
        layout.add_column(no_wrap=True)
        layout.add_column(no_wrap=True)
        layout.add_row("[bold]Keyboard[/]", "[bold]Commands[/]", "[bold]About[/]")
        layout.add_row(shortcuts, cmd_table, about)

        content = Table.grid(padding=(0, 1))
        content.add_column()
        content.add_row(title)
        content.add_row("")
        content.add_row(layout)
        content.add_row("")
        content.add_row("[dim]Esc Back[/]")

        return Panel(content, title="Help", border_style="magenta")
