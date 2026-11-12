"""
Markdown Quiz Bank Parser and Validator.
Provides line-level diagnostic validation, deterministic parsing,
and admin card preview generation for case study quiz banks.

[spec: QUIZ-003]
"""

import logging
from pathlib import Path
import re

logger = logging.getLogger("case_room.quiz_parser")


# [spec: QUIZ-003]
def get_case_resource_dir(case_name: str) -> Path:
    """Resolve the resource directory for a given case study."""
    base_res = Path(__file__).resolve().parent.parent.parent / "resource"
    case_dir = base_res / case_name
    if case_dir.is_dir():
        return case_dir
    # Case-insensitive fallback
    if base_res.exists():
        for d in base_res.iterdir():
            if d.is_dir() and d.name.lower() == case_name.lower():
                return d
    return case_dir


# [spec: QUIZ-003]
def parse_quiz_markdown(content: str, filename: str = "quiz.md") -> list[dict]:
    """
    Parse a case study quiz markdown string into structured question dictionaries.
    Extracts Q1..Qn, metadata (type, hint, official answer), question prompt,
    MCQ options (with checked answer), and open-ended rubric points.
    """
    lines = content.splitlines()
    questions: list[dict] = []

    # Find question boundary lines: ## Q<N>: <Topic>
    q_start_indices: list[tuple[int, str, int, str]] = []
    q_heading_re = re.compile(r"^##\s+Q(\d+)[:\s]+(.*)$", re.IGNORECASE)

    for idx, line in enumerate(lines):
        m = q_heading_re.match(line.strip())
        if m:
            q_num = int(m.group(1))
            topic = m.group(2).strip()
            q_id = f"Q{q_num}"
            q_start_indices.append((idx, q_id, q_num, topic))

    total_q = len(q_start_indices)

    for i, (start_idx, q_id, q_num, topic) in enumerate(q_start_indices):
        end_idx = q_start_indices[i + 1][0] if i + 1 < total_q else len(lines)
        block_lines = lines[start_idx + 1 : end_idx]

        q_type = "mcq"
        hint = ""
        official_answer = ""
        prompt_lines: list[str] = []
        options: list[str] = []
        correct_option = ""
        rubric_points: list[str] = []

        current_section = "metadata"  # "metadata", "question", "rubric"

        for line in block_lines:
            s_line = line.strip()

            # Section headings
            if re.match(r"^###\s+Question\b", s_line, re.IGNORECASE):
                current_section = "question"
                continue
            if re.match(r"^###\s+Answer\s*\(Rubric\)", s_line, re.IGNORECASE) or re.match(
                r"^###\s+Rubric\b", s_line, re.IGNORECASE
            ):
                current_section = "rubric"
                continue

            # Metadata parsing (can appear before ### Question or within metadata section)
            m_type = re.match(r"^[-*]\s+\*\*Type\*\*[:\s]+(.*)$", s_line, re.IGNORECASE)
            if m_type:
                raw_type = m_type.group(1).strip().lower()
                q_type = "open_ended" if any(k in raw_type for k in ("open", "analytical")) else "mcq"
                continue

            m_hint = re.match(r"^[-*]\s+\*\*Hint\*\*[:\s]+(.*)$", s_line, re.IGNORECASE)
            if m_hint:
                hint = m_hint.group(1).strip()
                continue

            m_ans = re.match(r"^[-*]\s+\*\*Official\s+Answer\*\*[:\s]+(.*)$", s_line, re.IGNORECASE)
            if m_ans:
                official_answer = m_ans.group(1).strip()
                continue

            # Question body or options
            if current_section == "question":
                # Check for MCQ checkbox option
                m_opt = re.match(r"^[-*]\s+\[([ xX])\]\s+([A-Da-d]\).*)$", s_line)
                if m_opt:
                    is_checked = m_opt.group(1).lower() == "x"
                    opt_text = m_opt.group(2).strip()
                    options.append(opt_text)
                    if is_checked:
                        letter = opt_text[0].upper()
                        correct_option = letter
                elif not s_line.startswith(("---", "```")):
                    prompt_lines.append(line)

            # Rubric section bullet points
            elif current_section == "rubric":
                m_rub = re.match(r"^[-*]\s+(.*)$", s_line)
                if m_rub:
                    rubric_points.append(m_rub.group(1).strip())
                elif s_line and not s_line.startswith(("---", "```")):
                    rubric_points.append(s_line)

        prompt_text = "\n".join(prompt_lines).strip()

        question_dict = {
            "id": q_id,
            "question_number": q_num,
            "total_questions": total_q,
            "topic": topic,
            "type": q_type,
            "prompt_text": prompt_text,
            "hint": hint,
            "official_answer": official_answer,
        }

        if q_type == "mcq":
            question_dict["options"] = options
            question_dict["correct_option"] = correct_option
        else:
            question_dict["rubric_key_points"] = rubric_points

        questions.append(question_dict)

    return questions


