# [spec: UI-001]
# [spec: UI-002]
"""
Dark Theme comprehensive CSS overrides for Gradio containers, tables, inputs, chips, event cards, and omnibar.
"""

CSS_DARK_THEME = """
/* Complete, harmonious Gemini Dark Mode */
html.dark, body.dark, gradio-app.dark, html.dark gradio-app, .gradio-container.dark, [data-theme='dark'] {
    background-color: #131314 !important;
    background-image: none !important;
    color: #E3E3E3 !important;
}

html.dark .gemini-nav-bar,
body.dark .gemini-nav-bar,
.gradio-container.dark .gemini-nav-bar,
[data-theme='dark'] .gemini-nav-bar,
.dark .gemini-nav-bar {
    background: #1E1F20 !important;
    border: 1px solid #3C4043 !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
}

html.dark .gemini-sparkle-avatar,
body.dark .gemini-sparkle-avatar,
.gradio-container.dark .gemini-sparkle-avatar,
[data-theme='dark'] .gemini-sparkle-avatar,
.dark .gemini-sparkle-avatar {
    background: #2D2F31 !important;
}

html.dark .gemini-brand-title,
body.dark .gemini-brand-title,
.gradio-container.dark .gemini-brand-title,
[data-theme='dark'] .gemini-brand-title,
.dark .gemini-brand-title {
    color: #F8FAFC !important;
}

html.dark .gemini-brand-badge,
body.dark .gemini-brand-badge,
.gradio-container.dark .gemini-brand-badge,
[data-theme='dark'] .gemini-brand-badge,
.dark .gemini-brand-badge {
    background: #28354A !important;
    color: #8AB4F8 !important;
    border: 1px solid #3B82F6 !important;
}

html.dark .gemini-case-chip,
body.dark .gemini-case-chip,
.gradio-container.dark .gemini-case-chip,
[data-theme='dark'] .gemini-case-chip,
.dark .gemini-case-chip {
    background: #2D2F31 !important;
    border: 1px solid #484C50 !important;
    color: #E3E3E3 !important;
}

html.dark .gemini-case-chip span,
body.dark .gemini-case-chip span,
.gradio-container.dark .gemini-case-chip span,
[data-theme='dark'] .gemini-case-chip span,
.dark .gemini-case-chip span {
    color: #E3E3E3 !important;
}

html.dark .gemini-mode-chip,
body.dark .gemini-mode-chip,
.gradio-container.dark .gemini-mode-chip,
[data-theme='dark'] .gemini-mode-chip,
.dark .gemini-mode-chip {
    background: #1E293B !important;
    border: 1px solid #4F46E5 !important;
    color: #C7D2FE !important;
}

html.dark .gemini-mode-chip span,
body.dark .gemini-mode-chip span,
.gradio-container.dark .gemini-mode-chip span,
[data-theme='dark'] .gemini-mode-chip span,
.dark .gemini-mode-chip span {
    color: #C7D2FE !important;
}

html.dark .gemini-session-chip,
body.dark .gemini-session-chip,
.gradio-container.dark .gemini-session-chip,
[data-theme='dark'] .gemini-session-chip,
.dark .gemini-session-chip {
    background: #064E3B !important;
    border: 1px solid #059669 !important;
    color: #A7F3D0 !important;
}

html.dark .gemini-session-chip span,
body.dark .gemini-session-chip span,
.gradio-container.dark .gemini-session-chip span,
[data-theme='dark'] .gemini-session-chip span,
.dark .gemini-session-chip span {
    color: #A7F3D0 !important;
}

html.dark .gemini-theme-toggle-btn,
body.dark .gemini-theme-toggle-btn,
.gradio-container.dark .gemini-theme-toggle-btn,
[data-theme='dark'] .gemini-theme-toggle-btn,
.dark .gemini-theme-toggle-btn {
    background: #2D2F31 !important;
    border: 1.5px solid #484C50 !important;
    color: #E3E3E3 !important;
}

html.dark .gemini-theme-toggle-btn:hover,
body.dark .gemini-theme-toggle-btn:hover,
.gradio-container.dark .gemini-theme-toggle-btn:hover,
[data-theme='dark'] .gemini-theme-toggle-btn:hover,
.dark .gemini-theme-toggle-btn:hover {
    background: #3C4043 !important;
    border-color: #8AB4F8 !important;
    color: #F8FAFC !important;
}

html.dark button[role="tab"],
body.dark button[role="tab"],
.gradio-container.dark button[role="tab"],
[data-theme='dark'] button[role="tab"] {
    color: #9AA0A6 !important;
}

html.dark button[role="tab"].selected,
body.dark button[role="tab"].selected,
.gradio-container.dark button[role="tab"].selected,
[data-theme='dark'] button[role="tab"].selected,
html.dark button[role="tab"][aria-selected="true"],
body.dark button[role="tab"][aria-selected="true"],
.gradio-container.dark button[role="tab"][aria-selected="true"],
[data-theme='dark'] button[role="tab"][aria-selected="true"] {
    background: #28354A !important;
    color: #8AB4F8 !important;
    border-color: #3B82F6 !important;
}

html.dark .gemini-greeting-headline,
body.dark .gemini-greeting-headline,
.gradio-container.dark .gemini-greeting-headline,
[data-theme='dark'] .gemini-greeting-headline {
    color: #F8FAFC !important;
}

html.dark .gemini-greeting-subtext,
body.dark .gemini-greeting-subtext,
.gradio-container.dark .gemini-greeting-subtext,
[data-theme='dark'] .gemini-greeting-subtext {
    color: #9AA0A6 !important;
}

/* Student Name Input Dark Mode Overrides */
html.dark #student-name-box input,
body.dark #student-name-box input,
.gradio-container.dark #student-name-box input,
[data-theme='dark'] #student-name-box input,
.dark #student-name-box input,
html.dark #student-name-box textarea,
body.dark #student-name-box textarea,
.gradio-container.dark #student-name-box textarea,
[data-theme='dark'] #student-name-box textarea,
.dark #student-name-box textarea,
html.dark .gemini-name-input input,
body.dark .gemini-name-input input,
.gradio-container.dark .gemini-name-input input,
[data-theme='dark'] .gemini-name-input input,
.dark .gemini-name-input input,
html.dark .gemini-name-input textarea,
body.dark .gemini-name-input textarea,
.gradio-container.dark .gemini-name-input textarea,
[data-theme='dark'] .gemini-name-input textarea,
.dark .gemini-name-input textarea {
    background: #1E1F20 !important;
    color: #F8FAFC !important;
    border: 1.5px solid #484C50 !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3) !important;
}

html.dark #student-name-box input::placeholder,
body.dark #student-name-box input::placeholder,
.gradio-container.dark #student-name-box input::placeholder,
[data-theme='dark'] #student-name-box input::placeholder,
.dark #student-name-box input::placeholder,
html.dark #student-name-box textarea::placeholder,
body.dark #student-name-box textarea::placeholder,
.gradio-container.dark #student-name-box textarea::placeholder,
[data-theme='dark'] #student-name-box textarea::placeholder,
.dark #student-name-box textarea::placeholder,
html.dark .gemini-name-input input::placeholder,
body.dark .gemini-name-input input::placeholder,
.gradio-container.dark .gemini-name-input input::placeholder,
[data-theme='dark'] .gemini-name-input input::placeholder,
.dark .gemini-name-input input::placeholder,
html.dark .gemini-name-input textarea::placeholder,
body.dark .gemini-name-input textarea::placeholder,
.gradio-container.dark .gemini-name-input textarea::placeholder,
[data-theme='dark'] .gemini-name-input textarea::placeholder,
.dark .gemini-name-input textarea::placeholder {
    color: #9AA0A6 !important;
    opacity: 1 !important;
    white-space: nowrap !important;
    text-overflow: ellipsis !important;
    overflow: hidden !important;
}

html.dark #student-name-box input::-webkit-input-placeholder,
body.dark #student-name-box input::-webkit-input-placeholder,
.gradio-container.dark #student-name-box input::-webkit-input-placeholder,
[data-theme='dark'] #student-name-box input::-webkit-input-placeholder,
.dark #student-name-box input::-webkit-input-placeholder,
html.dark #student-name-box textarea::-webkit-input-placeholder,
body.dark #student-name-box textarea::-webkit-input-placeholder,
.gradio-container.dark #student-name-box textarea::-webkit-input-placeholder,
[data-theme='dark'] #student-name-box textarea::-webkit-input-placeholder,
.dark #student-name-box textarea::-webkit-input-placeholder,
html.dark .gemini-name-input input::-webkit-input-placeholder,
body.dark .gemini-name-input input::-webkit-input-placeholder,
.gradio-container.dark .gemini-name-input input::-webkit-input-placeholder,
[data-theme='dark'] .gemini-name-input input::-webkit-input-placeholder,
.dark .gemini-name-input input::-webkit-input-placeholder,
html.dark .gemini-name-input textarea::-webkit-input-placeholder,
body.dark .gemini-name-input textarea::-webkit-input-placeholder,
.gradio-container.dark .gemini-name-input textarea::-webkit-input-placeholder,
[data-theme='dark'] .gemini-name-input textarea::-webkit-input-placeholder,
.dark .gemini-name-input textarea::-webkit-input-placeholder {
    color: #9AA0A6 !important;
    opacity: 1 !important;
    white-space: nowrap !important;
    text-overflow: ellipsis !important;
    overflow: hidden !important;
}

html.dark #student-name-box input:focus,
body.dark #student-name-box input:focus,
.gradio-container.dark #student-name-box input:focus,
[data-theme='dark'] #student-name-box input:focus,
.dark #student-name-box input:focus,
html.dark #student-name-box textarea:focus,
body.dark #student-name-box textarea:focus,
.gradio-container.dark #student-name-box textarea:focus,
[data-theme='dark'] #student-name-box textarea:focus,
.dark #student-name-box textarea:focus,
html.dark .gemini-name-input input:focus,
body.dark .gemini-name-input input:focus,
.gradio-container.dark .gemini-name-input input:focus,
[data-theme='dark'] .gemini-name-input input:focus,
.dark .gemini-name-input input:focus,
html.dark .gemini-name-input textarea:focus,
body.dark .gemini-name-input textarea:focus,
.gradio-container.dark .gemini-name-input textarea:focus,
[data-theme='dark'] .gemini-name-input textarea:focus,
.dark .gemini-name-input textarea:focus {
    background: #242628 !important;
    border-color: #8AB4F8 !important;
    color: #FFFFFF !important;
    box-shadow: 0 0 0 3.5px rgba(138, 180, 248, 0.22) !important;
}

/* Starter Pills Dark Mode */
html.dark .gemini-starter-pill,
body.dark .gemini-starter-pill,
.gradio-container.dark .gemini-starter-pill,
[data-theme='dark'] .gemini-starter-pill,
.dark .gemini-starter-pill {
    background: #1E1F20 !important;
    border: 1px solid #3C4043 !important;
    color: #E3E3E3 !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2) !important;
}

html.dark .gemini-starter-pill:hover,
body.dark .gemini-starter-pill:hover,
.gradio-container.dark .gemini-starter-pill:hover,
[data-theme='dark'] .gemini-starter-pill:hover,
.dark .gemini-starter-pill:hover {
    background: #2D2F31 !important;
    border-color: #8AB4F8 !important;
    color: #8AB4F8 !important;
    box-shadow: 0 4px 12px rgba(138, 180, 248, 0.2) !important;
}

/* Event Cards & Wait Cards Dark Mode */
html.dark .gemini-event-card,
body.dark .gemini-event-card,
.gradio-container.dark .gemini-event-card,
[data-theme='dark'] .gemini-event-card,
.dark .gemini-event-card {
    background: #1E1F20 !important;
    border-color: #3C4043 !important;
    border-left-color: #8AB4F8 !important;
    color: #F8FAFC !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
}

html.dark .gemini-event-header,
body.dark .gemini-event-header,
.gradio-container.dark .gemini-event-header,
[data-theme='dark'] .gemini-event-header,
.dark .gemini-event-header {
    border-bottom-color: #2D2F31 !important;
}

html.dark .gemini-event-badge,
body.dark .gemini-event-badge,
.gradio-container.dark .gemini-event-badge,
[data-theme='dark'] .gemini-event-badge,
.dark .gemini-event-badge {
    background: #28354A !important;
    color: #8AB4F8 !important;
    border-color: #3B82F6 !important;
}

html.dark .gemini-event-title,
body.dark .gemini-event-title,
.gradio-container.dark .gemini-event-title,
[data-theme='dark'] .gemini-event-title,
.dark .gemini-event-title {
    color: #F8FAFC !important;
}

html.dark .gemini-event-body,
body.dark .gemini-event-body,
.gradio-container.dark .gemini-event-body,
[data-theme='dark'] .gemini-event-body,
.dark .gemini-event-body {
    color: #E3E3E3 !important;
}

html.dark .gemini-event-hint,
body.dark .gemini-event-hint,
.gradio-container.dark .gemini-event-hint,
[data-theme='dark'] .gemini-event-hint,
.dark .gemini-event-hint {
    color: #9AA0A6 !important;
}

html.dark .gemini-wait-card,
body.dark .gemini-wait-card,
.gradio-container.dark .gemini-wait-card,
[data-theme='dark'] .gemini-wait-card,
.dark .gemini-wait-card {
    background: #2B2111 !important;
    border-color: #F59E0B !important;
}

html.dark .gemini-wait-title,
body.dark .gemini-wait-title,
.gradio-container.dark .gemini-wait-title,
[data-theme='dark'] .gemini-wait-title,
.dark .gemini-wait-title {
    color: #FCD34D !important;
}

html.dark .gemini-wait-body,
body.dark .gemini-wait-body,
.gradio-container.dark .gemini-wait-body,
[data-theme='dark'] .gemini-wait-body,
.dark .gemini-wait-body {
    color: #FDE68A !important;
}

/* Chat Messages & Markdown Dark Mode */
html.dark .chatbot .message-row.user-row .message,
body.dark .chatbot .message-row.user-row .message,
.gradio-container.dark .chatbot .message-row.user-row .message,
html.dark .chatbot div[data-testid="user"] > div,
body.dark .chatbot div[data-testid="user"] > div,
.gradio-container.dark .chatbot div[data-testid="user"] > div,
html.dark .chatbot .user.message,
body.dark .chatbot .user.message,
.gradio-container.dark .chatbot .user.message,
html.dark .chatbot .message.user,
body.dark .chatbot .message.user,
.gradio-container.dark .chatbot .message.user {
    background: #28354A !important;
    color: #E8F0FE !important;
    border-color: #3B82F6 !important;
}

html.dark .chatbot .message-row.bot-row .message,
body.dark .chatbot .message-row.bot-row .message,
.gradio-container.dark .chatbot .message-row.bot-row .message,
html.dark .chatbot div[data-testid="bot"] > div,
body.dark .chatbot div[data-testid="bot"] > div,
.gradio-container.dark .chatbot div[data-testid="bot"] > div,
html.dark .chatbot .bot.message,
body.dark .chatbot .bot.message,
.gradio-container.dark .chatbot .bot.message,
html.dark .chatbot .message.bot,
body.dark .chatbot .message.bot,
.gradio-container.dark .chatbot .message.bot {
    color: #E3E3E3 !important;
}

html.dark .chatbot .prose h1,
html.dark .chatbot .prose h2,
html.dark .chatbot .prose h3,
body.dark .chatbot .prose h1,
body.dark .chatbot .prose h2,
body.dark .chatbot .prose h3,
.gradio-container.dark .chatbot .prose h1,
.gradio-container.dark .chatbot .prose h2,
.gradio-container.dark .chatbot .prose h3 {
    color: #F8FAFC !important;
}

html.dark .chatbot .prose table,
body.dark .chatbot .prose table,
.gradio-container.dark .chatbot .prose table {
    background: #1E1F20 !important;
    border-color: #3C4043 !important;
}

html.dark .chatbot .prose th,
body.dark .chatbot .prose th,
.gradio-container.dark .chatbot .prose th {
    background: #2D2F31 !important;
    color: #E3E3E3 !important;
    border-color: #3C4043 !important;
}

html.dark .chatbot .prose td,
body.dark .chatbot .prose td,
.gradio-container.dark .chatbot .prose td {
    color: #C4C7C5 !important;
    border-color: #2D2F31 !important;
}

html.dark .chatbot .prose blockquote,
body.dark .chatbot .prose blockquote,
.gradio-container.dark .chatbot .prose blockquote {
    background: #1E1F20 !important;
    border-left-color: #8AB4F8 !important;
    color: #E3E3E3 !important;
}

/* Chat Box Container Dark Mode */
html.dark #main-chatbot,
body.dark #main-chatbot,
.gradio-container.dark #main-chatbot,
[data-theme='dark'] #main-chatbot,
.dark #main-chatbot {
    background: #18191B !important;
    border: 1.5px solid #3C4043 !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35) !important;
}

/* Floating Omnibar Dark Mode */
html.dark .chat-interface > div:last-child,
body.dark .chat-interface > div:last-child,
.gradio-container.dark .chat-interface > div:last-child,
[data-theme='dark'] .chat-interface > div:last-child,
.dark .chat-interface > div:last-child,
html.dark div.group:has(#gemini-prompt-input),
body.dark div.group:has(#gemini-prompt-input),
.gradio-container.dark div.group:has(#gemini-prompt-input),
[data-theme='dark'] div.group:has(#gemini-prompt-input),
.dark div.group:has(#gemini-prompt-input) {
    background: linear-gradient(180deg, rgba(19, 19, 20, 0) 0%, #131314 35%, #131314 100%) !important;
}

html.dark .chat-interface form,
body.dark .chat-interface form,
.gradio-container.dark .chat-interface form,
[data-theme='dark'] .chat-interface form,
.dark .chat-interface form,
html.dark .chat-interface > div:last-child > div,
body.dark .chat-interface > div:last-child > div,
.gradio-container.dark .chat-interface > div:last-child > div,
[data-theme='dark'] .chat-interface > div:last-child > div,
.dark .chat-interface > div:last-child > div,
html.dark .chat-interface div:has(> #gemini-prompt-input),
body.dark .chat-interface div:has(> #gemini-prompt-input),
.gradio-container.dark .chat-interface div:has(> #gemini-prompt-input),
[data-theme='dark'] .chat-interface div:has(> #gemini-prompt-input),
.dark .chat-interface div:has(> #gemini-prompt-input),
html.dark form:has(> #gemini-prompt-input),
body.dark form:has(> #gemini-prompt-input),
.gradio-container.dark form:has(> #gemini-prompt-input),
[data-theme='dark'] form:has(> #gemini-prompt-input),
.dark form:has(> #gemini-prompt-input),
html.dark div.form:has(> #gemini-prompt-input),
body.dark div.form:has(> #gemini-prompt-input),
.gradio-container.dark div.form:has(> #gemini-prompt-input),
[data-theme='dark'] div.form:has(> #gemini-prompt-input),
.dark div.form:has(> #gemini-prompt-input) {
    background: #1E1F20 !important;
    border-color: #3C4043 !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
}

html.dark .chat-interface form:focus-within,
body.dark .chat-interface form:focus-within,
.gradio-container.dark .chat-interface form:focus-within,
[data-theme='dark'] .chat-interface form:focus-within,
.dark .chat-interface form:focus-within,
html.dark .chat-interface > div:last-child > div:focus-within,
body.dark .chat-interface > div:last-child > div:focus-within,
.gradio-container.dark .chat-interface > div:last-child > div:focus-within,
[data-theme='dark'] .chat-interface > div:last-child > div:focus-within,
.dark .chat-interface > div:last-child > div:focus-within,
html.dark form:has(> #gemini-prompt-input):focus-within,
body.dark form:has(> #gemini-prompt-input):focus-within,
.gradio-container.dark form:has(> #gemini-prompt-input):focus-within,
[data-theme='dark'] form:has(> #gemini-prompt-input):focus-within,
.dark form:has(> #gemini-prompt-input):focus-within,
html.dark div.form:has(> #gemini-prompt-input):focus-within,
body.dark div.form:has(> #gemini-prompt-input):focus-within,
.gradio-container.dark div.form:has(> #gemini-prompt-input):focus-within,
[data-theme='dark'] div.form:has(> #gemini-prompt-input):focus-within,
.dark div.form:has(> #gemini-prompt-input):focus-within {
    border-color: #8AB4F8 !important;
    box-shadow: 0 4px 24px rgba(138, 180, 248, 0.25) !important;
}
html.dark .chat-interface textarea,
body.dark .chat-interface textarea,
.gradio-container.dark .chat-interface textarea,
[data-theme='dark'] .chat-interface textarea,
.dark .chat-interface textarea,
html.dark #gemini-prompt-input textarea,
body.dark #gemini-prompt-input textarea,
.gradio-container.dark #gemini-prompt-input textarea,
[data-theme='dark'] #gemini-prompt-input textarea,
.dark #gemini-prompt-input textarea,
html.dark .chat-interface input,
body.dark .chat-interface input,
.gradio-container.dark .chat-interface input,
[data-theme='dark'] .chat-interface input,
.dark .chat-interface input,
html.dark #gemini-prompt-input input,
body.dark #gemini-prompt-input input,
.gradio-container.dark #gemini-prompt-input input,
[data-theme='dark'] #gemini-prompt-input input,
.dark #gemini-prompt-input input {
    color: #F8FAFC !important;
    -webkit-text-fill-color: #F8FAFC !important;
}
html.dark .chat-interface textarea::placeholder,
body.dark .chat-interface textarea::placeholder,
.gradio-container.dark .chat-interface textarea::placeholder,
[data-theme='dark'] .chat-interface textarea::placeholder,
.dark .chat-interface textarea::placeholder,
html.dark #gemini-prompt-input textarea::placeholder,
body.dark #gemini-prompt-input textarea::placeholder,
.gradio-container.dark #gemini-prompt-input textarea::placeholder,
[data-theme='dark'] #gemini-prompt-input textarea::placeholder,
.dark #gemini-prompt-input textarea::placeholder {
    color: #9AA0A6 !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #9AA0A6 !important;
}
html.dark .chat-interface textarea::-webkit-input-placeholder,
body.dark .chat-interface textarea::-webkit-input-placeholder,
.gradio-container.dark .chat-interface textarea::-webkit-input-placeholder,
[data-theme='dark'] .chat-interface textarea::-webkit-input-placeholder,
.dark .chat-interface textarea::-webkit-input-placeholder,
html.dark #gemini-prompt-input textarea::-webkit-input-placeholder,
body.dark #gemini-prompt-input textarea::-webkit-input-placeholder,
.gradio-container.dark #gemini-prompt-input textarea::-webkit-input-placeholder,
[data-theme='dark'] #gemini-prompt-input textarea::-webkit-input-placeholder,
.dark #gemini-prompt-input textarea::-webkit-input-placeholder {
    color: #9AA0A6 !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #9AA0A6 !important;
}
/* Quiz Option Pills Dark Mode */
html.dark .quiz-opt-pill,
body.dark .quiz-opt-pill,
.gradio-container.dark .quiz-opt-pill,
[data-theme='dark'] .quiz-opt-pill {
    background: #1E1F20 !important;
    border-color: #3C4043 !important;
    color: #F8FAFC !important;
}
html.dark .quiz-opt-pill:hover,
body.dark .quiz-opt-pill:hover,
.gradio-container.dark .quiz-opt-pill:hover,
[data-theme='dark'] .quiz-opt-pill:hover {
    border-color: #8AB4F8 !important;
    background: #2D2F31 !important;
}
html.dark .quiz-opt-pill strong,
body.dark .quiz-opt-pill strong,
.gradio-container.dark .quiz-opt-pill strong,
[data-theme='dark'] .quiz-opt-pill strong {
    color: #8AB4F8 !important;
}
html.dark .classroom-footer,
body.dark .classroom-footer,
.gradio-container.dark .classroom-footer {
    border-top-color: #2D2F31 !important;
    color: #9AA0A6 !important;
}
html.dark .quiz-bank-section,
body.dark .quiz-bank-section,
.gradio-container.dark .quiz-bank-section,
[data-theme='dark'] .quiz-bank-section {
    background: #18191B !important;
    border-color: #3C4043 !important;
}
html.dark details.quiz-bank-item,
body.dark details.quiz-bank-item,
.gradio-container.dark details.quiz-bank-item,
[data-theme='dark'] details.quiz-bank-item {
    background: #131314 !important;
    border-color: #3C4043 !important;
}
html.dark summary.quiz-bank-summary:hover,
body.dark summary.quiz-bank-summary:hover,
.gradio-container.dark summary.quiz-bank-summary:hover,
[data-theme='dark'] summary.quiz-bank-summary:hover {
    background: #2D2F31 !important;
}
html.dark article.quiz-bank-card,
body.dark article.quiz-bank-card,
.gradio-container.dark article.quiz-bank-card,
[data-theme='dark'] article.quiz-bank-card {
    background: #1E1F20 !important;
    border-top-color: #3C4043 !important;
}
html.dark .quiz-bank-options .quiz-opt-pill.quiz-opt-pill-correct,
body.dark .quiz-bank-options .quiz-opt-pill.quiz-opt-pill-correct,
.gradio-container.dark .quiz-bank-options .quiz-opt-pill.quiz-opt-pill-correct,
[data-theme='dark'] .quiz-bank-options .quiz-opt-pill.quiz-opt-pill-correct,
html.dark .quiz-bank-options .quiz-opt-pill.quiz-opt-pill-correct:hover,
body.dark .quiz-bank-options .quiz-opt-pill.quiz-opt-pill-correct:hover,
.gradio-container.dark .quiz-bank-options .quiz-opt-pill.quiz-opt-pill-correct:hover,
[data-theme='dark'] .quiz-bank-options .quiz-opt-pill.quiz-opt-pill-correct:hover {
    background: #064E3B !important;
    border: 2px solid #10B981 !important;
    color: #ECFDF5 !important;
    font-weight: 600 !important;
    box-shadow: inset 4px 0 0 #34D399, 0 2px 8px rgba(16, 185, 129, 0.18) !important;
}
html.dark .quiz-bank-options .quiz-opt-pill.quiz-opt-pill-correct strong,
body.dark .quiz-bank-options .quiz-opt-pill.quiz-opt-pill-correct strong,
.gradio-container.dark .quiz-bank-options .quiz-opt-pill.quiz-opt-pill-correct strong,
[data-theme='dark'] .quiz-bank-options .quiz-opt-pill.quiz-opt-pill-correct strong {
    color: #34D399 !important;
}
html.dark .quiz-opt-correct-tag,
body.dark .quiz-opt-correct-tag,
.gradio-container.dark .quiz-opt-correct-tag,
[data-theme='dark'] .quiz-opt-correct-tag {
    background: #047857 !important;
    color: #ECFDF5 !important;
    border: 1px solid #34D399 !important;
}
html.dark .quiz-bank-alert-banner,
body.dark .quiz-bank-alert-banner,
.gradio-container.dark .quiz-bank-alert-banner,
[data-theme='dark'] .quiz-bank-alert-banner,
html.dark .quiz-bank-section.is-error,
body.dark .quiz-bank-section.is-error,
.gradio-container.dark .quiz-bank-section.is-error,
[data-theme='dark'] .quiz-bank-section.is-error {
    background: #2C1215 !important;
    border: 2px solid #EF4444 !important;
    border-left: 6px solid #F87171 !important;
    color: #FEE2E2 !important;
    box-shadow: 0 4px 16px rgba(239, 68, 68, 0.22) !important;
}
html.dark .quiz-bank-status-pill.is-error,
body.dark .quiz-bank-status-pill.is-error,
.gradio-container.dark .quiz-bank-status-pill.is-error,
[data-theme='dark'] .quiz-bank-status-pill.is-error {
    background: #DC2626 !important;
    border-color: #F87171 !important;
    color: #FFFFFF !important;
}
html.dark .quiz-bank-alert-sub,
body.dark .quiz-bank-alert-sub,
.gradio-container.dark .quiz-bank-alert-sub,
[data-theme='dark'] .quiz-bank-alert-sub,
html.dark .quiz-bank-error-lead,
body.dark .quiz-bank-error-lead,
.gradio-container.dark .quiz-bank-error-lead,
[data-theme='dark'] .quiz-bank-error-lead,
html.dark .quiz-bank-alert-case-title,
body.dark .quiz-bank-alert-case-title,
.gradio-container.dark .quiz-bank-alert-case-title,
[data-theme='dark'] .quiz-bank-alert-case-title,
html.dark .quiz-bank-errors,
body.dark .quiz-bank-errors,
.gradio-container.dark .quiz-bank-errors,
[data-theme='dark'] .quiz-bank-errors,
html.dark .quiz-bank-remediation,
body.dark .quiz-bank-remediation,
.gradio-container.dark .quiz-bank-remediation,
[data-theme='dark'] .quiz-bank-remediation {
    color: #FEE2E2 !important;
}
html.dark .quiz-bank-section.is-error .quiz-bank-errors code,
body.dark .quiz-bank-section.is-error .quiz-bank-errors code,
.gradio-container.dark .quiz-bank-section.is-error .quiz-bank-errors code,
[data-theme='dark'] .quiz-bank-section.is-error .quiz-bank-errors code,
html.dark .quiz-bank-alert-banner .quiz-bank-errors code,
body.dark .quiz-bank-alert-banner .quiz-bank-errors code,
.gradio-container.dark .quiz-bank-alert-banner .quiz-bank-errors code,
[data-theme='dark'] .quiz-bank-alert-banner .quiz-bank-errors code,
html.dark .quiz-bank-remediation code,
body.dark .quiz-bank-remediation code,
.gradio-container.dark .quiz-bank-remediation code,
[data-theme='dark'] .quiz-bank-remediation code {
    background: #450A0A !important;
    border-color: #F87171 !important;
    color: #FEE2E2 !important;
}
"""
