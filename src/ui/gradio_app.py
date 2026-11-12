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
Gradio Blocks application layout and interactive component wiring for Jarvis Chatbot.
Separates UI component assembly from the core streaming chat engine.
"""

import html
from collections.abc import Callable
from pathlib import Path

import gradio as gr

from config import app_state, get_available_case_studies
from core.cache_manager import get_or_create_cache
from core.quiz_parser import collect_case_setup_errors, get_quiz_validation_status
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
from ui.ui_theme import CLIENT_HERO_HTML, DEMO_LOAD_JS, get_instant_greeting

RESOURCE_ROOT = Path(__file__).resolve().parent.parent.parent / "resource"


# [spec: CACHE-003]
# [spec: QUIZ-004]
def _build_startup_quiz_alert_html() -> str:
    """Render a prominent pre-auth alert callout in Admin Tab for incomplete case folders or invalid quiz banks."""
    failures = collect_case_setup_errors(RESOURCE_ROOT)
    if not failures:
        return ""
    sections = []
    for entry in failures:
        safe_case = html.escape(str(entry["case_name"]))
        safe_path = html.escape(str(entry["quiz_path"]))
        err_items = "".join(f"<li>{html.escape(str(e))}</li>" for e in entry.get("errors", []))
        remediations = entry.get("remediations") or [
            f"uv run python src/tools/validate_quiz.py --case {entry['case_name']}",
        ]
        rem_parts = []
        for cmd in remediations:
            if cmd == "See docs/ADDING_A_CASE_STUDY.md":
                rem_parts.append(
                    '<div class="quiz-bank-remediation">🔧 Remediation: See <code>docs/ADDING_A_CASE_STUDY.md</code></div>'
                )
            else:
                rem_parts.append(
                    f'<div class="quiz-bank-remediation">🔧 Remediation: <code>{html.escape(str(cmd))}</code></div>'
                )
        remediation_html = "".join(rem_parts)
        sections.append(
            '<div class="quiz-bank-alert-case">'
            f'<div class="quiz-bank-alert-case-title">❌ <strong>{safe_case}</strong> '
            f"(<code>{safe_path}</code> — {len(entry.get('errors', []))} issue(s))</div>"
            f'<ul class="quiz-bank-errors">{err_items}</ul>'
            f"{remediation_html}"
            "</div>"
        )
    return (
        '<div class="quiz-bank-alert-banner" role="alert">'
        '<div class="quiz-bank-alert-header">'
        '<span class="quiz-bank-status-pill is-error">🚨 Startup Case Study &amp; Quiz Validation Errors</span>'
        '<span class="quiz-bank-alert-sub">Empty case folders block chat; Quiz Mode falls back to oral exam until fixed</span>'
        "</div>"
        f"{''.join(sections)}"
        "</div>"
    )


# [spec: ADMIN-001]
# [spec: UI-005]
def poll_and_push_announcements(history, session_state, student_name):
    """Automatically push mode changes & Quiz Question #1 into connected student chat windows."""
    if session_state is None:
        session_state = {"last_mode_version": 0, "last_mode": ""}

    current_version = app_state.mode_version
    current_mode = app_state.active_mode
    last_version = session_state.get("last_mode_version", 0)

    if history and len(history) > 0:
        last_turn = history[-1]
        if isinstance(last_turn, dict) and last_turn.get("role") == "user":
            return gr.skip(), session_state

    if last_version == 0:
        session_state["last_mode_version"] = current_version
        session_state["last_mode"] = current_mode
        if current_mode == "quiz" and app_state.active_case_study and (not history or len(history) <= 1):
            q1_msg = get_instant_greeting(student_name, "quiz")
            new_history = list(history) if history else []
            new_history.append({"role": "assistant", "content": q1_msg})
            return new_history, session_state
        return gr.skip(), session_state

    if current_version > last_version:
        session_state["last_mode_version"] = current_version
        session_state["last_mode"] = current_mode
        announcement_msg = get_instant_greeting(student_name, "mode_change")
        new_history = list(history) if history else []
        new_history.append({"role": "assistant", "content": announcement_msg})
        return new_history, session_state

    return gr.skip(), session_state


