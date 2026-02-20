# Colaberry Skill Gap Analyzer

A deterministic Python-based skill gap analyzer that compares job descriptions (JD) against candidate skills and returns structured, categorized results.

---

## Objective

Identify missing technical skills between a job description and a candidate profile, then generate a clear structured output for review, reporting, or integration.

---

## Supported Candidate Inputs

- **Manual Input** (`--skills`) — space-separated list of skills entered directly
- **Resume Text** (`--resume`) — raw resume text or path to a `.txt` file
- **LinkedIn Text** (`--linkedin`) — raw LinkedIn profile text or path to a `.txt` file

All three sources can be used together. Skills are extracted from resume/LinkedIn text using the same deterministic tokenization pipeline and merged with manually supplied skills before gap analysis runs.

---

## System Architecture

```text
  Manual Skills       Resume Text       LinkedIn Text
  (--skills)          (--resume)        (--linkedin)
       │                   │                  │
       │            extract_skills_from_text() │
       │            [analyzer.py]       │      │
       └───────────────────┴──────────────────┘
                           │
                    Merged Skills List
                           │
                           ▼
         JD Text ──► _extract_jd_tokens()
                     [analyzer.py]
                           │
                           ▼
                      analyze_gap()
                     [analyzer.py]
                           │
                           ▼
                     SkillGapResult
                  (categorized + prioritized)
```

---

## Project Structure

```
colaberry-project/
│
├── src/skillgap_analyzer/
│   ├── __init__.py
│   ├── __main__.py        # Entry point: python -m skillgap_analyzer
│   ├── analyzer.py        # Core logic: extract_skills_from_text(), analyze_gap()
│   ├── cli.py             # CLI: argument parsing, _load_text(), skill merging
│   └── schema.py          # Dataclasses: SkillGapInput, SkillCategory, SkillGapResult
│
├── tests/
│   └── test_analyzer.py   # Unit tests for analyzer and extraction logic
│
├── directives/            # SOPs and runbooks (human-readable)
├── execution/             # Deterministic execution scripts
├── agents/                # Agent persona definitions
├── config/                # Environment configuration (no secrets)
│
├── pyproject.toml
├── .gitignore
└── README.md
```

---

## Core Modules

### `analyzer.py`

| Function | Description |
|---|---|
| `extract_skills_from_text(text)` | Tokenizes free-form text (resume, LinkedIn). Returns a deduplicated, sorted list of normalized skill tokens. |
| `analyze_gap(gap_input)` | Compares merged skills against JD tokens. Returns categorized and prioritized missing skills. |
| `_extract_jd_tokens(jd_text)` | Tokenizes JD text using regex; counts unigrams and allowlisted bigrams; filters stopwords. |
| `_normalize_user_skills(raw_skills)` | Lowercases, strips whitespace, splits on commas. |
| `_categorize(skill)` | Maps skill to Technical / Soft Skill / Tool/Other. |
| `_prioritize(frequency)` | Maps frequency to High / Medium / Low. |

### `cli.py`

| Item | Description |
|---|---|
| `_load_text(value)` | If `value` is a valid file path, reads it as UTF-8; otherwise returns `value` as raw text. |
| `build_parser()` | Defines `--jd`, `--skills`, `--resume`, `--linkedin` arguments. |
| `main()` | Orchestrates: loads inputs, merges skills from all sources, calls `analyze_gap()`, prints JSON. |

### `schema.py`

| Class | Fields |
|---|---|
| `SkillGapInput` | `jd_text: str`, `skills: list[str]` |
| `SkillCategory` | `skill: str`, `category: str`, `priority: str` |
| `SkillGapResult` | `categories: list[SkillCategory]` |

---

## Usage

### Install (editable)

```bash
pip install -e .
```

### Manual skills only

```bash
python -m skillgap_analyzer \
  --jd "We need a Python and AWS developer with SQL experience." \
  --skills python sql
```

### Resume text only

```bash
python -m skillgap_analyzer \
  --jd "We need a Python and AWS developer with SQL experience." \
  --resume "Experienced developer with Python, SQL, and Docker skills."
```

### Resume from file

```bash
python -m skillgap_analyzer \
  --jd "We need a Python and AWS developer with SQL experience." \
  --resume /path/to/resume.txt
```

### LinkedIn text only

```bash
python -m skillgap_analyzer \
  --jd "We need a Python and AWS developer with SQL experience." \
  --linkedin "Senior engineer with AWS and Node experience."
```

### Combined: manual + resume + LinkedIn

```bash
python -m skillgap_analyzer \
  --jd "We need a Python and AWS developer with SQL experience." \
  --skills excel \
  --resume "Experienced developer with Python and SQL skills." \
  --linkedin "AWS and Node engineer with leadership experience."
```

### JD from stdin

```bash
cat job_description.txt | python -m skillgap_analyzer --skills python sql
```

### Example output

```json
{
  "categories": [
    { "skill": "aws", "category": "Technical", "priority": "High" },
    { "skill": "node", "category": "Technical", "priority": "Low" }
  ]
}
```

---

## Tests

```bash
python -m pytest -v
```

| Test | What it validates |
|---|---|
| `test_analyze_gap_returns_result` | Smoke test — analyze_gap returns a non-empty result |
| `test_gap_analysis_filters_and_categorizes` | Filtering, stopword removal, correct categorization |
| `test_extract_skills_from_text_returns_tokens` | Extraction returns a non-empty lowercased list |
| `test_extract_skills_from_text_deduplicates` | Duplicate tokens appear exactly once |
| `test_extract_skills_from_text_removes_stopwords` | Stopwords never appear in extracted output |
| `test_merged_skills_from_resume_excluded_from_gaps` | Resume-extracted skills are not reported as gaps |
| `test_merged_skills_from_all_sources` | Manual + resume + LinkedIn all contribute to gap exclusion |

---

## Design Principles

- **Deterministic** — no randomness, no external API calls
- **Pure core** — `analyze_gap()` and `extract_skills_from_text()` are pure functions (no I/O)
- **Testable** — all core logic is importable and independently testable
- **Layer-separated** — extraction logic lives in `analyzer.py`; orchestration lives in `cli.py`
- **Intern-safe** — no destructive operations, no secrets, one-command test execution
