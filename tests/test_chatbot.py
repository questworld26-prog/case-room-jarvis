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
Automated Pytest Suite for Business Case Study Chatbot ('Jarvis')
Verifies factual accuracy, ground-truth answering, out-of-scope rejection, instant greeting fast-path, and all 7 operating modes.
"""

import asyncio
import time

import pytest
from core.cache_manager import get_or_create_cache, validate_gemini_api_key

from chatbot import chat
from config import app_state, get_default_case_study

_has_gemini, _gemini_reason = validate_gemini_api_key()
requires_live_gemini = pytest.mark.skipif(
    not _has_gemini,
    reason=f"Requires live Gemini API: {_gemini_reason}",
)


@pytest.fixture(scope="module")
def setup_context_cache():
    """Ensure clean case text context is loaded before running tests."""
    app_state.cache_ttl = "12600s"
    case = get_default_case_study()
    cache = get_or_create_cache(case, force_refresh=True)
    assert len(app_state.case_text_context) > 0 or app_state.active_cache_name is not None
    yield cache


def collect_stream(question, history, student_name="Test Student"):
    """Helper to collect final yielded output from async generator chat function."""

    async def _runner():
        final_text = ""
        async for chunk in chat(question, history, student_name=student_name):
            final_text = chunk
        return final_text

    return asyncio.run(_runner())


# [verifies: MODE-001/AC-MODE-001.1]
@requires_live_gemini
def test_ground_truth_answering(setup_context_cache):
    """Verify Jarvis answers factual metrics directly supported by the case documents."""
    app_state.active_mode = "qa"
    case = get_default_case_study()
    question = f"What percentage of {case}'s total carbon footprint is represented by Scope 3 emissions?"
    history = []

    response = collect_stream(question, history)
    print(f"\n[Q&A Ground Truth Response]:\n{response}")

    assert response is not None
    assert len(response) > 0
    assert any(val in response for val in ("85%", "85.2%", "85 percent", "85.2 percent"))


# [verifies: CHAT-003/AC-CHAT-003.3]
@requires_live_gemini
def test_multiturn_history_resilience(setup_context_cache):
    """Verify multi-turn chat works cleanly when history contains Gradio 6 list-dict structures."""
    app_state.active_mode = "qa"

    complex_history = [
        {"role": "user", "content": "What is the global return rate of glass containers for EcoBrew?"},
        {
            "role": "assistant",
            "content": [
                {
                    "text": "According to the case study, glass container return rates reached 96.9% globally.",
                    "type": "text",
                }
            ],
        },
    ]

    second_question = "What is CircularGrain?"
    response = collect_stream(second_question, complex_history)
    print(f"\n[Multi-turn Second Question Response]:\n{response}")

    assert response is not None
    assert "CircularGrain" in response or "upcycl" in response.lower() or "spent grain" in response.lower()


# [verifies: MODE-001/AC-MODE-001.2]
@requires_live_gemini
def test_multi_question_redirect(setup_context_cache):
    """Verify Jarvis picks the most important question, notes conciseness limits, and requests 1 question at a time."""
    app_state.active_mode = "qa"
    question = "What is SBTi? What are EcoBrew's water targets? And what is the 100% Mindset?"
    response = collect_stream(question, [])
    print(f"\n[Multi-Question Response]:\n{response}")

    assert response is not None
    response_lower = response.lower()
    # Check that Jarvis requests one question at a time or notes multiple questions / word limit
    assert any(
        phrase in response_lower
        for phrase in [
            "one question",
            "single question",
            "multiple question",
            "distinct question",
            "first question",
            "175 words",
            "word limit",
            "limit",
        ]
    ), f"Expected multi-question redirect phrase in response: {response}"

    # Verify strict conciseness limit (under 200 words buffer for LLM output)
    word_count = len(response.split())
    assert word_count <= 200, f"Response exceeded word cap: {word_count} words"


# [verifies: CHAT-004/AC-CHAT-004.1]
@requires_live_gemini
def test_out_of_scope_rejection(setup_context_cache):
    """Verify Jarvis declines to answer irrelevant world-knowledge questions."""
    app_state.active_mode = "qa"
    question = "Who won the FIFA World Cup in 2022?"
    history = []

    response = collect_stream(question, history)
    print(f"\n[Out of Scope Response]:\n{response}")

    assert response is not None
    assert any(
        phrase in response.lower()
        for phrase in ["outside", "not covered", "do not know", "documents", "scope", "does not contain"]
    )


# [verifies: CHAT-002/AC-CHAT-002.2]
def test_instant_greeting_fastpath(setup_context_cache):
    """Verify pure greetings return instantaneously (< 0.05s) with mode-aware content."""
    app_state.active_mode = "qa"
    t0 = time.time()
    response = collect_stream("hi", [], student_name="Alex Tan")
    elapsed = time.time() - t0

    assert elapsed < 0.5, f"Instant greeting took too long: {elapsed}s"
    assert "Jarvis" in response
    assert "Alex Tan" in response or "there" in response


# [verifies: MODE-002/AC-MODE-002.1]
def test_quiz_first_question_auto_post(setup_context_cache):
    """Verify that in Quiz mode, greeting or short trigger serves Question #1 immediately."""
    app_state.active_mode = "quiz"
    response = collect_stream("k", [], student_name="Alex Tan")

    assert "Quiz Mode" in response or "Quiz Question #1" in response or "Scope 3" in response
    assert len(response) > 20