def _bind_quick_submit_button(chatbot_interface: gr.ChatInterface, btn: gr.Button, prompt_text: str) -> None:
    """Wire a Gradio Button directly into ChatInterface's streaming submission pipeline."""
    submit_fn = chatbot_interface._stream_fn if chatbot_interface.is_generator else chatbot_interface._submit_fn
    submit_wrapped = chatbot_interface._api_wrapper(chatbot_interface.fn, submit_fn)
    submit_wrapped.__name__ = "_submit_fn"

    btn.click(
        fn=lambda: prompt_text,
        inputs=None,
        outputs=[chatbot_interface.textbox],
        queue=False,
        api_visibility="undocumented",
    ).then(
        chatbot_interface._clear_and_save_textbox,
        inputs=[chatbot_interface.textbox],
        outputs=[chatbot_interface.textbox, chatbot_interface.saved_input],
        queue=False,
        api_visibility="undocumented",
    ).then(
        chatbot_interface._append_message_to_history,
        inputs=[chatbot_interface.saved_input, chatbot_interface.chatbot],
        outputs=[chatbot_interface.chatbot],
        queue=False,
        api_visibility="undocumented",
    ).then(
        fn=submit_wrapped,
        inputs=[chatbot_interface.saved_input, chatbot_interface.chatbot_state] + chatbot_interface.additional_inputs,
        outputs=[chatbot_interface.null_component, chatbot_interface.chatbot] + chatbot_interface.additional_outputs,
        concurrency_limit=chatbot_interface.concurrency_limit,
        show_progress=chatbot_interface.show_progress,
        api_visibility="undocumented",
    ).then(
        fn=lambda x: (x, x),
        inputs=[chatbot_interface.chatbot],
        outputs=[chatbot_interface.chatbot_state, chatbot_interface.chatbot_value],
        queue=False,
        api_visibility="undocumented",
    ).then(
        fn=lambda: gr.update(value=None, interactive=True),
        inputs=None,
        outputs=[chatbot_interface.textbox],
        queue=False,
        api_visibility="undocumented",
    )


def _build_student_tab(chat_fn: Callable) -> None:
    """Construct Tab 1: Student Chatroom with starter pills, chat stream, and bridge buttons."""
    with gr.TabItem("💬 Student Chatroom"):
        with gr.Row(elem_classes=["gemini-student-name-row"]):
            student_name_input = gr.Textbox(
                label="",
                show_label=False,
                placeholder="👤 Enter your full name (e.g. Alex Tan, Priya Sharma)",
                lines=1,
                scale=4,
                elem_id="student-name-box",
                elem_classes=["gemini-name-input"],
            )
        gr.HTML(
            '<div class="gemini-greeting-hero" id="gemini-greeting-hero">'
            '<div class="gemini-greeting-headline"><span class="gemini-text-gradient">Hello.</span>'
            "<span>Where would you like to start?</span></div>"
            '<div class="gemini-greeting-subtext">'
            "Analyze strategic choices, evaluate financial exhibits, or test your hypotheses on the case."
            "</div></div>"
        )
        with gr.Row(elem_classes=["gemini-starters-grid"]):
            btn_q1 = gr.Button("📊 Strategic Choices & Trade-offs", elem_classes=["gemini-starter-pill"])
            btn_q2 = gr.Button("📈 Financial & Valuation Analysis", elem_classes=["gemini-starter-pill"])
            btn_q3 = gr.Button("🎯 Sustainability & Scope 3 Targets", elem_classes=["gemini-starter-pill"])

        chatbot_widget = gr.Chatbot(
            value=None,
            height=600,
            show_label=False,
            elem_id="main-chatbot",
            elem_classes=["gemini-chatbot-stream"],
            layout="bubble",
        )
        chat_textbox = gr.Textbox(
            placeholder="Ask anything about the case study...",
            show_label=False,
            lines=1,
            max_lines=5,
            elem_id="gemini-prompt-input",
            submit_btn="↑",
        )
        chatbot_interface = gr.ChatInterface(
            fn=chat_fn,
            chatbot=chatbot_widget,
            textbox=chat_textbox,
            additional_inputs=[student_name_input],
            cache_examples=False,
        )
        student_session_state = gr.State(value={"last_mode_version": 0, "last_mode": ""})
        gr.Timer(value=2.5).tick(
            fn=poll_and_push_announcements,
            inputs=[chatbot_widget, student_session_state, student_name_input],
            outputs=[chatbot_widget, student_session_state],
        )
        with gr.Row(elem_classes=["gemini-hidden-quiz-row"]):
            quiz_btns = [
                gr.Button(ch, elem_id=f"quiz-choice-btn-{ch}", elem_classes=["gemini-hidden-bridge"])
                for ch in ("A", "B", "C", "D")
            ]

        starters = (
            (btn_q1, "What are the key strategic choices outlined in the case study?"),
            (btn_q2, "How would you evaluate the financial performance presented in the case study?"),
            (btn_q3, "What are the primary sustainability targets mentioned in the case study?"),
        )
        for btn, prompt_str in (*starters, *zip(quiz_btns, ("A", "B", "C", "D"), strict=True)):
            _bind_quick_submit_button(chatbot_interface, btn, prompt_str)


