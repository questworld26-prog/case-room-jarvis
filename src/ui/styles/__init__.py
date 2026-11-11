"""
Modular styles package combining design tokens, layout, chat components, and dark theme overrides.
"""

from ui.styles.chat import CSS_CHAT
from ui.styles.dark_theme import CSS_DARK_THEME
from ui.styles.layout import CSS_LAYOUT
from ui.styles.tokens import CSS_TOKENS

# Assembled Custom CSS for the Gradio Interface
custom_css = f"{CSS_TOKENS}\n{CSS_LAYOUT}\n{CSS_CHAT}\n{CSS_DARK_THEME}"

__all__ = [
    "CSS_TOKENS",
    "CSS_LAYOUT",
    "CSS_CHAT",
    "CSS_DARK_THEME",
    "custom_css",
]
