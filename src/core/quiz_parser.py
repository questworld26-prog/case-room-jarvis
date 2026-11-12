"""
Markdown Quiz Bank Parser and Validator.
Provides line-level diagnostic validation, deterministic parsing,
and admin card preview generation for case study quiz banks.

[spec: QUIZ-003]
"""

import logging
import re
import sys
from pathlib import Path

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


def _validate_mcq_options(
    line_no: int,
    q_num: int,
    options: list[tuple[int, str, str, bool]],
    errors: list[str],
) -> None:
    """Validate MCQ option count, uniqueness (A-D), non-empty text, and single correct mark."""
    seen_letters: set[str] = set()
    for opt_line_no, letter, opt_body, _checked in options:
        if letter not in ("A", "B", "C", "D"):
            errors.append(
                f"Line {opt_line_no}: Question Q{q_num} has invalid option letter '{letter})' (expected A-D)."
            )
        if letter in seen_letters:
            errors.append(f"Line {opt_line_no}: Question Q{q_num} has duplicate option letter '{letter})'.")
        seen_letters.add(letter)
        if not opt_body:
            errors.append(f"Line {opt_line_no}: Question Q{q_num} option {letter}) has empty text.")

    if len(options) != 4:
        errors.append(
            f"Line {line_no}: Question Q{q_num} (MCQ) expected exactly 4 options (A-D), found {len(options)}."
        )
    checked_count = sum(1 for _, _, _, checked in options if checked)
    if checked_count == 0:
        errors.append(f"Line {line_no}: Question Q{q_num} (MCQ) has no correct option marked. Mark one with '- [x]'.")
    elif checked_count > 1:
        errors.append(f"Line {line_no}: Question Q{q_num} (MCQ) has multiple options marked correct ({checked_count}).")


def _validate_question_block(
    line_no: int,
    q_num: int,
    block: list[str],
    seen_q_nums: set[int],
    errors: list[str],
) -> None:
    """Validate a single question section block for schema, metadata, prompt, and option/rubric rules."""
    if q_num in seen_q_nums:
        errors.append(f"Line {line_no}: Duplicate question number Q{q_num} (each question must use a unique Q<N>).")
    seen_q_nums.add(q_num)

    q_type = "mcq"
    has_type = False
    has_official_ans = False
    has_question_heading = False
    question_heading_line = line_no
    prompt_lines: list[str] = []
    options: list[tuple[int, str, str, bool]] = []
    rubric_points: list[str] = []
    current_sec = "metadata"

    for offset, raw_line in enumerate(block):
        current_line_no = line_no + offset
        s_line = raw_line.strip()

        if re.match(r"^###\s+Question\b", s_line, re.IGNORECASE):
            has_question_heading = True
            question_heading_line = current_line_no
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
            raw_val = m_type.group(1).strip()
            raw_lower = raw_val.lower()
            if any(k in raw_lower for k in ("open", "analytical")):
                q_type = "open_ended"
            elif any(k in raw_lower for k in ("mcq", "multiple")):
                q_type = "mcq"
            else:
                errors.append(
                    f"Line {current_line_no}: Question Q{q_num} has unrecognized question type '{raw_val}'. "
                    "Expected 'MCQ' or 'Open-Ended'."
                )
            continue

        m_ans = re.match(r"^[-*]\s+\*\*Official\s+Answer\*\*[:\s]+(.*)$", s_line, re.IGNORECASE)
        if m_ans:
            has_official_ans = True
            if not m_ans.group(1).strip():
                errors.append(f"Line {current_line_no}: Question Q{q_num} has an empty '- **Official Answer**:' field.")
            continue

        if current_sec == "question":
            m_opt = re.match(r"^[-*]\s+\[([ xX])\]\s+([A-Za-z])\)(.*)$", s_line)
            if m_opt:
                checked = m_opt.group(1).lower() == "x"
                options.append((current_line_no, m_opt.group(2).upper(), m_opt.group(3).strip(), checked))
            elif s_line and not s_line.startswith(("---", "```")):
                prompt_lines.append(s_line)
        elif current_sec == "rubric":
            m_rub = re.match(r"^[-*]\s+(.*)$", s_line)
            if m_rub and m_rub.group(1).strip():
                rubric_points.append(m_rub.group(1).strip())

    if not has_type:
        errors.append(f"Line {line_no}: Question Q{q_num} missing '- **Type**: MCQ' or 'Open-Ended'.")
    if not has_official_ans:
        errors.append(f"Line {line_no}: Question Q{q_num} missing '- **Official Answer**: ...'.")
    if not has_question_heading:
        errors.append(f"Line {line_no}: Question Q{q_num} missing explicit '### Question' heading.")
    elif not prompt_lines:
        errors.append(
            f"Line {question_heading_line}: Question Q{q_num} has empty question prompt text under '### Question'."
        )

    if q_type == "mcq":
        _validate_mcq_options(line_no, q_num, options, errors)
    elif not rubric_points:
        errors.append(
            f"Line {line_no}: Question Q{q_num} (Open-Ended) missing criteria bullets under '### Answer (Rubric)'."
        )