# [spec: QUIZ-003]
def _render_quiz_question_item(q: dict, idx: int, is_open: bool) -> str:
    """Render a single semantic <details>/<article> card for the Quiz Bank section."""
    topic = html.escape(str(q.get("topic", f"Question {idx}")))
    q_type = q.get("type", "mcq")
    type_label = "MCQ" if q_type == "mcq" else "Open-Ended"
    prompt_text = html.escape(str(q.get("prompt_text", "")))
    correct_opt = str(q.get("correct_option", "")).strip().upper()

    body_parts = [f'<p class="quiz-bank-prompt">{prompt_text}</p>']
    if q_type == "mcq" and q.get("options"):
        opt_html = []
        for opt in q["options"]:
            escaped_opt = html.escape(str(opt))
            letter = str(opt)[0].upper() if len(str(opt)) >= 2 and str(opt)[1] == ")" else ""
            is_correct = bool(letter and letter == correct_opt)
            pill_cls = "quiz-opt-pill quiz-opt-pill-correct" if is_correct else "quiz-opt-pill"
            badge_html = f"<strong>{html.escape(str(opt)[:2])}</strong> " if letter else ""
            text_html = html.escape(str(opt)[2:].strip()) if letter else escaped_opt
            correct_tag = '<span class="quiz-opt-correct-tag">✓ Correct Answer</span>' if is_correct else ""
            opt_html.append(f'<div class="{pill_cls}">{badge_html}<span>{text_html}</span>{correct_tag}</div>')
        body_parts.append(f'<div class="quiz-bank-options">{"".join(opt_html)}</div>')
    elif q.get("rubric_key_points"):
        pts = "".join(f"<li>{html.escape(str(pt))}</li>" for pt in q["rubric_key_points"])
        body_parts.append(
            f'<div class="quiz-bank-rubric"><strong>Answer Rubric Key Points:</strong><ul>{pts}</ul></div>'
        )

    footer_parts = []
    if q.get("hint"):
        footer_parts.append(f"<span><strong>Hint:</strong> {html.escape(str(q['hint']))}</span>")
    if q.get("official_answer"):
        footer_parts.append(f"<span><strong>Official Answer:</strong> {html.escape(str(q['official_answer']))}</span>")
    footer_html = f'<footer class="quiz-bank-footer">{"".join(footer_parts)}</footer>' if footer_parts else ""

    open_attr = " open" if is_open else ""
    return (
        f'<details class="quiz-bank-item"{open_attr}>'
        f'<summary class="quiz-bank-summary">'
        f'<span class="quiz-bank-qbadge">Q{idx}</span>'
        f'<span class="quiz-bank-type-pill">{type_label}</span>'
        f"<span>{topic}</span>"
        f"</summary>"
        f'<article class="quiz-bank-card">{"".join(body_parts)}{footer_html}</article>'
        f"</details>"
    )


