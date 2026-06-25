from __future__ import annotations

from typing import Any

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from rafikone.dashboard.router import Router
from rafikone.dashboard.screens import Screen
from rafikone.scanner import get_stats


class StatsScreen(Screen):
    def __init__(self, router: Router) -> None:
        super().__init__(router)
        self._stats: dict = {}

    def on_enter(self, data: dict[str, Any] | None = None) -> None:
        try:
            self._stats = get_stats()
        except Exception:
            self._stats = {}

    def handle_key(self, key: str) -> str | None:
        return None

    def render(self) -> Panel:
        title = Text("Statistics", style="bold cyan")

        s = self._stats

        total_q = s.get("total_quotations", 0)
        today_q = "—"
        this_month = "—"
        try:
            from datetime import date
            today = date.today().isoformat()
            month_prefix = today[:7]
            from rafikone.scanner import scan_quotations
            today_q = len(scan_quotations(date_filter=today))
            this_month = len(scan_quotations(date_filter=month_prefix))
        except Exception:
            pass

        info = Table.grid(padding=(0, 2))
        info.add_column(style="bold", width=22)
        info.add_column()

        info.add_row("Total Quotations", str(total_q))
        info.add_row("Today", str(today_q))
        info.add_row("This Month", str(this_month))
        info.add_row("Total Sites", str(s.get("total_sites", 0)))
        info.add_row("Total Years", str(s.get("total_years", 0)))
        info.add_row("Total Months", str(s.get("total_months", 0)))
        info.add_row("")
        info.add_row("Total PDFs", str(s.get("total_pdfs", 0)))
        info.add_row("Invoice Folders", str(s.get("total_invoices", 0)))
        info.add_row("Payment Folders", str(s.get("total_payments", 0)))
        info.add_row("Challan Folders", str(s.get("total_challans", 0)))
        info.add_row("")
        info.add_row("Latest", str(s.get("latest_quotation", "N/A")))
        info.add_row("Oldest", str(s.get("first_quotation", "N/A")))

        try:
            from rafikone.config import get_project_root
            root = get_project_root()
            import shutil
            total_size = 0
            for f in root.rglob("*"):
                if f.is_file():
                    total_size += f.stat().st_size
            if total_size < 1024**2:
                size_str = f"{total_size / 1024:.1f} KB"
            else:
                size_str = f"{total_size / 1024 ** 2:.1f} MB"
            info.add_row("Disk Usage", size_str)
        except Exception:
            pass

        hint = Text("Esc Back")
        hint.stylize("dim")

        content = Table.grid(padding=(0, 1))
        content.add_column()
        content.add_row(title)
        content.add_row(Text(""))
        content.add_row(info)
        content.add_row(Text(""))
        content.add_row(hint)

        return Panel(content, title="Statistics", border_style="yellow")
