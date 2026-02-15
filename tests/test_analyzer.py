"""Tests for skill gap analysis logic."""

from skillgap_analyzer.analyzer import analyze_gap
from skillgap_analyzer.schema import SkillGapInput


def test_analyze_gap_returns_result():
    gap_input = SkillGapInput(jd_text="example job description", skills=["python"])
    result = analyze_gap(gap_input)
    assert result.categories is not None
    assert len(result.categories) > 0


def test_gap_analysis_filters_and_categorizes():
    jd = (
        "We need a data analyst with Python, SQL, communication, "
        "and AWS experience. Python and SQL are required. SQL is used daily."
    )
    gap_input = SkillGapInput(jd_text=jd, skills=["excel", "sql"])
    result = analyze_gap(gap_input)

    returned_skills = {c.skill for c in result.categories}
    skill_to_category = {c.skill: c.category for c in result.categories}

    # sql is a user skill — must be excluded from gaps
    assert "sql" not in returned_skills

    # python and aws are missing — must appear
    assert "python" in returned_skills
    assert "aws" in returned_skills

    # stopwords must never leak through
    assert "need" not in returned_skills
    assert "used" not in returned_skills
    assert "daily" not in returned_skills
    assert "required" not in returned_skills
    assert "experience" not in returned_skills

    # python and aws must be categorised as Technical
    assert skill_to_category["python"] == "Technical"
    assert skill_to_category["aws"] == "Technical"