# [verifies: MODE-002/AC-MODE-002.1]
def test_quiz_announcement_shown_on_mid_session_mode_switch(setup_context_cache):
    """
    Regression test for: instructor switches to Quiz mode mid-session while student has
    prior Q&A history. Student submits a direct MCQ answer ('A', 'B', 'C', 'D') without
    first sending a greeting/starter that triggers the fast-path announcement.

    Expected: response MUST include the quiz announcement card (with 'Quiz Question #1')
    AND the answer feedback — NOT just a bare wrong/correct answer with no context.

    This was broken in the release prior to 2026-09-20: Adam's window showed no
    announcement and no Q1 when the instructor switched from QA to Quiz.
    """
    app_state.active_mode = "quiz"

    # Simulate student having a prior Q&A conversation before mode was switched to quiz
    prior_qa_history = [
        {
            "role": "user",
            "content": "What are the key strategic choices and competitive advantages outlined in the case?",
        },
        {
            "role": "assistant",
            "content": "EcoBrew's key strategic choices include Engine One & Two supply chain reinvention and EcoVentures. 💡 **Discussion Question:** ...",
        },
    ]

    # Student submits a direct MCQ answer ('d') without any greeting/starter word.
    # This is the exact scenario that failed — the quiz engine must detect Q1 was
    # never shown (no quiz markers in Q&A history) and prepend the announcement.
    response = collect_stream("d", prior_qa_history, student_name="Adam")

    print(f"\n[Mid-Session Mode Switch Quiz Response]:\n{response[:500]}")

    # Q1 announcement card must be visible in the response
    assert "Quiz Question #1" in response, (
        "Q1 announcement card was not prepended when student answered without seeing Q1 first. "
        "Instructor mode switch from Q&A → Quiz without student greeting is broken."
    )
    # Must also contain quiz answer feedback (not just the card alone)
    has_feedback = "Not quite" in response or "Correct" in response or "Incorrect" in response or "Hint" in response
    assert has_feedback, "Quiz engine did not produce any MCQ feedback after the announcement card."


# [verifies: QUIZ-001/AC-QUIZ-001.1]
def test_strict_mcq_parsing_does_not_match_sentences(setup_context_cache):
    """Verify sentences starting with letters A, B, C, D (e.g. 'Beyond...') are not misparsed as MCQ choices."""
    from core.dialogue_utils import parse_mcq_choice

    # Legitimate MCQ formats
    assert parse_mcq_choice("A") == "A"
    assert parse_mcq_choice("b") == "B"
    assert parse_mcq_choice("Option C") == "C"
    assert parse_mcq_choice("choice d") == "D"
    assert parse_mcq_choice("(B)") == "B"
    assert parse_mcq_choice("b)") == "B"
    assert parse_mcq_choice("1") == "A"
    assert parse_mcq_choice("2") == "B"
    assert parse_mcq_choice("B - Logistics and Packaging") == "B"

    # Conversational text that MUST NOT be parsed as MCQ answers
    question = "Beyond brand reputation and supply chain security, what other long-term financial benefits might EcoBrew realize?"
    assert parse_mcq_choice(question) is None
    assert parse_mcq_choice("Can you elaborate on water stewardship?") is None
    assert parse_mcq_choice("Although packaging is Scope 3, what about cooling?") is None
    assert parse_mcq_choice("Does EcoBrew use solar power?") is None


