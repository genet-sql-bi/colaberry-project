"""Shared test fixtures and helpers for the skillgap-analyzer test suite."""

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Phrase baked into the fixture PDF — tests assert this appears in extracted text.
LINKEDIN_PDF_PHRASE = "Python SQL AWS Docker leadership collaboration"


def _make_minimal_pdf(text: str) -> bytes:
    """Return bytes of a minimal valid PDF-1.4 file with *text* in a content stream.

    The text is placed in a single Tj operator using a standard Type1 Helvetica
    font with WinAnsiEncoding, which pypdf can extract without any additional
    font-resource files.

    Passing an empty string produces a valid PDF whose page yields no extractable
    text — useful for testing the empty-PDF error path.
    """
    content = f"BT\n/F1 12 Tf\n50 750 Td\n({text}) Tj\nET\n".encode("latin-1")

    o1 = b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    o2 = b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    o3 = (
        b"3 0 obj\n"
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]\n"
        b"   /Contents 4 0 R\n"
        b"   /Resources << /Font << /F1 5 0 R >> >> >>\n"
        b"endobj\n"
    )
    o4 = (
        b"4 0 obj\n<< /Length " + str(len(content)).encode() + b" >>\n"
        b"stream\n" + content + b"endstream\nendobj\n"
    )
    o5 = (
        b"5 0 obj\n"
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica\n"
        b"   /Encoding /WinAnsiEncoding >>\n"
        b"endobj\n"
    )

    header = b"%PDF-1.4\n"
    objects = [o1, o2, o3, o4, o5]

    # Compute exact byte offsets for the xref table.
    offsets: list[int] = []
    pos = len(header)
    body = b""
    for obj in objects:
        offsets.append(pos)
        body += obj
        pos += len(obj)

    xref_pos = len(header) + len(body)

    # Each xref entry is exactly 20 bytes: 10-digit offset + " " + 5-digit gen
    # + " " + "n"/"f" + " " + LF.
    xref = b"xref\n0 6\n" + b"0000000000 65535 f \n"
    for off in offsets:
        xref += f"{off:010d} 00000 n \n".encode()

    trailer = (
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n"
        + str(xref_pos).encode()
        + b"\n%%EOF\n"
    )

    return header + body + xref + trailer


@pytest.fixture(scope="session", autouse=True)
def linkedin_fixture_pdf() -> Path:
    """Generate tests/fixtures/linkedin_sample.pdf once per test session.

    The file is written to a deterministic path so tests can pass the path
    string directly to _load_text().  The fixtures/ directory is gitignored.
    """
    FIXTURES_DIR.mkdir(exist_ok=True)
    pdf_path = FIXTURES_DIR / "linkedin_sample.pdf"
    pdf_path.write_bytes(_make_minimal_pdf(LINKEDIN_PDF_PHRASE))
    return pdf_path
