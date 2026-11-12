# [spec: UI-001]
# [spec: UI-002]
# [spec: UI-003]
"""
Design system tokens, typography imports, and CSS custom variables for Light and Dark modes.
"""

CSS_TOKENS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@500;600;700&display=swap');

/* Design System CSS Variables */
:root {
    color-scheme: light dark;
    --gemini-canvas-bg: #E8EEF5;
    --gemini-canvas-gradient: linear-gradient(180deg, #E2E9F3 0%, #EDF2F8 45%, #E6ECF5 100%);
    --body-background-fill: var(--gemini-canvas-bg);
    --background-fill-primary: #FFFFFF;
    --background-fill-secondary: #F8FAFC;
    --block-background-fill: #FFFFFF;
    --panel-background-fill: #FFFFFF;
    --block-border-color: #CBD5E1;
    --border-color-primary: #CBD5E1;
    --gemini-text-main: #1F2937;
    --gemini-text-muted: #475569;
    --gemini-nav-bg: #FFFFFF;
    --gemini-nav-border: #94A3B8;
    --gemini-nav-shadow: 0 4px 14px rgba(15, 23, 42, 0.07);
    --gemini-title-color: #0F172A;
    --gemini-badge-bg: #E8F0FE;
    --gemini-badge-border: #93C5FD;
    --gemini-badge-color: #1557B0;
    --gemini-sparkle-bg: #F0F4F9;
    --gemini-case-chip-bg: #F1F5F9;
    --gemini-case-chip-border: #94A3B8;
    --gemini-case-chip-color: #334155;
    --gemini-mode-chip-bg: #EEF2FF;
    --gemini-mode-chip-border: #818CF8;
    --gemini-mode-chip-color: #3730A3;
    --gemini-session-chip-bg: #ECFDF5;
    --gemini-session-chip-border: #34D399;
    --gemini-session-chip-color: #065F46;
    --gemini-toggle-btn-bg: #F8FAFC;
    --gemini-toggle-btn-border: #94A3B8;
    --gemini-toggle-btn-color: #334155;

    --gemini-input-bg: #FFFFFF;
    --gemini-input-border: #94A3B8;
    --gemini-input-text: #0F172A;
    --gemini-input-placeholder: #64748B;
    --gemini-input-focus-border: #1A73E8;
    --gemini-input-focus-glow: rgba(26, 115, 232, 0.18);

    --gemini-pill-bg: #FFFFFF;
    --gemini-pill-border: #94A3B8;
    --gemini-pill-text: #1E293B;
    --gemini-pill-hover-bg: #EFF6FF;
    --gemini-pill-hover-border: #1A73E8;
    --gemini-pill-hover-text: #1557B0;

    --gemini-chat-bg: #FFFFFF;
    --gemini-chat-border: #94A3B8;
    --gemini-chat-shadow: 0 4px 16px rgba(15, 23, 42, 0.07);

    --gemini-prompt-bg: #FFFFFF;
    --gemini-prompt-border: #94A3B8;
    --gemini-prompt-shadow: 0 6px 24px rgba(15, 23, 42, 0.10);
    --gemini-prompt-text: #0F172A;
    --gemini-prompt-placeholder: #64748B;
    --gemini-prompt-focus-border: #1A73E8;
    --gemini-prompt-focus-glow: rgba(26, 115, 232, 0.20);
    --gemini-prompt-footer-grad: linear-gradient(180deg, rgba(232, 238, 245, 0) 0%, #E8EEF5 35%, #E8EEF5 100%);

    /* Event Cards, Wait Cards, Dividers & Quiz Accents */
    --gemini-card-bg: #FFFFFF;
    --gemini-card-border: #CBD5E1;
    --gemini-card-accent: #1A73E8;
    --gemini-card-divider: #E2E8F0;
    --gemini-card-title: #0F172A;
    --gemini-card-body: #334155;
    --gemini-card-hint: #64748B;
    --gemini-wait-bg: #FFFBEB;
    --gemini-wait-border: #F59E0B;
    --gemini-wait-title: #92400E;
    --gemini-wait-body: #78350F;
    --gemini-hr-color: #CBD5E1;
    --gemini-quiz-accent: #1A73E8;
}

:root[data-theme='light'],
html:not(.dark) {
    color-scheme: light;
}

:root.dark,
:root[data-theme='dark'],
html.dark,
html[data-theme='dark'],
body.dark,
body[data-theme='dark'],
.gradio-container.dark,
.gradio-container[data-theme='dark'],
[data-theme='dark'],
.dark {
    color-scheme: dark;
    --gemini-canvas-bg: #131314;
    --gemini-canvas-gradient: none;
    --body-background-fill: #131314;
    --gemini-text-main: #E3E3E3;
    --gemini-text-muted: #9AA0A6;
    --gemini-nav-bg: #1E1F20;
    --gemini-nav-border: #3C4043;
    --gemini-nav-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
    --gemini-title-color: #F8FAFC;
    --gemini-badge-bg: #28354A;
    --gemini-badge-border: #3B82F6;
    --gemini-badge-color: #8AB4F8;
    --gemini-sparkle-bg: #2D2F31;
    --gemini-case-chip-bg: #2D2F31;
    --gemini-case-chip-border: #484C50;
    --gemini-case-chip-color: #E3E3E3;
    --gemini-mode-chip-bg: #1E293B;
    --gemini-mode-chip-border: #4F46E5;
    --gemini-mode-chip-color: #C7D2FE;
    --gemini-session-chip-bg: #064E3B;
    --gemini-session-chip-border: #059669;
    --gemini-session-chip-color: #A7F3D0;
    --gemini-toggle-btn-bg: #2D2F31;
    --gemini-toggle-btn-border: #484C50;
    --gemini-toggle-btn-color: #E3E3E3;

    --gemini-input-bg: #1E1F20;
    --gemini-input-border: #484C50;
    --gemini-input-text: #F8FAFC;
    --gemini-input-placeholder: #9AA0A6;
    --gemini-input-focus-border: #8AB4F8;
    --gemini-input-focus-glow: rgba(138, 180, 248, 0.22);

    --gemini-pill-bg: #1E1F20;
    --gemini-pill-border: #3C4043;
    --gemini-pill-text: #E3E3E3;
    --gemini-pill-hover-bg: #2D2F31;
    --gemini-pill-hover-border: #8AB4F8;
    --gemini-pill-hover-text: #8AB4F8;

    --gemini-chat-bg: #18191B;
    --gemini-chat-border: #3C4043;
    --gemini-chat-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);

    --gemini-prompt-bg: #1E1F20;
    --gemini-prompt-border: #3C4043;
    --gemini-prompt-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    --gemini-prompt-text: #F8FAFC;
    --gemini-prompt-placeholder: #9AA0A6;
    --gemini-prompt-focus-border: #8AB4F8;
    --gemini-prompt-focus-glow: rgba(138, 180, 248, 0.25);
    --gemini-prompt-footer-grad: linear-gradient(180deg, rgba(19, 19, 20, 0) 0%, #131314 35%, #131314 100%);

    /* Event Cards, Wait Cards, Dividers & Quiz Accents (WCAG AA/AAA Dark Mode) */
    --gemini-card-bg: #1E1F20;
    --gemini-card-border: #3C4043;
    --gemini-card-accent: #8AB4F8;
    --gemini-card-divider: #2D2F31;
    --gemini-card-title: #F8FAFC;
    --gemini-card-body: #E3E3E3;
    --gemini-card-hint: #9AA0A6;
    --gemini-wait-bg: #2B2111;
    --gemini-wait-border: #F59E0B;
    --gemini-wait-title: #FCD34D;
    --gemini-wait-body: #FDE68A;
    --gemini-hr-color: #3C4043;
    --gemini-quiz-accent: #8AB4F8;
}
"""
