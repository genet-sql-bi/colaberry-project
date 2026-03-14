from __future__ import annotations

from pathlib import Path

from config import get_skill_vocabulary_path


def load_skill_vocabulary(path: str | None = None) -> set[str]:
    """Load a newline-separated vocabulary of skills from a text file.

    - Normalizes to lowercase
    - Strips whitespace
    - Ignores empty lines
    - Uses configured default path when path is None.
    """
    if path is None:
        path = get_skill_vocabulary_path()

    skills: set[str] = set()
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            cleaned = line.strip().lower()
            if cleaned:
                skills.add(cleaned)
    return skills
