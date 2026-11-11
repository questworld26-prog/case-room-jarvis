# UI Design System, Theme Engine & Event Card Specifications

## UI-001: WCAG AA and AAA Color Contrast Compliance

The UI design token system shall enforce WCAG 2.1 AA and AAA contrast ratios across light and dark themes for all interactive text and badges.

Acceptance Criteria:
- AC-UI-001.1: While dark mode is active, the UI theme engine shall maintain a contrast ratio of at least 15.0 for prompt input text and at least 4.5 for placeholder text.
- AC-UI-001.2: While light mode is active, the UI theme engine shall maintain a contrast ratio of at least 15.0 for prompt input text and at least 4.5 for placeholder text.
- AC-UI-001.3: The UI theme engine shall maintain a contrast ratio of at least 12.0 for header navigation brand titles and at least 7.0 for header badges across both themes.
- AC-UI-001.4: The UI theme engine shall maintain a contrast ratio of at least 12.0 for student name input text and at least 4.5 for student name placeholders across both themes.

## UI-002: Prompt Input and Student Name Pill CSS Token Architecture

The UI stylesheet modules shall bind prompt input fields and the student name pill to semantic CSS custom properties with high-specificity dark mode overrides.

Acceptance Criteria:
- AC-UI-002.1: The stylesheet token module shall define `--gemini-prompt-text` and `--gemini-prompt-placeholder` variables and bind them to both `color` and `-webkit-text-fill-color`.
- AC-UI-002.2: While dark mode is active, the dark theme stylesheet shall override prompt textarea and prose colors across `.gradio-container.dark`, `body.dark`, and `[data-theme="dark"]` selectors.
- AC-UI-002.3: The layout and dark theme stylesheets shall constrain `#student-name-box` to a single-line pill with ellipsis overflow truncation and charcoal `#1E1F20` dark background styling.

## UI-003: Header Navigation Bar and Brand Typography

The layout stylesheet shall style the header navigation bar and brand badges using theme-aware CSS custom properties.

Acceptance Criteria:
- AC-UI-003.1: The layout stylesheet shall style `.gemini-nav-bar` with `--gemini-nav-bg` background, `--gemini-nav-border` border, and a 16px border radius.
- AC-UI-003.2: The layout stylesheet shall bind `.gemini-brand-title` and `.gemini-brand-badge` colors to `--gemini-title-color`, `--gemini-badge-bg`, and `--gemini-badge-color`.

## UI-004: Early Theme Injection and Client-Side Theme Switching

The client script module shall execute synchronous theme detection in the document head and provide accessible client-side theme switching controls.

Acceptance Criteria:
- AC-UI-004.1: When the page document head loads, `HEAD_THEME_SCRIPT` shall synchronously inspect URL parameters, localStorage, and system color-scheme preferences to apply dark mode classes before first paint.
- AC-UI-004.2: The client hero script shall define `applyGeminiTheme`, `toggleGeminiTheme`, and `initGeminiTheme` functions that synchronize theme classes across all `.gradio-container` instances.
- AC-UI-004.3: The navigation bar HTML shall render the `#gemini-theme-toggle` button with an `aria-label` attribute and SVG sun and moon icons instead of an emoji icon.

## UI-005: Event Cards, Interactive Quiz Pills and Gradio Layout

The UI component modules shall render theme-aware event cards, keyboard-accessible quiz option pills, and the assembled Gradio Blocks interface.

Acceptance Criteria:
- AC-UI-005.1: When rendering mode switch or post-quiz wait cards, the event card module shall apply `.gemini-event-card` and `.gemini-wait-card` classes with a contrast ratio of at least 7.0.
- AC-UI-005.2: When rendering multiple-choice quiz cards, the quiz engine shall emit option pills with `role="button"`, `tabindex="0"`, and `data-choice` attributes while collapsing empty chat viewports.
- AC-UI-005.3: When the Gradio `demo` application initializes or serves HTTP theme requests, the UI theme module shall inject `custom_css`, `HEAD_THEME_SCRIPT`, and `CLIENT_HERO_HTML`.

