"""Unit tests for curriculum recommendation generation."""

import pytest

from skillgap_analyzer.analyzer import generate_curriculum_recommendation
from skillgap_analyzer.schema import (
    SkillCategory, SkillGapResult, Priority,
    CurriculumRecommendation, LearningPathModule, LearningObjective,
)


def test_generate_curriculum_recommendation_returns_recommendation():
    """Smoke test — function returns a CurriculumRecommendation object."""
    gap_result = SkillGapResult(categories=[
        SkillCategory(skill="python", category="Technical", priority=Priority.High),
    ])
    result = generate_curriculum_recommendation(gap_result)
    assert isinstance(result, CurriculumRecommendation)


def test_generate_curriculum_recommendation_creates_one_module_per_gap():
    """Each gap skill becomes exactly one LearningPathModule."""
    gaps = [
        SkillCategory(skill="python", category="Technical", priority=Priority.High),
        SkillCategory(skill="sql", category="Technical", priority=Priority.Medium),
        SkillCategory(skill="aws", category="Technical", priority=Priority.Low),
    ]
    gap_result = SkillGapResult(categories=gaps)
    result = generate_curriculum_recommendation(gap_result)

    assert len(result.modules) == 3
    assert result.total_modules == 3


def test_generate_curriculum_recommendation_total_modules_count():
    """total_modules field matches length of modules list."""
    gaps = [
        SkillCategory(skill="python", category="Technical", priority=Priority.High),
        SkillCategory(skill="communication", category="Soft Skill", priority=Priority.Medium),
    ]
    gap_result = SkillGapResult(categories=gaps)
    result = generate_curriculum_recommendation(gap_result)

    assert result.total_modules == len(result.modules)
    assert result.total_modules == 2


def test_generate_curriculum_recommendation_estimated_hours_heuristic():
    """Estimated hours follow fixed heuristic: High=10.0, Medium=5.0, Low=2.0."""
    gaps = [
        SkillCategory(skill="python", category="Technical", priority=Priority.High),
        SkillCategory(skill="sql", category="Technical", priority=Priority.Medium),
        SkillCategory(skill="excel", category="Tool/Other", priority=Priority.Low),
    ]
    gap_result = SkillGapResult(categories=gaps)
    result = generate_curriculum_recommendation(gap_result)

    assert result.modules[0].estimated_hours == 10.0  # High
    assert result.modules[1].estimated_hours == 5.0   # Medium
    assert result.modules[2].estimated_hours == 2.0   # Low


def test_generate_curriculum_recommendation_total_estimated_hours():
    """Total estimated hours is sum of individual module hours."""
    gaps = [
        SkillCategory(skill="python", category="Technical", priority=Priority.High),      # 10.0
        SkillCategory(skill="sql", category="Technical", priority=Priority.Medium),       # 5.0
        SkillCategory(skill="aws", category="Technical", priority=Priority.Medium),       # 5.0
        SkillCategory(skill="excel", category="Tool/Other", priority=Priority.Low),       # 2.0
    ]
    gap_result = SkillGapResult(categories=gaps)
    result = generate_curriculum_recommendation(gap_result)

    expected_total = 10.0 + 5.0 + 5.0 + 2.0
    assert result.total_estimated_hours == expected_total
    assert result.total_estimated_hours == 22.0


def test_generate_curriculum_recommendation_sequence_numbers():
    """Sequence numbers are assigned in order starting at 1."""
    gaps = [
        SkillCategory(skill="python", category="Technical", priority=Priority.High),
        SkillCategory(skill="sql", category="Technical", priority=Priority.Medium),
        SkillCategory(skill="aws", category="Technical", priority=Priority.Low),
    ]
    gap_result = SkillGapResult(categories=gaps)
    result = generate_curriculum_recommendation(gap_result)

    assert result.modules[0].sequence_number == 1
    assert result.modules[1].sequence_number == 2
    assert result.modules[2].sequence_number == 3


