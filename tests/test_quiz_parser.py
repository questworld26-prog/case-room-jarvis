"""
Unit tests for Case Study Markdown Quiz Bank Parsing, Validation, and Admin Inspection.
[spec: QUIZ-003]
"""

from pathlib import Path
import tempfile
import pytest

from core.quiz_parser import (
    load_case_quiz_bank,
    parse_quiz_markdown,
    validate_quiz_file,
    get_quiz_validation_status,
)


# [verifies: QUIZ-003/AC-QUIZ-003.1]
def test_parse_mcq_question():
    """Verify parsing a valid multiple-choice question from markdown extracts all fields."""
    sample_md = (
        "# Sample Case Quiz\n\n"
        "## Q1: Scope 3 Carbon Footprint\n"
        "- **Type**: MCQ\n"
        "- **Hint**: Think about where the vast majority of emissions occur.\n"
        "- **Official Answer**: Over 85% of emissions are Scope 3, and packaging is largest.\n\n"
        "### Question\n"
        "What percentage of the total carbon footprint is Scope 3 emissions?\n\n"
        "- [ ] A) ~50% of total footprint; Logistics is largest (45%)\n"
        "- [x] B) Over 85% of total footprint; Packaging manufacturing is largest (38.1%)\n"
        "- [ ] C) ~30% of total footprint; Brewery operations is largest (60%)\n"
        "- [ ] D) Over 95% of total footprint; Agriculture is largest (50%)\n"
    )
    questions = parse_quiz_markdown(sample_md)
    assert len(questions) == 1
    q = questions[0]
    assert q["id"] == "Q1"
    assert q["question_number"] == 1
    assert q["topic"] == "Scope 3 Carbon Footprint"
    assert q["type"] == "mcq"
    assert q["prompt_text"] == "What percentage of the total carbon footprint is Scope 3 emissions?"
    assert len(q["options"]) == 4
    assert q["options"][0].startswith("A)")
    assert q["options"][1].startswith("B)")
    assert q["correct_option"] == "B"
    assert "Think about where" in q["hint"]
    assert "Over 85% of emissions" in q["official_answer"]


# [verifies: QUIZ-003/AC-QUIZ-003.2]
def test_parse_open_ended_question():
    """Verify parsing a valid open-ended question extracts rubric key points and prompt."""
    sample_md = (
        "## Q4: Supply Chain Transformation\n"
        "- **Type**: Open-Ended\n"
        "- **Hint**: Focus on legacy efficiency vs digital investments.\n"
        "- **Official Answer**: Engine One operational gains fund Engine Two.\n\n"
        "### Question\n"
        "Analyze the strategic relationship between Engine One and Engine Two.\n\n"
        "### Answer (Rubric)\n"
        "- Engine One is the legacy, cost-focused supply chain.\n"
        "- Engine Two is the digital, sustainable supply chain.\n"
        "- Cost savings from Engine One fund Engine Two.\n"
    )
    questions = parse_quiz_markdown(sample_md)
    assert len(questions) == 1
    q = questions[0]
    assert q["id"] == "Q4"
    assert q["question_number"] == 4
    assert q["topic"] == "Supply Chain Transformation"
    assert q["type"] == "open_ended"
    assert q["prompt_text"] == "Analyze the strategic relationship between Engine One and Engine Two."
    assert len(q["rubric_key_points"]) == 3
    assert "Engine One is the legacy" in q["rubric_key_points"][0]
    assert "Engine Two is the digital" in q["rubric_key_points"][1]
    assert "Cost savings from Engine One" in q["rubric_key_points"][2]
    assert "Focus on legacy" in q["hint"]
    assert "Engine One operational gains" in q["official_answer"]


# [verifies: QUIZ-003/AC-QUIZ-003.3]
def test_schema_violations_line_diagnostics():
    """Verify validate_quiz_file catches missing checkboxes, bad options, and reports line numbers."""
    malformed_md = (
        "## Q1: Malformed MCQ\n"
        "- **Type**: MCQ\n"
        "- **Official Answer**: Something.\n\n"
        "### Question\n"
        "Select one option?\n\n"
        "- [ ] A) Option A\n"
        "- [ ] B) Option B\n"
        "- [ ] C) Option C\n"
        "- [ ] D) Option D\n\n"
        "## Q2: Broken Open Ended\n"
        "- **Type**: Open-Ended\n\n"
        "### Question\n"
        "Explain the case dynamics.\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
        tf.write(malformed_md)
        tf_path = Path(tf.name)

    try:
        is_valid, errors = validate_quiz_file(tf_path)
        assert is_valid is False
        assert len(errors) >= 2
        # Check that error messages include line numbers
        assert any("Line " in err and "no correct option marked" in err.lower() for err in errors)
        assert any("Line " in err and ("rubric" in err.lower() or "official answer" in err.lower()) for err in errors)
    finally:
        if tf_path.exists():
            tf_path.unlink()


# [verifies: QUIZ-003/AC-QUIZ-003.4]
def test_invalid_or_missing_quiz_bank_handling(caplog):
    """Verify system logs error and provides safe fallback structure when quiz.md is missing or malformed."""
    bank = load_case_quiz_bank("NonExistentCaseStudyXYZ")
    assert bank == []

    status = get_quiz_validation_status("NonExistentCaseStudyXYZ")
    assert status["is_valid"] is False
    assert "No markdown quiz bank found" in status["alert_message"]


# [verifies: QUIZ-003/AC-QUIZ-003.5]
def test_admin_quiz_validation_and_preview(tmp_path, monkeypatch):
    """Verify get_quiz_validation_status returns ready badge and HTML cards for admin inspection."""
    case_dir = tmp_path / "resource" / "MockCase"
    case_dir.mkdir(parents=True)
    quiz_file = case_dir / "quiz.md"
    quiz_file.write_text(
        "## Q1: Overview Check\n"
        "- **Type**: MCQ\n"
        "- **Official Answer**: B is correct.\n\n"
        "### Question\n"
        "What is the core target?\n\n"
        "- [ ] A) 50%\n"
        "- [x] B) 100%\n"
        "- [ ] C) 25%\n"
        "- [ ] D) 75%\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("core.quiz_parser.get_case_resource_dir", lambda case: tmp_path / "resource" / case)

    status = get_quiz_validation_status("MockCase")
    assert status["is_valid"] is True
    assert "🟢 Quiz Ready" in status["badge"]
    assert status["total_questions"] == 1
    assert len(status["preview_cards"]) == 1
    assert "quiz-opt-pill" in status["preview_cards"][0]
    assert "What is the core target?" in status["preview_cards"][0]
