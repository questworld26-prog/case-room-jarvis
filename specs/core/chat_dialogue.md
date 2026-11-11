# Core Chat Dialogue & Session Guardrail Specifications

## CHAT-001: Input Validation and Pre-Flight Guardrail Interception

When a student submits a chat message, the chatbot engine shall validate pre-flight session preconditions before invoking the language model.

Acceptance Criteria:
- AC-CHAT-001.1: If the submitted message is empty or contains only whitespace, then the chatbot engine shall return an empty string without invoking the language model.
- AC-CHAT-001.2: If no active case study is selected or the loaded case context is empty, then the chatbot engine shall yield a warning prompt instructing the instructor to load a case study.
- AC-CHAT-001.3: If the student name field is blank, whitespace, or set to the default anonymous label, then the chatbot engine shall yield a warning requiring the student to enter a name.
- AC-CHAT-001.4: When a student submits an oversized string or an emoji-only message, the dialogue builder shall construct a valid request payload without raising an exception.

## CHAT-002: Instant Greeting and Welcome Card Fast-Path

When a student initiates a session or sends a conversational greeting, the chatbot engine shall serve deterministic HTML event cards without calling the language model.

Acceptance Criteria:
- AC-CHAT-002.1: When a student submits a short conversational greeting, the greeting regex classifier shall match the greeting while ignoring substantive case questions.
- AC-CHAT-002.2: When a greeting is matched in a non-quiz mode, the chatbot engine shall return the mode-aware instant greeting card in under 0.5 seconds.
- AC-CHAT-002.3: When a chat session initializes, the UI factory shall render the initial welcome card and strip that welcome card before building language model history.
- AC-CHAT-002.4: While interactive quiz mode is active, when a student sends a quiz starter phrase, the chatbot engine shall intercept the message and post Question 1 unless another mode is active.

## CHAT-003: Dialogue History Normalization and Mermaid Sanitization

The dialogue utility module shall normalize multimodal Gradio history structures into alternating user-model turns and sanitize Mermaid diagrams.

Acceptance Criteria:
- AC-CHAT-003.1: When extracting text from Gradio message payloads, the dialogue utility module shall normalize strings, content-block lists, and dictionaries into plain strings.
- AC-CHAT-003.2: When cleaning chat history for the language model, the dialogue utility module shall remove injected HTML broadcast banners and welcome cards.
- AC-CHAT-003.3: When building Gemini content payloads, the dialogue utility module shall merge consecutive same-role turns so that user and model roles strictly alternate.
- AC-CHAT-003.4: When a model response contains a Mermaid code block, the dialogue utility module shall strip the Mermaid block so Gradio renders valid markdown.

## CHAT-004: Scope Boundaries, Output Limits, Visual Fallbacks and Concurrency

While processing student prompts across concurrent sessions, the chatbot engine shall enforce case scope boundaries, output word caps, static chart fallbacks, and session isolation.

Acceptance Criteria:
- AC-CHAT-004.1: If a student asks a question unrelated to the active case study, then the chatbot engine shall decline the off-topic request and redirect to the case.
- AC-CHAT-004.2: When generating a response, the chatbot engine shall cap output length within the configured word ceiling without mid-sentence truncation.
- AC-CHAT-004.3: When a student requests a visual chart or graph, the chatbot engine shall append the matching static chart image path to the response.
- AC-CHAT-004.4: While 50 concurrent students or simulated student personas interact simultaneously, the chatbot engine shall isolate session states and reject adversarial or off-topic prompts.
