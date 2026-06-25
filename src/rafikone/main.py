from __future__ import annotations

import csv
import json
import shutil
from datetime import date, datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from rafikone.config import (
    ConfigError,
    get_config,
    get_project_root,
    set_project_root,
)
from rafikone.creator import create_quotation
from rafikone.display import (
    print_doctor,
    print_quotation_detail,
    print_quotations_table,
    print_stats,
    print_success,
    print_tree,
)
from rafikone.interactive import confirm_create, pick_date, pick_site
from rafikone.numbering import get_latest_number, get_next_number
from rafikone.opener import open_folder
from rafikone.scanner import (
    find_quotation,
    find_quotation_by_number,
    get_stats,
    get_tree_structure,
    scan_all,
    scan_quotations,
)

app = typer.Typer(
    name="rafikone",
    help="Ubuntu CLI Quotation Manager",
    no_args_is_help=False,
    rich_markup_mode="rich",
)
console = Console()


def _handle_error(msg: str, detail: str = "", fix: str = "") -> None:
    lines = [f"[bold red]{msg}[/]"]
    if detail:
        lines.append(f"\n[dim]{detail}[/]")
    if fix:
        lines.append(f"\n[yellow]How to fix:[/] {fix}")
    console.print(Panel("\n".join(lines), title="Error", border_style="red"))
    raise typer.Exit(1)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        from rafikone.dashboard.app import DashboardApp
        try:
            DashboardApp().run()
        except (KeyboardInterrupt, SystemExit):
            pass
        except Exception as e:
            _handle_error(
                "Dashboard error",
                detail=str(e),
                fix="Check your configuration with 'rafikone config'.",
            )


@app.command()
def init() -> None:
    """Set up the project root directory.

    Prompts for the path to your project folder containing the Quotations directory.
    This path is stored permanently in ~/.config/rafikone/config.json.

    Examples:\n
        rafikone init
    """
    try:
        root = get_project_root()
        console.print(f"[yellow]Project already configured:[/] {root}")
        override = Prompt.ask("Re-configure?", default="n")
        if override.lower() not in ("y", "yes"):
            return
    except ConfigError:
        pass

    path = Prompt.ask("Enter project root path")
    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        _handle_error(
            "Path does not exist",
            detail=f"The path '{resolved}' was not found on this system.",
            fix="Check the path and try again. Use tab completion to avoid typos.",
        )

    set_project_root(str(resolved))
    console.print(f"[green]✔ Project root set to:[/] {resolved}")


@app.command()
def config() -> None:
    """Display or update configuration.

    Shows the current project root path and allows updating it.

    Examples:\n
        rafikone config
    """
    try:
        cfg = get_config()
    except ConfigError as e:
        _handle_error(
            "No configuration found",
            detail=str(e),
            fix="Run 'rafikone init' to set up your project root.",
        )

    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="bold")
    grid.add_column()
    for key, value in cfg.items():
        grid.add_row(f"• {key}", str(value))

    console.print(Panel(grid, title="Configuration"))

    update = Prompt.ask("Update project root?", default="n")
    if update.lower() in ("y", "yes"):
        new_path = Prompt.ask("New project root path")
        resolved = Path(new_path).expanduser().resolve()
        if not resolved.exists():
            _handle_error(
                "Path does not exist",
                detail=f"The path '{resolved}' was not found.",
                fix="Check the path and try again.",
            )
        set_project_root(str(resolved))
        console.print(f"[green]✔ Updated to:[/] {resolved}")


@app.command()
def new() -> None:
    """Create a new quotation.

    Interactive wizard that:\n
        1. Lets you pick an existing site or create a new one\n
        2. Asks for the quotation date\n
        3. Auto-generates the next quotation number\n
        4. Creates the full folder structure\n
        5. Creates a blank placeholder PDF\n

    Examples:\n
        rafikone new
    """
    site = pick_site()
    date_str = pick_date(date.today().isoformat())
    qtn_number = get_next_number()

    if not confirm_create(site, date_str, qtn_number):
        console.print("[yellow]Cancelled.[/]")
        raise typer.Exit(0)

    qtn = create_quotation(site, date_str, qtn_number)
    print_success(qtn)