# [spec: QUIZ-003]
# [spec: QUIZ-004]
def _render_admin_quiz_preview(case_name: str | None) -> str:
    """Render standalone Quiz Bank HTML section with status banner and collapsible question cards."""
    if not case_name:
        return (
            '<div class="quiz-bank-section">'
            '<div class="quiz-bank-banner">'
            '<span class="quiz-bank-status-pill is-warning">⏳ No Case Loaded</span>'
            '<span class="quiz-bank-source-meta">Select a case study above to inspect its quiz bank.</span>'
            "</div></div>"
        )

    status = get_quiz_validation_status(case_name)
    safe_case = html.escape(str(case_name))
    badge = html.escape(str(status["badge"]))
    source_meta = f'<span class="quiz-bank-source-meta">Source: <code>resource/{safe_case}/quiz.md</code></span>'

    if not status["is_valid"]:
        alert_msg = html.escape(str(status["alert_message"]))
        is_missing = badge.startswith("⚠️")
        err_items = "".join(f"<li>{html.escape(str(e))}</li>" for e in status.get("errors", []))
        err_list = f'<ul class="quiz-bank-errors">{err_items}</ul>' if err_items else ""
        if is_missing:
            remediation = (
                '<div class="quiz-bank-remediation">🔧 Remediation: See <code>docs/ADDING_A_CASE_STUDY.md</code></div>'
            )
        else:
            remediation = (
                '<div class="quiz-bank-remediation">🔧 Fix errors and verify: '
                f"<code>uv run python src/tools/validate_quiz.py --case {safe_case}</code></div>"
            )
        return (
            '<div class="quiz-bank-section is-error">'
            f'<div class="quiz-bank-banner"><span class="quiz-bank-status-pill is-error">{badge}</span>{source_meta}</div>'
            f'<p class="quiz-bank-error-lead">{alert_msg}</p>{err_list}{remediation}'
            "</div>"
        )

    questions = status.get("questions", [])
    items_html = "".join(_render_quiz_question_item(q, idx, idx == 1) for idx, q in enumerate(questions, start=1))
    return (
        '<div class="quiz-bank-section">'
        f'<div class="quiz-bank-banner"><span class="quiz-bank-status-pill">{badge}</span>{source_meta}</div>'
        f'<section class="quiz-bank-accordion" aria-label="Case Study Quiz Questions">{items_html}</section>'
        "</div>"
    )


# [spec: ADMIN-001]
# [spec: CACHE-003]
# [spec: QUIZ-003]
# [spec: QUIZ-004]
def _load_selected_case_study(selected_case):
    if not selected_case:
        return (
            "⚠️ Please select a valid business case study.",
            gr.update(),
            get_admin_status(),
            _render_admin_quiz_preview(selected_case),
            _build_startup_quiz_alert_html(),
        )
    app_state.active_case_study = selected_case
    get_or_create_cache(selected_case, force_refresh=True, ttl=app_state.cache_ttl)
    app_state.reload_case_quiz_banks()
    has_case_text = bool((app_state.case_text_context or "").strip())

    if has_case_text:
        app_state.session_locked = True
        app_state.notify_mode_change()
        cache_status_info = ""
        if app_state.active_cache_name:
            cache_status_info = f"\n\n⚡ **Gemini Context Cache ACTIVE** ({app_state.active_cache_name[-18:]}, TTL: {app_state.cache_ttl})"
        status = f"✅ Active Case Study set to: **{selected_case}** (Loaded {len(app_state.case_text_context):,} chars clean text context){cache_status_info}"
        locked_input = gr.update(
            interactive=False, label=f"🔒 Session ID (Locked — Class is Live: {app_state.session_id})"
        )
    else:
        app_state.session_locked = False
        app_state.active_cache_name = None
        app_state.cache_info = {}
        status = (
            f"❌ **Case Study Incomplete: {selected_case}** (Loaded 0 chars clean text context — "
            f"no readable PDFs, exhibits, or `extracted_context.txt` found in `resource/{selected_case}/`). "
            "Student Chatroom will remain blocked until case documents are added and reloaded."
        )
        locked_input = gr.update()

    quiz_val = get_quiz_validation_status(selected_case)
    if quiz_val["is_valid"]:
        status += f"\n\n{quiz_val['badge']}"
    else:
        status += (
            f"\n\n⚠️ **No verified quiz bank found for this case ({quiz_val['badge']}).** "
            f"Add or fix questions in `resource/{selected_case}/quiz.md` before running Quiz Mode."
        )
    return (
        status,
        locked_input,
        get_admin_status(),
        _render_admin_quiz_preview(selected_case),
        _build_startup_quiz_alert_html(),
    )


