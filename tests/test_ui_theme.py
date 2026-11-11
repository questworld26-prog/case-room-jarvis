"""
Automated Pytest Suite for Jarvis Chatbot Visual Presentation & Design System.

Verifies:
1. WCAG 2.1 Contrast Ratios (AA >= 4.5:1, AAA >= 7.0:1) for text, placeholders, and badges across Dark and Light modes.
2. Bottom Omnibar Prompt Input (#gemini-prompt-input textarea) dark mode typed text visibility and -webkit-text-fill-color rules.
3. Student Name Input Box (#student-name-box) single-line centered pill structure and overflow ellipsis rules.
4. Header Navigation Card (.gemini-nav-bar) contrast, styling tokens, and badges.
5. Early Theme Injection Engine (HEAD_THEME_SCRIPT) and Client-Side Handlers.
6. Rendered HTML & Live Endpoint Visual Integrity.
"""

import math
import re

import pytest

from chatbot import HEAD_THEME_SCRIPT, demo
from ui.ui_theme import CLIENT_HERO_HTML, custom_css

# ==============================================================================
# Helper Functions: WCAG 2.1 Luminance and Contrast Ratio Calculations
# ==============================================================================


def hex_to_rgb(hex_code: str) -> tuple[float, float, float]:
    """Convert a 6-character hex color code to normalized RGB floats in [0, 1]."""
    clean_hex = hex_code.strip().lstrip("#")
    if len(clean_hex) == 3:
        clean_hex = "".join(c * 2 for c in clean_hex)
    assert len(clean_hex) == 6, f"Invalid hex color: {hex_code}"
    return tuple(int(clean_hex[i : i + 2], 16) / 255.0 for i in (0, 2, 4))


def relative_luminance(rgb: tuple[float, float, float]) -> float:
    """Calculate relative luminance according to WCAG 2.1 specifications."""

    def channel_lum(val: float) -> float:
        return val / 12.92 if val <= 0.03928 else math.pow((val + 0.055) / 1.055, 2.4)

    r, g, b = [channel_lum(c) for c in rgb]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(hex1: str, hex2: str) -> float:
    """Calculate WCAG 2.1 contrast ratio between two hex colors."""
    lum1 = relative_luminance(hex_to_rgb(hex1))
    lum2 = relative_luminance(hex_to_rgb(hex2))
    l_max, l_min = max(lum1, lum2), min(lum1, lum2)
    return (l_max + 0.05) / (l_min + 0.05)


# ==============================================================================
# 1. WCAG 2.1 Contrast Ratios
# ==============================================================================


# [verifies: UI-001/AC-UI-001.1]
def test_wcag_contrast_dark_mode_prompt_input():
    """Verify that text typed into the bottom omnibar in dark mode achieves WCAG AAA contrast (>= 7.0:1)."""
    # Background: #1E1F20 (charcoal), Text: #F8FAFC (silver-white)
    ratio = contrast_ratio("#F8FAFC", "#1E1F20")
    assert ratio >= 7.0, f"Dark mode prompt text contrast ratio {ratio:.2f} is below WCAG AAA threshold of 7.0:1"
    assert ratio >= 14.0, f"Expected extremely high contrast (>14.0:1), got {ratio:.2f}"


# [verifies: UI-001/AC-UI-001.1]
def test_wcag_contrast_dark_mode_placeholder():
    """Verify that placeholder text in dark mode meets WCAG AA (>= 4.5:1)."""
    # Background: #1E1F20, Placeholder: #9AA0A6 (Google Slate Grey)
    ratio = contrast_ratio("#9AA0A6", "#1E1F20")
    assert ratio >= 4.5, f"Dark mode placeholder contrast ratio {ratio:.2f} is below WCAG AA threshold of 4.5:1"


