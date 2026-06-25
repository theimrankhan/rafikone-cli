from __future__ import annotations

from pathlib import Path


def create_blank_pdf(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    content = _generate_pdf_content()
    with open(path, "wb") as f:
        f.write(content)


def _generate_pdf_content() -> bytes:
    lines = [
        b"%PDF-1.4",
        b"1 0 obj",
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"endobj",
        b"2 0 obj",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"endobj",
        b"3 0 obj",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>",
        b"endobj",
        b"xref",
        b"0 4",
        b"0000000000 65535 f ",
        b"0000000009 00000 n ",
        b"0000000058 00000 n ",
        b"0000000115 00000 n ",
        b"trailer",
        b"<< /Size 4 /Root 1 0 R >>",
        b"startxref",
        b"190",
        b"%%EOF",
    ]
    return b"\r\n".join(lines)
