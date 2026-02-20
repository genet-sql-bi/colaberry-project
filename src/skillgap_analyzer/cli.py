"""CLI entry point for the Skill Gap Analyzer."""

import argparse
import json
import sys
from pathlib import Path

from skillgap_analyzer.analyzer import analyze_gap, extract_skills_from_text
from skillgap_analyzer.schema import SkillGapInput


def _load_text(value: str) -> str:
    """Return file contents if value is a valid file path; otherwise return value as-is."""
    path = Path(value)
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyse skill gaps against a job description.",
    )
    parser.add_argument(
        "--jd",
        type=str,
        default=None,
        help="Job description text. If omitted, reads from stdin.",
    )
    parser.add_argument(
        "--skills",
        type=str,
        nargs="+",
        default=[],
        help="Manual list of candidate skills.",
    )
    parser.add_argument(
        "--resume",
        type=str,
        default=None,
        help="Resume text or path to a resume .txt file.",
    )
    parser.add_argument(
        "--linkedin",
        type=str,
        default=None,
        help="LinkedIn profile text or path to a .txt file.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    jd_text = args.jd if args.jd is not None else sys.stdin.read()

    # Collect skills from all three sources and merge into one list.
    all_skills: list[str] = list(args.skills)

    if args.resume:
        resume_text = _load_text(args.resume)
        all_skills.extend(extract_skills_from_text(resume_text))

    if args.linkedin:
        linkedin_text = _load_text(args.linkedin)
        all_skills.extend(extract_skills_from_text(linkedin_text))

    gap_input = SkillGapInput(jd_text=jd_text, skills=all_skills)
    result = analyze_gap(gap_input)

    print(json.dumps(
        {
            "categories": [
                {"skill": c.skill, "category": c.category, "priority": c.priority}
                for c in result.categories
            ],
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
