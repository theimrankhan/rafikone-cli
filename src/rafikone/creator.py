from __future__ import annotations

from pathlib import Path

from rafikone.config import get_project_root
from rafikone.models import Quotation
from rafikone.pdf import create_blank_pdf

SUBFOLDERS = ["Invoices", "Payments", "Challans", "Site_Photos"]


def create_quotation(site_name: str, date_str: str, qtn_number: str) -> Quotation:
    root = get_project_root()
    safe_site = site_name.strip()
    site_dir = root / "Quotations" / safe_site
    date_dir = site_dir / date_str
    qtn_dir = date_dir / f"QTN-{qtn_number}"

    site_code = safe_site.split("_")[0] if "_" in safe_site else safe_site
    pdf_name = f"{site_code}_QTN-{qtn_number}_{date_str}.pdf"
    pdf_path = qtn_dir / pdf_name

    qtn_dir.mkdir(parents=True, exist_ok=True)

    subfolders = {}
    for sf in SUBFOLDERS:
        sf_path = qtn_dir / sf
        sf_path.mkdir(exist_ok=True)
        subfolders[sf] = sf_path

    if not pdf_path.exists():
        create_blank_pdf(pdf_path)

    return Quotation(
        number=qtn_number,
        site=safe_site,
        date=date_str,
        path=qtn_dir,
        pdf_exists=pdf_path.exists(),
        has_invoices=(qtn_dir / "Invoices").exists(),
        has_payments=(qtn_dir / "Payments").exists(),
        has_challans=(qtn_dir / "Challans").exists(),
        has_site_photos=(qtn_dir / "Site_Photos").exists(),
        subfolders=subfolders,
    )