# [spec: QUIZ-003]
# [spec: QUIZ-004]
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

    seen_q_nums: set[int] = set()
    for i, (line_no, q_num, _topic) in enumerate(question_starts):
        next_line_no = question_starts[i + 1][0] if i + 1 < len(question_starts) else len(lines) + 1
        block = lines[line_no - 1 : next_line_no - 1]
        _validate_question_block(line_no, q_num, block, seen_q_nums, errors)

    return len(errors) == 0, errors


# [spec: QUIZ-003]
def load_case_quiz_bank(case_dir_or_name: Path | str) -> list[dict]:
    """
    Load and parse the quiz bank for a case study from its markdown file (quiz.md).
    Returns a list of structured question dicts, or [] if missing or invalid.
    """
    case_dir = case_dir_or_name if isinstance(case_dir_or_name, Path) else get_case_resource_dir(str(case_dir_or_name))

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


def _build_preview_card_md(question: dict, total: int) -> str:
    """Format a single parsed quiz question into student-facing preview card markup."""
    q_num = question.get("question_number", 1)
    tot = question.get("total_questions", total)
    prompt_text = question.get("prompt_text", "")
    q_type = question.get("type", "mcq")

    correct_opt = str(question.get("correct_option", "")).strip().upper()

    card_lines = [f"🎯 **Quiz Question #{q_num} of {tot}**\n\n{prompt_text}"]
    if q_type == "mcq" and "options" in question:
        card_lines.append("")
        for opt in question["options"]:
            if opt.startswith(("A)", "B)", "C)", "D)")):
                badge = opt[:2]
                letter = badge[0].upper()
                rest = opt[2:].strip()
                is_correct = bool(correct_opt and letter == correct_opt)
                pill_cls = "quiz-opt-pill quiz-opt-pill-correct" if is_correct else "quiz-opt-pill"
                correct_tag = '<span class="quiz-opt-correct-tag">✓ Correct Answer</span>' if is_correct else ""
                card_lines.append(
                    f'<div class="{pill_cls}" role="button" tabindex="0" data-choice="{letter}">'
                    f"<strong>{badge}</strong> <span>{rest}</span>{correct_tag}</div>"
                )
            else:
                card_lines.append(f'<div class="quiz-opt-pill" role="button" tabindex="0">{opt}</div>')
    else:
        card_lines.append("\n*💡 Type your analysis in 2–3 sentences below!*")
    return "\n".join(card_lines)


