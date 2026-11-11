# [spec: UI-002]
# [spec: UI-003]
"""
Layout styles: Canvas, Navigation Header, Tabs, Hero Greeting, Student Name Input, and Mobile Responsiveness.
"""

CSS_LAYOUT = """
/* Clean, Airy Gemini Canvas */
html, body {
    width: 100% !important;
    max-width: 100% !important;
    overflow-x: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
    background-color: var(--gemini-canvas-bg) !important;
    color: var(--gemini-text-main) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    -webkit-font-smoothing: antialiased !important;
}

.gradio-container {
    max-width: 980px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    padding: 8px 18px 24px 18px !important;
    background: transparent !important;
}

/* Gemini Top Navigation Bar */
.gemini-nav-bar {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    padding: 10px 18px !important;
    background: var(--gemini-nav-bg) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid var(--gemini-nav-border) !important;
    border-radius: 16px !important;
    margin-bottom: 10px !important;
    box-shadow: var(--gemini-nav-shadow) !important;
}

.gemini-nav-brand {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
}

.gemini-sparkle-avatar {
    width: 32px !important;
    height: 32px !important;
    border-radius: 10px !important;
    background: var(--gemini-sparkle-bg) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    flex-shrink: 0 !important;
}

.gemini-brand-text-group {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
}

.gemini-brand-title {
    font-family: 'Outfit', sans-serif !important;
    font-size: 20px !important;
    font-weight: 700 !important;
    color: var(--gemini-title-color) !important;
    letter-spacing: -0.4px !important;
}

.gemini-brand-badge {
    background: var(--gemini-badge-bg) !important;
    color: var(--gemini-badge-color) !important;
    border: 1px solid var(--gemini-badge-border) !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    padding: 2px 8px !important;
    border-radius: 12px !important;
    letter-spacing: 0.3px !important;
    text-transform: uppercase !important;
}

.gemini-nav-meta {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
}

.gemini-case-chip {
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
    background: var(--gemini-case-chip-bg) !important;
    border: 1px solid var(--gemini-case-chip-border) !important;
    color: var(--gemini-case-chip-color) !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    padding: 4px 12px !important;
    border-radius: 16px !important;
}

.case-dot {
    width: 6px !important;
    height: 6px !important;
    border-radius: 50% !important;
    background-color: #3B82F6 !important;
}

.gemini-mode-chip {
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
    background: var(--gemini-mode-chip-bg) !important;
    border: 1px solid var(--gemini-mode-chip-border) !important;
    color: var(--gemini-mode-chip-color) !important;
    font-size: 11.5px !important;
    font-weight: 600 !important;
    padding: 4px 10px !important;
    border-radius: 16px !important;
}

.gemini-mode-chip span {
    color: var(--gemini-mode-chip-color) !important;
}

.mode-dot {
    width: 6px !important;
    height: 6px !important;
    border-radius: 50% !important;
    background-color: #6366F1 !important;
}

.gemini-session-chip {
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
    background: var(--gemini-session-chip-bg) !important;
    border: 1px solid var(--gemini-session-chip-border) !important;
    color: var(--gemini-session-chip-color) !important;
    font-size: 11.5px !important;
    font-weight: 600 !important;
    padding: 4px 10px !important;
    border-radius: 16px !important;
}

.gemini-session-chip span {
    color: var(--gemini-session-chip-color) !important;
}

.case-chip span,
.gemini-case-chip span {
    color: var(--gemini-case-chip-color) !important;
}

.session-pulse {
    width: 6px !important;
    height: 6px !important;
    border-radius: 50% !important;
    background-color: #10B981 !important;
    box-shadow: 0 0 6px #10B981 !important;
}

/* Gemini Minimalist Tabs */
div.tab-nav,
.tabs > div:first-child {
    border: none !important;
    background: transparent !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    padding: 2px 0 8px 0 !important;
    margin-bottom: 4px !important;
    border-bottom: 1px solid var(--gemini-nav-border) !important;
}

button[role="tab"] {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 20px !important;
    padding: 6px 14px !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    color: var(--gemini-text-muted) !important;
    transition: all 0.2s ease !important;
}

button[role="tab"].selected,
button[role="tab"][aria-selected="true"] {
    background: var(--gemini-badge-bg) !important;
    color: var(--gemini-badge-color) !important;
    border-color: var(--gemini-badge-border) !important;
    font-weight: 600 !important;
}

/* Discreet Instructor Tab Button */
button[role="tab"]:nth-child(2) {
    font-size: 11.5px !important;
    opacity: 0.72 !important;
    font-weight: 400 !important;
    color: var(--gemini-text-muted) !important;
    transition: all 0.2s ease !important;
}

button[role="tab"]:nth-child(2):hover {
    opacity: 1 !important;
    color: var(--gemini-title-color) !important;
    background: var(--gemini-case-chip-bg) !important;
}

/* Centered Reading Column */
.chat-interface,
#main-chatbot,
.gemini-greeting-hero,
#gemini-greeting-hero,
.gemini-student-name-row,
.gemini-starters-grid {
    max-width: 800px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

/* Empty State Greeting */
.gemini-greeting-hero,
#gemini-greeting-hero {
    text-align: center !important;
    padding: 12px 16px 6px 16px !important;
    margin-bottom: 4px !important;
    transition: opacity 0.3s ease !important;
}

.gemini-greeting-headline {
    font-family: 'Outfit', sans-serif !important;
    font-size: 25px !important;
    font-weight: 700 !important;
    color: var(--gemini-title-color) !important;
    letter-spacing: -0.4px !important;
    line-height: 1.25 !important;
    margin-bottom: 4px !important;
}

.gemini-text-gradient {
    background: linear-gradient(135deg, #4285F4 0%, #9B72CB 50%, #D96570 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    margin-right: 4px !important;
}

.gemini-greeting-subtext {
    font-size: 13.5px !important;
    color: var(--gemini-text-muted) !important;
    max-width: 520px !important;
    margin: 0 auto !important;
    line-height: 1.45 !important;
}

/* Student Name Input Pill */
.gemini-student-name-row {
    max-width: 540px !important;
    margin: 4px auto 8px auto !important;
}

.gemini-student-name-row .wrap,
.gemini-student-name-row div,
#student-name-box,
#student-name-box > div,
#student-name-box .wrap,
#student-name-box label {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    padding: 0 !important;
}

#student-name-box input,
#student-name-box textarea,
.gemini-name-input input,
.gemini-name-input textarea {
    background: var(--gemini-input-bg) !important;
    border: 1.5px solid var(--gemini-input-border) !important;
    border-radius: 28px !important;
    padding: 10px 22px !important;
    font-size: 14.5px !important;
    line-height: 22px !important;
    height: 44px !important;
    min-height: 44px !important;
    max-height: 44px !important;
    color: var(--gemini-input-text) !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04) !important;
    transition: all 0.2s ease !important;
    text-align: center !important;
    resize: none !important;
    overflow: hidden !important;
    white-space: nowrap !important;
    text-overflow: ellipsis !important;
    box-sizing: border-box !important;
}

#student-name-box input.gemini-input-attention,
#student-name-box textarea.gemini-input-attention {
    border-color: #F59E0B !important;
    box-shadow: 0 0 0 4px rgba(245, 158, 11, 0.28) !important;
}

#student-name-box input::placeholder,
#student-name-box textarea::placeholder,
.gemini-name-input input::placeholder,
.gemini-name-input textarea::placeholder {
    color: var(--gemini-input-placeholder) !important;
    opacity: 1 !important;
    font-weight: 450 !important;
    white-space: nowrap !important;
    text-overflow: ellipsis !important;
    overflow: hidden !important;
}

#student-name-box input::-webkit-input-placeholder,
#student-name-box textarea::-webkit-input-placeholder,
.gemini-name-input input::-webkit-input-placeholder,
.gemini-name-input textarea::-webkit-input-placeholder {
    color: var(--gemini-input-placeholder) !important;
    opacity: 1 !important;
    white-space: nowrap !important;
    text-overflow: ellipsis !important;
    overflow: hidden !important;
}

#student-name-box input:focus,
#student-name-box textarea:focus,
.gemini-name-input input:focus,
.gemini-name-input textarea:focus {
    background: var(--gemini-input-bg) !important;
    border-color: var(--gemini-input-focus-border) !important;
    box-shadow: 0 0 0 3.5px var(--gemini-input-focus-glow) !important;
    color: var(--gemini-input-text) !important;
    outline: none !important;
}

/* Discussion Starter Pills */
.gemini-starters-grid {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 8px !important;
    justify-content: center !important;
    margin: 4px auto 8px auto !important;
    border: none !important;
    background: transparent !important;
}

.gemini-starters-grid > div {
    border: none !important;
    background: transparent !important;
}

.gemini-starter-pill {
    background: var(--gemini-pill-bg) !important;
    border: 1.5px solid var(--gemini-pill-border) !important;
    border-radius: 22px !important;
    color: var(--gemini-pill-text) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    min-height: 38px !important;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.05) !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
    white-space: nowrap !important;
}

/* Hidden Quiz Bridge Buttons (DOM-mounted for Gradio 6 event pipeline, visually offscreen) */
.gemini-hidden-quiz-row,
.gemini-hidden-bridge {
    position: fixed !important;
    left: -9999px !important;
    top: -9999px !important;
    width: 1px !important;
    height: 1px !important;
    min-height: 1px !important;
    max-height: 1px !important;
    padding: 0 !important;
    margin: 0 !important;
    opacity: 0 !important;
    pointer-events: none !important;
    overflow: hidden !important;
    border: none !important;
}

.gemini-starter-pill:hover {
    background: var(--gemini-pill-hover-bg) !important;
    border-color: var(--gemini-pill-hover-border) !important;
    color: var(--gemini-pill-hover-text) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 10px rgba(66, 133, 244, 0.12) !important;
}

.gemini-starter-pill:focus-visible,
button:focus-visible,
.quiz-opt-pill:focus-visible {
    outline: 2px solid var(--gemini-input-focus-border) !important;
    outline-offset: 2px !important;
}

button, .gemini-starter-pill, .quiz-opt-pill, button[role="tab"] {
    min-height: 42px !important;
    touch-action: manipulation;
}

@media (max-width: 768px) {
    /* Prevent iOS Safari auto-zoom on mobile inputs */
    input, textarea, select, #student-name-box input, .chat-interface input, .chat-interface textarea {
        font-size: 16px !important;
    }
    .gradio-container {
        padding: 4px !important;
    }
    .gemini-nav-bar {
        padding: 8px 12px !important;
        margin-bottom: 8px !important;
    }
    .gemini-brand-title {
        font-size: 17px !important;
    }
    .gemini-case-chip,
    .gemini-mode-chip {
        display: none !important;
    }
    .gemini-greeting-headline {
        font-size: 20px !important;
    }
    .gemini-greeting-subtext {
        font-size: 12.5px !important;
    }
    #main-chatbot, .chatbot, div[data-testid="chatbot"] {
        height: calc(100dvh - 220px) !important;
        min-height: 300px !important;
    }
    .chat-interface > div:last-child {
        padding: 8px 0 6px 0 !important;
    }
    .classroom-footer {
        display: none !important;
    }
}

.classroom-footer {
    text-align: center;
    padding: 16px 0 8px 0;
    margin-top: 20px;
    border-top: 1px solid var(--gemini-nav-border);
    color: var(--gemini-text-muted);
    font-size: 12.5px;
    font-weight: 500;
}

/* Theme Toggle Button (Vector SVG Sun/Moon) */
.gemini-theme-toggle-btn {
    background: var(--gemini-toggle-btn-bg) !important;
    border: 1px solid var(--gemini-toggle-btn-border) !important;
    color: var(--gemini-toggle-btn-color) !important;
    border-radius: 50% !important;
    width: 34px !important;
    height: 34px !important;
    min-width: 34px !important;
    max-width: 34px !important;
    min-height: 34px !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease !important;
}

.gemini-theme-toggle-btn:hover {
    background: var(--gemini-case-chip-bg) !important;
    border-color: var(--gemini-input-focus-border) !important;
    color: var(--gemini-title-color) !important;
}

.gemini-theme-toggle-btn .theme-icon-sun {
    display: none;
}

.gemini-theme-toggle-btn .theme-icon-moon {
    display: block;
}

html.dark .gemini-theme-toggle-btn .theme-icon-sun,
body.dark .gemini-theme-toggle-btn .theme-icon-sun,
.gradio-container.dark .gemini-theme-toggle-btn .theme-icon-sun,
[data-theme='dark'] .gemini-theme-toggle-btn .theme-icon-sun {
    display: block;
}

html.dark .gemini-theme-toggle-btn .theme-icon-moon,
body.dark .gemini-theme-toggle-btn .theme-icon-moon,
.gradio-container.dark .gemini-theme-toggle-btn .theme-icon-moon,
[data-theme='dark'] .gemini-theme-toggle-btn .theme-icon-moon {
    display: none;
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }
}
"""
