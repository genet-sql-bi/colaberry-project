"""CLI entry point for the Skill Gap Analyzer."""

import argparse
import json
import re
import sys
from pathlib import Path

import pypdf

from skillgap_analyzer.service import analyze_skill_gap


def _extract_pdf_text(path: Path) -> str:
    """Extract text from all pages of a PDF and return as a single normalized string.

    Whitespace is collapsed to single spaces for determinism.
    Raises ValueError if no text can be extracted (e.g. scanned/image-only PDF).
    """
    reader = pypdf.PdfReader(str(path))
    parts = [page.extract_text() or "" for page in reader.pages]
    normalized = re.sub(r"\s+", " ", " ".join(parts)).strip()
    if not normalized:
        raise ValueError(
            f"No text could be extracted from '{path}'. "
            "The PDF may be scanned or image-only."
        )
    return normalized


def _load_text(value: str) -> str:
    """Return file contents if value is a valid file path; otherwise return value as-is.

    Supported file types: .txt (read directly), .pdf (text extracted via pypdf).
    Any other file extension raises ValueError.
    Non-path strings are returned unchanged as raw text.
    """
    path = Path(value)
    if path.is_file():
        suffix = path.suffix.lower()
        if suffix == ".txt":
            return path.read_text(encoding="utf-8")
        if suffix == ".pdf":
            return _extract_pdf_text(path)
        raise ValueError(f"Unsupported file type: {path.suffix}")
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
        help="Resume text or path to a resume file (.txt or .pdf).",
    )
    parser.add_argument(
        "--linkedin",
        type=str,
        default=None,
        help="LinkedIn profile text or path to a file (.txt or .pdf).",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    input_data: dict = {
        "jd_text": args.jd if args.jd is not None else sys.stdin.read(),
        "skills": list(args.skills),
    }
    if args.resume:
        input_data["resume_text"] = _load_text(args.resume)
    if args.linkedin:
        input_data["linkedin_text"] = _load_text(args.linkedin)

    print(json.dumps(analyze_skill_gap(input_data), indent=2))


if __name__ == "__main__":
    main()
