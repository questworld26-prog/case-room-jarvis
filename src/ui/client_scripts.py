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
Client-side JavaScript handlers and Top Navigation Bar HTML template for Jarvis Chatbot.
"""

CLIENT_SCRIPTS_JS = """
<script>
    function getStudentNameInputEl() {
        var nameInputs = document.querySelectorAll("#student-name-box input, #student-name-box textarea, input[placeholder*='Alex Tan'], textarea[placeholder*='Alex Tan'], input[placeholder*='full name'], textarea[placeholder*='full name']");
        for (var i = 0; i < nameInputs.length; i++) {
            if (nameInputs[i]) return nameInputs[i];
        }
        return null;
    }

    function focusStudentNameInput() {
        var el = getStudentNameInputEl();
        if (el && !el.value) {
            try {
                el.focus({ preventScroll: true });
            } catch (e) {
                el.focus();
            }
        }
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
        var nameEl = getStudentNameInputEl();
        var hasName = nameEl && nameEl.value && nameEl.value.trim().length > 0 && nameEl.value.trim() !== "Anonymous Student";

        if (promptEl) {
            setNativeInputValue(promptEl, promptText);
        }

        if (!hasName && nameEl) {
            nameEl.classList.add("gemini-input-attention");
            var origPlaceholder = nameEl.getAttribute("placeholder") || "";
            nameEl.setAttribute("placeholder", "⚠️ Enter your full name first, then press Enter!");
            try {
                nameEl.focus({ preventScroll: false });
            } catch (e) {
                nameEl.focus();
            }
            setTimeout(function() {
                nameEl.classList.remove("gemini-input-attention");
                if (origPlaceholder) nameEl.setAttribute("placeholder", origPlaceholder);
            }, 3500);
            return;
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

    function scrollToTopOnLoad() {
        if (window.scrollTo) {
            window.scrollTo({ top: 0, left: 0, behavior: "instant" });
        }
        if (document.documentElement) {
            document.documentElement.scrollTop = 0;
        }
        if (document.body) {
            document.body.scrollTop = 0;
        }
        var gradioContainer = document.querySelector(".gradio-container");
        if (gradioContainer) {
            gradioContainer.scrollTop = 0;
        }
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

        // Sync dynamic case study & mode badges in top navigation header from latest event card
        var eventCards = targetContainer.querySelectorAll(".gemini-event-card[data-case-name]");
        if (eventCards && eventCards.length > 0) {
            var latestCard = eventCards[eventCards.length - 1];
            var caseName = latestCard.getAttribute("data-case-name");
            var modeLabel = latestCard.getAttribute("data-mode-label");
            var caseChipEl = document.getElementById("gemini-nav-case-label");
            var modeChipEl = document.getElementById("gemini-nav-mode-label");
            if (caseName && caseChipEl) {
                caseChipEl.textContent = caseName + " Case Study";
            }
            if (modeLabel && modeChipEl) {
                modeChipEl.textContent = modeLabel;
            }
        }
    }

    function applyGeminiTheme(theme) {
        var root = document.documentElement;
        var body = document.body;
        var containers = document.querySelectorAll(".gradio-container");
        var toggleBtn = document.getElementById("gemini-theme-toggle");
        var metaScheme = document.querySelector('meta[name="color-scheme"]');
        if (theme === "dark") {
            root.classList.add("dark");
            root.setAttribute("data-theme", "dark");
            if (body) {
                body.classList.add("dark");
                body.setAttribute("data-theme", "dark");
            }
            containers.forEach(function(c) {
                c.classList.add("dark");
                c.setAttribute("data-theme", "dark");
            });
            if (toggleBtn) toggleBtn.setAttribute("aria-pressed", "true");
            if (metaScheme) metaScheme.setAttribute("content", "dark");
            try { localStorage.setItem("gemini_theme_preference", "dark"); } catch(e) {}
        } else {
            root.classList.remove("dark");
            root.removeAttribute("data-theme");
            if (body) {
                body.classList.remove("dark");
                body.removeAttribute("data-theme");
            }
            containers.forEach(function(c) {
                c.classList.remove("dark");
                c.removeAttribute("data-theme");
            });
            if (toggleBtn) toggleBtn.setAttribute("aria-pressed", "false");
            if (metaScheme) metaScheme.setAttribute("content", "light");
            try { localStorage.setItem("gemini_theme_preference", "light"); } catch(e) {}
        }
    }

    window.toggleGeminiTheme = function() {
        var isDark = document.documentElement.classList.contains("dark") ||
                     (document.body && document.body.classList.contains("dark")) ||
                     (document.querySelector(".gradio-container") && document.querySelector(".gradio-container").classList.contains("dark"));
        var target = isDark ? "light" : "dark";
        applyGeminiTheme(target);
        var sysDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
        var sysTheme = sysDark ? "dark" : "light";
        if (target === sysTheme) {
            try { localStorage.removeItem("gemini_theme_preference"); } catch(e) {}
            var metaScheme = document.querySelector('meta[name="color-scheme"]');
            if (metaScheme) metaScheme.setAttribute("content", "light dark");
        }
    };

    function initGeminiTheme() {
        var params = new URLSearchParams(window.location.search);
        var urlTheme = params.get("__theme");
        var hasDarkClass = document.documentElement.classList.contains("dark") ||
                           (document.body && document.body.classList.contains("dark")) ||
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
        applyGeminiTheme(saved);
    }

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

    function bindDelegatedInteractions() {
        if (window.__jarvisDelegatedBound) return;
        window.__jarvisDelegatedBound = true;

        // 1. Click on Quiz Option Pill (.quiz-opt-pill)
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

        // 2. Keyboard Enter / Space on Quiz Option Pill (WCAG 2.1.1 Keyboard operable)
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
                    e.preventDefault(); // Prevent page scroll on Spacebar keydown
                }
            }

            // If student finishes typing their name in #student-name-box and hits Enter:
            // Either submit any waiting prompt in the omnibar, or focus the omnibar!
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

        // 3. OS color-scheme live change listener when no explicit user override is pinned
        if (window.matchMedia) {
            var mq = window.matchMedia("(prefers-color-scheme: dark)");
            if (mq && mq.addEventListener) {
                mq.addEventListener("change", function(evt) {
                    var pinned = null;
                    try { pinned = localStorage.getItem("gemini_theme_preference"); } catch(e) {}
                    if (!pinned) {
                        applyGeminiTheme(evt.matches ? "dark" : "light");
                    }
                });
            }
        }
    }

    function setupClientHandlers() {
        bindDelegatedInteractions();
        initGeminiTheme();
        scrollToTopOnLoad();
        [50, 150, 300, 600, 1000].forEach(function(delay) {
            setTimeout(scrollToTopOnLoad, delay);
            setTimeout(initGeminiTheme, delay);
        });

        [100, 400, 900].forEach(function(delay) {
            setTimeout(focusStudentNameInput, delay);
        });

        var autoScrollDebounce = null;
        var targetContainer = document.getElementById("main-chatbot") || document.querySelector(".chatbot");
        if (targetContainer) {
            var observer = new MutationObserver(function() {
                syncEmptyStateVisibility();
                if (autoScrollDebounce) clearTimeout(autoScrollDebounce);
                autoScrollDebounce = setTimeout(function() {
                    var botMessages = targetContainer.querySelectorAll(".message-row.bot, .bot.message, .message.bot, [data-testid='bot']");
                    if (botMessages && botMessages.length > 0) {
                        var latestBotMsg = botMessages[botMessages.length - 1];
                        latestBotMsg.scrollIntoView({ behavior: "smooth", block: "nearest" });
                    }
                }, 100);
            });
            observer.observe(targetContainer, { childList: true, subtree: true });
        }
        syncEmptyStateVisibility();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", setupClientHandlers);
    } else {
        setupClientHandlers();
    }
    window.addEventListener("load", scrollToTopOnLoad);
    window.addEventListener("pageshow", scrollToTopOnLoad);