def test_generate_curriculum_recommendation_preserves_priority_order():
    """Module ordering preserves the input gap order (priority-based from analyzer)."""
    gaps = [
        SkillCategory(skill="python", category="Technical", priority=Priority.High),
        SkillCategory(skill="sql", category="Technical", priority=Priority.Medium),
        SkillCategory(skill="aws", category="Technical", priority=Priority.High),
    ]
    gap_result = SkillGapResult(categories=gaps)
    result = generate_curriculum_recommendation(gap_result)

    skill_order = [m.skill_name for m in result.modules]
    assert skill_order == ["python", "sql", "aws"]


def test_generate_curriculum_recommendation_learning_objectives_count_high():
    """High-priority modules have 3 learning objectives."""
    gaps = [
        SkillCategory(skill="python", category="Technical", priority=Priority.High),
    ]
    gap_result = SkillGapResult(categories=gaps)
    result = generate_curriculum_recommendation(gap_result)

    assert len(result.modules[0].learning_objectives) == 3


def test_generate_curriculum_recommendation_learning_objectives_count_medium():
    """Medium-priority modules have 2 learning objectives."""
    gaps = [
        SkillCategory(skill="sql", category="Technical", priority=Priority.Medium),
    ]
    gap_result = SkillGapResult(categories=gaps)
    result = generate_curriculum_recommendation(gap_result)

    assert len(result.modules[0].learning_objectives) == 2


def test_generate_curriculum_recommendation_learning_objectives_count_low():
    """Low-priority modules have 2 learning objectives."""
    gaps = [
        SkillCategory(skill="excel", category="Tool/Other", priority=Priority.Low),
    ]
    gap_result = SkillGapResult(categories=gaps)
    result = generate_curriculum_recommendation(gap_result)

    assert len(result.modules[0].learning_objectives) == 2


def test_generate_curriculum_recommendation_learning_objectives_target_levels():
    """Learning objectives have correct target_level assignments."""
    gaps = [
        SkillCategory(skill="python", category="Technical", priority=Priority.High),
    ]
    gap_result = SkillGapResult(categories=gaps)
    result = generate_curriculum_recommendation(gap_result)

    objectives = result.modules[0].learning_objectives
    # High priority should have 3 objectives with levels 1, 2, 3
    assert objectives[0].target_level == 1
    assert objectives[1].target_level == 2
    assert objectives[2].target_level == 3


def test_generate_curriculum_recommendation_learning_objectives_medium_target_levels():
    """Medium/Low-priority modules should have objectives with levels 1, 2 only."""
    gaps = [
        SkillCategory(skill="sql", category="Technical", priority=Priority.Medium),
    ]
    gap_result = SkillGapResult(categories=gaps)
    result = generate_curriculum_recommendation(gap_result)

    objectives = result.modules[0].learning_objectives
    assert objectives[0].target_level == 1
    assert objectives[1].target_level == 2


def test_generate_curriculum_recommendation_objectives_contain_skill_name():
    """Learning objective descriptions reference the skill name."""
    gaps = [
        SkillCategory(skill="python", category="Technical", priority=Priority.High),
    ]
    gap_result = SkillGapResult(categories=gaps)
    result = generate_curriculum_recommendation(gap_result)

    objectives = result.modules[0].learning_objectives
    assert "python" in objectives[0].objective.lower()
    assert "python" in objectives[1].objective.lower()
    assert "python" in objectives[2].objective.lower()


def test_generate_curriculum_recommendation_prerequisites_empty_phase1():
    """Phase 1: prerequisites list is empty for all modules."""
    gaps = [
        SkillCategory(skill="python", category="Technical", priority=Priority.High),
        SkillCategory(skill="sql", category="Technical", priority=Priority.Medium),
    ]
    gap_result = SkillGapResult(categories=gaps)
    result = generate_curriculum_recommendation(gap_result)

    for module in result.modules:
        assert module.prerequisites == []


