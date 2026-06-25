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
            subtitle = f"[dim]Site: {self._filter_site}[/]"
        elif self._filter_date:
            subtitle = f"[dim]Date: {self._filter_date}[/]"
        else:
            subtitle = f"[dim]{len(self._quotations)} quotations[/]"

        table = Table(box=None, show_header=True, header_style="bold", padding=(0, 2))
        table.add_column("", no_wrap=True, width=2)
        table.add_column("QTN", style="cyan", no_wrap=True)
        table.add_column("Site")
        table.add_column("Date", style="yellow")
        table.add_column("PDF", no_wrap=True, justify="center")

        for i, q in enumerate(self._quotations):
            pointer = "▸" if i == self._selected_index else " "
            style = "" if i == self._selected_index else "dim"
            pdf_icon = "[green]✓[/]" if q.pdf_exists else "[dim]✗[/]"
            table.add_row(
                f"[bold]{pointer}[/]",
                f"[{style}]QTN-{q.number}[/]",
                f"[{style}]{q.site}[/]",
                f"[{style}]{q.date}[/]",
                pdf_icon,
            )

        content = Table.grid(padding=(0, 1))
        content.add_column()
        content.add_row(title)
        content.add_row(subtitle)
        content.add_row("")
        content.add_row(table)
        content.add_row("")
        content.add_row("[dim]↑↓ Navigate | Enter Details | Esc Back[/]")

        return Panel(content, title="List", border_style="blue")
