from __future__ import annotations

from rafikone.models import Quotation, Site


def print_quotations_table(
    quotations: list[Quotation], detailed: bool = False
) -> None:
    from rich.console import Console
    from rich.table import Table
    from rich.text import Text

    console = Console()

    if detailed:
        table = Table(show_edge=False, leading=0, padding=(0, 1))
        table.add_column("QTN", style="cyan", no_wrap=True)
        table.add_column("Site")
        table.add_column("Date", style="yellow")
        table.add_column("PDF", no_wrap=True, justify="center")
        table.add_column("Inv", no_wrap=True, justify="center")
        table.add_column("Pay", no_wrap=True, justify="center")
        table.add_column("Chl", no_wrap=True, justify="center")
        table.add_column("Phs", no_wrap=True, justify="center")

        for q in quotations:
            table.add_row(
                f"QTN-{q.number}",
                q.site,
                q.date,
                _icon(q.pdf_exists),
                _icon(q.has_invoices),
                _icon(q.has_payments),
                _icon(q.has_challans),
                _icon(q.has_site_photos),
            )
    else:
        table = Table(show_edge=False, leading=1)
        table.add_column("QTN", style="cyan", no_wrap=True)
        table.add_column("Site")
        table.add_column("Date", style="yellow")
        table.add_column("Path", style="dim", overflow="fold")

        for q in quotations:
            table.add_row(f"QTN-{q.number}", q.site, q.date, str(q.path))

    console.print(table)


def print_quotation_detail(qtn: Quotation) -> None:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()

    info = Table.grid(padding=(0, 1))
    info.add_column()
    info.add_column()

    info.add_row("Quotation Number", f"[bold cyan]QTN-{qtn.number}[/]")
    info.add_row("Site", qtn.site)
    info.add_row("Date", f"[yellow]{qtn.date}[/]")
    info.add_row("Full Path", f"[dim]{qtn.path}[/]")

    folder_size = _get_folder_size(qtn.path)
    last_mod = _get_last_modified(qtn.path)
    info.add_row("Folder Size", folder_size)
    info.add_row("Last Modified", last_mod)
    info.add_row("")

    _add_check(info, "PDF", qtn.pdf_exists)
    _add_check(info, "Invoices", qtn.has_invoices)
    _add_check(info, "Payments", qtn.has_payments)
    _add_check(info, "Challans", qtn.has_challans)
    _add_check(info, "Site_Photos", qtn.has_site_photos)

    invoice_count = _count_files(qtn.path / "Invoices")
    payment_count = _count_files(qtn.path / "Payments")
    challan_count = _count_files(qtn.path / "Challans")
    photo_count = _count_files(qtn.path / "Site_Photos")
    info.add_row("")
    info.add_row("Invoice Files", str(invoice_count))
    info.add_row("Payment Files", str(payment_count))
    info.add_row("Challan Files", str(challan_count))
    info.add_row("Photo Files", str(photo_count))

    panel = Panel(info, title=f"QTN-{qtn.number}")
    console.print(panel)


def print_stats(stats: dict) -> None:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()

    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="bold")
    grid.add_column()

    labels = {
        "total_sites": "Total Sites",
        "total_quotations": "Total Quotations",
        "total_years": "Total Years",
        "total_months": "Total Months",
        "latest_quotation": "Latest Quotation",
        "first_quotation": "First Quotation",
        "total_pdfs": "Total PDFs",
        "total_invoices": "Invoice Folders",
        "total_payments": "Payment Folders",
        "total_challans": "Challan Folders",
    }

    for key, label in labels.items():
        value = stats.get(key, "N/A")
        grid.add_row(f"• {label}", str(value))

    console.print(Panel(grid, title="Statistics"))


def print_tree(tree: list) -> None:
    from rich.console import Console
    from rich.tree import Tree

    console = Console()
    root = Tree("[bold]Quotations[/]")

    def add_children(items: list, parent: Tree) -> None:
        for name, is_dir, children in items:
            if is_dir:
                branch = parent.add(f"[bold]{name}/[/]")
                if children:
                    add_children(children, branch)
            else:
                parent.add(name)

    if tree:
        add_children(tree, root)
    console.print(root)


def print_doctor(report: list[str]) -> None:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()
    if not report:
        console.print(Panel("[green]✓ No issues found[/]", title="Doctor Report"))
        return

    table = Table(title="Issues Found", box=None)
    table.add_column("Type", style="red", width=12)
    table.add_column("Description", overflow="fold")

    for entry in report:
        parts = entry.split(":", 1)
        if len(parts) == 2:
            table.add_row(parts[0].strip(), parts[1].strip())
        else:
            table.add_row("", entry)

    console.print(table)


def print_success(qtn: Quotation) -> None:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()

    info = Table.grid(padding=(0, 1))
    info.add_column()
    info.add_column()

    info.add_row("Quotation Number", f"[bold cyan]QTN-{qtn.number}[/]")
    info.add_row("Site", qtn.site)
    info.add_row("Date", f"[yellow]{qtn.date}[/]")
    info.add_row("Folder", f"[dim]{qtn.path}[/]")
    info.add_row("")

    info.add_row("  [green]✓[/] PDF", "")
    info.add_row("  [green]✓[/] Invoices", "")
    info.add_row("  [green]✓[/] Payments", "")
    info.add_row("  [green]✓[/] Challans", "")
    info.add_row("  [green]✓[/] Site_Photos", "")

    panel = Panel(info, title="[green]✔ Quotation Created Successfully[/]")
    console.print(panel)

    cmds = Table.grid(padding=(0, 2))
    cmds.add_column(style="bold dim", width=26)
    cmds.add_column()
    cmds.add_row("Next commands:", "")
    cmds.add_row(f"  rafikone open {qtn.number}", "   Open quotation folder")
    cmds.add_row(f"  rafikone info {qtn.number}", "  View quotation details")
    console.print(Panel(cmds, title="Next Steps"))


def _add_check(table, label: str, exists: bool) -> None:
    from rich.text import Text

    icon = Text("✓", style="green") if exists else Text("✗", style="red dim")
    table.add_row(f"  {icon}", label)


def _icon(exists: bool) -> str:
    return "[green]✓[/]" if exists else "[dim]✗[/]"


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
    if total < 1024 ** 2:
        return f"{total / 1024:.1f} KB"
    return f"{total / 1024 ** 2:.1f} MB"


def _get_last_modified(path: Path) -> str:
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return "Unknown"
    from datetime import datetime
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")


def _count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for f in path.iterdir() if f.is_file())
