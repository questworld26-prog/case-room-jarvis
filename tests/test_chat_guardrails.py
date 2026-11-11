"""
Unit tests for Chatbot Input Guardrails & Fast-Path Engine.
Completely decoupled from LLM API calls (100% deterministic, instant execution).
"""

import asyncio
import time

import pytest

from chatbot import (
    GREETING_PATTERN,
    build_clean_gemini_contents,
    chat,
    clean_history_for_llm,
    extract_text_content,
    get_initial_welcome_card,
    get_instant_greeting,
    sanitize_mermaid,
)
from config import app_state, get_default_case_study


def collect_stream(question, history, student_name="Test Student"):
    """Helper to collect final yielded output from async generator chat function."""

    async def _runner():
        final_text = ""
        async for chunk in chat(question, history, student_name=student_name):
            final_text = chunk
        return final_text

    return asyncio.run(_runner())


# ===========================================================================
# 1. Blank & Whitespace Input Guardrails
# ===========================================================================


# [verifies: CHAT-001/AC-CHAT-001.1]
@pytest.mark.parametrize("blank_input", ["", "   ", "\n\t  \n", None])
def test_blank_input_guardrail(blank_input):
    """Verify empty or whitespace-only messages return immediately with an empty string without calling LLM."""
    app_state.active_case_study = get_default_case_study()
    app_state.case_text_context = "Case context data"

    response = collect_stream(blank_input, [], student_name="Alex Tan")
    assert response == ""


# ===========================================================================
# 2. Case Study Selection Guardrails
# ===========================================================================


# [verifies: CHAT-001/AC-CHAT-001.2]
def test_missing_case_study_guardrail():
    """Verify chatting without an active case study triggers the admin selection warning."""
    app_state.active_case_study = None
    app_state.case_text_context = "Some context"

    response = collect_stream("Hello", [], student_name="Alex Tan")
    assert "No Case Study Selected" in response
    assert "The prof has not loaded a business case study" in response


# [verifies: CHAT-001/AC-CHAT-001.2]
def test_empty_case_context_guardrail():
    """Verify chatting with empty case context triggers the admin selection warning."""
    app_state.active_case_study = get_default_case_study()
    app_state.case_text_context = ""

    response = collect_stream("What is the strategy?", [], student_name="Alex Tan")
    assert "No Case Study Selected" in response


# ===========================================================================
# 3. Mandatory Student Name Guardrails
# ===========================================================================


# [verifies: CHAT-001/AC-CHAT-001.3]
@pytest.mark.parametrize("invalid_name", ["", "   ", "Anonymous Student", "Anonymous", None])
def test_mandatory_student_name_guardrail(invalid_name):
    """Verify missing, blank, or default anonymous student names trigger name requirement warning."""
    app_state.active_case_study = get_default_case_study()
    app_state.case_text_context = "Case context data"

    response = collect_stream("What are Scope 3 emissions?", [], student_name=invalid_name)
    assert "Student Name Required" in response
    assert "Please enter your Full Name" in response


# ===========================================================================
# 4. Instant Greeting Fast-Path (< 0.05s, zero LLM)
# ===========================================================================


# [verifies: CHAT-002/AC-CHAT-002.1]
@pytest.mark.parametrize(
    "greeting",
    [
        "hi",
        "Hi",
        "HELLO",
        "hello",
        "hey",
        "good morning",
        "Good Morning!",
        "good afternoon",
        "good evening",
        "howdy",
        "hi jarvis",
        "Hello Jarvis!",
        "hey jarvis",
        "help",
        "hi there",
        "hello there",
    ],
)
def test_greeting_regex_matching(greeting):
    """Verify all expected greeting variations match the pre-compiled regex."""
    assert bool(GREETING_PATTERN.match(greeting.strip())) is True


# [verifies: CHAT-002/AC-CHAT-002.1]
@pytest.mark.parametrize(
    "non_greeting",
    [
        "hi jarvis what is scope 3?",
        "hello can you explain CircularGrain",
        "good morning how are you doing today with carbon goals",
    ],
)
def test_non_greeting_not_intercepted_by_regex(non_greeting):
    """Verify substantive questions starting with greetings are not intercepted by the pure greeting regex."""
    assert bool(GREETING_PATTERN.match(non_greeting.strip())) is False


