# Pedagogical Modes (Modes 1–2) Specifications

## MODE-001: Mode 1 Standard QA Pedagogical Mode

While `qa` mode is active, the chatbot engine shall provide concise, case-grounded answers and enforce single-question focus.

Acceptance Criteria:
- AC-MODE-001.1: While `qa` mode is active, when a student asks a case question, the chatbot engine shall generate a grounded response under 175 words and conclude with a follow-up question.
- AC-MODE-001.2: While `qa` mode is active, if a student asks 2 or more distinct questions in one turn, then the chatbot engine shall answer only the first question and append a single-question note.
- AC-MODE-001.3: If an obsolete mode identifier such as citation mode is set, then the application state shall fall back to `qa` mode.

## MODE-002: Mode 2 Interactive Quiz and Assessment Pedagogical Mode

While `quiz` mode is active, the chatbot engine shall orchestrate structured 5-question assessments, mid-session mode switch announcements, and post-quiz completion locks.

Acceptance Criteria:
- AC-MODE-002.1: When `quiz` mode is activated at session start or via a mid-session broadcast, the chatbot engine shall display the quiz announcement card and post Question 1.
- AC-MODE-002.2: While `quiz` mode is active, when a student submits a quiz response, the chatbot engine shall return targeted grading feedback and omit general discussion question headers.
- AC-MODE-002.3: While a student has completed all 5 quiz questions in `quiz` mode, when the student submits any subsequent message, the chatbot engine shall return the post-quiz waiting card.
