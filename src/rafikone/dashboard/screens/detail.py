from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from rafikone.dashboard.router import Router
from rafikone.dashboard.screens import Screen
from rafikone.scanner import find_quotation_by_number

ACTIONS = [
    ("Open Folder", "open"),
    ("Open PDF", "open_pdf"),
    ("Open Invoice Folder", "open_invoice"),
    ("Open Payment Folder", "open_payment"),
    ("Open Challan Folder", "open_challan"),
    ("Copy Folder Path", "copy_path"),
    ("Back", "back"),
]


def _count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for f in path.iterdir() if f.is_file())


def _get_folder_size(path: Path) -> str:
    total = 0
    try:
        for f in path.rglob("*"):
            if f.is_file():
                total += f.stat().st_size
    except OSError:
        return "Unknown"
    if total < 1024:
        return f"{total} B"
    if total < 1024**2:
        return f"{total / 1024:.1f} KB"
    return f"{total / 1024 ** 2:.1f} MB"


def _get_last_modified(path: Path) -> str:
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return "Unknown"
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")


class DetailScreen(Screen):
    def __init__(self, router: Router) -> None:
        super().__init__(router)
        self._qtn = None
        self._actions = ACTIONS

    def on_enter(self, data: dict[str, Any] | None = None) -> None:
        self._selected_index = 0
        if data and "number" in data:
            self._qtn = find_quotation_by_number(data["number"])

    def handle_key(self, key: str) -> str | None:
        if key == "up":
            self._selected_index = (self._selected_index - 1) % len(self._actions)
            return None
        if key == "down":
            self._selected_index = (self._selected_index + 1) % len(self._actions)
            return None
        if key == "enter":
            return self._do_action()
        return None

    def _do_action(self) -> str | None:
        _label, action = self._actions[self._selected_index]
        if action == "back":
            return "back"
        if self._qtn is None:
            return None

        if action == "open":
            return f"cmd:{self._qtn.path}"

        if action == "open_pdf":
            for f in self._qtn.path.iterdir():
                if f.suffix.lower() == ".pdf" and "_Challan" not in f.name:
                    return f"cmd:{f}"
            return None

        if action == "open_invoice":
            target = self._qtn.path / "Invoices"
            if target.exists():
                return f"cmd:{target}"
            return None

        if action == "open_payment":
            target = self._qtn.path / "Payments"
            if target.exists():
                return f"cmd:{target}"
            return None

        if action == "open_challan":
            target = self._qtn.path / "Challans"
            if target.exists():
                return f"cmd:{target}"
            return None

        if action == "copy_path":
            return self._copy_path()

        return None

    def _copy_path(self) -> str | None:
        path_str = str(self._qtn.path)
        try:
            import pyperclip
            pyperclip.copy(path_str)
        except ImportError:
            try:
                import subprocess
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=path_str.encode(),
                    check=True,
                )
            except Exception:
                print(f"\n[dim]Path: {path_str}[/]")
                input("Press Enter to continue...")
        return None

    def render(self) -> Panel:
        if self._qtn is None:
            return Panel("[yellow]Quotation not found[/]", title="Error")

        q = self._qtn

        info = Table.grid(padding=(0, 1))
        info.add_column(style="bold", width=18)
        info.add_column()

        pdf_icon = "[green]✓[/]" if q.pdf_exists else "[red]✗[/]"
        inv_icon = "[green]✓[/]" if q.has_invoices else "[dim]✗[/]"
        pay_icon = "[green]✓[/]" if q.has_payments else "[dim]✗[/]"
        chl_icon = "[green]✓[/]" if q.has_challans else "[dim]✗[/]"
        pho_icon = "[green]✓[/]" if q.has_site_photos else "[dim]✗[/]"

        info.add_row("Number", f"[bold cyan]QTN-{q.number}[/]")
        info.add_row("Site", q.site)
        info.add_row("Date", f"[yellow]{q.date}[/]")
        info.add_row("Size", _get_folder_size(q.path))
        info.add_row("Modified", _get_last_modified(q.path))
        info.add_row("")
        info.add_row("PDF", pdf_icon)
        info.add_row("Invoices", f"{inv_icon}  ({_count_files(q.path / 'Invoices')} files)")
        info.add_row("Payments", f"{pay_icon}  ({_count_files(q.path / 'Payments')} files)")
        info.add_row("Challans", f"{chl_icon}  ({_count_files(q.path / 'Challans')} files)")
        info.add_row("Photos", f"{pho_icon}  ({_count_files(q.path / 'Site_Photos')} files)")
        info.add_row("")
        info.add_row("Path", f"[dim]{q.path}[/]")

        menu = Table.grid(padding=(0, 2))
        menu.add_column()
        for i, (label, _action) in enumerate(self._actions):
            prefix = "▸ " if i == self._selected_index else "  "
            style = "bold white" if i == self._selected_index else "dim"
            menu.add_row(f"{prefix}[{style}]{label}[/]")

        layout = Table.grid(padding=(0, 4))
        layout.add_column(no_wrap=True)
        layout.add_column(no_wrap=True)
        layout.add_row(info, menu)

        return Panel(layout, title=f"QTN-{q.number}", border_style="green")
