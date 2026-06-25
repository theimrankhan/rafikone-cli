from __future__ import annotations

from typing import Any

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from rafikone.dashboard.router import Router
from rafikone.dashboard.screens import Screen
from rafikone.scanner import scan_quotations


class ListScreen(Screen):
    def __init__(self, router: Router) -> None:
        super().__init__(router)
        self._quotations: list = []
        self._selected_index = 0
        self._filter_site = ""
        self._filter_date = ""

    def on_enter(self, data: dict[str, Any] | None = None) -> None:
        self._selected_index = 0
        if data:
            self._filter_site = data.get("site", "")
            self._filter_date = data.get("date", "")
        else:
            self._filter_site = ""
            self._filter_date = ""
        try:
            self._quotations = scan_quotations(
                site_filter=self._filter_site or None,
                date_filter=self._filter_date or None,
            )
        except Exception:
            self._quotations = []

    def handle_key(self, key: str) -> str | None:
        if key == "up":
            self._selected_index = max(0, self._selected_index - 1)
            return None
        if key == "down":
            self._selected_index = min(len(self._quotations) - 1, self._selected_index + 1)
            return None
        if key == "enter":
            if self._quotations:
                qtn = self._quotations[self._selected_index]
                self.router.push("detail", {"number": qtn.number})
            return None
        return None

    def render(self) -> Panel:
        title = Text("Quotations", style="bold cyan")

        if self._filter_site:
            subtitle = Text(f"Site: {self._filter_site}")
        elif self._filter_date:
            subtitle = Text(f"Date: {self._filter_date}")
        else:
            subtitle = Text(f"{len(self._quotations)} quotations")
        subtitle.stylize("dim")

        table = Table(box=None, show_header=True, header_style="bold", padding=(0, 2))
        table.add_column("", no_wrap=True, width=2)
        table.add_column("QTN", style="cyan", no_wrap=True)
        table.add_column("Site")
        table.add_column("Date", style="yellow")
        table.add_column("PDF", no_wrap=True, justify="center")

        for i, q in enumerate(self._quotations):
            pointer = Text("▸" if i == self._selected_index else " ")
            pointer.stylize("bold")

            qtn_text = Text(f"QTN-{q.number}")
            site_text = Text(q.site)
            date_text = Text(q.date)

            if i != self._selected_index:
                qtn_text.stylize("dim")
                site_text.stylize("dim")
                date_text.stylize("dim")

            pdf_icon = Text("✓")
            pdf_icon.stylize("green" if q.pdf_exists else "dim")

            table.add_row(pointer, qtn_text, site_text, date_text, pdf_icon)

        hint = Text("↑↓ Navigate | Enter Details | Esc Back")
        hint.stylize("dim")

        content = Table.grid(padding=(0, 1))
        content.add_column()
        content.add_row(title)
        content.add_row(subtitle)
        content.add_row(Text(""))
        content.add_row(table)
        content.add_row(Text(""))
        content.add_row(hint)

        return Panel(content, title="List", border_style="blue")