@app.command()
def next() -> None:
    """Show latest and next quotation numbers.

    Displays the highest existing quotation number and the next one that
    will be assigned by 'rafikone new'.

    Examples:\n
        rafikone next
    """
    try:
        latest = get_latest_number()
        next_num = get_next_number()
    except ConfigError as e:
        _handle_error(
            "Cannot read quotation numbers",
            detail=str(e),
            fix="Run 'rafikone init' first to configure your project root.",
        )

    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="bold")
    grid.add_column()
    grid.add_row("Latest", f"[cyan]QTN-{latest}[/]")
    grid.add_row("Next", f"[bold green]QTN-{next_num}[/]")

    console.print(Panel(grid, title="Quotation Numbers"))


@app.command(name="list")
def list_cmd(
    site: str = typer.Option(
        None, "--site", "-s",
        help="Filter by site name (case-insensitive, ignores dashes/underscores)",
    ),
    date: str = typer.Option(
        None, "--date", "-d",
        help="Filter by year (YYYY), month (YYYY-MM), or exact date (YYYY-MM-DD)",
    ),
    detailed: bool = typer.Option(
        False, "--detailed",
        help="Show status columns (PDF, Invoices, Payments, Challans, Photos)",
    ),
    missing_pdf: bool = typer.Option(
        False, "--missing-pdf",
        help="Show only quotations missing a quotation PDF",
    ),
) -> None:
    """List all quotations.

    Shows all quotations sorted by newest first. Supports filtering by site
    and date, and a detailed view with status indicators.

    Examples:\n
        rafikone list\n
        rafikone list --site akash\n
        rafikone list --date 2026\n
        rafikone list --date 2026-06\n
        rafikone list --detailed\n
        rafikone list --missing-pdf
    """
    try:
        qtns = scan_quotations(site_filter=site, date_filter=date, missing_pdf=missing_pdf)
    except ConfigError as e:
        _handle_error(
            "Cannot list quotations",
            detail=str(e),
            fix="Run 'rafikone init' first to configure your project root.",
        )

    if not qtns:
        console.print("[yellow]No quotations found.[/]")
        return

    print_quotations_table(qtns, detailed=detailed)


@app.command()
def recent() -> None:
    """Display the 10 most recent quotations.

    Shows the latest 10 quotations sorted by date, newest first.

    Examples:\n
        rafikone recent
    """
    try:
        qtns = scan_quotations(limit=10)
    except ConfigError as e:
        _handle_error(
            "Cannot read quotations",
            detail=str(e),
            fix="Run 'rafikone init' first to configure your project root.",
        )

    if not qtns:
        console.print("[yellow]No quotations found.[/]")
        return

    print_quotations_table(qtns)


@app.command()
def today() -> None:
    """Display quotations created today.

    Filters quotations to show only those matching today's date.

    Examples:\n
        rafikone today
    """
    today_str = date.today().isoformat()
    try:
        qtns = scan_quotations(date_filter=today_str)
    except ConfigError as e:
        _handle_error(
            "Cannot read quotations",
            detail=str(e),
            fix="Run 'rafikone init' first to configure your project root.",
        )

    if not qtns:
        console.print("[yellow]No quotations found for today.[/]")
        return

    print_quotations_table(qtns)


@app.command()
def search(
    query: str = typer.Argument(
        ..., help="Quotation number, site name, or date to search for"
    ),
) -> None:
    """Search for a quotation.

    Searches by quotation number, site name, or date. Search is
    case-insensitive and ignores underscores and hyphens.

    Examples:\n
        rafikone search 0034\n
        rafikone search akash\n
        rafikone search 2026-06\n
        rafikone search "94 akash"
    """
    try:
        qtn = find_quotation(query)
    except ConfigError as e:
        _handle_error(
            "Cannot search quotations",
            detail=str(e),
            fix="Run 'rafikone init' first to configure your project root.",
        )

    if qtn is None:
        console.print(f"[yellow]No quotation found matching:[/] {query}")
        return

    print_quotation_detail(qtn)


@app.command()
def info(
    number: str = typer.Argument(
        ..., help="Quotation number (e.g. 0034 or 34)"
    ),
) -> None:
    """Show detailed information about a quotation.

    Displays folder path, size, last modified date, PDF status, subfolder
    status, and file counts for each subfolder.

    Examples:\n
        rafikone info 0034\n
        rafikone info 34
    """
    try:
        qtn = find_quotation_by_number(number)
    except ConfigError as e:
        _handle_error(
            "Cannot read quotation info",
            detail=str(e),
            fix="Run 'rafikone init' first to configure your project root.",
        )

    if qtn is None:
        console.print(f"[yellow]Quotation QTN-{number} not found.[/]")
        return

    print_quotation_detail(qtn)


