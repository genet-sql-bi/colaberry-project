from __future__ import annotations

import os
from pathlib import Path

DEFAULT_SKILL_VOCAB_PATH = Path("data/skills.txt")


def get_skill_vocabulary_path() -> str:
    """Return configured skill vocabulary path with default fallback."""
    return os.getenv("SKILL_VOCAB_PATH", str(DEFAULT_SKILL_VOCAB_PATH))