# [spec: ADMIN-001]
# [spec: ADMIN-002]
def _unlock_admin_panel(input_password):
    if verify_admin_password(input_password):
        return (
            gr.update(visible=True),
            "🔓 **Instructor controls unlocked successfully!**",
            gr.update(visible=False),
            get_admin_status(),
            gr.update(active=True),
        )
    # Skip updates on unmounted panels/timer so Gradio's pre-mount cache cannot replay stale hide state on retry
    return (
        gr.skip(),
        "❌ **Incorrect password. Access denied.**",
        gr.skip(),
        gr.skip(),
        gr.skip(),
    )


# [spec: ADMIN-001]
def _refresh_dashboard_if_unlocked(input_password):
    if verify_admin_password(input_password):
        return generate_live_dashboard_data()
    return gr.skip(), gr.skip(), gr.skip()


def _build_admin_mode_and_framework_controls(
    admin_summary_banner: gr.Markdown,
    admin_startup_quiz_alert: gr.HTML,
) -> None:
    """Build classroom mode radio, broadcast button, and custom framework controls."""
    gr.Markdown("## Classroom Mode & Configuration Controls")
    gr.Markdown(
        "*Select a mode below, then click **📢 Broadcast Mode to Students** to apply it live to all student browsers.*"
    )
    with gr.Row():
        with gr.Column(scale=1):
            mode_radio = gr.Radio(
                choices=app_state.get_mode_radio_choices(),
                value=app_state.active_mode,
                label="Active Pedagogical Mode",
            )
            mode_radio.change(
                fn=lambda m: (set_pending_mode(m), get_admin_status())[1],
                inputs=mode_radio,
                outputs=admin_summary_banner,
            )
            broadcast_btn = gr.Button("📢 Broadcast Mode to Students", variant="primary")
            broadcast_btn.click(
                fn=lambda: (confirm_mode_broadcast(), get_admin_status())[1],
                outputs=admin_summary_banner,
            ).then(
                fn=_build_startup_quiz_alert_html,
                outputs=admin_startup_quiz_alert,
                queue=False,
                show_progress="hidden",
            )

        with gr.Column(scale=1, visible=app_state.has_framework_modes()):
            fw_choices = list(app_state.get_all_frameworks().keys())
            framework_dropdown = gr.Dropdown(
                choices=fw_choices,
                value=app_state.selected_framework
                if app_state.selected_framework in fw_choices
                else (fw_choices[0] if fw_choices else None),
                label="Active Analysis Framework",
            )
            fw_status = gr.Markdown()
            framework_dropdown.change(
                fn=lambda fw: (update_framework(fw), get_admin_status()),
                inputs=framework_dropdown,
                outputs=[fw_status, admin_summary_banner],
            )
            with gr.Accordion("➕ Add Custom Framework", open=False):
                custom_fw_name = gr.Textbox(label="Framework Name (e.g. McKinsey 7S)")
                custom_fw_desc = gr.Textbox(label="Framework Analysis Instructions", lines=2)
                add_fw_btn = gr.Button("Add & Select Framework")
                add_fw_btn.click(
                    fn=lambda n, d: (*add_custom_fw(n, d), get_admin_status()),
                    inputs=[custom_fw_name, custom_fw_desc],
                    outputs=[framework_dropdown, fw_status, admin_summary_banner],
                )


