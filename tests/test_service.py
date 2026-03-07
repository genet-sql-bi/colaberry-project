"""Tests for the analyze_skill_gap programmatic entrypoint."""

from skillgap_analyzer.analyzer import extract_text_from_pdf_bytes
from skillgap_analyzer.service import analyze_skill_gap
from tests.conftest import _make_minimal_pdf


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


# ---------------------------------------------------------------------------
# Resume PDF extraction → skill merge pipeline
# ---------------------------------------------------------------------------


def test_resume_pdf_skills_extracted_and_excluded():
    """Skills in an uploaded resume PDF must not appear as gaps after extraction."""
    pdf_bytes = _make_minimal_pdf("Python SQL Docker pandas")
    resume_text = extract_text_from_pdf_bytes(pdf_bytes)
    result = analyze_skill_gap({
        "jd_text": "Python SQL Docker pandas AWS developer",
        "resume_text": resume_text,
    })
    gap_skills = {c["skill"] for c in result["categories"]}
    # Skills present in the PDF are covered — should not be gaps
    assert "python" not in gap_skills
    assert "sql" not in gap_skills
    assert "docker" not in gap_skills
    assert "pandas" not in gap_skills
    # Skill absent from the PDF should still surface as a gap
    assert "aws" in gap_skills


def test_manual_and_resume_skills_merged_no_duplicates():
    """Providing the same skill manually and in resume text causes no errors or duplicates."""
    result = analyze_skill_gap({
        "jd_text": "Python SQL AWS Docker developer",
        "skills": ["python"],        # also present in resume_text below
        "resume_text": "python sql developer",
    })
    gap_skills = [c["skill"] for c in result["categories"]]
    # python is covered by both sources — must not appear as a gap at all
    assert "python" not in gap_skills
    # python must not appear twice (deduplication check)
    assert gap_skills.count("python") == 0
    # aws and docker are not covered — should be gaps
    assert "aws" in gap_skills
    assert "docker" in gap_skills


def test_manual_and_resume_skills_combined_exclusion():
    """Manual skills + resume skills together cover disjoint sets of JD requirements."""
    result = analyze_skill_gap({
        "jd_text": "Python SQL AWS Docker pandas developer",
        "skills": ["aws"],            # manual
        "resume_text": "python sql developer",  # resume covers python, sql
    })
    gap_skills = {c["skill"] for c in result["categories"]}
    # aws from manual, python+sql from resume — all three excluded
    assert "aws" not in gap_skills
    assert "python" not in gap_skills
    assert "sql" not in gap_skills
    # docker and pandas not covered by either source — should be gaps
    assert "docker" in gap_skills
    assert "pandas" in gap_skills


# ---------------------------------------------------------------------------
# LinkedIn PDF extraction → skill merge pipeline
# ---------------------------------------------------------------------------


def test_linkedin_pdf_skills_extracted_and_excluded():
    """Skills in an uploaded LinkedIn PDF must not appear as gaps after extraction."""
    pdf_bytes = _make_minimal_pdf("Spark Kafka Airflow dbt")
    linkedin_text = extract_text_from_pdf_bytes(pdf_bytes)
    result = analyze_skill_gap({
        "jd_text": "Spark Kafka Airflow dbt AWS data engineer",
        "linkedin_text": linkedin_text,
    })
    gap_skills = {c["skill"] for c in result["categories"]}
    # Skills present in the LinkedIn PDF are covered — should not be gaps
    assert "spark" not in gap_skills
    assert "kafka" not in gap_skills
    assert "airflow" not in gap_skills
    assert "dbt" not in gap_skills
    # Skill absent from the PDF should still surface as a gap
    assert "aws" in gap_skills


def test_linkedin_pdf_merged_with_manual_no_duplicates():
    """Same skill in both manual list and LinkedIn PDF causes no errors or duplicates."""
    pdf_bytes = _make_minimal_pdf("Spark Kafka aws")
    linkedin_text = extract_text_from_pdf_bytes(pdf_bytes)
    result = analyze_skill_gap({
        "jd_text": "Spark Kafka AWS Docker data engineer",
        "skills": ["aws"],           # also present in the LinkedIn PDF
        "linkedin_text": linkedin_text,
    })
    gap_skills = [c["skill"] for c in result["categories"]]
    # aws covered by both — must not appear as a gap, and must not appear twice
    assert gap_skills.count("aws") == 0
    # docker not covered — should be a gap
    assert "docker" in gap_skills


def test_all_three_sources_merged_at_service_level():
    """Manual + resume_text + linkedin_text together exclude all covered skills."""
    result = analyze_skill_gap({
        "jd_text": "Python SQL AWS Docker Spark Kafka pandas developer",
        "skills": ["sql"],
        "resume_text": "python aws docker pandas analyst",
        "linkedin_text": "Spark Kafka engineer",
    })
    gap_skills = {c["skill"] for c in result["categories"]}
    # Every source contributes: sql (manual), python/aws/docker/pandas (resume), spark/kafka (linkedin)
    for covered in ["sql", "python", "aws", "docker", "pandas", "spark", "kafka"]:
        assert covered not in gap_skills, f"'{covered}' should be covered across all three sources"
