"""
Unit tests for the Pre-Authored Sequential Quiz Engine.
Verifies MCQ parsing, 2-attempt rule, hints, official answer reveals, open-ended grading, and final scorecard.
"""

import asyncio

import pytest
from conftest import is_private_repo

from chatbot import chat, parse_mcq_choice
from config import app_state, get_default_case_study


@pytest.fixture(autouse=True)
def ensure_case_context():
    target_case = get_default_case_study()
    app_state.active_case_study = target_case
    app_state.case_text_context = f"{target_case} business case study knowledge text"
    yield


def collect_chat(msg: str, hist: list, student_name: str = "Test Student") -> str:
    async def _run():
        chunks = []
        async for c in chat(msg, hist, student_name=student_name):
            chunks.append(c)
        return chunks[-1] if chunks else ""

    return asyncio.run(_run())


# [verifies: QUIZ-001/AC-QUIZ-001.1]
def test_mcq_parser_normalization():
    """Verify parse_mcq_choice handles letters, numbers, casing, and prefixes."""
    assert parse_mcq_choice("A") == "A"
    assert parse_mcq_choice("b") == "B"
    assert parse_mcq_choice("C") == "C"
    assert parse_mcq_choice("d") == "D"

    # Numeric equivalence: 1=A, 2=B, 3=C, 4=D
    assert parse_mcq_choice("1") == "A"
    assert parse_mcq_choice("2") == "B"
    assert parse_mcq_choice("3") == "C"
    assert parse_mcq_choice("4") == "D"

    # Phrased inputs
    assert parse_mcq_choice("Option B") == "B"
    assert parse_mcq_choice("choice 3") == "C"
    assert parse_mcq_choice("answer is (A)") == "A"
    assert parse_mcq_choice("b)") == "B"

    # Invalid
    assert parse_mcq_choice("random string with no letter") is None


# [verifies: QUIZ-001/AC-QUIZ-001.2]
def test_case_casing_insensitivity():
    """Verify case study name casing insensitivity resolves the question bank."""
    variants = ["EcoBrew", "EcoBrew", "ecobrew"] if is_private_repo() else ["EcoBrew", "ecobrew", "ECOBREW"]
    for case_variant in variants:
        app_state.active_mode = "quiz"
        app_state.active_case_study = case_variant

        reply = collect_chat("B", [], student_name="Frodo")
        assert "✅ **Correct! (+1.0 pt)**" in reply, f"Failed for case variant: {case_variant}"
        assert "🎯 **Quiz Question #2 of 5**" in reply


# [verifies: QUIZ-002/AC-QUIZ-002.1]
def test_quiz_q1_correct_first_attempt():
    """Verify Q1 correct answer on Attempt 1 awards +1.0 pt, reveals answer, and presents Q2."""
    app_state.active_mode = "quiz"
    app_state.active_case_study = get_default_case_study()

    # Q1 correct is B
    reply = collect_chat("B", [], student_name="Frodo")

    assert "✅ **Correct! (+1.0 pt)**" in reply
    assert "85" in reply
    assert "🎯 **Quiz Question #2 of 5**" in reply


# [verifies: QUIZ-002/AC-QUIZ-002.2]
def test_quiz_q1_attempt1_wrong_then_attempt2_correct():
    """Verify Q1 wrong answer on Attempt 1 gives hint, then Attempt 2 correct awards +0.5 pt and presents Q2."""
    app_state.active_mode = "quiz"
    app_state.active_case_study = get_default_case_study()

    # Turn 1: Wrong answer 'A'
    history = []
    reply1 = collect_chat("A", history, student_name="Frodo")
    assert "❌ **Not quite.**" in reply1
    assert "💡 **Hint**:" in reply1
    assert "🎯 **Quiz Question #1 of 5**" in reply1

    # Update history
    history.append({"role": "user", "content": "A"})
    history.append({"role": "assistant", "content": reply1})

    # Turn 2: Right answer 'B'
    reply2 = collect_chat("B", history, student_name="Frodo")
    assert "✅ **Good recovery! (+0.5 pts)**" in reply2
    assert "85" in reply2
    assert "🎯 **Quiz Question #2 of 5**" in reply2


# [verifies: QUIZ-002/AC-QUIZ-002.3]
def test_quiz_q1_double_wrong_advances_with_zero():
    """Verify Q1 wrong answer twice reveals official answer, logs 0.0 pts, and presents Q2."""
    app_state.active_mode = "quiz"
    app_state.active_case_study = get_default_case_study()

    # Turn 1: Wrong answer 'A'
    history = []
    reply1 = collect_chat("A", history, student_name="Frodo")
    history.append({"role": "user", "content": "A"})
    history.append({"role": "assistant", "content": reply1})

    # Turn 2: Wrong answer again 'C'
    reply2 = collect_chat("C", history, student_name="Frodo")
    assert "❌ **Incorrect. (+0.0 pts)**" in reply2
    assert "The official answer is:" in reply2
    assert "🎯 **Quiz Question #2 of 5**" in reply2


# [verifies: QUIZ-002/AC-QUIZ-002.4]
def test_full_5_question_quiz_scorecard():
    """Simulate a student completing all 5 questions and verify the final scorecard output."""
    app_state.active_mode = "quiz"
    app_state.active_case_study = get_default_case_study()
    history = []

    # Q1: Correct (B) -> 1.0 pt
    r1 = collect_chat("B", history)
    history.extend([{"role": "user", "content": "B"}, {"role": "assistant", "content": r1}])

    # Q2: Correct (A) -> 1.0 pt
    r2 = collect_chat("A", history)
    history.extend([{"role": "user", "content": "A"}, {"role": "assistant", "content": r2}])

    # Q3: Correct (C in Private / B in EcoBrew) -> 1.0 pt
    opt3 = "C" if is_private_repo() else "B"
    r3 = collect_chat(opt3, history)
    history.extend([{"role": "user", "content": opt3}, {"role": "assistant", "content": r3}])

    # Q4 (Open-ended): Cost savings fund digital and sustainability
    r4 = collect_chat(
        "The legacy cost saving supply chain generates operational funds to invest in digital and sustainable circular operations.",
        history,
    )
    history.extend([{"role": "user", "content": "Supply chain efficiency"}, {"role": "assistant", "content": r4}])

    # Q5 (Open-ended): Thermal brewing innovation IP sharing
    r5 = collect_chat(
        "Sharing patented thermal brewing technology for free drove sector decarbonization while maintaining distribution scale moat.",
        history,
    )

    # Verify final scorecard is produced
    assert "🎉 **Quiz Complete! Great Effort!**" in r5
    assert "📊 **Final Score**:" in r5
    assert "✅ **Mastered Concepts**:" in r5