# [spec: QUIZ-003]
def validate_quiz_file(file_path: Path | str) -> tuple[bool, list[str]]:
    """
    Validate a markdown quiz bank file against strict pedagogical and schema rules.
    Returns (is_valid, list_of_error_strings_with_line_numbers).
    """
    path = Path(file_path)
    if not path.is_file():
        return False, [f"Quiz file not found: {path}"]

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as exc:
        return False, [f"Unable to read {path}: {exc}"]

    lines = content.splitlines()
    errors: list[str] = []

    q_heading_re = re.compile(r"^##\s+Q(\d+)[:\s]+(.*)$", re.IGNORECASE)
    question_starts: list[tuple[int, int, str]] = []

    for idx, line in enumerate(lines, start=1):
        m = q_heading_re.match(line.strip())
        if m:
            question_starts.append((idx, int(m.group(1)), m.group(2).strip()))

    if not question_starts:
        return False, [f"Line 1: No questions found matching '## Q<N>: <Topic>' in {path.name}"]

    # Validate each question block
    for i, (line_no, q_num, topic) in enumerate(question_starts):
        next_line_no = question_starts[i + 1][0] if i + 1 < len(question_starts) else len(lines) + 1
        block = lines[line_no - 1 : next_line_no - 1]

        # Scan block for metadata and sections
        q_type = "mcq"
        has_type = False
        has_official_ans = False
        has_question_heading = False
        options: list[tuple[int, str, bool]] = []
        rubric_points: list[str] = []
        current_sec = "metadata"

        for offset, raw_line in enumerate(block):
            current_line_no = line_no + offset
            s_line = raw_line.strip()

            if re.match(r"^###\s+Question\b", s_line, re.IGNORECASE):
                has_question_heading = True
                current_sec = "question"
                continue
            if re.match(r"^###\s+Answer\s*\(Rubric\)", s_line, re.IGNORECASE) or re.match(
                r"^###\s+Rubric\b", s_line, re.IGNORECASE
            ):
                current_sec = "rubric"
                continue

            m_type = re.match(r"^[-*]\s+\*\*Type\*\*[:\s]+(.*)$", s_line, re.IGNORECASE)
            if m_type:
                has_type = True
                raw_type = m_type.group(1).strip().lower()
                q_type = "open_ended" if any(k in raw_type for k in ("open", "analytical")) else "mcq"
                continue

            if re.match(r"^[-*]\s+\*\*Official\s+Answer\*\*[:\s]+(.*)$", s_line, re.IGNORECASE):
                has_official_ans = True
                continue

            if current_sec == "question":
                m_opt = re.match(r"^[-*]\s+\[([ xX])\]\s+([A-Da-d]\).*)$", s_line)
                if m_opt:
                    checked = m_opt.group(1).lower() == "x"
                    options.append((current_line_no, m_opt.group(2).strip(), checked))

            elif current_sec == "rubric":
                m_rub = re.match(r"^[-*]\s+(.*)$", s_line)
                if m_rub:
                    rubric_points.append(m_rub.group(1).strip())

        # Assertions per question
        if not has_type:
            errors.append(f"Line {line_no}: Question Q{q_num} missing '- **Type**: MCQ' or 'Open-Ended'.")
        if not has_official_ans:
            errors.append(f"Line {line_no}: Question Q{q_num} missing '- **Official Answer**: ...'.")
        if not has_question_heading:
            errors.append(f"Line {line_no}: Question Q{q_num} missing explicit '### Question' heading.")

        if q_type == "mcq":
            if len(options) != 4:
                errors.append(
                    f"Line {line_no}: Question Q{q_num} (MCQ) expected exactly 4 options (A-D), found {len(options)}."
                )
            checked_count = sum(1 for _, _, checked in options if checked)
            if checked_count == 0:
                errors.append(
                    f"Line {line_no}: Question Q{q_num} (MCQ) has no correct option marked. Mark one with '- [x]'."
                )
            elif checked_count > 1:
                errors.append(
                    f"Line {line_no}: Question Q{q_num} (MCQ) has multiple options marked correct ({checked_count})."
                )
        else:
            if not rubric_points:
                errors.append(
                    f"Line {line_no}: Question Q{q_num} (Open-Ended) missing criteria bullets under '### Answer (Rubric)'."
                )

    return len(errors) == 0, errors


