"""Typed structures for Skill Gap Analyzer inputs and outputs."""

from dataclasses import dataclass, field
from enum import Enum


class Priority(str, Enum):
    High = "High"
    Medium = "Medium"
    Low = "Low"


@dataclass
class SkillGapInput:
    """Input to the skill gap analysis."""

    jd_text: str
    skills: list[str] = field(default_factory=list)


@dataclass
class SkillCategory:
    """A single categorized skill with its gap priority."""

    skill: str
    category: str
    priority: Priority


@dataclass
class SkillGapResult:
    """Output of the skill gap analysis."""

    categories: list[SkillCategory] = field(default_factory=list)
