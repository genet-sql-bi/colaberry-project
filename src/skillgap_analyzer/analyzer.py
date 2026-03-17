"""Pure skill-gap analysis logic — no I/O, no orchestration."""

import io
import re
from collections import Counter

from config import get_skill_vocabulary_path
from skillgap_analyzer.schema import SkillCategory, SkillGapInput, SkillGapResult
from skill_loader import load_skill_vocabulary

# ---------------------------------------------------------------------------
# Blocklist — words that must never appear as skills
# Covers generic English, HR/job-posting jargon, and job-title words.
# ---------------------------------------------------------------------------
BLOCKLIST = frozenset({
    # Articles, conjunctions, prepositions
    "the", "and", "with", "for", "that", "this", "from", "are", "will",
    "you", "our", "your", "have", "has", "been", "being", "was", "were",
    "not", "but", "they", "their", "can", "able", "about", "into",
    "all", "also", "than", "more", "other", "some", "such", "must",
    "should", "would", "could", "may", "who", "which", "how", "what",
    # HR / job-posting jargon
    "need", "needs", "required", "experience", "used", "daily",
    "looking", "seeking", "job", "role", "firm", "status", "global",
    "any", "including", "existing", "employees", "privacy", "issues",
    "changes", "workplaces", "where", "work", "best", "law",
    "team", "teams", "business", "company", "position", "candidate",
    "candidates", "applicant", "applicants", "joining", "strong",
    "good", "great", "excellent", "proficient", "ability", "abilities",
    "skills", "knowledge", "understanding", "support", "provide", "review",
    "perform", "manage", "create", "build", "develop", "implement",
    "ensure", "maintain", "track", "drive", "define", "help", "assist",
    "using", "working", "various", "relevant", "current", "new", "key",
    "core", "per", "well", "level", "highly", "next", "time", "type",
    "way", "part", "both", "each", "every", "few", "most", "just",
    "very", "often", "across", "between", "through", "within", "along",
    "around", "against", "based", "given", "related", "wide", "full",
    "high", "low", "large", "small", "open", "real", "live", "run",
    "point", "area", "areas", "end", "start", "make", "take", "give",
    "show", "know", "see", "think", "come", "get", "put", "let", "ask",
    "join", "use", "plus", "own", "set", "list", "long", "short", "fast",
    "day", "days", "year", "years", "month", "months", "number", "numbers",
    # Generic domain words — not skills on their own
    "data", "analyst", "engineer", "developer", "manager", "senior",
    "junior", "lead", "head", "staff", "requires", "requires", "involves",
    "awareness", "preferred", "ideal",
})

# ---------------------------------------------------------------------------
# Canonical skill vocabulary — the allowlist
# Only tokens in SKILL_VOCAB (or SKILL_PHRASES) can appear in results.
# ---------------------------------------------------------------------------

_TECHNICAL_SKILLS = frozenset({
    # Programming languages
    "python", "sql", "r", "java", "scala", "javascript", "typescript",
    "golang", "bash", "powershell", "matlab", "ruby",
    # Data / ML libraries
    "pandas", "numpy", "matplotlib", "seaborn", "scipy", "sklearn",
    "tensorflow", "pytorch", "keras", "xgboost", "lightgbm", "plotly",
    # Data platforms and warehouses
    "snowflake", "databricks", "bigquery", "redshift", "athena",
    "spark", "hadoop", "kafka", "airflow", "dbt", "flink",
    # Databases
    "postgresql", "mysql", "sqlite", "mongodb", "redis", "cassandra",
    "elasticsearch", "oracle",
    # BI and visualization tools
    "tableau", "excel", "looker", "grafana", "metabase", "powerbi",
    # Cloud and DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
    "git", "github", "gitlab", "jenkins",
    # Web and backend frameworks
    "react", "node", "nodejs", "flask", "fastapi", "django",
    # General technical concepts
    "statistics", "regression", "clustering", "classification", "forecasting",
    "optimization", "modeling", "analytics", "etl", "database",
    "visualization", "reporting", "dashboards", "pipeline",
    "devops", "agile", "scrum",
})

_SOFT_SKILLS = frozenset({
    "communication", "leadership", "collaboration", "teamwork",
    "mentoring", "presentation", "documentation",
})

