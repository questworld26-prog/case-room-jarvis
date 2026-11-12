# Copyright 2026 Sukti Ghosh and Prithis Samaddar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Unit tests for Case Study Markdown Quiz Bank Parsing, Validation, and Admin Inspection.
[spec: QUIZ-003]
"""

import tempfile
from pathlib import Path

from core.quiz_parser import (
    get_quiz_validation_status,
    load_case_quiz_bank,
    parse_quiz_markdown,
    validate_quiz_file,
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


# [verifies: ADMIN-002/AC-ADMIN-002.2]
def test_admin_quiz_bank_section_and_answer_highlight(tmp_path, monkeypatch):
    """Verify standalone quiz bank preview section highlights correct MCQ options and uses accordion cards."""
    from ui.gradio_app import _render_admin_quiz_preview

    case_dir = tmp_path / "resource" / "MockCase"
    case_dir.mkdir(parents=True)
    (case_dir / "quiz.md").write_text(
        "## Q1: Target Check\n"
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

    html = _render_admin_quiz_preview("MockCase")
    assert 'class="quiz-bank-section"' in html
    assert 'class="quiz-bank-accordion"' in html
    assert 'class="quiz-opt-pill quiz-opt-pill-correct"' in html
    assert "✓ Correct Answer" in html


# [verifies: QUIZ-004/AC-QUIZ-004.1]
def test_startup_quiz_alert_banner_formatting(tmp_path):
    """Verify startup quiz diagnostics produce a bordered terminal alert banner with line errors and fix command."""
    from core.quiz_parser import collect_quiz_bank_startup_errors, format_quiz_startup_alert

    broken_dir = tmp_path / "BrokenCase"
    broken_dir.mkdir()
    (broken_dir / "quiz.md").write_text(
        "## Q1: Missing Checkbox\n"
        "- **Type**: MCQ\n"
        "- **Official Answer**: Secret answer text.\n\n"
        "### Question\n"
        "Pick one.\n\n"
        "- [ ] A) One\n"
        "- [ ] B) Two\n"
        "- [ ] C) Three\n"
        "- [ ] D) Four\n",
        encoding="utf-8",
    )

    errors_by_case = collect_quiz_bank_startup_errors(tmp_path)
    assert len(errors_by_case) == 1
    assert errors_by_case[0]["case_name"] == "BrokenCase"
    banner = format_quiz_startup_alert(errors_by_case, use_color=False)
    assert "QUIZ BANK VALIDATION FAILED" in banner
    assert "BrokenCase" in banner
    assert "resource/BrokenCase/quiz.md" in banner
    assert "Line " in banner
    assert "uv run python src/tools/validate_quiz.py --case BrokenCase" in banner
    assert format_quiz_startup_alert([], use_color=False) == ""


# [verifies: QUIZ-004/AC-QUIZ-004.2]
def test_admin_startup_quiz_alert_html_callout(tmp_path, monkeypatch):
    """Verify admin tab startup alert banner exposes file/line errors without leaking quiz content before auth."""
    from ui.gradio_app import _build_startup_quiz_alert_html

    broken_dir = tmp_path / "BrokenCase"
    broken_dir.mkdir()
    (broken_dir / "quiz.md").write_text(
        "## Q1: Broken Check\n"
        "- **Type**: MCQ\n"
        "- **Official Answer**: CONFIDENTIAL_SOLUTION_TEXT\n\n"
        "### Question\n"
        "CONFIDENTIAL_PROMPT_TEXT\n\n"
        "- [ ] A) Opt1\n"
        "- [ ] B) Opt2\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("ui.gradio_app.RESOURCE_ROOT", tmp_path)

    alert_html = _build_startup_quiz_alert_html()
    assert 'class="quiz-bank-alert-banner"' in alert_html
    assert 'role="alert"' in alert_html
    assert "BrokenCase/quiz.md" in alert_html
    assert "Line " in alert_html
    assert "uv run python src/tools/validate_quiz.py --case BrokenCase" in alert_html
    assert "CONFIDENTIAL_SOLUTION_TEXT" not in alert_html
    assert "CONFIDENTIAL_PROMPT_TEXT" not in alert_html


# [verifies: QUIZ-004/AC-QUIZ-004.4]
def test_admin_alert_clears_and_chatbot_bank_refreshes_after_fix(tmp_path, monkeypatch):
    """Verify fixing quiz.md clears the top validation banner and updates chatbot/engine live quiz banks."""
    import chatbot
    import config
    from core.quiz_engine import parse_quiz_state_from_history
    from core.quiz_parser import load_case_quiz_bank
    from ui import admin_handlers, gradio_app

    case_dir = tmp_path / "SampleCase"
    case_dir.mkdir()
    (case_dir / "extracted_context.txt").write_text("Sample case background text for testing.", encoding="utf-8")
    quiz_file = case_dir / "quiz.md"
    quiz_file.write_text(
        "## Q1: Broken Startup\n"
        "- **Type**: MCQ\n"
        "- **Official Answer**: Answer A.\n\n"
        "### Question\n"
        "Which option?\n\n"
        "- [ ] A) Opt1\n"
        "- [ ] B) Opt2\n",
        encoding="utf-8",
    )

    def _mock_load_all():
        bank = load_case_quiz_bank(case_dir)
        return {"SampleCase": bank} if bank else {}

    monkeypatch.setattr(gradio_app, "RESOURCE_ROOT", tmp_path)
    monkeypatch.setattr("core.quiz_parser.get_case_resource_dir", lambda name: tmp_path / name)
    monkeypatch.setattr(gradio_app, "get_or_create_cache", lambda *args, **kwargs: None)
    monkeypatch.setattr(admin_handlers, "get_or_create_cache", lambda *args, **kwargs: None)
    monkeypatch.setattr(config, "load_all_case_quiz_banks", _mock_load_all)
    monkeypatch.setattr(config.app_state, "active_case_study", "SampleCase")
    monkeypatch.setattr(config.app_state, "case_text_context", "Sample case background text for testing.")
    monkeypatch.setattr(config.app_state, "session_locked", False)

    # Simulate broken startup state (bank empty on initial startup)
    config.app_state.reload_case_quiz_banks()
    assert chatbot._resolve_quiz_bank() == []
    assert "SampleCase/quiz.md" in gradio_app._build_startup_quiz_alert_html()

    # Instructor fixes quiz.md while server is running and clicks Load Selected Case Study
    quiz_file.write_text(
        "## Q1: Repaired Question\n"
        "- **Type**: MCQ\n"
        "- **Official Answer**: Option A is correct.\n\n"
        "### Question\n"
        "Which option is right?\n\n"
        "- [x] A) Right choice\n"
        "- [ ] B) Wrong choice 1\n"
        "- [ ] C) Wrong choice 2\n"
        "- [ ] D) Wrong choice 3\n",
        encoding="utf-8",
    )

    result = gradio_app._load_selected_case_study("SampleCase")
    assert len(result) == 5
    status, _locked, _summary, preview_html, startup_alert_html = result
    assert "Quiz Ready: 1 questions verified" in status
    assert "Quiz Ready: 1 questions verified" in preview_html
    assert startup_alert_html == ""

    # Chatbot and quiz engine must immediately see the repaired bank without restart
    resolved = chatbot._resolve_quiz_bank()
    assert len(resolved) == 1
    assert resolved[0]["topic"] == "Repaired Question"

    # Quiz engine total bank lookup reflects reloaded bank cleanly
    done, q_idx, attempt, scores, missed = parse_quiz_state_from_history([], lambda c: str(c or ""))
    assert (done, q_idx, attempt, scores, missed) == (False, 0, 1, [], [])

    # Broadcast and cache refresh handlers also trigger reload synchronization
    reloaded = []
    monkeypatch.setattr(config.app_state, "reload_case_quiz_banks", lambda: reloaded.append(True))
    admin_handlers.confirm_mode_broadcast()
    admin_handlers.refresh_cache_action()
    assert len(reloaded) == 2


# [verifies: QUIZ-004/AC-QUIZ-004.5]
def test_validate_quiz_file_edge_cases(tmp_path):
    """Verify validate_quiz_file catches duplicate Q numbers, empty prompts, bad types, duplicate letters, and blank options."""
    from core.quiz_parser import validate_quiz_file

    bad_quiz = tmp_path / "quiz.md"
    bad_quiz.write_text(
        "## Q1: Valid First Question\n"
        "- **Type**: MCQ\n"
        "- **Official Answer**: A is right.\n\n"
        "### Question\n"
        "First prompt?\n\n"
        "- [x] A) Alpha\n"
        "- [ ] B) Beta\n"
        "- [ ] C) Gamma\n"
        "- [ ] D) Delta\n\n"
        "## Q1: Duplicate Number And Empty Prompt\n"
        "- **Type**: Essay\n"
        "- **Official Answer**: Something.\n\n"
        "### Question\n\n"
        "- [x] A) Alpha\n"
        "- [ ] A) Duplicate Letter\n"
        "- [ ] B) \n"
        "- [ ] C) Gamma\n",
        encoding="utf-8",
    )

    is_valid, errors = validate_quiz_file(bad_quiz)
    assert is_valid is False
    joined = "\n".join(errors)
    assert "Duplicate question number Q1" in joined
    assert "unrecognized question type" in joined.lower()
    assert "prompt text" in joined.lower()
    assert "duplicate option letter" in joined.lower()
    assert "empty text" in joined.lower()
    assert all(err.startswith("Line ") for err in errors)
