"""Tests for the analyze_skill_gap programmatic entrypoint."""

from skillgap_analyzer.service import analyze_skill_gap


def test_analyze_skill_gap_returns_dict_with_categories():
    result = analyze_skill_gap({"jd_text": "Python SQL aws developer", "skills": []})
    assert isinstance(result, dict)
    assert "categories" in result
    assert isinstance(result["categories"], list)
    assert all({"skill", "category", "priority"} <= set(c) for c in result["categories"])


def test_analyze_skill_gap_excludes_manual_skills():
    result = analyze_skill_gap({
        "jd_text": "Python SQL aws developer",
        "skills": ["python", "sql"],
    })
    gap_skills = {c["skill"] for c in result["categories"]}
    assert "python" not in gap_skills
    assert "sql" not in gap_skills


def test_analyze_skill_gap_excludes_resume_text_skills():
    result = analyze_skill_gap({
        "jd_text": "Python SQL aws developer",
        "resume_text": "python sql",
    })
    gap_skills = {c["skill"] for c in result["categories"]}
    assert "python" not in gap_skills
    assert "sql" not in gap_skills


def test_analyze_skill_gap_excludes_linkedin_text_skills():
    result = analyze_skill_gap({
        "jd_text": "Python SQL aws developer",
        "linkedin_text": "python sql",
    })
    gap_skills = {c["skill"] for c in result["categories"]}
    assert "python" not in gap_skills
    assert "sql" not in gap_skills