def test_generate_curriculum_recommendation_skill_category_preserved():
    """Module skill_category matches the gap's category."""
    gaps = [
        SkillCategory(skill="python", category="Technical", priority=Priority.High),
        SkillCategory(skill="communication", category="Soft Skill", priority=Priority.Medium),
        SkillCategory(skill="azure", category="Tool/Other", priority=Priority.Low),
    ]
    gap_result = SkillGapResult(categories=gaps)
    result = generate_curriculum_recommendation(gap_result)

    assert result.modules[0].skill_category == "Technical"
    assert result.modules[1].skill_category == "Soft Skill"
    assert result.modules[2].skill_category == "Tool/Other"


def test_generate_curriculum_recommendation_gap_priority_preserved():
    """Module gap_priority matches the gap's priority."""
    gaps = [
        SkillCategory(skill="python", category="Technical", priority=Priority.High),
        SkillCategory(skill="sql", category="Technical", priority=Priority.Medium),
        SkillCategory(skill="excel", category="Tool/Other", priority=Priority.Low),
    ]
    gap_result = SkillGapResult(categories=gaps)
    result = generate_curriculum_recommendation(gap_result)

    assert result.modules[0].gap_priority == Priority.High
    assert result.modules[1].gap_priority == Priority.Medium
    assert result.modules[2].gap_priority == Priority.Low


def test_generate_curriculum_recommendation_learning_strategy_with_high_priority():
    """Learning strategy mentions high-priority count when present."""
    gaps = [
        SkillCategory(skill="python", category="Technical", priority=Priority.High),
        SkillCategory(skill="sql", category="Technical", priority=Priority.High),
        SkillCategory(skill="excel", category="Tool/Other", priority=Priority.Low),
    ]
    gap_result = SkillGapResult(categories=gaps)
    result = generate_curriculum_recommendation(gap_result)

    assert "Master 2 high-priority skills" in result.learning_strategy
    assert "Complete 3 modules total" in result.learning_strategy


def test_generate_curriculum_recommendation_learning_strategy_no_high_priority():
    """Learning strategy omits high-priority message when none exist."""
    gaps = [
        SkillCategory(skill="sql", category="Technical", priority=Priority.Medium),
        SkillCategory(skill="excel", category="Tool/Other", priority=Priority.Low),
    ]
    gap_result = SkillGapResult(categories=gaps)
    result = generate_curriculum_recommendation(gap_result)

    assert "Master" not in result.learning_strategy
    assert "Complete 2 modules total" in result.learning_strategy


def test_generate_curriculum_recommendation_empty_gap_result():
    """Empty gap result produces empty curriculum."""
    gap_result = SkillGapResult(categories=[])
    result = generate_curriculum_recommendation(gap_result)

    assert result.total_modules == 0
    assert result.total_estimated_hours == 0.0
    assert result.modules == []
    assert result.learning_strategy == "No gaps identified"


def test_generate_curriculum_recommendation_single_gap():
    """Single gap produces single module with correct metadata."""
    gaps = [
        SkillCategory(skill="docker", category="Technical", priority=Priority.High),
    ]
    gap_result = SkillGapResult(categories=gaps)
    result = generate_curriculum_recommendation(gap_result)

    assert len(result.modules) == 1
    assert result.total_modules == 1
    assert result.total_estimated_hours == 10.0
    assert result.modules[0].skill_name == "docker"
    assert result.modules[0].sequence_number == 1


def test_generate_curriculum_recommendation_is_deterministic():
    """Same input produces identical output on multiple calls."""
    gaps = [
        SkillCategory(skill="python", category="Technical", priority=Priority.High),
        SkillCategory(skill="sql", category="Technical", priority=Priority.Medium),
    ]
    gap_result = SkillGapResult(categories=gaps)

    result1 = generate_curriculum_recommendation(gap_result)
    result2 = generate_curriculum_recommendation(gap_result)

    # Compare key fields
    assert result1.total_modules == result2.total_modules
    assert result1.total_estimated_hours == result2.total_estimated_hours
    assert len(result1.modules) == len(result2.modules)

    for m1, m2 in zip(result1.modules, result2.modules):
        assert m1.skill_name == m2.skill_name
        assert m1.estimated_hours == m2.estimated_hours
        assert m1.sequence_number == m2.sequence_number
        assert len(m1.learning_objectives) == len(m2.learning_objectives)