def _build_admin_system_settings(
    load_case_btn: gr.Button,
    case_study_radio: gr.Radio,
    case_status_msg: gr.Markdown,
    admin_summary_banner: gr.Markdown,
    quiz_preview_html: gr.HTML,
    admin_startup_quiz_alert: gr.HTML,
) -> gr.Image:
    """Build TTL, Model ID, Session ID, cache reload, and QR code controls."""
    gr.Markdown("---")
    gr.Markdown("## System & Context Settings")
    with gr.Row():
        with gr.Column():
            ttl_input = gr.Textbox(
                label="1. Context Caching Time / TTL (e.g. 30s, 300s, 12600s)",
                value=app_state.cache_ttl,
                placeholder="e.g. 30s, 300s, 12600s",
            )
            ttl_input.change(fn=update_ttl, inputs=ttl_input, outputs=admin_summary_banner)
            model_input = gr.Textbox(label="2. Gemini Model ID", value=app_state.model_id)
            model_input.change(fn=update_model_id, inputs=model_input, outputs=admin_summary_banner)
            session_id_input = gr.Textbox(
                label="3. Active Classroom Session Identifier (e.g. Session_1, Section_A)",
                value=app_state.session_id,
                info="⚠️ Set this BEFORE loading the case study. It will lock once the class is live to protect analytics.",
            )

            def _update_session_id(s_id):
                if not getattr(app_state, "session_locked", False):
                    app_state.session_id = s_id.strip() if s_id and s_id.strip() else "Session_1"
                return get_admin_status()

            session_id_input.change(fn=_update_session_id, inputs=session_id_input, outputs=admin_summary_banner)
            load_case_btn.click(
                fn=_load_selected_case_study,
                inputs=case_study_radio,
                outputs=[
                    case_status_msg,
                    session_id_input,
                    admin_summary_banner,
                    quiz_preview_html,
                    admin_startup_quiz_alert,
                ],
            )
            refresh_btn = gr.Button("🔄 Reload Case Text Context", variant="primary")
            refresh_status = gr.Markdown()
            refresh_btn.click(fn=refresh_cache_action, outputs=refresh_status).then(
                fn=_build_startup_quiz_alert_html,
                outputs=admin_startup_quiz_alert,
                queue=False,
                show_progress="hidden",
            )

        with gr.Column():
            gr.Markdown("### Classroom Projection QR Code")
            qr_file = Path("./static/classroom_qr.png")
            qr_image = gr.Image(
                value=str(qr_file) if qr_file.exists() else None,
                label="Scan to Open Chatbot",
            )
    return qr_image


