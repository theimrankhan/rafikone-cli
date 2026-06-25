from __future__ import annotations

from typing import Any

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from rafikone.dashboard.router import Router
from rafikone.dashboard.screens import Screen
from rafikone.scanner import scan_all

SEARCHABLE_KEYS = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _-"
)


class SearchScreen(Screen):
    def __init__(self, router: Router) -> None:
        super().__init__(router)
        self._query = ""
        self._results: list = []
        self._all_qtns: list = []
        self._selected_index = 0

    def on_enter(self, data: dict[str, Any] | None = None) -> None:
        self._query = ""
        self._selected_index = 0
        self._all_qtns = []
        try:
            for site in scan_all():
                for q in site.quotations:
                    self._all_qtns.append(q)
        except Exception:
            self._all_qtns = []
        self._filter()

    def handle_key(self, key: str) -> str | None:
        if key == "up":
            self._selected_index = max(0, self._selected_index - 1)
            return None
        if key == "down":
            self._selected_index = min(len(self._results) - 1, self._selected_index + 1)
            return None
        if key == "enter":
            if self._results:
                qtn = self._results[self._selected_index]
                self.router.push("detail", {"number": qtn.number})
                return None
            return None
        if key == "backspace":
            self._query = self._query[:-1]
            self._selected_index = 0
            self._filter()
            return None
        if len(key) == 1 and key in SEARCHABLE_KEYS:
            self._query += key
            self._selected_index = 0
            self._filter()
            return None
        return None

    def _normalise(self, text: str) -> str:
        return text.lower().replace("_", "").replace("-", "").replace(" ", "")

    def _filter(self) -> None:
        if not self._query:
            self._results = list(self._all_qtns)
            return
        nq = self._normalise(self._query)
        self._results = [
            q for q in self._all_qtns
            if nq in q.number
            or nq in self._normalise(q.site)
            or nq in q.date.replace("-", "")
        ]

    def render(self) -> Panel:
        title = Text("Search Quotations", style="bold cyan")

        search_text = Text("Search: ")
        search_text.stylize("bold")
        search_text.append(self._query)
        cursor = Text("█")
        cursor.stylize("blink")
        search_text.append(cursor)

        count_text = Text(f"{len(self._results)} results")
        count_text.stylize("dim")

        table = Table(box=None, show_header=False, padding=(0, 1))
        table.add_column("", no_wrap=True, width=2)
        table.add_column("QTN", style="cyan", no_wrap=True, width=9)
        table.add_column("Site", no_wrap=True)
        table.add_column("Date", style="yellow", no_wrap=True)

        for i, q in enumerate(self._results[:20]):
            pointer = "▸" if i == self._selected_index else " "
            pointer_text = Text(pointer)
            pointer_text.stylize("bold")

            qtn_text = Text(f"QTN-{q.number}")
            site_text = Text(q.site)
            date_text = Text(q.date)
            if i != self._selected_index:
                qtn_text.stylize("dim")
                site_text.stylize("dim")
                date_text.stylize("dim")

            table.add_row(pointer_text, qtn_text, site_text, date_text)

        if len(self._results) > 20:
            more = Text(f"... and {len(self._results) - 20} more")
            more.stylize("dim")
            table.add_row(Text(""), more, Text(""), Text(""))

        hint = Text("Type to filter | ↑↓ Navigate | Enter Select | Esc Back")
        hint.stylize("dim")

        content = Table.grid(padding=(0, 1))
        content.add_column()
        content.add_row(title)
        content.add_row(Text(""))
        content.add_row(search_text)
        content.add_row(count_text)
        content.add_row(Text(""))
        content.add_row(table)
        content.add_row(Text(""))
        content.add_row(hint)

        return Panel(content, title="Search", border_style="green")
