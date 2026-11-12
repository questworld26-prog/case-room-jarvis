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
