"""
Standard Open-Source Pedagogical Mode Plugins (Mode 1: Standard Q&A, Mode 2: Interactive Quiz).
"""

from collections.abc import Callable

from core.plugin_protocol import ModePlugin


# [spec: MODE-001]
def get_qa_instruction(state: object) -> str:
    """Return system prompt instruction for Mode 1: Standard Q&A."""
    case_name = getattr(state, "active_case_study", None) or "the business case"
    return (
        "Mode: Standard Q&A\n"
        "Provide direct, clear, concise, and factual answers strictly under 175 words based on the case documents. "
        f"CASE SUMMARY / DETAILS REQUEST: If the student asks for a case overview, summary, or details (e.g. 'Explain case deets', 'Summarize the whole case', 'What is this about?'), provide an informative 2-3 sentence overview covering company background, core strategic dilemma, and key operational or commercial goals of {case_name} without deflecting into a greeting. "
        "MANDATORY MULTI-QUESTION RULE: If the student asks 2 or more separate questions in a single prompt (e.g. multiple '?'), select ONLY the FIRST question to answer. "
        "State 'Answering your question regarding [Topic]:', answer ONLY that single question, and append 'Note: Please ask one question at a time.' at the end. "
        "Do NOT answer the other questions. If the student asked only 1 single question (even if compound with clauses), answer it directly without adding any disclaimer. "
        "Do NOT include any page numbers, page citations, document citations, or source references (e.g. NEVER write '(Page 1)', '(Page 2)', or '[Document X]') unless the student explicitly asks for citations."
    )


# [spec: MODE-001]
# [spec: CHAT-002]
def get_qa_event_card(
    state: object,
    name_str: str,
    case_name: str,
    format_card_fn: Callable[..., str],
) -> str:
    """Render in-chat live mode switch event card for Mode 1: Standard Q&A."""
    return format_card_fn(
        badge_text="LIVE MODE SWITCH",
        title_text=f"Standard Q&A Mode • {case_name}",
        body_text=f"Hello {name_str}! I'm Jarvis, your AI companion for the <b>{case_name}</b> case study. What question or topic would you like to explore today?",
        hint_text="💡 Type your question below to get started!",
    )


# [spec: MODE-002]
def get_quiz_instruction(state: object) -> str:
    """Return system prompt instruction for Mode 2: Interactive Quiz & Assessment."""
    return (
        "Mode: Interactive Quiz & Knowledge Check\n"
        "Evaluate the student's input against the case details. If the student answers a quiz question or provides an input, "
        "give constructive feedback and scoring in 1-2 sentences, and ask the next targeted quiz question about specific case metrics, targets, or strategic decisions. "
        "DO NOT include any '💡 Discussion Question' or general discussion question in this mode; only provide feedback and ask the next quiz question. "
        "Total response must remain under 200 words."
    )


# [spec: MODE-002]
# [spec: CHAT-002]
def get_quiz_event_card(
    state: object,
    name_str: str,
    case_name: str,
    format_card_fn: Callable[..., str],
) -> str:
    """Render in-chat live mode switch event card for Mode 2: Interactive Quiz."""
    q1 = state.get_first_quiz_question() if hasattr(state, "get_first_quiz_question") else ""
    return format_card_fn(
        badge_text="LIVE MODE SWITCH",
        title_text=f"Interactive Quiz & Knowledge Check • {case_name}",
        body_text=q1.replace("\n", "<br>"),
        hint_text="💡 Click an option pill above or submit your response below!",
    )


# [spec: MODE-001]
# [spec: MODE-002]
def register_plugins(
    registry: dict[str, ModePlugin],
    frameworks: dict[str, str],
) -> None:
    """Register Mode 1 (Standard Q&A) and Mode 2 (Interactive Quiz) into MODE_REGISTRY."""
    registry["qa"] = ModePlugin(
        key="qa",
        radio_label="Mode 1 — Standard Q&A (Default)",
        order=1,
        requires_framework=False,
        max_history_turns=3,
        max_output_tokens=280,
        display_name_fn=lambda _state: "Mode 1 — Standard Q&A (Default)",
        instruction_fn=get_qa_instruction,
        event_card_fn=get_qa_event_card,
    )
    registry["quiz"] = ModePlugin(
        key="quiz",
        radio_label="Mode 2 — Interactive Quiz & Assessment",
        order=2,
        requires_framework=False,
        max_history_turns=3,
        max_output_tokens=280,
        display_name_fn=lambda _state: "Mode 2 — Interactive Quiz & Assessment",
        instruction_fn=get_quiz_instruction,
        event_card_fn=get_quiz_event_card,
    )