@app.command()
def open(
    number: str = typer.Argument(
        ..., help="Quotation number (e.g. 0034 or 34)"
    ),
) -> None:
    """Open the quotation folder in the file manager.

    Uses xdg-open to open the quotation's folder in your default file manager.

    Examples:\n
        rafikone open 0034
    """
    try:
        qtn = find_quotation_by_number(number)
    except ConfigError as e:
        _handle_error(
            "Cannot find quotation",
            detail=str(e),
            fix="Run 'rafikone init' first to configure your project root.",
        )

    if qtn is None:
        _handle_error(
            f"Quotation QTN-{number} not found",
            detail=f"No quotation with number {number} exists in the project.",
            fix="Use 'rafikone list' to see all quotations.",
        )

    open_folder(qtn.path)


@app.command()
def invoice(
    number: str = typer.Argument(
        ..., help="Quotation number (e.g. 0034 or 34)"
    ),
) -> None:
    """Open the Invoices folder for a quotation.

    Examples:\n
        rafikone invoice 0034
    """
    _open_subfolder(number, "Invoices")


@app.command()
def payment(
    number: str = typer.Argument(
        ..., help="Quotation number (e.g. 0034 or 34)"
    ),
) -> None:
    """Open the Payments folder for a quotation.

    Examples:\n
        rafikone payment 0034
    """
    _open_subfolder(number, "Payments")


@app.command()
def challan(
    number: str = typer.Argument(
        ..., help="Quotation number (e.g. 0034 or 34)"
    ),
) -> None:
    """Open the Challans folder for a quotation.

    Examples:\n
        rafikone challan 0034
    """
    _open_subfolder(number, "Challans")


@app.command()
def photos(
    number: str = typer.Argument(
        ..., help="Quotation number (e.g. 0034 or 34)"
    ),
) -> None:
    """Open the Site_Photos folder for a quotation.

    Examples:\n
        rafikone photos 0034
    """
    _open_subfolder(number, "Site_Photos")


@app.command()
def tree() -> None:
    """Display the full quotation folder tree.

    Shows the entire directory structure under Quotations/ in a
    tree format.

    Examples:\n
        rafikone tree
    """
    try:
        structure = get_tree_structure()
    except ConfigError as e:
        _handle_error(
            "Cannot read project structure",
            detail=str(e),
            fix="Run 'rafikone init' first to configure your project root.",
        )

    if not structure:
        console.print("[yellow]No quotations found.[/]")
        return

    print_tree(structure)


@app.command()
def stats() -> None:
    """Show quotation statistics.

    Displays total counts for sites, quotations, years, months, and
    subfolder types.

    Examples:\n
        rafikone stats
    """
    try:
        s = get_stats()
    except ConfigError as e:
        _handle_error(
            "Cannot read statistics",
            detail=str(e),
            fix="Run 'rafikone init' first to configure your project root.",
        )

    print_stats(s)


@app.command()
def export(
    fmt: str = typer.Option(
        "csv", "--format", "-f",
        help="Output format: csv or json",
    ),
    output: str = typer.Option(
        None, "--output", "-o",
        help="Output file path (default: rafikone-export-<timestamp>.csv/json)",
    ),
) -> None:
    """Export all quotations to CSV or JSON.

    Exports all quotations with full details including challan file names.
    Useful for reporting and analysis.

    Examples:\n
        rafikone export\n
        rafikone export --format json\n
        rafikone export --output my_export.csv
    """
    try:
        sites = scan_all()
    except ConfigError as e:
        _handle_error(
            "Cannot export quotations",
            detail=str(e),
            fix="Run 'rafikone init' first to configure your project root.",
        )

    all_qtns = [q for s in sites for q in s.quotations]
    if not all_qtns:
        console.print("[yellow]No quotations to export.[/]")
        return

    if fmt not in ("csv", "json"):
        _handle_error("Invalid format", detail="Supported formats: csv, json")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not output:
        output = f"rafikone-export-{timestamp}.{fmt}"

    out_path = Path(output).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for q in sorted(all_qtns, key=lambda x: (x.date, x.number)):
        rows.append({
            "QTN": q.full_number,
            "Site": q.site,
            "Date": q.date,
            "Has PDF": "Yes" if q.pdf_exists else "No",
            "Has Invoices": "Yes" if q.has_invoices else "No",
            "Has Payments": "Yes" if q.has_payments else "No",
            "Has Challans": "Yes" if q.has_challans else "No",
            "Has Site Photos": "Yes" if q.has_site_photos else "No",
            "Challan Count": len(q.challan_files),
            "Challan Files": "; ".join(q.challan_files),
            "Path": str(q.path),
        })

    try:
        if fmt == "csv":
            with out_path.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
        else:
            with out_path.open("w") as f:
                json.dump(rows, f, indent=2)
    except OSError as e:
        _handle_error("Failed to write export file", detail=str(e))

    console.print(f"[green]✔ Exported {len(rows)} quotations to:[/] {out_path}")