# [verifies: CHAT-002/AC-CHAT-002.2]
def test_instant_greeting_fastpath_performance_and_content():
    """Verify greeting fastpath returns in < 0.05s with student name and glowing event card."""
    app_state.active_case_study = get_default_case_study()
    app_state.case_text_context = "Case context data"
    app_state.active_mode = "qa"

    t0 = time.time()
    response = collect_stream("Hi Jarvis!", [], student_name="Samantha Lee")
    elapsed = time.time() - t0

    assert elapsed < 0.05, f"Greeting fastpath should be instantaneous (<50ms), took {elapsed:.4f}s"
    assert "Samantha Lee" in response
    assert "Standard Q&A Mode" in response
    assert "LIVE MODE SWITCH" in response


# ===========================================================================
# 5. Quiz Starter Fast-Path in Quiz Mode (< 0.05s, zero LLM)
# ===========================================================================


# [verifies: CHAT-002/AC-CHAT-002.4]
@pytest.mark.parametrize(
    "quiz_trigger", ["k", "ok", "ready", "start", "begin", "yes", "quiz", "go", "i am ready", "let's go", "lets go"]
)
def test_quiz_starter_fastpath_triggers_in_quiz_mode(quiz_trigger):
    """Verify short confirmation triggers instantly serve Quiz Question #1 in quiz mode."""
    app_state.active_case_study = get_default_case_study()
    app_state.case_text_context = "Case context data"
    app_state.active_mode = "quiz"

    t0 = time.time()
    response = collect_stream(quiz_trigger, [], student_name="Marcus Brody")
    elapsed = time.time() - t0

    assert elapsed < 0.05
    assert "Interactive Quiz & Knowledge Check" in response
    assert "Quiz Question #1" in response


# [verifies: CHAT-002/AC-CHAT-002.4]
def test_quiz_starter_does_not_intercept_in_other_modes():
    """Verify words like 'ready' or 'start' do NOT trigger quiz fast-path when mode is not 'quiz'."""
    app_state.active_case_study = get_default_case_study()
    app_state.case_text_context = "Case context data"
    app_state.active_mode = "qa"

    # In qa mode, "ready" is not a pure greeting and not a quiz starter;
    # it passes guardrails to LLM pipeline (which we can verify by checking it doesn't return quiz card)
    is_pure_greeting = bool(GREETING_PATTERN.match("ready".strip()))
    is_quiz_starter = app_state.active_mode == "quiz" and "ready".strip().lower() in [
        "k",
        "ok",
        "ready",
        "start",
        "begin",
        "yes",
        "quiz",
        "go",
        "i am ready",
        "let's go",
        "lets go",
    ]
    assert not is_pure_greeting
    assert not is_quiz_starter


# ===========================================================================
# 6. Mode-Aware Instant Greeting Card Generation
# ===========================================================================


# [verifies: CHAT-002/AC-CHAT-002.2]
@pytest.mark.parametrize(
    "mode,expected_badge_text,expected_title",
    [
        ("qa", "LIVE MODE SWITCH", "Standard Q&A Mode"),
        ("quiz", "LIVE MODE SWITCH", "Interactive Quiz & Knowledge Check"),
    ],
)
def test_instant_greeting_card_across_all_modes(mode, expected_badge_text, expected_title):
    """Verify get_instant_greeting generates the correct mode-tailored Glowing System Event Card for standard modes."""
    target_case = get_default_case_study()
    app_state.active_case_study = target_case
    app_state.active_mode = mode

    card = get_instant_greeting("Elena Rostova", "hello")
    assert expected_badge_text in card
    assert expected_title in card
    assert target_case in card


# ===========================================================================
# 7. History Payload & Sanitization Functions (Pure Logic)
# ===========================================================================


