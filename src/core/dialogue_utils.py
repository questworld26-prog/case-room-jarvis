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
Dialogue and text utilities for the business case chatbot.
Handles text extraction from Gradio structures, Mermaid diagram sanitization,
LLM history cleaning, message normalization, and MCQ input parsing.
"""

import re

from google.genai import types


# [spec: CHAT-003]
def extract_text_content(content) -> str:
    """Safely extract plain text from various Gradio chat history structures."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict):
                if "text" in item and isinstance(item["text"], str):
                    text_parts.append(item["text"])
                elif "value" in item and isinstance(item["value"], str):
                    text_parts.append(item["value"])
        return " ".join(text_parts)
    elif isinstance(content, dict):
        if "text" in content and isinstance(content["text"], str):
            return content["text"]
        elif "value" in content and isinstance(content["value"], str):
            return content["value"]
    return str(content) if content is not None else ""


# [spec: CHAT-003]
def sanitize_mermaid(text: str) -> str:
    """Completely strip mermaid text blocks to prevent Gradio v11 syntax errors."""
    if "```mermaid" not in text:
        return text
    return re.sub(r"```mermaid\s*\n.*?```", "", text, flags=re.DOTALL).strip()


# [spec: CHAT-002]
# [spec: CHAT-003]
def clean_history_for_llm(raw_text: str) -> str:
    """
    Sanitizes conversation history before feeding to Gemini LLM.
    Strips raw HTML announcement cards and CSS artifacts so the LLM never echoes back UI templates.
    """
    if not raw_text:
        return ""
    if (
        "LIVE MODE SWITCH" in raw_text
        or "LIVE CLASS UPDATE" in raw_text
        or "WELCOME" in raw_text
        or "<div style=" in raw_text
    ):
        text_only = re.sub(r"<[^>]+>", " ", raw_text)
        text_only = " ".join(text_only.split())
        # If the card embedded an active Quiz question, keep the question text for context
        if "Quiz Question" in text_only:
            m = re.search(r"(Quiz Question #\d+:[^💡]+)", text_only)
            if m:
                return m.group(1).strip()
        # Discard generic mode switch/welcome announcements from LLM history
        return ""
    return re.sub(r"<[^>]+>", "", raw_text).strip()


# [spec: CHAT-001]
# [spec: CHAT-003]
def build_clean_gemini_contents(recent_history: list, current_user_prompt: str) -> list:
    """
    Constructs strictly alternating (user -> model -> user -> model) dialogue for Gemini,
    ensuring no raw HTML clutter, duplicate consecutive roles, or orphan cards reach the LLM.
    """
    formatted_contents = []
    last_role = None

    for turn in recent_history:
        if hasattr(turn, "role"):
            raw_role = "user" if turn.role == "user" else "model"
            raw_content = turn.content
        elif isinstance(turn, dict):
            raw_role = "user" if turn.get("role") == "user" else "model"
            raw_content = turn.get("content")
        else:
            continue

        extracted = extract_text_content(raw_content)
        clean_text = clean_history_for_llm(extracted)
        if not clean_text:
            continue

        if raw_role == last_role and len(formatted_contents) > 0:
            existing_part = formatted_contents[-1].parts[0].text
            formatted_contents[-1] = types.Content(
                role=raw_role, parts=[types.Part.from_text(text=f"{existing_part}\n\n{clean_text}")]
            )
        else:
            formatted_contents.append(types.Content(role=raw_role, parts=[types.Part.from_text(text=clean_text)]))
            last_role = raw_role

    # Ensure conversation history begins with a user turn
    while formatted_contents and formatted_contents[0].role != "user":
        formatted_contents.pop(0)

    # Attach current user turn
    if formatted_contents and formatted_contents[-1].role == "user":
        existing_user_text = formatted_contents[-1].parts[0].text
        formatted_contents[-1] = types.Content(
            role="user", parts=[types.Part.from_text(text=f"{existing_user_text}\n\n{current_user_prompt}")]
        )
    else:
        formatted_contents.append(types.Content(role="user", parts=[types.Part.from_text(text=current_user_prompt)]))

    return formatted_contents


# [spec: QUIZ-001]
def parse_mcq_choice(user_text: str) -> str | None:
    """
    Robust normalization for MCQ inputs.
    Accepts 'a', 'b', 'c', 'd' (case-insensitive) and '1', '2', '3', '4' (1=A, 2=B, 3=C, 4=D).
    Also extracts explicit patterns like 'Option B', 'Choice B', 'B)', '(B)', 'Answer: C'.
    Guards against general English sentences starting with a/b/c/d (e.g., 'Beyond brand reputation...', 'Can you explain...').
    """
    if not user_text:
        return None
    raw = user_text.strip().lower()

    # 1. Direct single letter or number match
    direct_map = {"a": "A", "b": "B", "c": "C", "d": "D", "1": "A", "2": "B", "3": "C", "4": "D"}
    if raw in direct_map:
        return direct_map[raw]

    # 2. Match isolated single letter/number with punctuation e.g. "b.", "(b)", "b)", "[b]"
    m_isolated = re.fullmatch(r"[\(\[\{]?([a-d1-4])[\)\]\}\.\:\-]?\s*", raw)
    if m_isolated:
        return direct_map.get(m_isolated.group(1))

    # 3. Match explicit prefix patterns like 'option a', 'choice b', 'answer is c', 'answer: d'
    # Must NOT match general vocabulary words starting with a/b/c/d
    m_explicit = re.match(
        r"^(?:option|choice|answer\s*is|answer\s*[:\-])\s*[\(\[\{]?([a-d1-4])[\)\]\}]?\b",
        raw,
    )
    if m_explicit:
        return direct_map.get(m_explicit.group(1))

    # 4. If the message starts with an isolated letter followed by space/separator (e.g. "B - Logistics", "B) Over 85%")
    m_leading = re.match(r"^([a-d1-4])[\)\.\:\s\-]\s*", raw)
    if m_leading:
        return direct_map.get(m_leading.group(1))

    return None
