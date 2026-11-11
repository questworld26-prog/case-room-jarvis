"""Heuristic alignment scoring of student prompts against the active pedagogical mode."""

# [spec: ANLY-001]
_RELEVANCE_CUES = {
    "quiz": ["option", "answer", "choice", "a", "b", "c", "d", "correct", "question", "quiz", "why is", "score"],
    "qa": [
        "what",
        "who",
        "where",
        "when",
        "how",
        "why",
        "explain",
        "describe",
        "detail",
        "metric",
        "data",
        "target",
        "goal",
        "percent",
    ],
}


# [spec: ANLY-001]
def evaluate_mode_relevance(prompt: str, mode: str) -> str:
    """
    Evaluates whether a student question is relevant and aligned to the active learning mode.
    Returns: 'High', 'Medium', or 'Low'.
    """
    p = (prompt or "").strip().lower()
    m = (mode or "qa").lower()
    n_words = len(p.split())

    if not p or (n_words < 2 and p not in ["why", "how", "what", "yes", "no", "a", "b", "c", "d"]):
        return "Low"

    cue_hit = any(w in p for w in _RELEVANCE_CUES.get(m, []))
    if m == "quiz":
        return "High" if cue_hit or n_words <= 4 else "Medium"
    return "High" if cue_hit or n_words >= 3 else "Medium"
