"""Tests for CLI helper _load_text() — raw text, .txt, and .pdf loading."""

from pathlib import Path

import pytest

from skillgap_analyzer.cli import _load_text
from tests.conftest import FIXTURES_DIR, LINKEDIN_PDF_PHRASE, _make_minimal_pdf


# ---------------------------------------------------------------------------
# Raw string passthrough
# ---------------------------------------------------------------------------


def test_load_text_raw_string_is_returned_unchanged():
    """Non-path strings (raw text) are returned as-is."""
    raw = "Python SQL AWS Docker"
    assert _load_text(raw) == raw


def test_load_text_raw_string_with_spaces_is_returned_unchanged():
    """Multi-word raw text that happens to look like prose is not misinterpreted."""
    raw = "Senior developer proficient in Node and Docker"
    assert _load_text(raw) == raw


# ---------------------------------------------------------------------------
# .txt file loading
# ---------------------------------------------------------------------------


def test_load_text_reads_txt_file(tmp_path):
    """Content is read verbatim from a .txt file path."""
    txt = tmp_path / "resume.txt"
    txt.write_text("Python SQL AWS Docker", encoding="utf-8")
    assert _load_text(str(txt)) == "Python SQL AWS Docker"


def test_load_text_txt_preserves_whitespace(tmp_path):
    """Whitespace in .txt files is preserved (no normalization at this layer)."""
    txt = tmp_path / "profile.txt"
    content = "Python\nSQL\nAWS Docker"
    txt.write_text(content, encoding="utf-8")
    assert _load_text(str(txt)) == content


# ---------------------------------------------------------------------------
# .pdf file loading (the new path)
# ---------------------------------------------------------------------------


def test_load_text_pdf_returns_nonempty_string(linkedin_fixture_pdf):
    """_load_text() on the fixture PDF returns a non-empty string."""
    result = _load_text(str(linkedin_fixture_pdf))
    assert isinstance(result, str)
    assert len(result) > 0


def test_load_text_pdf_contains_known_phrase(linkedin_fixture_pdf):
    """Extracted PDF text contains the known phrase baked into the fixture."""
    result = _load_text(str(linkedin_fixture_pdf))
    assert "Python" in result


def test_load_text_pdf_whitespace_is_normalized(linkedin_fixture_pdf):
    """Extracted PDF text has no consecutive whitespace runs."""
    import re
    result = _load_text(str(linkedin_fixture_pdf))
    assert re.search(r"\s{2,}", result) is None


def test_load_text_pdf_skills_feed_into_gap_analysis(linkedin_fixture_pdf):
    """Text extracted from a PDF is compatible with extract_skills_from_text()."""
    from skillgap_analyzer.analyzer import extract_skills_from_text

    result = _load_text(str(linkedin_fixture_pdf))
    tokens = extract_skills_from_text(result)
    assert isinstance(tokens, list)
    assert "python" in tokens   # lowercased by extract_skills_from_text


# ---------------------------------------------------------------------------
# Error paths
# ---------------------------------------------------------------------------


def test_load_text_unsupported_extension_raises(tmp_path):
    """Files with unsupported extensions raise ValueError with a clear message."""
    bad = tmp_path / "profile.docx"
    bad.write_bytes(b"dummy content")
    with pytest.raises(ValueError, match="Unsupported file type"):
        _load_text(str(bad))


def test_load_text_empty_pdf_raises_descriptive_error(tmp_path):
    """PDFs with no extractable text raise ValueError describing the problem."""
    blank_pdf = tmp_path / "blank.pdf"
    blank_pdf.write_bytes(_make_minimal_pdf(""))  # valid PDF, empty Tj operator
    with pytest.raises(ValueError, match="No text could be extracted"):
        _load_text(str(blank_pdf))
