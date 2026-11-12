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

# [spec: UI-001]
# [spec: UI-002]
# [spec: UI-003]
# [spec: UI-004]
# [spec: UI-005]
"""
Modular UI & Presentation layer for Jarvis Chatbot.

This module acts as the public facade, re-exporting:
- Event cards & greeting handlers from `ui.event_cards`
- CSS stylesheets & tokens from `ui.styles`
- Client-side JavaScript & Navigation header from `ui.client_scripts`
- Early `<head>` theme detection script (`HEAD_THEME_SCRIPT`) and `DEMO_LOAD_JS`
"""

from ui.client_scripts import (
    CLIENT_SCRIPTS_JS,
    NAV_HEADER_HTML,
    build_client_hero_html,
)
from ui.event_cards import (
    GREETING_PATTERN,
    format_event_card,
    format_post_quiz_wait_card,
    get_initial_welcome_card,
    get_instant_greeting,
)
from ui.styles import custom_css

# Complete Client Hero HTML combining stylesheets, scripts, and navigation header
CLIENT_HERO_HTML = build_client_hero_html(custom_css)

DEMO_LOAD_JS = """() => {
    if (window.__initJarvisClientHandlers) {
        window.__initJarvisClientHandlers();
    }
    var btn = document.getElementById("gemini-theme-toggle");
    if (btn) {
        btn.onclick = function() { window.toggleGeminiTheme(); };
    }

    var params = new URLSearchParams(window.location.search);
    var urlTheme = params.get("__theme");
    var hasDarkClass = document.documentElement.classList.contains("dark") ||
                       document.body.classList.contains("dark") ||
                       (document.querySelector(".gradio-container") && document.querySelector(".gradio-container").classList.contains("dark"));
    var saved = urlTheme || (hasDarkClass ? "dark" : null);
    if (!saved) {
        try {
            saved = localStorage.getItem("gemini_theme_preference");
        } catch(e) {
            saved = null;
        }
    }
    if (!saved) {
        saved = (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) ? "dark" : "light";
    }
    if (window.applyGeminiTheme) {
        window.applyGeminiTheme(saved);
    }

    window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
    if (document.documentElement) document.documentElement.scrollTop = 0;
    if (document.body) document.body.scrollTop = 0;
    var navBar = document.querySelector('.gemini-nav-bar');
    if (navBar) navBar.scrollIntoView({ behavior: 'instant', block: 'start' });
}"""

