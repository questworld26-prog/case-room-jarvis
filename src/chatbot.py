"""
EcoBrew Business Case Discussion Chatbot ("Jarvis")
Tailored for 50 undergraduate students in a 3-hour class session.
High-Speed Cleaned Text Engine with Glowing System Event Mode Cards & Robust Multi-Turn Sanitization.
"""

import asyncio
import random
import re
import time
import traceback
from pathlib import Path

import gradio as gr
from google.genai import types

from config import PRE_AUTHORED_QUIZ_BANKS, app_state
from core.cache_manager import get_genai_client, get_or_create_cache
from core.dialogue_utils import (
    build_clean_gemini_contents,
    clean_history_for_llm,
    extract_text_content,
    parse_mcq_choice,
    sanitize_mermaid,
)
from core.logger import log_interaction
from core.quiz_engine import (
    evaluate_open_ended_quiz_response,
    format_quiz_question_card,
    format_quiz_scorecard,
    parse_quiz_state_from_history,
)
from ui.admin_handlers import (
    add_custom_fw,
    confirm_mode_broadcast,
    generate_live_dashboard_data,
    get_admin_status,
    refresh_cache_action,
    set_pending_mode,
    update_framework,
    update_model_id,
    update_ttl,
    verify_admin_password,
)
from ui.chart_generator import generate_generic_chart
from ui.gradio_app import build_gradio_demo
from ui.qr_generator import generate_qr_code
from ui.ui_theme import (
    GREETING_PATTERN,
    HEAD_THEME_SCRIPT,
    custom_css,
    format_event_card,
    format_post_quiz_wait_card,
    get_initial_welcome_card,
    get_instant_greeting,
)

__all__ = [
    "GREETING_PATTERN",
    "HEAD_THEME_SCRIPT",
    "add_custom_fw",
    "build_clean_gemini_contents",
    "chat",
    "clean_history_for_llm",
    "confirm_mode_broadcast",
    "demo",
    "evaluate_open_ended_quiz_response",
    "extract_text_content",
    "format_event_card",
    "format_quiz_question_card",
    "format_quiz_scorecard",
    "generate_live_dashboard_data",
    "get_admin_status",
    "get_initial_welcome_card",
    "get_instant_greeting",
    "get_or_create_cache",
    "launch_app",
    "parse_mcq_choice",
    "refresh_cache_action",
    "resolve_safe_static_path",
    "sanitize_mermaid",
    "set_pending_mode",
    "update_framework",
    "update_model_id",
    "update_ttl",
    "verify_admin_password",
]

_QUIZ_STARTERS = {"k", "ok", "ready", "start", "begin", "yes", "quiz", "go", "i am ready", "let's go", "lets go"}
_CHART_KEYWORDS = ("graph", "chart", "plot", "draw", "visualize", "visual", "grah")
STATIC_ROOT = (Path(__file__).resolve().parent.parent / "static").resolve()


def _resolve_quiz_bank() -> list:
    case_key = app_state.active_case_study or "EcoBrew"
    bank = PRE_AUTHORED_QUIZ_BANKS.get(case_key, [])
    if bank:
        return bank
    return next(
        (val for key, val in PRE_AUTHORED_QUIZ_BANKS.items() if key.lower() == case_key.lower()),
        [],
    )


def _was_q1_shown_in_history(q_idx: int, history: list) -> bool:
    if q_idx > 0:
        return True
    for h in history:
        role = h.get("role") if isinstance(h, dict) else getattr(h, "role", "")
        if role != "assistant":
            continue
        text = extract_text_content(h.get("content") if isinstance(h, dict) else getattr(h, "content", ""))
        if "Quiz Question #1" in text or "LIVE MODE SWITCH" in text:
            return True
    return False


