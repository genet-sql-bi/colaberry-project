"""Tests for skill gap analysis logic."""

from skillgap_analyzer.analyzer import analyze_gap, extract_skills_from_text
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


# ---------------------------------------------------------------------------
# extract_skills_from_text — resume / LinkedIn extraction
# ---------------------------------------------------------------------------

SAMPLE_RESUME = (
    "Experienced software engineer with skills in Python, SQL, and Docker. "
    "Worked extensively with AWS cloud infrastructure and React frontend. "
    "Strong communication and leadership abilities."
)

SAMPLE_LINKEDIN = (
    "Senior developer proficient in Node, Docker, and AWS. "
    "Led cross-functional teams demonstrating leadership and collaboration."
)


def test_extract_skills_from_text_returns_tokens():
    tokens = extract_skills_from_text(SAMPLE_RESUME)
    assert isinstance(tokens, list)
    assert len(tokens) > 0
    # All tokens must be lowercase and alphabetic
    for token in tokens:
        assert token == token.lower()
        assert token.isalpha() or " " in token  # allow bigram phrases


def test_extract_skills_from_text_deduplicates():
    text = "python python python sql sql"
    tokens = extract_skills_from_text(text)
    assert tokens.count("python") == 1
    assert tokens.count("sql") == 1


def test_extract_skills_from_text_removes_stopwords():
    tokens = extract_skills_from_text(SAMPLE_RESUME)
    stopwords_that_must_not_appear = {
        "the", "and", "with", "for", "experience", "used", "daily",
    }
    assert stopwords_that_must_not_appear.isdisjoint(set(tokens))


def test_merged_skills_from_resume_excluded_from_gaps():
    """Skills extracted from resume text must not appear as gaps."""
    jd = (
        "Looking for a developer with Python, AWS, Docker, and SQL skills. "
        "Python and AWS are required. Docker is used daily."
    )
    resume_skills = extract_skills_from_text(SAMPLE_RESUME)
    gap_input = SkillGapInput(jd_text=jd, skills=resume_skills)
    result = analyze_gap(gap_input)

    returned_skills = {c.skill for c in result.categories}
    # python, aws, docker, sql all appear in SAMPLE_RESUME — none should be a gap
    assert "python" not in returned_skills
    assert "aws" not in returned_skills
    assert "docker" not in returned_skills
    assert "sql" not in returned_skills


def test_merged_skills_from_all_sources():
    """Manual + resume + linkedin skills all contribute to gap exclusion."""
    jd = (
        "Seeking engineer with Python, AWS, Node, React, SQL, Docker, "
        "leadership, and collaboration. Python and AWS are critical."
    )
    manual_skills = ["sql"]
    resume_skills = extract_skills_from_text(SAMPLE_RESUME)   # covers python, aws, docker, react
    linkedin_skills = extract_skills_from_text(SAMPLE_LINKEDIN)  # covers node, leadership, collaboration

    all_skills = manual_skills + resume_skills + linkedin_skills
    gap_input = SkillGapInput(jd_text=jd, skills=all_skills)
    result = analyze_gap(gap_input)

    returned_skills = {c.skill for c in result.categories}
    # All skills covered across the three sources — none should be a gap
    for covered in ["python", "aws", "docker", "react", "sql", "node",
                    "leadership", "collaboration"]:
        assert covered not in returned_skills, f"{covered} should not be a gap"