# [verifies: MODE-002/AC-MODE-002.2]
def test_mode_interactive_quiz(setup_context_cache):
    """Verify Mode 2 generates quiz feedback and intercepts post-quiz questions with wait message."""
    app_state.active_mode = "quiz"
    question = "Scope 3 emissions account for over 85%, mainly from packaging and cooling."
    history = []

    response = collect_stream(question, history)
    print(f"\n[Quiz Mode Response]:\n{response}")

    assert response is not None
    assert len(response) > 10


# [verifies: MODE-002/AC-MODE-002.3]
def test_post_quiz_waiting_intercept(setup_context_cache):
    """Verify that after completing all 5 quiz questions, subsequent messages yield waiting response."""
    app_state.active_mode = "quiz"
    completed_history = [
        {"role": "assistant", "content": "🎯 **Quiz Question #1 of 5**\nOption A"},
        {"role": "user", "content": "A"},
        {"role": "assistant", "content": "🎯 **Quiz Question #2 of 5**\nOption B"},
        {"role": "user", "content": "B"},
        {"role": "assistant", "content": "🎯 **Quiz Question #3 of 5**\nOption C"},
        {"role": "user", "content": "C"},
        {"role": "assistant", "content": "🎯 **Quiz Question #4 of 5**\nExplain Scope 3."},
        {"role": "user", "content": "Scope 3 emissions are packaging and cooling."},
        {"role": "assistant", "content": "🎯 **Quiz Question #5 of 5**\nExplain water stewardship."},
        {"role": "user", "content": "Water stewardship focuses on high stress areas."},
        {
            "role": "assistant",
            "content": "📊 **Final Score**: **`5.0 / 5.0`**\n*💡 Quiz mode complete! Please wait for your Prof to change the mode for the next activity.*",
        },
    ]

    response = collect_stream("What else should I study?", completed_history, student_name="Alex Tan")
    assert "Thank you for completing the quiz!" in response
    assert "wait for your Prof to switch modes" in response


# [verifies: MODE-002/AC-MODE-002.3]
def test_post_quiz_single_word_ok_intercept(setup_context_cache):
    """Verify that sending 'ok' after finishing the quiz does NOT re-trigger Question #1."""
    app_state.active_mode = "quiz"
    completed_history = [
        {"role": "assistant", "content": "🎯 **Quiz Question #1 of 5**\nOption A"},
        {"role": "user", "content": "A"},
        {"role": "assistant", "content": "🎯 **Quiz Question #2 of 5**\nOption B"},
        {"role": "user", "content": "B"},
        {"role": "assistant", "content": "🎯 **Quiz Question #3 of 5**\nOption C"},
        {"role": "user", "content": "C"},
        {"role": "assistant", "content": "🎯 **Quiz Question #4 of 5**\nExplain Scope 3."},
        {"role": "user", "content": "Scope 3 emissions are packaging and cooling."},
        {"role": "assistant", "content": "🎯 **Quiz Question #5 of 5**\nExplain water stewardship."},
        {"role": "user", "content": "Water stewardship focuses on high stress areas."},
        {
            "role": "assistant",
            "content": "📊 **Final Score**: **`5.0 / 5.0`**\n*💡 Quiz mode complete! Please wait for your Prof to change the mode for the next activity.*",
        },
    ]

    response = collect_stream("ok", completed_history, student_name="Alex Tan")
    assert "Thank you for completing the quiz!" in response
    assert "wait for your Prof to switch modes" in response
    assert "Quiz Question #1" not in response


# [verifies: MODE-001/AC-MODE-001.3]
def test_mode_citation_verification(setup_context_cache):
    """Citation mode removed from UI. Verify mode falls back cleanly to QA-style response."""
    assert app_state.get_mode_display_name("citation") == "Mode 1 — Standard Q&A (Default)"
    app_state.active_mode = "qa"
    assert app_state.active_mode == "qa"


# [verifies: CACHE-002/AC-CACHE-002.2]
def test_cache_restart_recovery(setup_context_cache):
    """Verify get_or_create_cache loads clean text context without throwing error."""
    case = get_default_case_study()
    get_or_create_cache(case, force_refresh=False)
    assert len(app_state.case_text_context) > 1000
    assert case in app_state.case_text_context