# [spec: QUIZ-003]
def get_quiz_validation_status(case_name: str) -> dict:
    """
    Evaluate quiz readiness for instructor admin dashboard and card preview.
    Returns status metadata including badge, errors, questions, and pre-rendered card HTML previews.
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
            "questions": [],
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
            "questions": [],
        }

    questions = parse_quiz_markdown(quiz_file.read_text(encoding="utf-8"), filename=quiz_file.name)
    preview_cards = [_build_preview_card_md(q, len(questions)) for q in questions]
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
        "questions": questions,
    }


# [spec: QUIZ-004]
def collect_quiz_bank_startup_errors(resource_dir: Path | str | None = None) -> list[dict]:
    """Scan resource/<case>/ directories and return line-level validation failures for any invalid quiz.md."""
    base_res = (
        Path(resource_dir) if resource_dir is not None else Path(__file__).resolve().parent.parent.parent / "resource"
    )
    if not base_res.is_dir():
        return []

    failures: list[dict] = []
    for case_dir in sorted(d for d in base_res.iterdir() if d.is_dir() and not d.name.startswith(".")):
        quiz_file = case_dir / "quiz.md"
        if not quiz_file.is_file():
            quiz_file = case_dir / "Quiz.md"
        if not quiz_file.is_file():
            continue
        is_valid, errors = validate_quiz_file(quiz_file)
        if not is_valid:
            failures.append(
                {
                    "case_name": case_dir.name,
                    "quiz_path": f"resource/{case_dir.name}/{quiz_file.name}",
                    "errors": errors,
                }
            )
    return failures


# [spec: CACHE-003]
def has_case_source_materials(case_dir: Path) -> bool:
    """Return True if a case directory contains non-empty extracted text, any PDF, or any non-empty exhibit file."""
    extracted = case_dir / "extracted_context.txt"
    if extracted.is_file():
        try:
            if extracted.read_text(encoding="utf-8", errors="ignore").strip():
                return True
        except OSError:
            pass
    if any(case_dir.glob("**/*.pdf")):
        return True
    for pattern in ("supplementary_*.*", "exhibit_*.*"):
        for fp in case_dir.glob(pattern):
            try:
                if fp.is_file() and fp.read_text(encoding="utf-8", errors="ignore").strip():
                    return True
            except OSError:
                continue
    return False


# [spec: CACHE-003]
# [spec: QUIZ-004]
def collect_case_setup_errors(resource_dir: Path | str | None = None) -> list[dict]:
    """Scan case directories for missing source materials, missing quiz.md, or quiz schema errors."""
    base_res = (
        Path(resource_dir) if resource_dir is not None else Path(__file__).resolve().parent.parent.parent / "resource"
    )
    if not base_res.is_dir():
        return []

    failures: list[dict] = []
    for case_dir in sorted(d for d in base_res.iterdir() if d.is_dir() and not d.name.startswith(".")):
        case_errors: list[str] = []
        remediations: list[str] = []

        has_missing_materials = not has_case_source_materials(case_dir)
        if has_missing_materials:
            case_errors.append(
                f"No readable case materials (PDF, exhibits, or extracted_context.txt) found in resource/{case_dir.name}/."
            )

        quiz_file = case_dir / "quiz.md"
        if not quiz_file.is_file():
            quiz_file = case_dir / "Quiz.md"

        has_missing_quiz = not quiz_file.is_file()
        quiz_path = (
            f"resource/{case_dir.name}/"
            if has_missing_materials and has_missing_quiz
            else f"resource/{case_dir.name}/{quiz_file.name if quiz_file.is_file() else 'quiz.md'}"
        )
        if has_missing_quiz:
            case_errors.append(f"Missing markdown quiz bank: resource/{case_dir.name}/quiz.md.")
        else:
            is_valid, q_errors = validate_quiz_file(quiz_file)
            if not is_valid:
                case_errors.extend(q_errors)

        if has_missing_materials or has_missing_quiz:
            remediations.append("See docs/ADDING_A_CASE_STUDY.md")
        if not has_missing_quiz and case_errors:
            has_quiz_syntax_errors = len(case_errors) > (1 if has_missing_materials else 0)
            if has_quiz_syntax_errors:
                remediations.append(f"uv run python src/tools/validate_quiz.py --case {case_dir.name}")

        if case_errors:
            failures.append(
                {
                    "case_name": case_dir.name,
                    "quiz_path": quiz_path,
                    "errors": case_errors,
                    "remediations": remediations,
                }
            )
    return failures


# [spec: CACHE-003]
# [spec: QUIZ-004]
def format_quiz_startup_alert(errors_by_case: list[dict], use_color: bool | None = None) -> str:
    """Format a prominent bordered terminal banner summarizing startup case setup and quiz validation errors."""
    if not errors_by_case:
        return ""
    if use_color is None:
        use_color = hasattr(sys.stderr, "isatty") and sys.stderr.isatty()

    red = "\033[1;31m" if use_color else ""
    yellow = "\033[1;33m" if use_color else ""
    cyan = "\033[1;36m" if use_color else ""
    reset = "\033[0m" if use_color else ""

    bar = "=" * 72
    lines = [
        f"{red}{bar}{reset}",
        f"{red}🚨 ACTION REQUIRED: CASE STUDY SETUP / QUIZ BANK VALIDATION FAILED ON STARTUP{reset}",
        f"{red}{bar}{reset}",
    ]
    for entry in errors_by_case:
        case_name = entry["case_name"]
        quiz_path = entry["quiz_path"]
        errs = entry.get("errors", [])
        lines.append(f"{red}❌ Case Study: {case_name} ({quiz_path} — {len(errs)} issue(s)){reset}")
        for err in errs:
            lines.append(f"   • {err}")
        remediations = entry.get("remediations") or [
            f"uv run python src/tools/validate_quiz.py --case {case_name}",
        ]
        for cmd in remediations:
            lines.append(f"{cyan}   🔧 Action: {cmd}{reset}")
    lines.append(
        f"{yellow}⚠️ Incomplete case folders cannot serve grounded chat, and Quiz Mode falls back to oral exam until fixed.{reset}"
    )
    lines.append(f"{red}{bar}{reset}")
    return "\n".join(lines)
