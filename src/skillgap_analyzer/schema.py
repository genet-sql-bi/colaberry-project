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


@dataclass
class LearningObjective:
    """A single learning objective for a skill module."""

    objective: str
    target_level: int


@dataclass
class LearningPathModule:
    """A structured learning path module for a gap skill."""

    skill_name: str
    skill_category: str
    gap_priority: Priority
    learning_objectives: list[LearningObjective] = field(default_factory=list)
    estimated_hours: float = 0.0
    prerequisites: list[str] = field(default_factory=list)
    sequence_number: int = 0


@dataclass
class CurriculumRecommendation:
    """Structured curriculum recommendation derived from skill gaps."""

    total_modules: int = 0
    total_estimated_hours: float = 0.0
    modules: list[LearningPathModule] = field(default_factory=list)
    learning_strategy: str = ""
