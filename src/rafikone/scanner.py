from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from rafikone.config import get_project_root
from rafikone.models import Quotation, Site

SUBFOLDERS = {"Invoices", "Payments", "Challans", "Site_Photos"}
QTN_RE = re.compile(r"^QTN-(\d{4})$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CHALLAN_PDF_RE = re.compile(r"_Challan\.pdf$", re.IGNORECASE)


def scan_all() -> list[Site]:
    root = get_project_root()
    quotations_root = root / "Quotations"
    if not quotations_root.exists():
        return []

    sites: list[Site] = []
    for site_dir in sorted(quotations_root.iterdir()):
        if not site_dir.is_dir():
            continue
        site = Site(name=site_dir.name, path=site_dir)
        for date_dir in sorted(site_dir.iterdir()):
            if not date_dir.is_dir() or not DATE_RE.match(date_dir.name):
                continue
            for qtn_dir in sorted(date_dir.iterdir()):
                if not qtn_dir.is_dir():
                    continue
                m = QTN_RE.match(qtn_dir.name)
                if not m:
                    continue
                qtn = _scan_quotation(m.group(1), site.name, qtn_dir)
                site.quotations.append(qtn)
        if site.quotations:
            site.quotations.sort(key=lambda q: q.number, reverse=True)
        sites.append(site)

    return sites


def scan_quotations(
    site_filter: Optional[str] = None,
    date_filter: Optional[str] = None,
    limit: Optional[int] = None,
) -> list[Quotation]:
    result: list[Quotation] = []
    normalised_filter = _normalise_for_search(site_filter) if site_filter else None
    for site in scan_all():
        for q in site.quotations:
            if normalised_filter and normalised_filter not in _normalise_for_search(q.site):
                continue
            if date_filter and not q.date.startswith(date_filter):
                continue
            result.append(q)
    result.sort(key=lambda q: q.date + q.number, reverse=True)
    if limit:
        result = result[:limit]
    return result


def find_quotation(query: str) -> Optional[Quotation]:
    norm_query = _normalise_for_search(query)
    for site in scan_all():
        for q in site.quotations:
            if (
                query in q.number
                or query in q.date
                or norm_query in _normalise_for_search(q.site)
            ):
                return q
    return None


def _normalise_for_search(text: str) -> str:
    return text.lower().replace("_", "").replace("-", "").replace(" ", "")


def find_quotation_by_number(number: str) -> Optional[Quotation]:
    padded = number if len(number) == 4 else number.zfill(4)
    for site in scan_all():
        for q in site.quotations:
            if q.number == padded:
                return q
    return None


def get_stats() -> dict:
    sites = scan_all()
    all_qtns = [q for s in sites for q in s.quotations]
    years: set[str] = set()
    months: set[str] = set()
    pdf_count = 0
    invoice_count = 0
    payment_count = 0
    challan_count = 0

    for q in all_qtns:
        y, m, _ = q.date.split("-")
        years.add(y)
        months.add(f"{y}-{m}")
        if q.pdf_exists:
            pdf_count += 1
        if q.has_invoices:
            invoice_count += 1
        if q.has_payments:
            payment_count += 1
        if q.has_challans:
            challan_count += 1

    sorted_qtns = sorted(all_qtns, key=lambda q: int(q.number))

    return {
        "total_sites": len([s for s in sites if s.quotations]),
        "total_quotations": len(all_qtns),
        "total_years": len(years),
        "total_months": len(months),
        "latest_quotation": sorted_qtns[-1].full_number if sorted_qtns else "N/A",
        "first_quotation": sorted_qtns[0].full_number if sorted_qtns else "N/A",
        "total_pdfs": pdf_count,
        "total_invoices": invoice_count,
        "total_payments": payment_count,
        "total_challans": challan_count,
    }


def get_tree_structure() -> list:
    root = get_project_root()
    quotations_root = root / "Quotations"
    if not quotations_root.exists():
        return []
    return _build_tree_list(quotations_root)


def _scan_quotation(number: str, site_name: str, qtn_dir: Path) -> Quotation:
    date_part = qtn_dir.parent.name

    pdf_exists = False
    for f in qtn_dir.iterdir():
        if f.suffix.lower() == ".pdf" and not CHALLAN_PDF_RE.search(f.name):
            pdf_exists = True
            break

    subfolders: dict[str, Path] = {}
    for sf in SUBFOLDERS:
        sf_path = qtn_dir / sf
        if sf_path.exists():
            subfolders[sf] = sf_path

    return Quotation(
        number=number,
        site=site_name,
        date=date_part,
        path=qtn_dir,
        pdf_exists=pdf_exists,
        has_invoices=(qtn_dir / "Invoices").exists(),
        has_payments=(qtn_dir / "Payments").exists(),
        has_challans=(qtn_dir / "Challans").exists(),
        has_site_photos=(qtn_dir / "Site_Photos").exists(),
        subfolders=subfolders,
    )


def _build_tree_list(path: Path) -> list:
    items: list = []
    entries = sorted(path.iterdir())
    dirs = [e for e in entries if e.is_dir()]
    for d in dirs:
        children = _build_tree_list(d)
        items.append((d.name, True, children))
    files = [e for e in entries if e.is_file()]
    for f in files:
        items.append((f.name, False, None))
    return items