# [spec: QUIZ-003]
def load_case_quiz_bank(case_dir_or_name: Path | str) -> list[dict]:
    """
    Load and parse the quiz bank for a case study from its markdown file (quiz.md).
    Returns a list of structured question dicts, or [] if missing or invalid.
    """
    if isinstance(case_dir_or_name, Path):
        case_dir = case_dir_or_name
    else:
        case_dir = get_case_resource_dir(str(case_dir_or_name))

    quiz_file = case_dir / "quiz.md"
    if not quiz_file.is_file():
        quiz_file = case_dir / "Quiz.md"

    if not quiz_file.is_file():
        logger.warning("No markdown quiz bank found in %s", case_dir)
        return []

    is_valid, errors = validate_quiz_file(quiz_file)
    if not is_valid:
        logger.error("Quiz bank validation failed for %s:\n%s", quiz_file, "\n".join(errors))
        return []

    try:
        content = quiz_file.read_text(encoding="utf-8")
        return parse_quiz_markdown(content, filename=quiz_file.name)
    except Exception as exc:
        logger.error("Error reading quiz file %s: %s", quiz_file, exc)
        return []


# [spec: QUIZ-003]
def get_quiz_validation_status(case_name: str) -> dict:
    """
    Evaluate quiz readiness for instructor admin dashboard and card preview.
    Returns status metadata including badge, errors, and pre-rendered card HTML previews.
    """
    case_dir = get_case_resource_dir(case_name)
    quiz_file = case_dir / "quiz.md"
    if not quiz_file.is_file():
        quiz_file = case_dir / "Quiz.md"

    if not quiz_file.is_file():
        return {
            "is_valid": False,
            "badge": "⚠️ No Quiz Bank",
            "alert_message": f"No markdown quiz bank found in {case_dir.name}/quiz.md.",
            "errors": [f"Missing {quiz_file.name}"],
            "total_questions": 0,
            "preview_cards": [],
        }

    is_valid, errors = validate_quiz_file(quiz_file)
    if not is_valid:
        return {
            "is_valid": False,
            "badge": "🔴 Quiz Errors Found",
            "alert_message": f"Validation failed with {len(errors)} error(s) in {quiz_file.name}.",
            "errors": errors,
            "total_questions": 0,
            "preview_cards": [],
        }

    questions = parse_quiz_markdown(quiz_file.read_text(encoding="utf-8"), filename=quiz_file.name)

    # Generate preview cards matching student UI
    preview_cards: list[str] = []
    for q in questions:
        q_num = q.get("question_number", 1)
        tot = q.get("total_questions", len(questions))
        prompt_text = q.get("prompt_text", "")
        q_type = q.get("type", "mcq")

        card_lines = [f"🎯 **Quiz Question #{q_num} of {tot}**\n\n{prompt_text}"]
        if q_type == "mcq" and "options" in q:
            card_lines.append("")
            for opt in q["options"]:
                if opt.startswith(("A)", "B)", "C)", "D)")):
                    badge = opt[:2]
                    letter = badge[0].upper()
                    rest = opt[2:].strip()
                    card_lines.append(
                        f'<div class="quiz-opt-pill" role="button" tabindex="0" data-choice="{letter}">'
                        f"<strong>{badge}</strong> <span>{rest}</span></div>"
                    )
                else:
                    card_lines.append(f'<div class="quiz-opt-pill" role="button" tabindex="0">{opt}</div>')
        else:
            card_lines.append("\n*💡 Type your analysis in 2–3 sentences below!*")
        preview_cards.append("\n".join(card_lines))

    mcq_count = sum(1 for q in questions if q.get("type") == "mcq")
    open_count = len(questions) - mcq_count

    badge_text = f"🟢 Quiz Ready: {len(questions)} questions verified ({mcq_count} MCQ, {open_count} Open-Ended)"

    return {
        "is_valid": True,
        "badge": badge_text,
        "alert_message": "",
        "errors": [],
        "total_questions": len(questions),
        "preview_cards": preview_cards,
    }