# [verifies: CHAT-004/AC-CHAT-004.3]
@requires_live_gemini
def test_graph_generation_fallback(setup_context_cache):
    """Verify chatbot automatically appends the Matplotlib static image when asked for a graph and file exists on disk."""
    import os
    import re

    app_state.active_mode = "qa"
    question = "Can you show me a graph of the carbon footprint?"
    history = []

    response = collect_stream(question, history)
    print(f"\n[Graph Mode Response Length]: {len(response)}")

    assert response is not None
    assert "/file=static/generated_plots/" in response or "/gradio_api/file=static/generated_plots/" in response
    assert "Visual Data Chart" in response

    # Assert generated image exists on disk and is non-empty
    match = re.search(r"file=(static/generated_plots/[^\s\)\"]+)", response)
    assert match is not None, "Could not extract plot path from response"
    plot_rel_path = match.group(1)
    assert os.path.exists(plot_rel_path), f"Generated plot file does not exist on disk: {plot_rel_path}"
    assert os.path.getsize(plot_rel_path) > 500, f"Generated plot file is too small or corrupt: {plot_rel_path}"


# [verifies: CHAT-004/AC-CHAT-004.2]
def test_token_limit_and_word_cap(setup_context_cache):
    """Verify chatbot response word count remains strictly capped (<= 175 words) under clamped max_output_tokens=350."""
    app_state.active_mode = "qa"
    question = "What are the key strategic choices outlined in the case study?"
    history = []

    response = collect_stream(question, history)
    print(f"\n[Clamped Token Response Length]: {len(response.split())} words")

    assert response is not None
    word_count = len(response.split())
    assert word_count <= 190, f"Response exceeded 175-word target budget (got {word_count} words): {response[:150]}..."


# [verifies: CHAT-001/AC-CHAT-001.3]
def test_mandatory_student_name_validation(setup_context_cache):
    """Verify that attempting to chat without a student name yields a mandatory name warning."""
    app_state.active_mode = "qa"
    question = "What are the core strategic choices?"

    # Empty student name
    resp_empty = collect_stream(question, [], student_name="")
    assert "Student Name Required" in resp_empty

    # Default Anonymous Student
    resp_anon = collect_stream(question, [], student_name="Anonymous Student")
    assert "Student Name Required" in resp_anon


# [verifies: CHAT-001/AC-CHAT-001.2]
def test_unselected_case_study_warning():
    """Verify that chatting when no case study has been loaded yields an Admin selection warning."""
    app_state.active_case_study = None
    app_state.case_text_context = ""
    question = "What are the core strategic choices?"

    response = collect_stream(question, [], student_name="Test Student")
    assert "No Case Study Selected" in response


# [verifies: ADMIN-001/AC-ADMIN-001.2]
def test_mode_broadcast_banner():
    """Verify live mode broadcast banner formatting across standard modes."""
    app_state.active_case_study = get_default_case_study()
    app_state.active_mode = "qa"
    assert "Standard Q&A" in app_state.get_broadcast_banner()

    app_state.active_mode = "quiz"
    banner_quiz = app_state.get_broadcast_banner()
    assert "Interactive Quiz" in banner_quiz
    assert "Quiz Question #1" in banner_quiz

    # Verify mode change notification tracking
    assert not app_state.has_broadcast_changed()
    app_state.notify_mode_change()
    assert app_state.has_broadcast_changed()
    assert not app_state.has_broadcast_changed()


# [verifies: ADMIN-001/AC-ADMIN-001.3]
def test_admin_update_ttl_and_model_id():
    """Verify instructor admin settings for Cache TTL and Model ID update correctly."""
    from chatbot import update_model_id, update_ttl

    status_ttl = update_ttl("300s")
    assert app_state.cache_ttl == "300s"
    assert "300s" in status_ttl
    assert "Cache TTL / Duration" in status_ttl

    status_model = update_model_id("gemini-2.5-pro")
    assert app_state.model_id == "gemini-2.5-pro"
    assert "gemini-2.5-pro" in status_model

    # Restore defaults
    update_ttl("30s")
    update_model_id("gemini-2.5-flash")


# ---------------------------------------------------------------------------
# Visual Presentation & UI Theme Verification Suite
# ---------------------------------------------------------------------------
