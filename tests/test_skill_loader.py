"""Unit tests for dynamic skill vocabulary loader."""

import os
from pathlib import Path

from skill_loader import load_skill_vocabulary
from config import get_skill_vocabulary_path


def test_load_skill_vocabulary_reads_file_and_returns_set(tmp_path):
    content = "python\nsql\naws\n"
    file_path = tmp_path / "skills.txt"
    file_path.write_text(content, encoding="utf-8")

    result = load_skill_vocabulary(str(file_path))
    assert isinstance(result, set)
    assert result == {"python", "sql", "aws"}


def test_load_skill_vocabulary_default_path_uses_configured_path(monkeypatch, tmp_path):
    content = "python\nsql\n"
    file_path = tmp_path / "default_skills.txt"
    file_path.write_text(content, encoding="utf-8")
    monkeypatch.setenv("SKILL_VOCAB_PATH", str(file_path))

    result = load_skill_vocabulary(None)
    assert result == {"python", "sql"}


def test_load_skill_vocabulary_custom_path_override(monkeypatch, tmp_path):
    content = "aws\ndocker\n"
    file_path = tmp_path / "custom_skills.txt"
    file_path.write_text(content, encoding="utf-8")
    monkeypatch.setenv("SKILL_VOCAB_PATH", str(file_path))

    result = load_skill_vocabulary(None)
    assert result == {"aws", "docker"}


def test_get_skill_vocabulary_path_default(monkeypatch):
    monkeypatch.delenv("SKILL_VOCAB_PATH", raising=False)
    default_path = get_skill_vocabulary_path()
    assert default_path == str(Path("data/skills.txt"))


def test_load_skill_vocabulary_normalizes_whitespace_and_lowercase(tmp_path):
    content = "  PyThOn  \n  SQL\n  aws  \n"
    file_path = tmp_path / "skills.txt"
    file_path.write_text(content, encoding="utf-8")

    result = load_skill_vocabulary(str(file_path))
    assert "python" in result
    assert "sql" in result
    assert "aws" in result


def test_load_skill_vocabulary_ignores_empty_lines(tmp_path):
    content = "python\n\n   \nsql\n"
    file_path = tmp_path / "skills.txt"
    file_path.write_text(content, encoding="utf-8")

    result = load_skill_vocabulary(str(file_path))
    assert result == {"python", "sql"}