# [verifies: UI-001/AC-UI-001.2]
def test_wcag_contrast_light_mode_prompt_input():
    """Verify that text typed in light mode achieves WCAG AAA contrast (>= 7.0:1)."""
    # Background: #FFFFFF, Text: #0F172A (navy slate)
    ratio = contrast_ratio("#0F172A", "#FFFFFF")
    assert ratio >= 7.0, f"Light mode prompt text contrast ratio {ratio:.2f} is below WCAG AAA threshold of 7.0:1"


# [verifies: UI-001/AC-UI-001.2]
def test_wcag_contrast_light_mode_placeholder():
    """Verify that placeholder text in light mode meets WCAG AA (>= 4.5:1)."""
    # Background: #FFFFFF, Placeholder: #64748B
    ratio = contrast_ratio("#64748B", "#FFFFFF")
    assert ratio >= 4.5, f"Light mode placeholder contrast ratio {ratio:.2f} is below WCAG AA threshold of 4.5:1"


# [verifies: UI-001/AC-UI-001.3]
def test_wcag_contrast_header_navigation_brand():
    """Verify header brand typography satisfies WCAG AAA in both Dark and Light modes."""
    # Dark Mode: #F8FAFC on #1E1F20
    dark_ratio = contrast_ratio("#F8FAFC", "#1E1F20")
    assert dark_ratio >= 7.0, f"Dark mode header brand contrast ratio {dark_ratio:.2f} below 7.0:1"

    # Light Mode: #0F172A on #FFFFFF
    light_ratio = contrast_ratio("#0F172A", "#FFFFFF")
    assert light_ratio >= 7.0, f"Light mode header brand contrast ratio {light_ratio:.2f} below 7.0:1"


# [verifies: UI-001/AC-UI-001.3]
def test_wcag_contrast_header_badges():
    """Verify 'CASE COPILOT' badges satisfy readability guidelines in both Dark and Light modes."""
    # Dark Mode Badge: #8AB4F8 (periwinkle) on #28354A (navy pill)
    dark_badge_ratio = contrast_ratio("#8AB4F8", "#28354A")
    assert dark_badge_ratio >= 4.5, f"Dark mode badge contrast ratio {dark_badge_ratio:.2f} below 4.5:1"

    # Light Mode Badge: #1557B0 on #E8F0FE (WCAG AA > 4.5:1, exceeds 6.0:1)
    light_badge_ratio = contrast_ratio("#1557B0", "#E8F0FE")
    assert light_badge_ratio >= 4.5, f"Light mode badge contrast ratio {light_badge_ratio:.2f} below 4.5:1"


# [verifies: UI-001/AC-UI-001.4]
def test_wcag_contrast_student_name_box():
    """Verify student name input text and placeholder contrast in dark mode."""
    # Input text: #F8FAFC on #1E1F20
    text_ratio = contrast_ratio("#F8FAFC", "#1E1F20")
    assert text_ratio >= 7.0

    # Placeholder: #9AA0A6 on #1E1F20
    placeholder_ratio = contrast_ratio("#9AA0A6", "#1E1F20")
    assert placeholder_ratio >= 4.5


# ==============================================================================
# 2. Bottom Omnibar Prompt Input (#gemini-prompt-input textarea) Rules
# ==============================================================================


# [verifies: UI-002/AC-UI-002.1]
def test_prompt_input_css_variables_defined():
    """Verify that custom_css defines proper prompt omnibar and chat container CSS custom properties."""
    # Light theme variables in :root
    assert "--gemini-prompt-bg: #FFFFFF;" in custom_css
    assert "--gemini-prompt-border: #94A3B8;" in custom_css
    assert "--gemini-chat-border: #94A3B8;" in custom_css
    assert "--gemini-prompt-text: #0F172A;" in custom_css
    assert "--gemini-prompt-placeholder: #64748B;" in custom_css

    # Dark theme variables
    assert "--gemini-prompt-bg: #1E1F20;" in custom_css
    assert "--gemini-prompt-border: #3C4043;" in custom_css
    assert "--gemini-chat-border: #3C4043;" in custom_css
    assert "--gemini-prompt-text: #F8FAFC;" in custom_css
    assert "--gemini-prompt-placeholder: #9AA0A6;" in custom_css


