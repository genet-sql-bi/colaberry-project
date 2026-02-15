"""Pure skill-gap analysis logic — no I/O, no orchestration."""

import re
from collections import Counter

from skillgap_analyzer.schema import SkillCategory, SkillGapInput, SkillGapResult

STOPWORDS = frozenset({
    "the", "and", "with", "for", "that", "this", "from", "are", "will",
    "you", "our", "your", "have", "has", "been", "being", "was", "were",
    "not", "but", "they", "their", "can", "able", "about", "into",
    "all", "also", "than", "more", "other", "some", "such", "must",
    "should", "would", "could", "may", "who", "which", "how", "what",
    "need", "needs", "required", "experience", "data", "analyst", "used", "daily",
    "looking", "seeking",
})

TECHNICAL_SKILLS = frozenset({"python", "sql", "aws", "docker", "react", "node"})
SOFT_SKILLS = frozenset({"communication", "leadership", "collaboration"})

SKILL_PHRASES = frozenset({
    "machine learning", "data analysis", "project management", "deep learning"
})

MAX_JD_SKILLS = 20


def _normalize_user_skills(raw_skills: list[str]) -> set[str]:
    """Normalize user skills: split on commas, strip whitespace, lowercase."""
    normalized: set[str] = set()
    for entry in raw_skills:
        for skill in entry.split(","):
            cleaned = skill.strip().lower()
            if cleaned:
                normalized.add(cleaned)
    return normalized


def _extract_jd_tokens(jd_text: str) -> Counter:
    """Tokenize JD text with regex, detect allowlisted phrases, count frequencies."""
    counts: Counter = Counter()
    tokens = [
        t for t in re.findall(r"[a-zA-Z]+", jd_text.lower())
        if len(t) >= 3 and t not in STOPWORDS
    ]
    # Count unigrams
    for token in tokens:
        counts[token] += 1
    # Count allowlisted bigrams
    for i in range(len(tokens) - 1):
        phrase = tokens[i] + " " + tokens[i + 1]
        if phrase in SKILL_PHRASES:
            counts[phrase] += 1
    return counts


def _categorize(skill: str) -> str:
    if skill in TECHNICAL_SKILLS:
        return "Technical"
    if skill in SOFT_SKILLS:
        return "Soft Skill"
    return "Tool/Other"


def _prioritize(frequency: int) -> str:
    if frequency >= 3:
        return "High"
    if frequency == 2:
        return "Medium"
    return "Low"


def analyze_gap(gap_input: SkillGapInput) -> SkillGapResult:
    """Identify skills present in a JD but missing from the candidate's list.

    Pure function: no side-effects, no I/O.
    """
    user_skills = _normalize_user_skills(gap_input.skills)
    token_counts = _extract_jd_tokens(gap_input.jd_text)

    # Build categories with priority derived from full frequency counts
    # BEFORE trimming to top-20, so priority reflects true JD frequency.
    seen: set[str] = set()
    categories: list[SkillCategory] = []

    for skill, freq in token_counts.most_common():
        if skill in user_skills:
            continue
        if skill in seen:
            continue
        seen.add(skill)
        categories.append(
            SkillCategory(
                skill=skill,
                category=_categorize(skill),
                priority=_prioritize(freq),
            )
        )
        if len(categories) >= MAX_JD_SKILLS:
            break

    return SkillGapResult(categories=categories)
