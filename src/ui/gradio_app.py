"""
Gradio Blocks application layout and interactive component wiring for Jarvis Chatbot.
Separates UI component assembly from the core streaming chat engine.
"""

from collections.abc import Callable
from pathlib import Path

import gradio as gr

from config import PRE_AUTHORED_QUIZ_BANKS, app_state, get_available_case_studies
from core.cache_manager import get_or_create_cache
from core.quiz_parser import get_quiz_validation_status
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
def _render_admin_quiz_preview(case_name: str | None) -> str:
    """Render markdown status and interactive HTML card previews for the admin inspection accordion."""
    if not case_name:
        return "*Select and load a case study above to inspect its quiz bank.*"
    status = get_quiz_validation_status(case_name)
    if not status["is_valid"]:
        lines = [
            f"### {status['badge']}",
            f"> ⚠️ {status['alert_message']}",
            "",
            f"To enable curated Quiz Mode for **{case_name}**, create `resource/{case_name}/quiz.md`.",
        ]
        if status.get("errors"):
            lines.append("\n**Validation Diagnostics:**")
            for err in status["errors"]:
                lines.append(f"- ❌ `{err}`")
        return "\n".join(lines)

    lines = [
        f"### {status['badge']}",
        f"Found **{status['total_questions']} verified questions** in `resource/{case_name}/quiz.md`.",
        "",
        "---",
        "#### 👁️ Student Question Card Previews",
    ]
    for idx, card_html in enumerate(status["preview_cards"], start=1):
        lines.append(f"\n<details open><summary><b>Question #{idx} Card</b></summary>\n\n{card_html}\n\n</details>")
    return "\n".join(lines)


# [spec: ADMIN-001]
# [spec: QUIZ-003]
def _load_selected_case_study(selected_case):
    if not selected_case:
        return (
            "⚠️ Please select a valid business case study.",
            gr.update(),
            get_admin_status(),
            _render_admin_quiz_preview(selected_case),
        )
    app_state.active_case_study = selected_case
    app_state.session_locked = True
    get_or_create_cache(selected_case, force_refresh=True, ttl=app_state.cache_ttl)
    app_state.reload_case_quiz_banks()
    app_state.notify_mode_change()
    cache_status_info = ""
    if app_state.active_cache_name:
        cache_status_info = (
            f"\n\n⚡ **Gemini Context Cache ACTIVE** ({app_state.active_cache_name[-18:]}, TTL: {app_state.cache_ttl})"
        )
    status = f"✅ Active Case Study set to: **{selected_case}** (Loaded {len(app_state.case_text_context):,} chars clean text context){cache_status_info}"
    quiz_val = get_quiz_validation_status(selected_case)
    if quiz_val["is_valid"]:
        status += f"\n\n{quiz_val['badge']}"
    else:
        status += (
            f"\n\n⚠️ **No verified quiz bank found for this case ({quiz_val['badge']}).** "
            f"Add or fix questions in `resource/{selected_case}/quiz.md` before running Quiz Mode."
        )
    locked_input = gr.update(interactive=False, label=f"🔒 Session ID (Locked — Class is Live: {app_state.session_id})")
    return status, locked_input, get_admin_status(), _render_admin_quiz_preview(selected_case)


def _unlock_admin_panel(input_password):
    if verify_admin_password(input_password):
        return (
            gr.update(open=True, visible=True),
            "🔓 **Instructor controls unlocked successfully!**",
            gr.update(visible=False),
            get_admin_status(),
        )
    return (
        gr.update(open=False, visible=False),
        "❌ **Incorrect password. Access denied.**",
        gr.update(visible=True),
        get_admin_status(),
    )


def _build_admin_mode_and_framework_controls(admin_summary_banner: gr.Markdown) -> None:
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
    quiz_preview_md: gr.Markdown,
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
                outputs=[case_status_msg, session_id_input, admin_summary_banner, quiz_preview_md],
            )
            refresh_btn = gr.Button("🔄 Reload Case Text Context", variant="primary")
            refresh_status = gr.Markdown()
            refresh_btn.click(fn=refresh_cache_action, outputs=refresh_status)

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
        with gr.Row() as admin_auth_row:
            admin_pass_box = gr.Textbox(
                label="Enter Instructor Password",
                type="password",
                placeholder="Enter instructor password and press Enter or Unlock...",
                scale=3,
            )
            admin_unlock_btn = gr.Button("Unlock Admin Controls", variant="primary", scale=1)
        admin_auth_status = gr.Markdown("🔒 Enter instructor password to unlock controls.")

        with gr.Accordion("⚙️ Instructor Control Center", open=False, visible=False) as admin_content_panel:
            admin_summary_banner = gr.Markdown(value=get_admin_status())
            gr.Markdown("## 📚 Business Case Study Selection")
            gr.Markdown(
                "Select the business case study folder to use for this classroom session. Text context will be loaded on demand."
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
            with gr.Accordion("🎯 Case Study Quiz Bank & Live Card Preview", open=False):
                quiz_preview_md = gr.Markdown(value=_render_admin_quiz_preview(app_state.active_case_study))

            case_study_radio.change(
                fn=_render_admin_quiz_preview,
                inputs=case_study_radio,
                outputs=quiz_preview_md,
            )
            gr.Markdown("---")
            gr.Markdown("## 📊 Live Class Dashboard")
            live_student_count = gr.Markdown(
                value="🟢 **Students Active (last 5 min):** `0`  \n*Auto-refreshing every 10s...*"
            )
            with gr.Row():
                live_activity_plot = gr.Plot(label="📈 Student Activity Timeline (Messages / Min)", scale=1)
                live_latency_plot = gr.Plot(label="⚡ Response Latency Tracker (Seconds)", scale=1)
            dashboard_timer = gr.Timer(value=10.0)
            dashboard_timer.tick(
                fn=generate_live_dashboard_data,
                outputs=[live_student_count, live_activity_plot, live_latency_plot],
            )
            gr.Markdown("---")
            _build_admin_mode_and_framework_controls(admin_summary_banner)
            qr_image = _build_admin_system_settings(
                load_case_btn, case_study_radio, case_status_msg, admin_summary_banner, quiz_preview_md
            )

        admin_unlock_btn.click(
            fn=_unlock_admin_panel,
            inputs=admin_pass_box,
            outputs=[admin_content_panel, admin_auth_status, admin_auth_row, admin_summary_banner],
        )
        admin_pass_box.submit(
            fn=_unlock_admin_panel,
            inputs=admin_pass_box,
            outputs=[admin_content_panel, admin_auth_status, admin_auth_row, admin_summary_banner],
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