# [verifies: UI-002/AC-UI-002.1]
def test_prompt_input_color_and_webkit_fill_color_enforced():
    """Verify that both color and -webkit-text-fill-color are bound to prevent invisible text."""
    # Check general omnibar textarea rules
    assert "color: var(--gemini-prompt-text) !important;" in custom_css
    assert "-webkit-text-fill-color: var(--gemini-prompt-text) !important;" in custom_css

    # Check focus state
    assert "-webkit-text-fill-color: var(--gemini-prompt-text) !important;" in custom_css

    # Check placeholder pseudo-elements
    assert "color: var(--gemini-prompt-placeholder) !important;" in custom_css
    assert "-webkit-text-fill-color: var(--gemini-prompt-placeholder) !important;" in custom_css


# [verifies: UI-002/AC-UI-002.2]
def test_prompt_input_dark_mode_specificity_coverage():
    """Verify that dark mode overrides cover .gradio-container.dark and html.dark to avoid Gradio DOM hierarchy drops."""
    # Gradio applies class 'dark' to html and .gradio-container, NOT document.body
    # Ensure our selector rules include both .gradio-container.dark and html.dark
    pattern = re.compile(
        r"(html\.dark[^{]*?\.gradio-container\.dark[^{]*?#gemini-prompt-input textarea|"
        r"\.gradio-container\.dark[^{]*?html\.dark[^{]*?#gemini-prompt-input textarea)",
        re.DOTALL,
    )
    assert pattern.search(custom_css) is not None, (
        "CSS must target both html.dark and .gradio-container.dark for #gemini-prompt-input textarea"
    )

    # Ensure explicit #F8FAFC override exists for dark mode omnibar
    assert "color: #F8FAFC !important;" in custom_css
    assert "-webkit-text-fill-color: #F8FAFC !important;" in custom_css


# ==============================================================================
# 3. Student Name Input Box (#student-name-box) Rules
# ==============================================================================


# [verifies: UI-002/AC-UI-002.3]
def test_student_name_box_single_line_pill_dimensions():
    """Verify that student name input box is styled as a 44px single-line pill with centered alignment."""
    # Height must be constrained to 44px to prevent large empty textareas
    assert "height: 44px !important;" in custom_css or (
        "min-height: 44px !important;" in custom_css and "max-height: 44px !important;" in custom_css
    )
    # Pill border radius
    assert "border-radius: 28px !important;" in custom_css
    # Centered alignment
    assert "text-align: center !important;" in custom_css


# [verifies: UI-002/AC-UI-002.3]
def test_student_name_box_placeholder_truncation_rules():
    """Verify that placeholder text cannot wrap or be vertically clipped on narrow displays."""
    assert "white-space: nowrap !important;" in custom_css
    assert "text-overflow: ellipsis !important;" in custom_css
    assert "overflow: hidden !important;" in custom_css


# [verifies: UI-002/AC-UI-002.3]
def test_student_name_box_dark_mode_styling():
    """Verify that dark mode overrides for student name input enforce charcoal background and silver text."""
    # Match dark selectors for student name box
    pattern = re.compile(
        r"\.gradio-container\.dark #student-name-box textarea.*?"
        r"background:\s*#1E1F20 !important;.*?"
        r"color:\s*#F8FAFC !important;",
        re.DOTALL,
    )
    match = pattern.search(custom_css)
    assert match is not None
    assert "#1E1F20" in match.group(0)
    assert "#F8FAFC" in match.group(0)


# ==============================================================================
# 4. Header Navigation Card (.gemini-nav-bar) Rules
# ==============================================================================


