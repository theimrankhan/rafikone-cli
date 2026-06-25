from __future__ import annotations

import subprocess
from pathlib import Path

from rich.console import Console

console = Console()


def open_folder(path: Path) -> None:
    if not path.exists():
        console.print(f"[red]✗ Path does not exist:[/] {path}")
        raise SystemExit(1)
    if not path.is_dir():
        console.print(f"[red]✗ Not a directory:[/] {path}")
        raise SystemExit(1)

    try:
        subprocess.run(["xdg-open", str(path)], check=True)
    except FileNotFoundError:
        console.print(
            "[red]✗ xdg-open not found. Install it or open the folder manually.[/]"
        )
        raise SystemExit(1)
    except subprocess.CalledProcessError:
        console.print("[red]✗ Failed to open folder.[/]")
        raise SystemExit(1)
