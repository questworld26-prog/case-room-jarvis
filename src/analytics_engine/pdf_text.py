"""Text sanitizers for FPDF2 latin-1 rendering."""

import re


# [spec: ANLY-001]
def sanitize_pdf_text(text: str) -> str:
    """Sanitize unicode text into latin-1 compatible text for standard FPDF fonts."""
    if not text:
        return ""
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "--",
        "\u2022": "-",
        "\u2026": "...",
        "\u00a0": " ",
        "\u2122": "(TM)",
        "\u00ae": "(R)",
        "\u00a9": "(C)",
        "⚠️": "[Notice]",
        "📊": "",
        "👑": "[Top]",
        "⚡": "",
        "🎯": "",
        "🚀": "",
        "⏱️": "",
        "💡": "",
        "📄": "",
        "📥": "",
        "💬": "",
        "🤖": "",
        "🔍": "",
        "✅": "[Pass]",
        "❌": "[Fail]",
        "→": "->",
        "≥": ">=",
        "≤": "<=",
        "±": "+/-",
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    return text.encode("latin-1", "replace").decode("latin-1")


# [spec: ANLY-001]
def clean_markdown_text(text: str) -> str:
    """Strip all raw markdown asterisks, backticks, ascii block characters, and formatting markers."""
    if not text:
        return ""
    # Strip backticks
    text = text.replace("`", "")
    # Strip markdown headers at start of line
    text = re.sub(r"^#+\s*", "", text)
    # Strip double/single asterisks while keeping content: e.g. **Evaluate:** -> Evaluate:
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    # Strip any remaining stray asterisks
    text = text.replace("*", "")
    # Strip ascii blocks
    text = re.sub(r"[█▓▒░]+", "", text)
    # Normalize spaces
    text = re.sub(r"[ \t]+", " ", text)
    return sanitize_pdf_text(text.strip())
