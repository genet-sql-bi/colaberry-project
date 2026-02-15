"""CLI entry point for the Skill Gap Analyzer."""

import argparse
import json
import sys

from skillgap_analyzer.analyzer import analyze_gap
from skillgap_analyzer.schema import SkillGapInput


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
        help="List of candidate skills.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    jd_text = args.jd if args.jd is not None else sys.stdin.read()

    gap_input = SkillGapInput(jd_text=jd_text, skills=args.skills)
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