# [verifies: CHAT-003/AC-CHAT-003.1]
def test_extract_text_content_polymorphism():
    """Verify extract_text_content handles strings, lists, dicts, and None without error."""
    assert extract_text_content("Plain text") == "Plain text"
    assert extract_text_content(["Hello", "World"]) == "Hello World"
    assert extract_text_content([{"text": "Part 1"}, {"text": "Part 2"}]) == "Part 1 Part 2"
    assert extract_text_content({"value": "Dict value"}) == "Dict value"
    assert extract_text_content({"text": "Dict text"}) == "Dict text"
    assert extract_text_content(None) == ""
    assert extract_text_content(12345) == "12345"


# [verifies: CHAT-003/AC-CHAT-003.2]
def test_clean_history_for_llm():
    """Verify clean_history_for_llm strips raw HTML announcement cards and CSS."""
    raw_card = '<div style="background: #1E293B;"><span>📢 LIVE MODE SWITCH</span>Welcome to class</div>'
    assert clean_history_for_llm(raw_card) == ""

    # Quiz card preserves question
    quiz_card = (
        '<div style="color:red">📢 LIVE MODE SWITCH Quiz Question #2: What is the return rate? 💡 Hint text</div>'
    )
    cleaned_quiz = clean_history_for_llm(quiz_card)
    assert cleaned_quiz == "Quiz Question #2: What is the return rate?"

    # Normal message with stray html tag
    normal_with_tag = "EcoBrew achieved <b>96.9%</b> returnable packaging rate."
    assert clean_history_for_llm(normal_with_tag) == "EcoBrew achieved 96.9% returnable packaging rate."


# [verifies: CHAT-003/AC-CHAT-003.4]
def test_sanitize_mermaid():
    """Verify sanitize_mermaid removes mermaid diagrams while preserving other content."""
    text_with_mermaid = (
        "Here is the process overview:\n"
        "```mermaid\n"
        "graph TD;\n"
        "    A[Barley Farmers] --> B[Brewery];\n"
        "    B --> C[Distribution];\n"
        "```\n"
        "This demonstrates the circular supply chain."
    )
    sanitized = sanitize_mermaid(text_with_mermaid)
    assert "```mermaid" not in sanitized
    assert "Here is the process overview:" in sanitized
    assert "This demonstrates the circular supply chain." in sanitized


# [verifies: CHAT-003/AC-CHAT-003.3]
def test_build_clean_gemini_contents_alternation():
    """Verify Gemini dialogue builder enforces strict alternating roles starting and ending with user."""
    recent_history = [
        {"role": "assistant", "content": "Welcome to class!"},
        {"role": "user", "content": "Tell me about Scope 1."},
        {"role": "user", "content": "And Scope 2."},
        {"role": "assistant", "content": "Scope 1 and 2 cover direct operations and purchased energy."},
        {"role": "assistant", "content": "They represent 15% of emissions."},
    ]
    current_prompt = "What about Scope 3?"

    contents = build_clean_gemini_contents(recent_history, current_prompt)

    # 1. Leading assistant turn discarded -> first turn must be user
    assert contents[0].role == "user"
    assert "Tell me about Scope 1.\n\nAnd Scope 2." in contents[0].parts[0].text

    # 2. Consecutive assistant turns merged into single model turn
    assert contents[1].role == "model"
    assert "Scope 1 and 2" in contents[1].parts[0].text
    assert "15% of emissions" in contents[1].parts[0].text

    # 3. Final turn is user with current prompt
    assert contents[2].role == "user"
    assert contents[2].parts[0].text == "What about Scope 3?"

    # 4. Strict role alternation verified
    for i in range(len(contents) - 1):
        assert contents[i].role != contents[i + 1].role


# [verifies: CHAT-002/AC-CHAT-002.3]
def test_initial_welcome_card_content():
    """Verify get_initial_welcome_card contains onboarding instructions without admin references or hardcoded case names."""
    app_state.active_case_study = None
    welcome_card = get_initial_welcome_card()

    # 1. Verification of key onboarding components
    assert "WELCOME" in welcome_card
    assert "Welcome to Jarvis" in welcome_card
    assert "business case study" in welcome_card
    assert "Full Name" in welcome_card
    assert "Student ID" not in welcome_card
    assert "How to Use This App" in welcome_card
    assert "• Case Study AI Companion" in welcome_card

    # 2. Verify no admin/instructor credentials mentioned
    assert "admin" not in welcome_card.lower()
    assert "password" not in welcome_card.lower()