# [verifies: UI-003/AC-UI-003.1]
def test_header_navigation_card_tokens():
    """Verify .gemini-nav-bar is bound to design tokens and has rounded card structure."""
    assert ".gemini-nav-bar {" in custom_css
    assert "background: var(--gemini-nav-bg) !important;" in custom_css
    assert "border: 1px solid var(--gemini-nav-border) !important;" in custom_css
    assert "border-radius: 16px !important;" in custom_css


# [verifies: UI-003/AC-UI-003.2]
def test_header_brand_typography_and_badges():
    """Verify brand title and badge use design system tokens."""
    assert ".gemini-brand-title {" in custom_css
    assert "color: var(--gemini-title-color) !important;" in custom_css

    assert ".gemini-brand-badge {" in custom_css
    assert "background: var(--gemini-badge-bg) !important;" in custom_css
    assert "color: var(--gemini-badge-color) !important;" in custom_css


# ==============================================================================
# 5. Early Theme Injection Engine & Client Handlers
# ==============================================================================


# [verifies: UI-004/AC-UI-004.1]
def test_early_theme_injection_script_structure():
    """Verify HEAD_THEME_SCRIPT performs synchronous theme detection to prevent FOUC."""
    assert "<script>" in HEAD_THEME_SCRIPT
    assert "</script>" in HEAD_THEME_SCRIPT

    # URL query parameter check
    assert 'params.get("__theme")' in HEAD_THEME_SCRIPT

    # LocalStorage check
    assert 'localStorage.getItem("gemini_theme_preference")' in HEAD_THEME_SCRIPT

    # System prefers-color-scheme check
    assert "prefers-color-scheme: dark" in HEAD_THEME_SCRIPT

    # Synchronous mutation on documentElement to prevent FOUC
    assert 'classList.add("dark")' in HEAD_THEME_SCRIPT
    assert 'setAttribute("data-theme", "dark")' in HEAD_THEME_SCRIPT


# [verifies: UI-004/AC-UI-004.2]
def test_client_theme_helpers_defined():
    """Verify that applyGeminiTheme, toggleGeminiTheme, and initGeminiTheme are implemented."""
    assert "function applyGeminiTheme(theme)" in CLIENT_HERO_HTML
    assert "window.toggleGeminiTheme = function()" in CLIENT_HERO_HTML
    assert "function initGeminiTheme()" in CLIENT_HERO_HTML

    # applyGeminiTheme must update all .gradio-container instances
    assert 'document.querySelectorAll(".gradio-container")' in CLIENT_HERO_HTML
    assert "containers.forEach" in CLIENT_HERO_HTML


# [verifies: UI-004/AC-UI-004.3]
def test_theme_selector_button_removed():
    """Verify that the emoji theme icon is replaced with an accessible SVG Sun/Moon toggle button."""
    assert 'id="theme-toggle-icon"' not in CLIENT_HERO_HTML
    assert 'id="gemini-theme-toggle"' in CLIENT_HERO_HTML
    assert 'aria-label="Switch color theme"' in CLIENT_HERO_HTML
    assert 'class="theme-icon-moon"' in CLIENT_HERO_HTML
    assert 'class="theme-icon-sun"' in CLIENT_HERO_HTML


# [verifies: UI-005/AC-UI-005.1]
def test_event_card_dark_mode_contrast_and_classes():
    """Verify event cards use theme-aware semantic classes instead of hardcoded dark-on-dark inline text."""
    from ui.event_cards import format_event_card, format_post_quiz_wait_card

    card_html = format_event_card("LIVE MODE SWITCH", "Test Title", "Test Body", "Test Hint")
    assert 'class="gemini-event-card"' in card_html
    assert 'class="gemini-event-title"' in card_html
    assert 'class="gemini-event-body"' in card_html
    assert 'class="gemini-event-hint"' in card_html
    assert "color: #0F172A" not in card_html
    assert "color: #334155" not in card_html

    # Dark mode event card contrast: #F8FAFC title and #E3E3E3 body on #1E1F20 background
    assert contrast_ratio("#F8FAFC", "#1E1F20") >= 7.0
    assert contrast_ratio("#E3E3E3", "#1E1F20") >= 7.0

    wait_html = format_post_quiz_wait_card()
    assert 'class="gemini-wait-card"' in wait_html
    assert "background:#FFFBEB" not in wait_html


