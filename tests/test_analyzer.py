"""Tests for skill gap analysis logic."""

import re

import pytest

from skillgap_analyzer.analyzer import (
    analyze_gap,
    extract_skills_from_text,
    extract_text_from_pdf_bytes,
)
from skillgap_analyzer.schema import SkillGapInput
from tests.conftest import _make_minimal_pdf


def test_analyze_gap_returns_result():
    gap_input = SkillGapInput(
        jd_text="We need a developer skilled in Python, SQL, and AWS.",
        skills=["python"],
    )
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


def test_extract_skills_from_text_preserves_phrase_matches_over_tokens():
    text = "Expert in machine learning and data science with python"
    tokens = extract_skills_from_text(text)
    assert "machine learning" in tokens
    assert "data science" in tokens
    assert "machine" not in tokens
    assert "learning" not in tokens
    assert "data" not in tokens
    assert "science" not in tokens
    assert "python" in tokens


def test_extract_skills_from_text_overlapping_phrase_suppression():
    text = "Experience with machine learning and deep learning models"
    tokens = extract_skills_from_text(text)
    assert "machine learning" in tokens
    assert "deep learning" in tokens
    assert "machine" not in tokens
    assert "learning" not in tokens


def test_extract_skills_from_text_is_deterministic_for_phrase_and_tokens():
    text = "Looking for machine learning, data science, and python expertise"
    result1 = extract_skills_from_text(text)
    result2 = extract_skills_from_text(text)
    assert result1 == result2
    assert "machine learning" in result1
    assert "data science" in result1
    assert "python" in result1


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


# ---------------------------------------------------------------------------
# Skill-quality tests — blocklist and allowlist behaviour
# ---------------------------------------------------------------------------

# Words from the requirements spec that must never appear as skill gaps
_GENERIC_NON_SKILLS = [
    "job", "role", "firm", "status", "global", "any", "including",
    "existing", "employees", "privacy", "issues", "changes", "workplaces",
    "where", "work", "best", "law",
]


@pytest.mark.parametrize("word", _GENERIC_NON_SKILLS)
def test_generic_word_excluded_from_analysis(word):
    """Every word in the blocklist must never appear as a skill gap."""
    jd = f"This position involves {word} and more {word}."
    result = analyze_gap(SkillGapInput(jd_text=jd, skills=[]))
    returned_skills = {c.skill for c in result.categories}
    assert word not in returned_skills, f"'{word}' leaked through as a skill gap"


def test_real_technical_skills_preserved():
    """Known canonical skills must surface as gaps when not supplied by the candidate."""
    jd = (
        "We are looking for a data analyst with Python, SQL, Excel, Tableau, "
        "and AWS experience. Strong pandas and numpy skills are required. "
        "Statistics knowledge is essential."
    )
    result = analyze_gap(SkillGapInput(jd_text=jd, skills=[]))
    returned_skills = {c.skill for c in result.categories}
    for expected in ["python", "sql", "excel", "tableau", "aws", "pandas", "numpy", "statistics"]:
        assert expected in returned_skills, f"'{expected}' should be identified as a skill gap"


def test_extraction_is_deterministic():
    """Calling extract_skills_from_text twice on the same input returns identical results."""
    text = "Python SQL AWS Docker communication leadership pandas numpy"
    assert extract_skills_from_text(text) == extract_skills_from_text(text)


# ---------------------------------------------------------------------------
# extract_text_from_pdf_bytes — PDF text extraction unit tests
# ---------------------------------------------------------------------------


def test_extract_text_from_pdf_bytes_returns_nonempty_string():
    """A valid PDF with content returns a non-empty string."""
    pdf_bytes = _make_minimal_pdf("Python SQL AWS Docker")
    text = extract_text_from_pdf_bytes(pdf_bytes)
    assert isinstance(text, str)
    assert len(text) > 0


def test_extract_text_from_pdf_bytes_contains_expected_content():
    """Extracted text contains the words baked into the PDF."""
    pdf_bytes = _make_minimal_pdf("Python SQL AWS Docker")
    text = extract_text_from_pdf_bytes(pdf_bytes)
    assert "Python" in text
    assert "SQL" in text
    assert "AWS" in text


def test_extract_text_from_pdf_bytes_normalizes_whitespace():
    """Extracted text has no consecutive whitespace runs."""
    pdf_bytes = _make_minimal_pdf("Python SQL AWS Docker")
    text = extract_text_from_pdf_bytes(pdf_bytes)
    assert re.search(r"\s{2,}", text) is None


def test_extract_text_from_pdf_bytes_raises_on_empty_pdf():
    """A valid PDF with no text content raises ValueError with a descriptive message."""
    pdf_bytes = _make_minimal_pdf("")
    with pytest.raises(ValueError, match="No text could be extracted"):
        extract_text_from_pdf_bytes(pdf_bytes)


# ---------------------------------------------------------------------------
# extract_skills_from_text — resume text skill detection
# ---------------------------------------------------------------------------

SAMPLE_RESUME_TEXT = (
    "Experienced data analyst with Python, SQL, pandas, and numpy. "
    "Built dashboards in Tableau and Excel. AWS certified with Docker experience."
)


def test_skills_detected_from_resume_text():
    """extract_skills_from_text returns all expected skills from resume text."""
    tokens = extract_skills_from_text(SAMPLE_RESUME_TEXT)
    for expected in ["python", "sql", "pandas", "numpy", "tableau", "excel", "aws", "docker"]:
        assert expected in tokens, f"'{expected}' not detected in resume text"


