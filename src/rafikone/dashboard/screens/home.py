from __future__ import annotations

from typing import Any

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from rafikone.config import get_project_root
from rafikone.dashboard.router import Router
from rafikone.dashboard.screens import Screen
from rafikone.scanner import get_stats, scan_quotations, scan_all

MENU_ITEMS = [
    ("Create Quotation", "go:create"),
    ("Search Quotations", "go:search"),
    ("List Quotations", "go:list"),
    ("Recent Quotations", "go:recent"),
    ("Statistics", "go:stats"),
    ("Settings", "go:settings"),
    ("Help", "go:help"),
    ("Exit", "exit"),
]


class HomeScreen(Screen):
    def __init__(self, router: Router) -> None:
        super().__init__(router)
        self._menu_items = MENU_ITEMS

    def render(self) -> Panel:
        title = Text("RAFIKONE CLI", style="bold cyan")
        version = Text("v1.1.0", style="dim")

        try:
            root = get_project_root()
            root_str = str(root)
        except Exception:
            root_str = "Not configured"

        try:
            stats = get_stats()
        except Exception:
            stats = {}

        try:
            today_count = len(
                scan_quotations(
                    date_filter=__import__("datetime").date.today().isoformat()
                )
            )
        except Exception:
            today_count = 0

        info = Table.grid(padding=(0, 2))
        info.add_column(style="bold")
        info.add_column()
        info.add_row(Text("Root"), Text(root_str))
        info.add_row(Text("Version"), Text("1.1.0"))
        info.add_row(Text(""))

        has_stats = bool(stats)
        if has_stats:
            info.add_row(Text("Total Quotations"), Text(str(stats.get("total_quotations", 0))))
            info.add_row(Text("Today"), Text(str(today_count)))
            info.add_row(Text("Latest"), Text(str(stats.get("latest_quotation", "N/A"))))
            try:
                missing = sum(
                    1 for s in scan_all() for q in s.quotations if not q.pdf_exists
                )
                info.add_row(Text("Missing PDFs"), Text(str(missing)))
            except Exception:
                pass
            info.add_row(Text(""))
            info.add_row(Text("Sites"), Text(str(stats.get("total_sites", 0))))
            info.add_row(Text("PDFs"), Text(str(stats.get("total_pdfs", 0))))
            info.add_row(Text("Invoices"), Text(str(stats.get("total_invoices", 0))))

        info.add_row(Text(""))
        hint = Text("↑↓ Navigate | Enter Select | Esc Back | q Quit | Ctrl+C Exit")
        hint.stylize("dim")
        info.add_row(hint, Text(""))

        menu = Table.grid(padding=(0, 2))
        menu.add_column()
        for i, (label, _action) in enumerate(self._menu_items):
            prefix = "▸ " if i == self._selected_index else "  "
            text = Text(f"{prefix}{label}")
            if i == self._selected_index:
                text.stylize("bold white")
            else:
                text.stylize("dim")
            menu.add_row(text)

        header = Table.grid(padding=(0, 2))
        header.add_column(no_wrap=True)
        header.add_row(title)
        header.add_row(version)

        layout = Table.grid(padding=(0, 4))
        layout.add_column(no_wrap=True)
        layout.add_column(no_wrap=True)
        layout.add_row(header, Text(""))
        layout.add_row(info, menu)

        return Panel(layout, title="Dashboard", border_style="cyan")

    def handle_key(self, key: str) -> str | None:
        if key == "up":
            self._selected_index = (self._selected_index - 1) % len(self._menu_items)
            return None
        if key == "down":
            self._selected_index = (self._selected_index + 1) % len(self._menu_items)
            return None
        if key == "enter":
            _label, action = self._menu_items[self._selected_index]
            if action == "exit":
                return "exit"
            if action == "go:create":
                return "go:create"
            if action == "go:recent":
                self.router.push("list")
                self.router.clear_data("list")
                return None
            return action
        if key == "/":
            return "go:search"
        if key == "?":
            return "go:help"
        return None

    def on_enter(self, data: dict[str, Any] | None = None) -> None:
        self._selected_index = 0
