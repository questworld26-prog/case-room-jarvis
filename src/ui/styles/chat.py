# [spec: UI-002]
# [spec: UI-005]
"""
Chat styles: Unboxed stream, User/Assistant message pills, Event Cards, Markdown & Table styling, Floating Omnibar, and Quiz Pills.
"""

CSS_CHAT = """
/* Clearly Bounded Chatbot Stream Surface (High Visibility in Light & Dark Modes) */
#main-chatbot {
    border: 1.5px solid var(--gemini-chat-border) !important;
    background: var(--gemini-chat-bg) !important;
    border-radius: 18px !important;
    box-shadow: var(--gemini-chat-shadow) !important;
    padding: 12px 16px !important;
    margin-top: 6px !important;
    margin-bottom: 8px !important;
}

#main-chatbot > .wrapper,
#main-chatbot .bubble-wrap,
#main-chatbot .message-wrap,
.chatbot > .wrapper,
.chatbot .bubble-wrap,
.chatbot .message-wrap {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    padding: 0 !important;
}

#main-chatbot,
.chatbot,
div[data-testid="chatbot"] {
    height: calc(100dvh - 240px) !important;
    min-height: 380px !important;
    max-height: none !important;
    transition: height 0.25s ease !important;
}

/* Compact Empty State so Hero + Starters + Omnibar fit in 100dvh with zero scroll */
body.gemini-chat-empty #main-chatbot,
body.gemini-chat-empty .chatbot,
body.gemini-chat-empty div[data-testid="chatbot"],
#main-chatbot.gemini-chat-empty {
    height: calc(100dvh - 420px) !important;
    min-height: 100px !important;
}

/* Hide unwanted bot avatar headers */
#main-chatbot header,
#main-chatbot .header,
#main-chatbot label,
#main-chatbot .bot-avatar,
#main-chatbot .bot-icon,
#main-chatbot button[aria-label="Chatbot"],
.chatbot .bot-label,
.chatbot .avatar,
.chatbot .bot-avatar,
.chatbot .bot-icon,
.chatbot .chat-message .avatar,
.chatbot .message-row.bot .avatar,
.chatbot .message-row .avatar,
.chatbot span.avatar,
.chatbot button.avatar,
.chatbot .header,
.chatbot .component-header,
.chatbot label,
div[data-testid="chatbot"] header,
div[data-testid="chatbot"] label,
div[data-testid="chatbot"] .header,
div[data-testid="chatbot"] [class*="avatar"],
div[data-testid="chatbot"] [class*="bot-label"],
div[data-testid="chatbot"] [class*="label"],
div[data-testid="chatbot"] button[aria-label="Chatbot"],
.chat-interface header,
.chat-interface .header,
.chat-interface label {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* User Message Pill */
.chatbot .message-row.user-row,
.chatbot .message-row:has(.user),
.chatbot div[data-testid="user"],
.chatbot .user.message,
.chatbot .message.user {
    justify-content: flex-end !important;
}

.chatbot .message-row.user-row .message,
.chatbot div[data-testid="user"] > div,
.chatbot .user.message,
.chatbot .message.user {
    background: var(--gemini-badge-bg) !important;
    color: var(--gemini-title-color) !important;
    border: 1px solid var(--gemini-badge-border) !important;
    border-radius: 20px 20px 4px 20px !important;
    padding: 12px 18px !important;
    max-width: 82% !important;
    margin-left: auto !important;
    box-shadow: 0 1px 3px rgba(66, 133, 244, 0.08) !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    line-height: 1.55 !important;
}

/* Assistant Message — Borderless Flow */
.chatbot .message-row.bot-row,
.chatbot .message-row:has(.bot),
.chatbot div[data-testid="bot"],
.chatbot .bot.message,
.chatbot .message.bot {
    justify-content: flex-start !important;
}

.chatbot .message-row.bot-row .message,
.chatbot div[data-testid="bot"] > div,
.chatbot .bot.message,
.chatbot .message.bot {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: var(--gemini-text-main) !important;
    padding: 8px 4px !important;
    max-width: 100% !important;
    margin-right: auto !important;
    font-size: 15.5px !important;
    line-height: 1.72 !important;
    font-weight: 400 !important;
}

/* Theme-Aware In-Chat Event & Mode Switch Cards */
.gemini-event-card {
    background: var(--gemini-card-bg) !important;
    border: 1px solid var(--gemini-card-border) !important;
    border-left: 4px solid var(--gemini-card-accent) !important;
    border-radius: 14px !important;
    padding: 16px 20px !important;
    margin: 14px 0 !important;
    box-shadow: var(--gemini-nav-shadow) !important;
    color: var(--gemini-card-title) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

.gemini-event-header {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    margin-bottom: 8px !important;
    border-bottom: 1px solid var(--gemini-card-divider) !important;
    padding-bottom: 8px !important;
    flex-wrap: wrap !important;
}

.gemini-event-badge {
    background: var(--gemini-badge-bg) !important;
    color: var(--gemini-badge-color) !important;
    border: 1px solid var(--gemini-badge-border) !important;
    font-weight: 700 !important;
    font-size: 11px !important;
    padding: 3px 9px !important;
    border-radius: 999px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

.gemini-event-title {
    font-weight: 600 !important;
    color: var(--gemini-card-title) !important;
    font-size: 14.5px !important;
}

.gemini-event-body {
    font-size: 14px !important;
    line-height: 1.6 !important;
    color: var(--gemini-card-body) !important;
    margin-top: 6px !important;
}

.gemini-event-hint {
    margin-top: 10px !important;
    font-size: 12.5px !important;
    color: var(--gemini-card-hint) !important;
    font-style: italic !important;
}

/* Theme-Aware Post-Quiz Wait Card */
.gemini-wait-card {
    border: 2px solid var(--gemini-wait-border) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    background: var(--gemini-wait-bg) !important;
    margin: 8px 0 !important;
}

.gemini-wait-title {
    font-weight: 700 !important;
    color: var(--gemini-wait-title) !important;
    font-size: 15px !important;
    margin-bottom: 8px !important;
}

.gemini-wait-body {
    color: var(--gemini-wait-body) !important;
    font-size: 14px !important;
    line-height: 1.5 !important;
}

/* Theme-Aware Quiz Horizontal Divider */
hr.gemini-quiz-divider,
.chatbot .prose hr {
    border: 0 !important;
    border-top: 1px solid var(--gemini-hr-color) !important;
    margin: 14px 0 !important;
}

/* Markdown Typography & Table Styling */
.chatbot .prose h1, .chatbot .prose h2, .chatbot .prose h3 {
    color: var(--gemini-title-color) !important;
    font-weight: 700 !important;
    letter-spacing: -0.3px !important;
    margin-top: 14px !important;
    margin-bottom: 6px !important;
}

.chatbot .prose p {
    margin-top: 6px !important;
    margin-bottom: 10px !important;
    line-height: 1.72 !important;
}

.chatbot .prose ul, .chatbot .prose ol {
    margin: 8px 0 !important;
    padding-left: 22px !important;
}

.chatbot .prose li {
    margin-bottom: 4px !important;
    line-height: 1.65 !important;
}

.chatbot .prose table {
    border-collapse: separate !important;
    border-spacing: 0 !important;
    border: 1px solid var(--gemini-card-border) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    background: var(--gemini-card-bg) !important;
    font-size: 13.5px !important;
    margin: 14px 0 !important;
    width: 100% !important;
    box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04) !important;
}

.chatbot .prose th {
    background: var(--gemini-case-chip-bg) !important;
    color: var(--gemini-card-title) !important;
    font-weight: 600 !important;
    padding: 10px 14px !important;
    border-bottom: 1px solid var(--gemini-card-border) !important;
    text-align: left !important;
}

.chatbot .prose td {
    padding: 10px 14px !important;
    border-bottom: 1px solid var(--gemini-card-divider) !important;
    color: var(--gemini-card-body) !important;
}

.chatbot .prose tr:last-child td {
    border-bottom: none !important;
}

.chatbot .prose blockquote {
    border-left: 3.5px solid var(--gemini-card-accent) !important;
    background: var(--gemini-sparkle-bg) !important;
    border-radius: 0 8px 8px 0 !important;
    padding: 10px 16px !important;
    margin: 12px 0 !important;
    color: var(--gemini-card-body) !important;
}

/* Floating Bottom Omnibar */
.chat-interface > div:last-child,
div.group:has(#gemini-prompt-input) {
    position: sticky !important;
    bottom: 0px !important;
    background: var(--gemini-prompt-footer-grad) !important;
    padding: 10px 0 8px 0 !important;
    z-index: 20 !important;
    border: none !important;
    box-shadow: none !important;
}

div.group:has(#gemini-prompt-input) > .styler,
div.group:has(#gemini-prompt-input) .row {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.chat-interface form,
.chat-interface > div:last-child > div,
.chat-interface div:has(> #gemini-prompt-input),
form:has(> #gemini-prompt-input),
div.form:has(> #gemini-prompt-input) {
    max-width: 800px !important;
    width: 100% !important;
    margin: 0 auto !important;
    background: var(--gemini-prompt-bg) !important;
    border: 1.5px solid var(--gemini-prompt-border) !important;
    border-radius: 32px !important;
    padding: 4px 8px 4px 18px !important;
    box-shadow: var(--gemini-prompt-shadow) !important;
    transition: all 0.2s ease !important;
    display: flex !important;
    align-items: center !important;
}

#gemini-prompt-input,
#gemini-prompt-input > .wrap,
#gemini-prompt-input .input-container {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    width: 100% !important;
}

.chat-interface form:focus-within,
.chat-interface > div:last-child > div:focus-within,
.chat-interface div:has(> #gemini-prompt-input):focus-within,
form:has(> #gemini-prompt-input):focus-within,
div.form:has(> #gemini-prompt-input):focus-within {
    border-color: var(--gemini-prompt-focus-border) !important;
    box-shadow: 0 4px 24px var(--gemini-prompt-focus-glow) !important;
}

.chat-interface textarea,
#gemini-prompt-input textarea,
.chat-interface input,
#gemini-prompt-input input {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
    padding: 8px 0 !important;
    font-size: 15px !important;
    color: var(--gemini-prompt-text) !important;
    -webkit-text-fill-color: var(--gemini-prompt-text) !important;
    resize: none !important;
}

.chat-interface textarea::placeholder,
#gemini-prompt-input textarea::placeholder,
.chat-interface input::placeholder,
#gemini-prompt-input input::placeholder {
    color: var(--gemini-prompt-placeholder) !important;
    -webkit-text-fill-color: var(--gemini-prompt-placeholder) !important;
    opacity: 1 !important;
}

.chat-interface textarea::-webkit-input-placeholder,
#gemini-prompt-input textarea::-webkit-input-placeholder,
.chat-interface input::-webkit-input-placeholder,
#gemini-prompt-input input::-webkit-input-placeholder {
    color: var(--gemini-prompt-placeholder) !important;
    -webkit-text-fill-color: var(--gemini-prompt-placeholder) !important;
    opacity: 1 !important;
}

.chat-interface textarea:focus,
#gemini-prompt-input textarea:focus,
.chat-interface input:focus,
#gemini-prompt-input input:focus {
    outline: none !important;
    border: none !important;
    box-shadow: none !important;
    color: var(--gemini-prompt-text) !important;
    -webkit-text-fill-color: var(--gemini-prompt-text) !important;
}

/* Circular Send Button (↑) */
.chat-interface button[type="submit"],
.chat-interface button[aria-label="Submit"],
.chat-interface button.primary,
#gemini-prompt-input button {
    border-radius: 50% !important;
    width: 38px !important;
    height: 38px !important;
    min-width: 38px !important;
    max-width: 38px !important;
    background: #1A73E8 !important;
    color: #FFFFFF !important;
    border: none !important;
    padding: 0 !important;
    margin-left: 8px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 2px 6px rgba(26, 115, 232, 0.25) !important;
}

.chat-interface button[type="submit"]:hover,
.chat-interface button[aria-label="Submit"]:hover,
.chat-interface button.primary:hover,
#gemini-prompt-input button:hover {
    background: #1557B0 !important;
    transform: scale(1.06) !important;
    box-shadow: 0 4px 10px rgba(26, 115, 232, 0.35) !important;
}

/* Interactive Clickable Quiz Option Pills */
.quiz-opt-pill {
    background: var(--gemini-pill-bg) !important;
    border: 1.5px solid var(--gemini-pill-border) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    margin: 8px 0 !important;
    color: var(--gemini-card-title) !important;
    font-size: 14px !important;
    line-height: 1.5 !important;
    box-shadow: 0 2px 4px rgba(15, 23, 42, 0.04) !important;
    transition: background-color 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease !important;
    cursor: pointer !important;
    user-select: none !important;
    display: flex !important;
    align-items: baseline !important;
    gap: 6px !important;
}

.quiz-opt-pill:hover {
    border-color: var(--gemini-pill-hover-border) !important;
    background: var(--gemini-pill-hover-bg) !important;
    box-shadow: 0 4px 12px rgba(66, 133, 244, 0.14) !important;
}

.quiz-opt-pill:active,
.quiz-opt-pill.quiz-opt-pill-selected {
    border-color: var(--gemini-input-focus-border) !important;
    background: var(--gemini-badge-bg) !important;
    box-shadow: 0 0 0 3px var(--gemini-input-focus-glow) !important;
}

.quiz-opt-pill strong {
    color: var(--gemini-quiz-accent) !important;
    margin-right: 4px !important;
    font-weight: 700 !important;
    flex-shrink: 0 !important;
}
"""
