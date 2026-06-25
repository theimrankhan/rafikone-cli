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

        shortcuts.add_row(Text("↑ ↓"), Text("Navigate"))
        shortcuts.add_row(Text("Enter"), Text("Select / Confirm"))
        shortcuts.add_row(Text("Esc / q"), Text("Go back"))
        shortcuts.add_row(Text("Ctrl+C"), Text("Exit application"))
        shortcuts.add_row(Text("Ctrl+L"), Text("Refresh screen"))
        shortcuts.add_row(Text(""), Text(""))

        cmd_table = Table.grid(padding=(0, 2))
        cmd_table.add_column(style="bold", width=26)
        cmd_table.add_column()

        cmds = [
            ("rafikone", "Open interactive dashboard"),
            ("rafikone new", "Create a new quotation"),
            ("rafikone list", "List all quotations"),
            ("rafikone list --detailed", "List with status columns"),
            ("rafikone list --site akash", "Filter by site"),
            ("rafikone search akash", "Search quotations"),
            ("rafikone info 0034", "Quotation details"),
            ("rafikone open 0034", "Open folder"),
            ("rafikone stats", "Show statistics"),
            ("rafikone doctor", "Check for issues"),
            ("rafikone init", "Set up project root"),
            ("rafikone config", "View/update config"),
        ]
        for cmd, desc in cmds:
            cmd_table.add_row(Text(cmd), Text(desc))
        cmd_table.add_row(Text(""), Text(""))

        about = Table.grid(padding=(0, 2))
        about.add_column(style="bold", width=16)
        about.add_column()

        about.add_row(Text("Name"), Text("RafikOne CLI"))
        about.add_row(Text("Version"), Text("1.1.0"))
        about.add_row(Text("License"), Text("MIT"))
        about.add_row(Text("Author"), Text("Rafikone"))
        about.add_row(Text(""), Text(""))

        desc1 = Text("Keyboard-friendly terminal")
        desc1.stylize("dim")
        desc2 = Text("quotation manager.")
        desc2.stylize("dim")
        about.add_row(desc1, Text(""))
        about.add_row(desc2, Text(""))

        layout = Table.grid(padding=(0, 4))
        layout.add_column(no_wrap=True)
        layout.add_column(no_wrap=True)
        layout.add_column(no_wrap=True)

        kbd_head = Text("Keyboard")
        kbd_head.stylize("bold")
        cmd_head = Text("Commands")
        cmd_head.stylize("bold")
        about_head = Text("About")
        about_head.stylize("bold")

        layout.add_row(kbd_head, cmd_head, about_head)
        layout.add_row(shortcuts, cmd_table, about)

        hint = Text("Esc Back")
        hint.stylize("dim")

        content = Table.grid(padding=(0, 1))
        content.add_column()
        content.add_row(title)
        content.add_row(Text(""))
        content.add_row(layout)
        content.add_row(Text(""))
        content.add_row(hint)

        return Panel(content, title="Help", border_style="magenta")
