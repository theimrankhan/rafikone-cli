from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Quotation:
    number: str
    site: str
    date: str
    path: Path
    pdf_exists: bool = False
    has_invoices: bool = False
    has_payments: bool = False
    has_challans: bool = False
    has_site_photos: bool = False
    subfolders: dict[str, Path] = field(default_factory=dict)

    @property
    def full_number(self) -> str:
        return f"QTN-{self.number}"


@dataclass
class Site:
    name: str
    path: Path
    quotations: list[Quotation] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.quotations)
