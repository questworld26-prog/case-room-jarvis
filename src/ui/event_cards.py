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
Event cards, announcement formatting, and greeting response logic for Jarvis Chatbot.
"""

import html
import re

from config import app_state

GREETING_PATTERN = re.compile(
    r"^(hi|hello|hey|good\s+morning|good\s+afternoon|good\s+evening|howdy|hi\s+jarvis|hello\s+jarvis|hey\s+jarvis|help|hi\s+there|hello\s+there)[\s!.,?]*$",
    re.IGNORECASE,
)


# [spec: CHAT-002]
# [spec: UI-005]
# [spec: ADMIN-001]
def format_event_card(badge_text: str, title_text: str, body_text: str, hint_text: str) -> str:
    """Render a clean, modern Gemini-style announcement card for in-chat events (Light & Dark theme aware)."""
    raw_case = app_state.active_case_study or "EcoBrew"
    raw_mode = app_state.get_mode_display_name() if hasattr(app_state, "get_mode_display_name") else "Standard Q&A"
    case_name = html.escape(str(raw_case), quote=True)
    mode_label = html.escape(str(raw_mode), quote=True)
    return (
        f'<div class="gemini-event-card" data-case-name="{case_name}" data-mode-label="{mode_label}">'
        f'<div class="gemini-event-header">'
        f'<span class="gemini-event-badge">📢 {badge_text}</span>'
        f'<span class="gemini-event-title">{title_text}</span>'
        f"</div>"
        f'<div class="gemini-event-body">'
        f"{body_text}"
        f"</div>"
        f'<div class="gemini-event-hint">'
        f"{hint_text}"
        f"</div>"
        f"</div>"
    )


# [spec: MODE-002]
# [spec: QUIZ-001]
# [spec: UI-005]
def format_post_quiz_wait_card() -> str:
    """Render a theme-aware waiting banner after a student completes the quiz."""
    return (
        '<div class="gemini-wait-card">'
        '<div class="gemini-wait-title">⏳ Waiting for Prof</div>'
        '<div class="gemini-wait-body">Thank you for completing the quiz! Please wait for your Prof to switch modes before asking further questions.</div>'
        "</div>"
    )


# [spec: CHAT-002]
# [spec: MODE-001]
# [spec: MODE-002]
# [spec: ADMIN-001]
def get_instant_greeting(student_name: str, message: str) -> str:
    """Generate mode-aware instant greeting response via the active ModePlugin."""
    raw_name = (
        student_name.strip()
        if student_name and student_name.strip() and student_name not in ["Anonymous Student", "Anonymous"]
        else "there"
    )
    name_str = html.escape(raw_name, quote=True)
    raw_case = app_state.active_case_study or "EcoBrew"
    case_name = html.escape(str(raw_case), quote=True)
    plugin = app_state.get_active_plugin()
    return plugin.event_card_fn(app_state, name_str, case_name, format_event_card)


# [spec: CHAT-002]
def get_initial_welcome_card() -> str:
    """Generate the initial onboarding welcome card displayed in the chat window on first load."""
    return format_event_card(
        badge_text="WELCOME",
        title_text="Welcome to Jarvis • Case Study AI Companion",
        body_text=(
            "Hello and welcome! I'm <b>Jarvis</b>, your AI companion for today's business case study discussion.<br><br>"
            "<b>📌 How to Use This App:</b><br>"
            "Please enter your <b>Full Name</b> in the box above and start asking questions related to the business case."
        ),
        hint_text="💡 Enter your name above and submit your first question below to get started!",
    )
