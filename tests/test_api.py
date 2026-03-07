"""Integration tests for the /analyze and /upload-analyze HTTP endpoints."""

from io import BytesIO

from fastapi.testclient import TestClient

from api.app import app
from tests.conftest import LINKEDIN_PDF_PHRASE, _make_minimal_pdf

client = TestClient(app)


def test_analyze_endpoint_returns_200():
    response = client.post(
        "/analyze",
        json={"jd_text": "Python SQL aws developer", "skills": []},
    )
    assert response.status_code == 200


def test_analyze_endpoint_returns_categories():
    body = client.post(
        "/analyze",
        json={"jd_text": "Python SQL aws developer", "skills": []},
    ).json()
    assert "categories" in body
    assert isinstance(body["categories"], list)
    assert all({"skill", "category", "priority"} <= set(c) for c in body["categories"])


def test_analyze_endpoint_excludes_supplied_skills():
    body = client.post(
        "/analyze",
        json={"jd_text": "Python SQL aws developer", "skills": ["python", "sql"]},
    ).json()
    gap_skills = {c["skill"] for c in body["categories"]}
    assert "python" not in gap_skills
    assert "sql" not in gap_skills


# ---------------------------------------------------------------------------
# /upload-analyze — multipart form endpoint
# ---------------------------------------------------------------------------


def test_upload_analyze_text_only_returns_200():
    response = client.post(
        "/upload-analyze",
        data={"jd_text": "Python SQL aws developer", "skills": ""},
    )
    assert response.status_code == 200


def test_upload_analyze_text_only_returns_categories():
    body = client.post(
        "/upload-analyze",
        data={"jd_text": "Python SQL aws developer", "skills": ""},
    ).json()
    assert "categories" in body
    assert isinstance(body["categories"], list)
    assert all({"skill", "category", "priority"} <= set(c) for c in body["categories"])


def test_upload_analyze_skills_field_excludes_gaps():
    body = client.post(
        "/upload-analyze",
        data={"jd_text": "Python SQL aws developer", "skills": "python, sql"},
    ).json()
    gap_skills = {c["skill"] for c in body["categories"]}
    assert "python" not in gap_skills
    assert "sql" not in gap_skills


def test_upload_analyze_with_resume_pdf_excludes_skills():
    pdf_bytes = _make_minimal_pdf("python sql")
    body = client.post(
        "/upload-analyze",
        data={"jd_text": "Python SQL aws developer", "skills": ""},
        files={"resume_file": ("resume.pdf", BytesIO(pdf_bytes), "application/pdf")},
    ).json()
    gap_skills = {c["skill"] for c in body["categories"]}
    assert "python" not in gap_skills
    assert "sql" not in gap_skills


def test_upload_analyze_with_linkedin_pdf_excludes_skills():
    pdf_bytes = _make_minimal_pdf(LINKEDIN_PDF_PHRASE)
    body = client.post(
        "/upload-analyze",
        data={"jd_text": "Python SQL aws developer leadership", "skills": ""},
        files={"linkedin_file": ("linkedin.pdf", BytesIO(pdf_bytes), "application/pdf")},
    ).json()
    gap_skills = {c["skill"] for c in body["categories"]}
    assert "python" not in gap_skills
    assert "leadership" not in gap_skills


def test_upload_analyze_without_files_ignores_missing_uploads():
    """Sending no files should still work — file fields are optional."""
    response = client.post(
        "/upload-analyze",
        data={"jd_text": "Python SQL aws developer", "skills": ""},
    )
    assert response.status_code == 200