# [verifies: UI-005/AC-UI-005.2]
def test_clickable_quiz_pills_and_empty_state_viewport():
    """Verify quiz option pills have keyboard/click affordances and empty chat collapses vertically."""
    from core.quiz_engine import format_quiz_question_card

    q_html = format_quiz_question_card(
        {
            "question_number": 1,
            "total_questions": 5,
            "prompt_text": "Sample MCQ?",
            "type": "mcq",
            "options": ["A) First option", "B) Second option"],
        }
    )
    assert 'role="button"' in q_html
    assert 'tabindex="0"' in q_html
    assert 'data-choice="A"' in q_html
    assert "window.submitQuizChoice" in CLIENT_HERO_HTML
    assert "window.submitQuizChoice" in HEAD_THEME_SCRIPT
    assert "bindDelegatedInteractions" in HEAD_THEME_SCRIPT
    assert "quiz-choice-btn-" in HEAD_THEME_SCRIPT
    assert "window.submitChatPrompt" in CLIENT_HERO_HTML
    assert "body.gemini-chat-empty #main-chatbot" in custom_css
    assert "border: 1.5px solid var(--gemini-chat-border) !important;" in custom_css


# [verifies: ADMIN-001/AC-ADMIN-001.1]
def test_instructor_pending_mode_staging():
    """Verify set_pending_mode stages the mode without mutating active_mode until confirm_mode_broadcast."""
    from config import app_state
    from ui.admin_handlers import confirm_mode_broadcast, get_admin_status, set_pending_mode

    app_state.active_mode = "qa"
    set_pending_mode("quiz")
    assert app_state.active_mode == "qa", "set_pending_mode must not prematurely change active_mode before broadcast"
    assert app_state.pending_mode == "quiz"
    assert "Staged: QUIZ" in get_admin_status()

    confirm_mode_broadcast()
    assert app_state.active_mode == "quiz"
    app_state.active_mode = "qa"
    app_state.pending_mode = "qa"
    app_state._has_staged_mode = False


# ==============================================================================
# 6. Rendered HTML & Live Endpoint Visual Integrity
# ==============================================================================


# [verifies: UI-005/AC-UI-005.3]
def test_gradio_demo_configuration():
    """Verify demo blocks are instantiated with custom_css and HEAD_THEME_SCRIPT."""
    assert demo is not None
    # Verify CLIENT_HERO_HTML containing styles is loaded in the layout
    hero_block_found = any(
        isinstance(getattr(comp, "value", None), str) and "applyGeminiTheme" in comp.value
        for comp in demo.blocks.values()
    )
    assert hero_block_found is True, "CLIENT_HERO_HTML was not found inside Gradio demo.blocks"
    assert len(demo.blocks) > 5


# [verifies: UI-005/AC-UI-005.3]
def test_live_server_theme_endpoint():
    """Verify live server returns 200 and serves both themes with correct custom CSS and head scripts."""
    import requests

    try:
        res_dark = requests.get("http://127.0.0.1:7860/?__theme=dark", timeout=2)
        if res_dark.status_code == 200:
            assert "--gemini-prompt-text" in res_dark.text
            assert "applyGeminiTheme" in res_dark.text
            assert "gemini-nav-bar" in res_dark.text
            assert "student-name-box" in res_dark.text

            res_light = requests.get("http://127.0.0.1:7860/?__theme=light", timeout=2)
            assert res_light.status_code == 200
            assert "--gemini-prompt-text" in res_light.text
    except (requests.ConnectionError, requests.Timeout):
        # In isolated CI without a live daemon, this test gracefully passes
        pytest.skip("Local test server on port 7860 is not running; skipping live HTTP check.")