@app.command()
def backup() -> None:
    """Backup the entire project to a zip archive.

    Creates a timestamped zip backup of the project root directory and
    saves it to ~/rafikone-backups/.

    Examples:\n
        rafikone backup
    """
    try:
        root = get_project_root()
    except ConfigError as e:
        _handle_error(
            "Cannot run backup",
            detail=str(e),
            fix="Run 'rafikone init' first to configure your project root.",
        )

    if not root.exists():
        _handle_error("Project root does not exist", detail=str(root))

    backup_dir = Path.home() / "rafikone-backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"rafikone-backup-{timestamp}"
    archive_path = backup_dir / archive_name

    try:
        with console.status("[yellow]Creating backup..."):
            shutil.make_archive(
                str(archive_path),
                "zip",
                root_dir=root.parent,
                base_dir=root.name,
            )
    except OSError as e:
        _handle_error("Backup failed", detail=str(e))

    final_path = backup_dir / f"{archive_name}.zip"
    size = final_path.stat().st_size
    size_str = f"{size / 1024 / 1024:.1f} MB" if size > 1024 * 1024 else f"{size / 1024:.1f} KB"
    console.print(f"[green]✔ Backup created:[/] {final_path} [dim]({size_str})[/]")


@app.command()
def doctor() -> None:
    """Check the quotation structure for issues.

    Scans all quotations and reports:\n
        \u2022 Missing PDF files\n
        \u2022 Missing subfolders (Invoices, Payments, Challans, Site_Photos)\n
        \u2022 Duplicate quotation numbers\n

    Examples:\n
        rafikone doctor
    """
    report: list[str] = []

    try:
        sites = scan_all()
    except ConfigError as e:
        _handle_error(
            "Cannot run doctor",
            detail=str(e),
            fix="Run 'rafikone init' first to configure your project root.",
        )

    qtn_numbers: dict[str, list[str]] = {}

    for site in sites:
        for q in site.quotations:
            padded = q.number.zfill(4)
            qtn_numbers.setdefault(padded, []).append(str(q.path))

            if not q.pdf_exists:
                report.append(f"Missing PDF: QTN-{q.number} at {q.path}")

            if not q.has_invoices:
                report.append(f"Missing Invoices: QTN-{q.number}")
            if not q.has_payments:
                report.append(f"Missing Payments: QTN-{q.number}")
            if not q.has_challans:
                report.append(f"Missing Challans: QTN-{q.number}")
            if not q.has_site_photos:
                report.append(f"Missing Site_Photos: QTN-{q.number}")

    for num, paths in qtn_numbers.items():
        if len(paths) > 1:
            report.append(f"Duplicate QTN: QTN-{num} at {', '.join(paths)}")

    print_doctor(report)


def _open_subfolder(number: str, subfolder: str) -> None:
    try:
        qtn = find_quotation_by_number(number)
    except ConfigError as e:
        _handle_error(
            "Cannot find quotation",
            detail=str(e),
            fix="Run 'rafikone init' first to configure your project root.",
        )

    if qtn is None:
        _handle_error(
            f"Quotation QTN-{number} not found",
            detail=f"No quotation with number {number} exists.",
            fix="Use 'rafikone list' to see all quotations.",
        )

    target = qtn.path / subfolder
    if not target.exists():
        _handle_error(
            f"{subfolder} folder not found",
            detail=f"QTN-{number} does not have a '{subfolder}' folder.",
            fix=f"Run 'rafikone info {number}' to see the quotation's structure.",
        )

    open_folder(target)


if __name__ == "__main__":
    app()