HEAD_THEME_SCRIPT = """
<meta name="color-scheme" content="light dark">
<script>
(function() {
    function detectTheme() {
        var params = new URLSearchParams(window.location.search);
        var urlTheme = params.get("__theme");
        if (urlTheme) return urlTheme;
        try {
            var saved = localStorage.getItem("gemini_theme_preference");
            if (saved) return saved;
        } catch(e) {}
        if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
            return "dark";
        }
        return "light";
    }

    var theme = detectTheme();
    var root = document.documentElement;
    var metaScheme = document.querySelector('meta[name="color-scheme"]');
    if (theme === "dark") {
        root.classList.add("dark");
        root.setAttribute("data-theme", "dark");
        if (metaScheme) metaScheme.setAttribute("content", "dark");
    } else {
        root.classList.remove("dark");
        root.setAttribute("data-theme", "light");
        if (metaScheme) metaScheme.setAttribute("content", "light");
    }

    window.applyGeminiTheme = function(t) {
        var isDark = (t === "dark");
        var r = document.documentElement;
        var b = document.body;
        var containers = document.querySelectorAll(".gradio-container");
        var toggleBtn = document.getElementById("gemini-theme-toggle");
        var meta = document.querySelector('meta[name="color-scheme"]');
        if (isDark) {
            r.classList.add("dark");
            r.setAttribute("data-theme", "dark");
            if (b) { b.classList.add("dark"); b.setAttribute("data-theme", "dark"); }
            containers.forEach(function(c) { c.classList.add("dark"); c.setAttribute("data-theme", "dark"); });
            if (toggleBtn) toggleBtn.setAttribute("aria-pressed", "true");
            if (meta) meta.setAttribute("content", "dark");
            try { localStorage.setItem("gemini_theme_preference", "dark"); } catch(e) {}
        } else {
            r.classList.remove("dark");
            r.removeAttribute("data-theme");
            if (b) { b.classList.remove("dark"); b.removeAttribute("data-theme"); }
            containers.forEach(function(c) { c.classList.remove("dark"); c.removeAttribute("data-theme"); });
            if (toggleBtn) toggleBtn.setAttribute("aria-pressed", "false");
            if (meta) meta.setAttribute("content", "light");
            try { localStorage.setItem("gemini_theme_preference", "light"); } catch(e) {}
        }
    };

    window.toggleGeminiTheme = function() {
        var isDark = document.documentElement.classList.contains("dark") ||
                     document.documentElement.getAttribute("data-theme") === "dark" ||
                     (document.body && document.body.classList.contains("dark")) ||
                     (document.querySelector(".gradio-container") && document.querySelector(".gradio-container").classList.contains("dark"));
        var target = isDark ? "light" : "dark";
        window.applyGeminiTheme(target);
        var sysDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
        var sysTheme = sysDark ? "dark" : "light";
        if (target === sysTheme) {
            try { localStorage.removeItem("gemini_theme_preference"); } catch(e) {}
            var meta = document.querySelector('meta[name="color-scheme"]');
            if (meta) meta.setAttribute("content", "light dark");
        }
    };

    function getStudentNameInputEl() {
        var nameInputs = document.querySelectorAll("#student-name-box input, #student-name-box textarea, input[placeholder*='Alex Tan'], textarea[placeholder*='Alex Tan'], input[placeholder*='full name'], textarea[placeholder*='full name']");
        for (var i = 0; i < nameInputs.length; i++) {
            if (nameInputs[i]) return nameInputs[i];
        }
        return null;
    }

    function setNativeInputValue(el, value) {
        if (!el) return;
        var proto = el.tagName === "TEXTAREA" ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
        var nativeSetter = Object.getOwnPropertyDescriptor(proto, "value");
        if (nativeSetter && nativeSetter.set) {
            nativeSetter.set.call(el, value);
        } else {
            el.value = value;
        }
        el.dispatchEvent(new Event("input", { bubbles: true }));
        el.dispatchEvent(new Event("change", { bubbles: true }));
    }

    window.submitChatPrompt = function(promptText) {
        if (!promptText) return;
        var promptEl = document.querySelector("#gemini-prompt-input textarea, #gemini-prompt-input input, .chat-interface textarea");
        if (promptEl) {
            setNativeInputValue(promptEl, promptText);
        }
        setTimeout(function() {
            var submitBtn = document.querySelector("#gemini-prompt-input button.submit-button, #gemini-prompt-input button[type='submit'], #gemini-prompt-input button[aria-label='Submit'], #gemini-prompt-input button, .chat-interface button[type='submit'], .chat-interface button[aria-label='Submit'], .chat-interface button.submit-button, .chat-interface button.primary");
            if (submitBtn) {
                submitBtn.click();
            } else if (promptEl) {
                promptEl.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", code: "Enter", keyCode: 13, which: 13, bubbles: true }));
            }
        }, 40);
    };

    window.submitQuizChoice = function(choiceLetter) {
        if (!choiceLetter) return;
        var cleanLetter = choiceLetter.trim().charAt(0).toUpperCase();
        var bridgeBtn = document.querySelector("button#quiz-choice-btn-" + cleanLetter + ", #quiz-choice-btn-" + cleanLetter + " button, #quiz-choice-btn-" + cleanLetter);
        if (bridgeBtn) {
            bridgeBtn.click();
            return;
        }
        window.submitChatPrompt(cleanLetter);
    };

    function extractQuizLetterFromPill(pillEl) {
        if (!pillEl) return null;
        var attrChoice = pillEl.getAttribute("data-choice");
        if (attrChoice && attrChoice.trim().length > 0) {
            return attrChoice.trim().charAt(0).toUpperCase();
        }
        var strongEl = pillEl.querySelector("strong");
        var raw = ((strongEl ? strongEl.textContent : pillEl.textContent) || "").trim();
        if (!raw) return null;
        var first = raw.charAt(0).toUpperCase();
        if ("ABCD".indexOf(first) !== -1 && (raw.length === 1 || raw.charAt(1) === ")" || raw.charAt(1) === "." || raw.charAt(1) === " ")) {
            return first;
        }
        return null;
    }

    function markQuizPillSelected(pillEl) {
        if (!pillEl) return;
        var parent = pillEl.parentElement;
        if (parent) {
            var siblings = parent.querySelectorAll(".quiz-opt-pill");
            for (var i = 0; i < siblings.length; i++) {
                siblings[i].classList.remove("quiz-opt-pill-selected");
            }
        }
        pillEl.classList.add("quiz-opt-pill-selected");
    }

    function syncEmptyStateVisibility() {
        var targetContainer = document.getElementById("main-chatbot") || document.querySelector(".chatbot");
        var heroGreeting = document.getElementById("gemini-greeting-hero");
        var startersGrid = document.querySelector(".gemini-starters-grid");
        if (!targetContainer) return;

        var messages = targetContainer.querySelectorAll(".message-row, [data-testid='user'], [data-testid='bot'], .message");
        if (messages && messages.length > 0) {
            if (heroGreeting) heroGreeting.style.display = "none";
            if (startersGrid) startersGrid.style.display = "none";
            targetContainer.classList.remove("gemini-chat-empty");
            if (document.body) document.body.classList.remove("gemini-chat-empty");
        } else {
            if (heroGreeting) heroGreeting.style.display = "block";
            if (startersGrid) startersGrid.style.display = "flex";
            targetContainer.classList.add("gemini-chat-empty");
            if (document.body) document.body.classList.add("gemini-chat-empty");
        }

        var eventCards = targetContainer.querySelectorAll(".gemini-event-card[data-case-name]");
        if (eventCards && eventCards.length > 0) {
            var latestCard = eventCards[eventCards.length - 1];
            var caseName = latestCard.getAttribute("data-case-name");
            var modeLabel = latestCard.getAttribute("data-mode-label");
            var caseChipEl = document.getElementById("gemini-nav-case-label");
            var modeChipEl = document.getElementById("gemini-nav-mode-label");
            if (caseName && caseChipEl) caseChipEl.textContent = caseName + " Case Study";
            if (modeLabel && modeChipEl) modeChipEl.textContent = modeLabel;
        }
    }

    function bindDelegatedInteractions() {
        if (window.__jarvisDelegatedBound) return;
        window.__jarvisDelegatedBound = true;

        document.addEventListener("click", function(e) {
            var pill = e.target && e.target.closest ? e.target.closest(".quiz-opt-pill") : null;
            if (pill) {
                var letter = extractQuizLetterFromPill(pill);
                if (letter) {
                    e.preventDefault();
                    markQuizPillSelected(pill);
                    window.submitQuizChoice(letter);
                }
            }
        });

        document.addEventListener("keydown", function(e) {
            var pill = e.target && e.target.closest ? e.target.closest(".quiz-opt-pill") : null;
            if (pill) {
                if (e.key === "Enter") {
                    var letter = extractQuizLetterFromPill(pill);
                    if (letter) {
                        e.preventDefault();
                        markQuizPillSelected(pill);
                        window.submitQuizChoice(letter);
                    }
                } else if (e.key === " ") {
                    e.preventDefault();
                }
            }

            var nameEl = getStudentNameInputEl();
            if (nameEl && e.target === nameEl && e.key === "Enter") {
                e.preventDefault();
                var promptEl = document.querySelector("#gemini-prompt-input textarea, #gemini-prompt-input input, .chat-interface textarea");
                if (promptEl && promptEl.value && promptEl.value.trim().length > 0) {
                    window.submitChatPrompt(promptEl.value.trim());
                } else if (promptEl) {
                    promptEl.focus();
                }
            }
        });

        document.addEventListener("keyup", function(e) {
            var pill = e.target && e.target.closest ? e.target.closest(".quiz-opt-pill") : null;
            if (pill && e.key === " ") {
                var letter = extractQuizLetterFromPill(pill);
                if (letter) {
                    e.preventDefault();
                    markQuizPillSelected(pill);
                    window.submitQuizChoice(letter);
                }
            }
        });

        if (window.matchMedia) {
            var mq = window.matchMedia("(prefers-color-scheme: dark)");
            if (mq && mq.addEventListener) {
                mq.addEventListener("change", function(evt) {
                    var pinned = null;
                    try { pinned = localStorage.getItem("gemini_theme_preference"); } catch(e) {}
                    if (!pinned) {
                        window.applyGeminiTheme(evt.matches ? "dark" : "light");
                    }
                });
            }
        }
    }

    window.__initJarvisClientHandlers = function() {
        bindDelegatedInteractions();
        syncEmptyStateVisibility();
        var targetContainer = document.getElementById("main-chatbot") || document.querySelector(".chatbot");
        if (targetContainer && !window.__jarvisObserverBound) {
            window.__jarvisObserverBound = true;
            var observer = new MutationObserver(function() {
                syncEmptyStateVisibility();
            });
            observer.observe(targetContainer, { childList: true, subtree: true });
        }
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", function() {
            window.applyGeminiTheme(theme);
            window.__initJarvisClientHandlers();
        });
    } else {
        window.applyGeminiTheme(theme);
        window.__initJarvisClientHandlers();
    }
})();
</script>
"""

__all__ = [
    "CLIENT_HERO_HTML",
    "CLIENT_SCRIPTS_JS",
    "DEMO_LOAD_JS",
    "GREETING_PATTERN",
    "HEAD_THEME_SCRIPT",
    "NAV_HEADER_HTML",
    "build_client_hero_html",
    "custom_css",
    "format_event_card",
    "format_post_quiz_wait_card",
    "get_initial_welcome_card",
    "get_instant_greeting",
]