def test_resume_text_extraction_excludes_non_skills():
    """Generic words in resume text must not appear in extracted skill tokens."""
    tokens = extract_skills_from_text(SAMPLE_RESUME_TEXT)
    for non_skill in ["experienced", "data", "analyst", "with", "built", "certified"]:
        assert non_skill not in tokens, f"'{non_skill}' should not be extracted as a skill"


def test_resume_text_to_gap_analysis_pipeline():
    """Skills extracted from resume text feed correctly into analyze_gap to exclude gaps."""
    resume_skills = extract_skills_from_text(SAMPLE_RESUME_TEXT)
    jd = "Seeking analyst with Python, SQL, pandas, numpy, Tableau, Excel, AWS, Docker, and Spark."
    result = analyze_gap(SkillGapInput(jd_text=jd, skills=resume_skills))
    gap_skills = {c.skill for c in result.categories}
    # All resume skills should be excluded from the gap
    for covered in ["python", "sql", "pandas", "numpy", "tableau", "excel", "aws", "docker"]:
        assert covered not in gap_skills, f"'{covered}' should be covered by resume, not a gap"
    # spark was not in the resume — it should be a gap
    assert "spark" in gap_skills


# ---------------------------------------------------------------------------
# extract_skills_from_text — LinkedIn text skill detection
# ---------------------------------------------------------------------------

SAMPLE_LINKEDIN_TEXT = (
    "Senior Data Engineer | AWS | Spark | Kafka | Python | SQL. "
    "Led teams building ETL pipelines with Airflow and dbt. "
    "Strong communication and collaboration across projects."
)


def test_skills_detected_from_linkedin_text():
    """extract_skills_from_text returns all expected skills from LinkedIn-style text."""
    tokens = extract_skills_from_text(SAMPLE_LINKEDIN_TEXT)
    for expected in ["aws", "spark", "kafka", "python", "sql", "etl", "airflow", "dbt",
                     "communication", "collaboration"]:
        assert expected in tokens, f"'{expected}' not detected in LinkedIn text"


def test_linkedin_only_ingestion_extracts_phrase_and_token_skills():
    linkedin_text = "Senior data professional with machine learning, data science, and python expertise."
    tokens = extract_skills_from_text(linkedin_text)
    assert "machine learning" in tokens
    assert "data science" in tokens
    assert "python" in tokens
    assert "machine" not in tokens
    assert "learning" not in tokens


def test_linkedin_text_extraction_excludes_non_skills():
    """Generic words in LinkedIn text must not appear in extracted skill tokens."""
    tokens = extract_skills_from_text(SAMPLE_LINKEDIN_TEXT)
    for non_skill in ["senior", "data", "engineer", "led", "teams", "building", "strong", "across"]:
        assert non_skill not in tokens, f"'{non_skill}' should not be extracted as a skill"


def test_linkedin_text_to_gap_analysis_pipeline():
    """Skills extracted from LinkedIn text feed correctly into analyze_gap to exclude gaps."""
    linkedin_skills = extract_skills_from_text(SAMPLE_LINKEDIN_TEXT)
    jd = "Seeking engineer with AWS, Spark, Kafka, Python, SQL, Airflow, dbt, and Snowflake."
    result = analyze_gap(SkillGapInput(jd_text=jd, skills=linkedin_skills))
    gap_skills = {c.skill for c in result.categories}
    # All LinkedIn skills should be excluded from the gap
    for covered in ["aws", "spark", "kafka", "python", "sql", "airflow", "dbt"]:
        assert covered not in gap_skills, f"'{covered}' should be covered by LinkedIn, not a gap"
    # snowflake was not on LinkedIn profile — it should be a gap
    assert "snowflake" in gap_skills


def test_all_three_sources_merged_for_gap_analysis():
    """Manual + resume + LinkedIn skills together exclude all covered skills."""
    manual = ["sql"]
    resume_skills = extract_skills_from_text(SAMPLE_RESUME_TEXT)   # python, pandas, numpy, tableau, excel, aws, docker
    linkedin_skills = extract_skills_from_text(SAMPLE_LINKEDIN_TEXT)  # aws, spark, kafka, python, sql, etl, airflow, dbt

    all_skills = manual + resume_skills + linkedin_skills
    jd = (
        "Seeking analyst with Python, SQL, pandas, numpy, Tableau, Excel, "
        "AWS, Docker, Spark, Kafka, Airflow, dbt, and Snowflake."
    )
    result = analyze_gap(SkillGapInput(jd_text=jd, skills=all_skills))
    gap_skills = {c.skill for c in result.categories}

    for covered in ["python", "sql", "pandas", "numpy", "tableau", "excel",
                    "aws", "docker", "spark", "kafka", "airflow", "dbt"]:
        assert covered not in gap_skills, f"'{covered}' should be covered across sources"
    # snowflake not covered by any source — should still be a gap
    assert "snowflake" in gap_skills


def test_analyzer_graceful_missing_configured_skill_vocab(monkeypatch):
    """Analyzer should still work if the configured skill vocab file is missing."""
    monkeypatch.setenv("SKILL_VOCAB_PATH", "does-not-exist-skills.txt")
    import importlib
    import skillgap_analyzer.analyzer as analyzer

    analyzer = importlib.reload(analyzer)
    tokens = analyzer.extract_skills_from_text("Python SQL AWS Docker")
    assert "python" in tokens
    assert "sql" in tokens
    assert "aws" in tokens
    assert "docker" in tokens
    # confirm missing file doesn't crash and still returns recognized skills
