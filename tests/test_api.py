"""Integration tests for the /analyze HTTP endpoint."""

from fastapi.testclient import TestClient

from api.app import app

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
