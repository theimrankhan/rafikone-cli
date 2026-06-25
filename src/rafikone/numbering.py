from __future__ import annotations

import re
from pathlib import Path

from rafikone.config import get_project_root

QTN_RE = re.compile(r"^QTN-(\d{4})$")


def get_latest_number() -> str:
    root = get_project_root()
    quotations_root = root / "Quotations"
    if not quotations_root.exists():
        return "0000"

    max_num = 0
    for site_dir in quotations_root.iterdir():
        if not site_dir.is_dir():
            continue
        for date_dir in site_dir.iterdir():
            if not date_dir.is_dir():
                continue
            for qtn_dir in date_dir.iterdir():
                if not qtn_dir.is_dir():
                    continue
                m = QTN_RE.match(qtn_dir.name)
                if m:
                    num = int(m.group(1))
                    if num > max_num:
                        max_num = num
    return f"{max_num:04d}"


def get_next_number() -> str:
    latest = get_latest_number()
    return f"{int(latest) + 1:04d}"