# Load external dynamic skill vocabulary if available.
def _load_dynamic_skill_sets(path: str | None = None) -> tuple[set[str], set[str]]:
    if path is None:
        path = get_skill_vocabulary_path()
    loaded: set[str] = set()
    try:
        loaded = load_skill_vocabulary(path)
    except (FileNotFoundError, OSError):
        loaded = set()

    token_skills: set[str] = set()
    phrase_skills: set[str] = set()
    for entry in loaded:
        if " " in entry:
            phrase_skills.add(entry)
        else:
            token_skills.add(entry)
    return token_skills, phrase_skills

_EXTERNAL_SKILL_TOKENS, _EXTERNAL_SKILL_PHRASES = _load_dynamic_skill_sets()

# All recognized single-token skills
SKILL_VOCAB = _TECHNICAL_SKILLS | _SOFT_SKILLS | _EXTERNAL_SKILL_TOKENS

# ---------------------------------------------------------------------------
# Multi-word skill phrases
# Detected on raw (unfiltered) tokens so that short words like "bi" are found.
# ---------------------------------------------------------------------------

_TECHNICAL_PHRASES = frozenset({
    "machine learning", "deep learning", "data analysis", "data science",
    "data engineering", "data visualization", "data modeling",
    "natural language processing", "computer vision",
    "business intelligence", "statistical analysis",
    "time series", "feature engineering",
})

_SOFT_PHRASES = frozenset({
    "project management", "product management",
})

_TOOL_PHRASES = frozenset({
    "power bi",
})

SKILL_PHRASES = (
    _TECHNICAL_PHRASES | _SOFT_PHRASES | _TOOL_PHRASES | _EXTERNAL_SKILL_PHRASES
)

MAX_JD_SKILLS = 20


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

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
    """Tokenize text, detect allowlisted phrases, apply vocabulary filter.

    Phrase-first approach:
      1) Detect multi-word phrases from SKILL_PHRASES, favoring longer phrase matches first.
      2) Mark consumed raw token spans so overlapping single-token matches from the same span are suppressed.
      3) Count single-token skills from SKILL_VOCAB on unused raw tokens.

    Pure function: no side-effects, no I/O.
    """
    counts: Counter = Counter()
    raw = re.findall(r"[a-zA-Z]+", jd_text.lower())

    # Build fast phrase lookup from token tuple to canonical phrase text.
    phrase_lookup = {tuple(phrase.split()): phrase for phrase in SKILL_PHRASES}
    phrase_lengths = sorted({len(tokens) for tokens in phrase_lookup}, reverse=True)

    used_tokens: set[int] = set()
    for i in range(len(raw)):
        if i in used_tokens:
            continue
        for length in phrase_lengths:
            if length < 2 or i + length > len(raw):
                continue
            span = tuple(raw[i : i + length])
            phrase = phrase_lookup.get(span)
            if phrase is None:
                continue
            counts[phrase] += 1
            used_tokens.update(range(i, i + length))
            break

    # Count single-token skills that are allowed and not blocked, skipping phrase tokens.
    for idx, token in enumerate(raw):
        if idx in used_tokens:
            continue
        if len(token) >= 3 and token in SKILL_VOCAB and token not in BLOCKLIST:
            counts[token] += 1

    return counts


def _categorize(skill: str) -> str:
    if skill in _TECHNICAL_SKILLS or skill in _TECHNICAL_PHRASES:
        return "Technical"
    if skill in _SOFT_SKILLS or skill in _SOFT_PHRASES:
        return "Soft Skill"
    return "Tool/Other"


def _prioritize(frequency: int) -> str:
    if frequency >= 3:
        return "High"
    if frequency == 2:
        return "Medium"
    return "Low"


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract and normalize text from a PDF byte stream.

    Pure transformation: accepts bytes, returns a whitespace-normalized string.
    Raises ValueError if no text can be extracted.
    """
    from pypdf import PdfReader  # imported here to keep the module importable without pypdf

    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = " ".join(page.extract_text() or "" for page in reader.pages).strip()
    if not text:
        raise ValueError("No text could be extracted from PDF")
    return re.sub(r"\s+", " ", text)


def extract_skills_from_text(text: str) -> list[str]:
    """Extract recognized skill tokens from free-form text (resume, LinkedIn, etc.).

    Only tokens present in SKILL_VOCAB or SKILL_PHRASES pass through —
    generic English and HR jargon are excluded by the vocabulary filter.
    Returns a deduplicated, sorted list suitable for passing into SkillGapInput.skills.

    Pure function: no side-effects, no I/O.
    """
    counts = _extract_jd_tokens(text)
    return sorted(counts.keys())


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
