from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from rafikone.config import get_project_root


def pick_site() -> str:
    root = get_project_root()
    quotations_root = root / "Quotations"
    existing_sites = _get_existing_sites(quotations_root)

    console = Console()
    title = "Select or create a site"

    if existing_sites:
        choices = existing_sites + [questionary.Separator(), "─── Create new site ───"]
        selected = questionary.select(
            title,
            choices=choices,
            use_shortcuts=True,
            qmark="",
            pointer="▸",
        ).ask()
    else:
        selected = None

    if selected is None:
        console.print("[yellow]Selection cancelled.[/]")
        raise SystemExit(0)

    if selected == "─── Create new site ───":
        name = questionary.text("Enter new site name:").ask()
        if not name or not name.strip():
            console.print("[red]Site name cannot be empty.[/]")
            raise SystemExit(1)
        return _normalise_name(name.strip())

    return selected


def pick_date(default_date: str | None = None) -> str:
    if default_date is None:
        default_date = date.today().isoformat()

    result = questionary.text(
        "Quotation date",
        default=default_date,
    ).ask()

    if result is None:
        console = Console()
        console.print("[yellow]Cancelled.[/]")
        raise SystemExit(0)

    result = result.strip()

    if re.match(r"^\d{4}-\d{2}-\d{2}$", result):
        return result

    console = Console()
    console.print("[red]Invalid date format. Use YYYY-MM-DD.[/]")
    return pick_date(default_date)


def confirm_create(site: str, date_str: str, qtn_number: str) -> bool:
    console = Console()
    panel = Panel(
        f"[bold]Site:[/] {site}\n"
        f"[bold]Date:[/] {date_str}\n"
        f"[bold]Quotation:[/] QTN-{qtn_number}\n"
        f"[bold]Folder:[/] Quotations/{site}/{date_str}/QTN-{qtn_number}",
        title="Create Quotation",
    )
    console.print(panel)
    result = questionary.confirm("Create this quotation?", default=True).ask()
    if result is None:
        return False
    return result


def _get_existing_sites(quotations_root: Path) -> list[str]:
    if not quotations_root.exists():
        return []
    return sorted(d.name for d in quotations_root.iterdir() if d.is_dir())


def _normalise_name(name: str) -> str:
    return name.strip().replace(" ", "_")