def _build_admin_tab() -> gr.Image:
    """Construct Tab 2: Password-Protected Instructor Admin Panel."""
    with gr.TabItem("🔐 Instructor Admin Panel"):
        gr.Markdown("## 🔐 Instructor Authentication & Case Management")
        admin_startup_quiz_alert = gr.HTML(
            value=_build_startup_quiz_alert_html,
            elem_id="admin-startup-quiz-alert",
        )
        with gr.Row(elem_id="admin-auth-row") as admin_auth_row:
            admin_pass_box = gr.Textbox(
                label="Enter Instructor Password",
                type="password",
                placeholder="Enter instructor password and press Enter or Unlock...",
                scale=3,
            )
            admin_unlock_btn = gr.Button("Unlock Admin Controls", variant="primary", scale=1)
        admin_auth_status = gr.Markdown("🔒 Enter instructor password to unlock controls.")

        with gr.Column(visible=False, elem_id="admin-control-center") as admin_content_panel:
            admin_summary_banner = gr.Markdown(value=get_admin_status())
            gr.Markdown("## 📚 Business Case Study Selection")
            gr.Markdown(
                "Select the business case study folder to use for this classroom session. Text context will be loaded on demand. *(Note: **EcoBrew** is a built-in fictional demonstration case)*."
            )
            with gr.Row():
                case_study_radio = gr.Radio(
                    choices=get_available_case_studies(),
                    value=app_state.active_case_study,
                    label="Available Case Studies in resource/ Directory",
                    scale=3,
                )
                load_case_btn = gr.Button("🚀 Load Selected Case Study", variant="primary", scale=1)
            case_status_msg = gr.Markdown(
                value=f"Active Case Study: **{app_state.active_case_study or 'Not Initialized (Select and click Load)'}**"
            )

            gr.Markdown("---")
            gr.Markdown("## 🎯 Case Study Quiz Bank")
            gr.Markdown(
                "Inspect verified assessment questions, answer keys, and student card previews from the selected case study's `quiz.md` before starting Quiz Mode."
            )
            quiz_preview_html = gr.HTML(value=_render_admin_quiz_preview(app_state.active_case_study))
            case_study_radio.change(
                fn=lambda sc: (_render_admin_quiz_preview(sc), _build_startup_quiz_alert_html()),
                inputs=case_study_radio,
                outputs=[quiz_preview_html, admin_startup_quiz_alert],
                queue=False,
                show_progress="hidden",
            )

            gr.Markdown("---")
            gr.Markdown("## 📊 Live Class Dashboard")
            live_student_count = gr.Markdown(
                value="🟢 **Students Active (last 5 min):** `0`  \n*Auto-refreshing every 10s...*"
            )
            with gr.Row():
                live_activity_plot = gr.Plot(label="📈 Student Activity Timeline (Messages / Min)", scale=1)
                live_latency_plot = gr.Plot(label="⚡ Response Latency Tracker (Seconds)", scale=1)
            gr.Markdown("---")
            _build_admin_mode_and_framework_controls(admin_summary_banner, admin_startup_quiz_alert)
            qr_image = _build_admin_system_settings(
                load_case_btn,
                case_study_radio,
                case_status_msg,
                admin_summary_banner,
                quiz_preview_html,
                admin_startup_quiz_alert,
            )

        dashboard_timer = gr.Timer(value=10.0, active=False)
        dashboard_timer.tick(
            fn=generate_live_dashboard_data,
            outputs=[live_student_count, live_activity_plot, live_latency_plot],
        )

        unlock_outputs = [
            admin_content_panel,
            admin_auth_status,
            admin_auth_row,
            admin_summary_banner,
            dashboard_timer,
        ]
        dashboard_outputs = [live_student_count, live_activity_plot, live_latency_plot]
        for trigger in (admin_unlock_btn.click, admin_pass_box.submit):
            trigger(
                fn=_unlock_admin_panel,
                inputs=admin_pass_box,
                outputs=unlock_outputs,
                queue=False,
                show_progress="hidden",
            ).then(
                fn=_refresh_dashboard_if_unlocked,
                inputs=admin_pass_box,
                outputs=dashboard_outputs,
                show_progress="hidden",
            ).then(
                fn=_build_startup_quiz_alert_html,
                outputs=admin_startup_quiz_alert,
                queue=False,
                show_progress="hidden",
            )
    return qr_image


# [spec: UI-004]
# [spec: UI-005]
# [spec: ADMIN-001]
def build_gradio_demo(chat_fn: Callable) -> gr.Blocks:
    """Assemble and return the full Gradio Blocks interface."""
    with gr.Blocks(title="Jarvis AI — Business Case Copilot") as demo_app:
        gr.HTML(CLIENT_HERO_HTML)
        with gr.Tabs():
            _build_student_tab(chat_fn)
            qr_image = _build_admin_tab()

        gr.HTML(
            '<div class="classroom-footer">'
            "<p>© 2026 Sukti Ghosh and Prithis Samaddar. All rights reserved. | Jarvis Classroom Case Study Companion</p>"
            "</div>"
        )
        demo_app.load(js=DEMO_LOAD_JS)
        demo_app.load(
            fn=lambda: str(Path("./static/classroom_qr.png")) if Path("./static/classroom_qr.png").exists() else None,
            outputs=qr_image,
        )
    return demo_app