</script>
"""

NAV_HEADER_HTML = """
<!-- Sleek Gemini Top Navigation Bar -->
<header class="gemini-nav-bar">
    <div class="gemini-nav-brand">
        <div class="gemini-sparkle-avatar">
            <svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L14.6 9.4L22 12L14.6 14.6L12 22L9.4 14.6L2 12L9.4 9.4L12 2Z" fill="url(#gemini-sparkle-grad)"/>
                <defs>
                    <linearGradient id="gemini-sparkle-grad" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
                        <stop stop-color="#4285F4"/>
                        <stop offset="0.45" stop-color="#9B72CB"/>
                        <stop offset="1" stop-color="#D96570"/>
                    </linearGradient>
                </defs>
            </svg>
        </div>
        <div class="gemini-brand-text-group">
            <span class="gemini-brand-title">Jarvis</span>
            <span class="gemini-brand-badge">Case Copilot</span>
        </div>
    </div>
    <div class="gemini-nav-meta">
        <div class="gemini-case-chip">
            <span class="case-dot" aria-hidden="true"></span>
            <span id="gemini-nav-case-label">EcoBrew Case Study</span>
        </div>
        <div class="gemini-mode-chip" id="gemini-nav-mode-chip">
            <span class="mode-dot" aria-hidden="true"></span>
            <span id="gemini-nav-mode-label">Standard Q&A</span>
        </div>
        <div class="gemini-session-chip">
            <span class="session-pulse" aria-hidden="true"></span>
            <span>Live Class</span>
        </div>
        <button type="button" id="gemini-theme-toggle" class="gemini-theme-toggle-btn" onclick="window.toggleGeminiTheme()" aria-label="Switch color theme" aria-pressed="false" title="Switch Light / Dark theme">
            <svg class="theme-icon-moon" aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            </svg>
            <svg class="theme-icon-sun" aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="5"></circle>
                <line x1="12" y1="1" x2="12" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="23"></line>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                <line x1="1" y1="12" x2="3" y2="12"></line>
                <line x1="21" y1="12" x2="23" y2="12"></line>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg>
        </button>
    </div>
</header>
"""


# [spec: UI-004]
# [spec: UI-005]
def build_client_hero_html(css_content: str) -> str:
    """Compose the complete Client Hero HTML embedding stylesheet, client JS, and navigation header."""
    return f"<style>\n{css_content}\n</style>\n{CLIENT_SCRIPTS_JS}\n{NAV_HEADER_HTML}"