def _score_mcq_turn(
    stripped_msg: str,
    current_q: dict,
    q_idx: int,
    attempt: int,
    scores: list,
    missed_concepts: list,
    reply_parts: list,
) -> tuple[bool, int, bool]:
    user_choice = parse_mcq_choice(stripped_msg)
    q_num = current_q.get("question_number", q_idx + 1)
    if user_choice is None:
        reply_parts.clear()
        reply_parts.append(
            f"⚠️ **Unrecognized Choice**: Please enter **A, B, C, or D** (or 1, 2, 3, 4) to answer Question #{q_num}.\n\n"
            f"{format_quiz_question_card(current_q)}"
        )
        return False, q_idx, True

    is_correct = user_choice == current_q.get("correct_option", "A").upper()
    official_ans = current_q.get("official_answer", "")
    hint_text = current_q.get("hint", "")

    if is_correct:
        pts = 1.0 if attempt == 1 else 0.5
        badge = "✅ **Correct! (+1.0 pt)**" if attempt == 1 else "✅ **Good recovery! (+0.5 pts)**"
        reply_parts.append(f"{badge}\n\n{official_ans}")
        scores.append(pts)
        return True, q_idx + 1, False

    if attempt == 1:
        reply_parts.append(
            f"❌ **Not quite.**\n\n💡 **Hint**: {hint_text}\n\n"
            f"*Please try once more for Question #{q_num} (Reply with A, B, C, or D below):*\n\n"
            f"{format_quiz_question_card(current_q)}"
        )
        return False, q_idx, False

    reply_parts.append(f"❌ **Incorrect. (+0.0 pts)** *(Marked for review)*\n\nThe official answer is: {official_ans}")
    scores.append(0.0)
    missed_concepts.append(current_q.get("topic", f"Question #{q_num}"))
    return True, q_idx + 1, False


async def _score_open_ended_turn(
    stripped_msg: str,
    current_q: dict,
    q_idx: int,
    attempt: int,
    scores: list,
    missed_concepts: list,
    reply_parts: list,
) -> tuple[bool, int]:
    q_num = current_q.get("question_number", q_idx + 1)
    official_ans = current_q.get("official_answer", "")
    hint_text = current_q.get("hint", "")
    score_awarded, feedback_text = await evaluate_open_ended_quiz_response(stripped_msg, current_q)

    if score_awarded >= 0.5:
        if score_awarded >= 1.0:
            reply_parts.append(
                f"🌟 **Excellent Analysis! (+1.0 pt)**\n\n{feedback_text}\n\n**Official Summary**: {official_ans}"
            )
            scores.append(1.0)
        else:
            reply_parts.append(
                f"✅ **Good Analysis! (+0.5 pts)** *(Partial credit)*\n\n{feedback_text}\n\n**Official Summary**: {official_ans}"
            )
            scores.append(0.5)
        return True, q_idx + 1

    if attempt == 1:
        reply_parts.append(
            f"❌ **Not quite.**\n\n💡 **Hint**: {hint_text}\n\n"
            f"*Please refine your analysis for Question #{q_num}:*\n\n"
            f"{format_quiz_question_card(current_q)}"
        )
        return False, q_idx

    reply_parts.append(
        f"❌ **Zero credit. (+0.0 pts)** *(Marked for review)*\n\n{feedback_text}\n\n**Official Summary**: {official_ans}"
    )
    scores.append(0.0)
    missed_concepts.append(current_q.get("topic", f"Question #{q_num}"))
    return True, q_idx + 1