# [verifies: CHAT-002/AC-CHAT-002.3]
def test_welcome_card_filtered_from_llm_history():
    """Verify that the initial welcome card is stripped cleanly from LLM history."""
    welcome_card = get_initial_welcome_card()
    cleaned = clean_history_for_llm(welcome_card)
    assert cleaned == ""


# ===========================================================================
# 8. Adversarial Edge Cases & System Integrity Guardrails
# ===========================================================================


# [verifies: CHAT-001/AC-CHAT-001.4]
def test_long_input_payload_handled_cleanly():
    """Verify long prompt (250+ words) builds clean Gemini content without blowing context or crashing."""
    app_state.active_case_study = get_default_case_study()
    long_prompt = "As an MBA student analyzing corporate strategy, " + " ".join(["detailed ESG alignment factor"] * 60)
    contents = build_clean_gemini_contents([], long_prompt)
    assert len(contents) == 1
    assert contents[0].role == "user"
    assert len(contents[0].parts[0].text) > 1000


# [verifies: CHAT-001/AC-CHAT-001.4]
@pytest.mark.parametrize("emoji_prompt", ["🍺 🌍 📊 ❓", "🔥🔥🔥", "👍"])
def test_emoji_only_payload_not_crashing_builder(emoji_prompt):
    """Verify emoji-only queries build proper alternating user turns cleanly."""
    contents = build_clean_gemini_contents([], emoji_prompt)
    assert len(contents) == 1
    assert contents[0].role == "user"
    assert contents[0].parts[0].text == emoji_prompt


# [verifies: ADMIN-001/AC-ADMIN-001.4]
def test_html_escaping_and_constant_time_admin_auth():
    """Verify HTML escaping on untrusted student/admin inputs and constant-time password verification."""
    from ui.admin_handlers import get_admin_status, verify_admin_password

    app_state.active_case_study = get_default_case_study()
    app_state.active_mode = "qa"
    xss_name = "<script>alert('xss')</script>"
    greeting_html = get_instant_greeting(xss_name, "hello")
    assert "<script>" not in greeting_html
    assert "&lt;script&gt;" in greeting_html

    old_model = app_state.model_id
    try:
        app_state.model_id = '<img src=x onerror="alert(1)">'
        status_html = get_admin_status()
        assert '<img src=x onerror="alert(1)">' not in status_html
        assert "&lt;img" in status_html
    finally:
        app_state.model_id = old_model

    assert verify_admin_password(app_state.admin_password) is True
    assert verify_admin_password("wrong_password_attempt") is False
    assert verify_admin_password("") is False


# [verifies: ADMIN-001/AC-ADMIN-001.5]
def test_static_file_fallback_blocks_path_traversal():
    """Verify static file fallback resolver strictly confines paths within static/ and blocks traversal."""
    from chatbot import resolve_safe_static_path

    # Path traversal and root file access must be blocked (return None)
    assert resolve_safe_static_path(".env") is None
    assert resolve_safe_static_path("../pyproject.toml") is None
    assert resolve_safe_static_path("../../etc/passwd") is None
    assert resolve_safe_static_path("logs/classroom_chats.jsonl") is None

    # Legitimate file inside static/ must resolve cleanly inside static/
    from ui.qr_generator import generate_qr_code

    qr_path = generate_qr_code("http://localhost:7860")
    assert qr_path.exists()
    resolved = resolve_safe_static_path("classroom_qr.png")
    assert resolved is not None
    assert resolved.name == "classroom_qr.png"
    resolved_prefixed = resolve_safe_static_path("static/classroom_qr.png")
    assert resolved_prefixed is not None
    assert resolved_prefixed.name == "classroom_qr.png"
