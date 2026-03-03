"""Programmatic orchestration entrypoint for the skill-gap pipeline."""

from skillgap_analyzer.analyzer import analyze_gap, extract_skills_from_text
from skillgap_analyzer.schema import SkillGapInput


def analyze_skill_gap(input_data: dict) -> dict:
    """Programmatic entrypoint for the skill-gap pipeline.

    Accepts pre-loaded text (no file I/O, no CLI args) and returns the
    SkillGapResult serialised as a plain dict.

    Expected keys:
        jd_text       (str, required)  – job description text already loaded
        skills        (list[str], opt) – manually supplied candidate skills
        resume_text   (str, opt)       – resume text already loaded
        linkedin_text (str, opt)       – LinkedIn profile text already loaded
    """
    all_skills: list[str] = list(input_data.get("skills", []))

    resume_text = input_data.get("resume_text", "")
    if resume_text:
        all_skills.extend(extract_skills_from_text(resume_text))

    linkedin_text = input_data.get("linkedin_text", "")
    if linkedin_text:
        all_skills.extend(extract_skills_from_text(linkedin_text))

    result = analyze_gap(SkillGapInput(jd_text=input_data["jd_text"], skills=all_skills))
    return {
        "categories": [
            {"skill": c.skill, "category": c.category, "priority": c.priority}
            for c in result.categories
        ]
    }