async def _handle_quiz_turn(
    message: str,
    stripped_msg: str,
    history: list,
    clean_sname: str,
    start_time: float,
    quiz_bank: list,
    quiz_state: tuple,
) -> str:
    _, q_idx, attempt, scores_hist, missed_hist = quiz_state
    scores = list(scores_hist)
    missed_concepts = list(missed_hist)
    current_q = quiz_bank[q_idx]
    q_type = current_q.get("type", "mcq")

    reply_parts: list[str] = []
    if not _was_q1_shown_in_history(q_idx, history):
        reply_parts.append(get_instant_greeting(clean_sname, stripped_msg))
        reply_parts.append("\n\n---\n\n*Your answer to Quiz Question #1 has been received — here is your result:*\n\n")

    if q_type == "mcq":
        advanced, q_idx, unrecognized = _score_mcq_turn(
            stripped_msg, current_q, q_idx, attempt, scores, missed_concepts, reply_parts
        )
        if unrecognized:
            fast_reply = reply_parts[0]
            log_interaction(
                mode="quiz",
                framework=None,
                prompt=message,
                response=fast_reply,
                latency_seconds=time.time() - start_time,
                student_name=clean_sname,
                session_id=app_state.session_id,
                turn_number=(len(history) // 2) + 1,
                history_depth=len(history),
                prompt_word_count=len(stripped_msg.split()),
            )
            return fast_reply
    else:
        advanced, q_idx = await _score_open_ended_turn(
            stripped_msg, current_q, q_idx, attempt, scores, missed_concepts, reply_parts
        )

    if q_idx < len(quiz_bank) and advanced:
        reply_parts.append('\n<hr class="gemini-quiz-divider">\n')
        reply_parts.append(format_quiz_question_card(quiz_bank[q_idx]))
    elif q_idx >= len(quiz_bank):
        reply_parts.append('\n<hr class="gemini-quiz-divider">\n')
        reply_parts.append(format_quiz_scorecard(scores, missed_concepts, quiz_bank))

    final_quiz_reply = "\n\n".join(p for p in reply_parts if p)
    log_interaction(
        mode="quiz",
        framework=None,
        prompt=message,
        response=final_quiz_reply,
        latency_seconds=time.time() - start_time,
        student_name=clean_sname,
        session_id=app_state.session_id,
        turn_number=(len(history) // 2) + 1 if history else 1,
        history_depth=len(history) if history else 0,
        prompt_word_count=len(stripped_msg.split()),
    )
    return final_quiz_reply


def _prepare_gemini_request(message: str, history: list) -> tuple[list, str, bool]:
    max_turns = app_state.get_active_plugin().max_history_turns
    recent_history = history[-max_turns:] if len(history) > max_turns else history
    user_prompt = message
    if any(kw in message.lower() for kw in _CHART_KEYWORDS):
        user_prompt += (
            "\n\n[Format Requirement: Summarize the key data in a concise Markdown table (2-5 rows max) followed by 1 key insight sentence. "
            "Do NOT discuss your inability or ability to generate images, graphs, or charts; the visual chart is attached automatically by the platform.]"
        )

    mode_instruction = app_state.get_mode_instruction()
    use_cached_content = bool(getattr(app_state, "active_cache_name", None))
    if use_cached_content and mode_instruction:
        user_prompt = (
            f"### ACTIVE OPERATING MODE & DIRECTIVES ###\n{mode_instruction}\n\n[Student Message]:\n{user_prompt}"
        )

    formatted_contents = build_clean_gemini_contents(recent_history, user_prompt)
    dynamic_sys = app_state.get_system_instruction()
    full_sys = (
        dynamic_sys
        if use_cached_content
        else f"{dynamic_sys}\n\n### BUSINESS CASE STUDY KNOWLEDGE BASE GROUND TRUTH ###\n{app_state.case_text_context}"
    )
    return formatted_contents, full_sys, use_cached_content


def _compute_retry_wait(err_str: str, retry_attempt: int) -> float | None:
    lower_err = err_str.lower()
    is_transient = any(
        kw in lower_err
        for kw in (
            "429",
            "resource_exhausted",
            "quota",
            "503",
            "unavailable",
            "remoteprotocolerror",
            "disconnected",
            "connection",
            "reset",
            "closed",
        )
    )
    if not is_transient:
        return None
    delay_match = re.search(r"retry in (\d+(?:\.\d+)?)s", err_str, re.IGNORECASE)
    if delay_match:
        return min(float(delay_match.group(1)) + random.uniform(0.5, 2.0), 60.0)
    return (2.0**retry_attempt) + random.uniform(0.5, 2.0)


def _should_invalidate_context_cache(err_str: str, use_cached_content: bool) -> bool:
    if not use_cached_content:
        return False
    return any(
        kw in err_str.lower() for kw in ("cached_content", "permission_denied", "not found", "cache", "404", "403")
    )


def _log_chat_turn(
    mode: str, prompt: str, response: str, start_time: float, clean_sname: str, history: list, word_count: int
) -> None:
    log_interaction(
        mode=mode,
        framework=app_state.selected_framework,
        prompt=prompt,
        response=response,
        latency_seconds=round(time.time() - start_time, 3),
        student_name=clean_sname,
        session_id=app_state.session_id,
        turn_number=(len(history) // 2) + 1 if history else 1,
        history_depth=len(history) if history else 0,
        prompt_word_count=word_count,
    )


async def _stream_gemini_with_retries(message: str, history: list, clean_sname: str, start_time: float):
    client = get_genai_client()
    formatted_contents, full_system_instruction, use_cached_content = _prepare_gemini_request(message, history)
    dynamic_sys = app_state.get_system_instruction()
    token_limit = app_state.get_active_plugin().max_output_tokens
    max_retries = 4

    for retry_attempt in range(1, max_retries + 1):
        try:
            cfg = {
                "temperature": 0.2,
                "max_output_tokens": token_limit,
                "thinking_config": types.ThinkingConfig(thinking_budget=0),
            }
            cfg["cached_content" if use_cached_content else "system_instruction"] = (
                app_state.active_cache_name if use_cached_content else full_system_instruction
            )
            response_stream = await client.aio.models.generate_content_stream(
                model=app_state.model_id, contents=formatted_contents, config=types.GenerateContentConfig(**cfg)
            )
            partial_text = ""
            async for chunk in response_stream:
                if chunk.text:
                    partial_text += chunk.text
                    yield sanitize_mermaid(partial_text)

            if any(kw in message.lower() for kw in ("graph", "chart", "plot", "draw", "visualize", "visual")):
                try:
                    partial_text += await asyncio.to_thread(generate_generic_chart, message)
                    yield sanitize_mermaid(partial_text)
                except Exception as chart_err:
                    print(f"Notice: chart generation fallback error: {chart_err}")

            _log_chat_turn(
                app_state.active_mode, message, partial_text, start_time, clean_sname, history, len(message.split())
            )
            return
        except Exception as e:
            err_str = str(e)
            print(
                f"\n❌ [API ERROR] Attempt {retry_attempt}/{max_retries} ({time.strftime('%Y-%m-%d %H:%M:%S')}): {err_str}"
            )
            if _should_invalidate_context_cache(err_str, use_cached_content):
                app_state.active_cache_name = None
                use_cached_content = False
                full_system_instruction = f"{dynamic_sys}\n\n### BUSINESS CASE STUDY KNOWLEDGE BASE GROUND TRUTH ###\n{app_state.case_text_context}"
                if retry_attempt < max_retries:
                    continue
            wait_sec = _compute_retry_wait(err_str, retry_attempt)
            if wait_sec is not None and retry_attempt < max_retries:
                print(
                    f"⏳ Rate limit or busy ({err_str[:40]}). Retrying attempt {retry_attempt + 1}/{max_retries} in {wait_sec:.2f}s..."
                )
                await asyncio.sleep(wait_sec)
                continue
            traceback.print_exc()
            yield "⚠️ I am experiencing a temporary connection delay with the AI service. Please wait a moment and try asking your question again."
            _log_chat_turn(
                app_state.active_mode,
                message,
                f"[API ERROR] {err_str[:150]}",
                start_time,
                clean_sname,
                history,
                len(message.split()),
            )
            return


# [spec: CHAT-001]
# [spec: CHAT-002]
# [spec: CHAT-003]
# [spec: CHAT-004]
# [spec: MODE-001]
# [spec: MODE-002]
# [spec: QUIZ-001]
# [spec: QUIZ-002]
# [spec: PRIV-001]
# [spec: ADMIN-001]
# [spec: EVAL-001]
async def chat(message: str, history: list, student_name: str = ""):
    """Main streaming chat completion handler."""
    if not message or not message.strip():
        yield ""
        return
    if not app_state.active_case_study or not app_state.case_text_context:
        yield "⚠️ **No Case Study Selected**: The prof has not loaded a business case study for this session yet. Please inform the prof."
        return
    clean_sname = student_name.strip() if student_name and isinstance(student_name, str) else ""
    if not clean_sname or clean_sname in ["Anonymous Student", "Anonymous"]:
        yield "⚠️ **Student Name Required**: Please enter your Full Name in the field above before submitting a question."
        return

    start_time = time.time()
    stripped_msg = message.strip()
    quiz_state = (
        parse_quiz_state_from_history(history, extract_text_content)
        if app_state.active_mode == "quiz" and history
        else (False, 0, 1, [], [])
    )
    is_quiz_completed_in_history = quiz_state[0]

    if app_state.active_mode == "quiz" and is_quiz_completed_in_history:
        yield format_post_quiz_wait_card()
        _log_chat_turn(
            "quiz", message, "[POST-QUIZ WAIT INTERCEPT]", start_time, clean_sname, history, len(stripped_msg.split())
        )
        return

    is_pure_greeting = bool(GREETING_PATTERN.match(stripped_msg))
    is_quiz_starter = (
        app_state.active_mode == "quiz" and not is_quiz_completed_in_history and stripped_msg.lower() in _QUIZ_STARTERS
    )
    if is_pure_greeting or is_quiz_starter:
        fast_reply = get_instant_greeting(clean_sname, stripped_msg)
        yield fast_reply
        _log_chat_turn(
            app_state.active_mode, message, fast_reply, start_time, clean_sname, history, len(stripped_msg.split())
        )
        return

    quiz_bank = _resolve_quiz_bank()
    if app_state.active_mode == "quiz" and quiz_bank:
        yield await _handle_quiz_turn(message, stripped_msg, history, clean_sname, start_time, quiz_bank, quiz_state)
        return

    async for chunk in _stream_gemini_with_retries(message, history, clean_sname, start_time):
        yield chunk


demo = build_gradio_demo(chat)


# [spec: ADMIN-001]
def resolve_safe_static_path(file_path: str) -> Path | None:
    """Resolve a requested static file path strictly inside STATIC_ROOT; return None on traversal."""
    if not file_path or not isinstance(file_path, str):
        return None
    cleaned = file_path.strip().lstrip("/")
    if cleaned.startswith("static/"):
        cleaned = cleaned[len("static/") :]
    try:
        candidate = (STATIC_ROOT / cleaned).resolve()
        if candidate.is_relative_to(STATIC_ROOT) and candidate.is_file():
            return candidate
    except Exception:
        return None
    return None


# [spec: UI-004]
# [spec: UI-005]
# [spec: ADMIN-001]
def launch_app(share: bool = True):
    from fastapi import HTTPException
    from starlette.responses import FileResponse

    server_name, server_port, share_url = demo.launch(
        share=share,
        theme=gr.themes.Soft(),
        css=custom_css,
        head=HEAD_THEME_SCRIPT,
        allowed_paths=["static"],
        prevent_thread_lock=True,
    )

    if hasattr(demo, "app") and demo.app is not None:

        @demo.app.get("/file={file_path:path}")
        async def serve_file_fallback(file_path: str):
            safe_path = resolve_safe_static_path(file_path)
            if safe_path is None:
                raise HTTPException(status_code=404, detail="File not found")
            return FileResponse(safe_path)

    target_url = share_url if share_url else f"http://{server_name or 'localhost'}:{server_port or 7860}"
    print("\n" + "=" * 60)
    print("🚀 CLASSROOM CHATBOT IS LIVE!")
    print(f"🔗 URL for Students: {target_url}")
    print("=" * 60 + "\n")
    generate_qr_code(target_url)


if __name__ == "__main__":
    launch_app()
    while True:
        time.sleep(1)
