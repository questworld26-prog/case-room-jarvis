"""
CLI Pre-Flight Quiz Bank Linter and Diagnostic Validator.
Validates case study markdown quiz banks against pedagogical and schema rules before class.

Usage:
    uv run python -m tools.validate_quiz
    uv run python -m tools.validate_quiz --case EcoBrew
    uv run python -m tools.validate_quiz --case EcoBrew --strict

[spec: QUIZ-003]
"""

import argparse
import sys
from pathlib import Path

# Ensure src/ is on sys.path for direct module execution
src_path = Path(__file__).resolve().parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from core.quiz_parser import parse_quiz_markdown, validate_quiz_file


# [spec: QUIZ-003]
def validate_case_quiz(case_dir: Path) -> tuple[bool, str]:
    """Validate a single case study directory's quiz.md file."""
    quiz_file = case_dir / "quiz.md"
    if not quiz_file.is_file():
        quiz_file = case_dir / "Quiz.md"

    if not quiz_file.is_file():
        return False, f"⚠️ No quiz.md found in {case_dir.name}/ (optional for free-form QA, required for Quiz Mode)."

    is_valid, errors = validate_quiz_file(quiz_file)
    if not is_valid:
        lines = [f"❌ FAILED: {case_dir.name}/quiz.md ({len(errors)} error(s)):"]
        for err in errors:
            lines.append(f"   • {err}")
        return False, "\n".join(lines)

    questions = parse_quiz_markdown(quiz_file.read_text(encoding="utf-8"), filename=quiz_file.name)
    mcq_count = sum(1 for q in questions if q.get("type") == "mcq")
    open_count = len(questions) - mcq_count

    detail_lines = [f"✅ PASSED: {case_dir.name}/quiz.md"]
    detail_lines.append(f"   • {len(questions)} total questions ({mcq_count} MCQ, {open_count} Open-Ended)")
    for q in questions:
        q_type_str = "MCQ" if q.get("type") == "mcq" else "Open-Ended"
        correct_str = f" [Ans: {q.get('correct_option')}]" if q.get("type") == "mcq" else ""
        detail_lines.append(f"   • {q['id']} ({q_type_str}): {q['topic']}{correct_str}")

    return True, "\n".join(detail_lines)


# [spec: QUIZ-003]
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate case study markdown quiz banks (resource/<CaseName>/quiz.md)."
    )
    parser.add_argument(
        "--case",
        type=str,
        default="all",
        help="Case study directory name to validate (e.g. EcoBrew, EcoBrew, or 'all')",
    )
    parser.add_argument(
        "--resource-dir",
        type=str,
        default=str(Path(__file__).resolve().parent.parent.parent / "resource"),
        help="Path to case studies resource directory",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat missing quiz banks as errors",
    )

    args = parser.parse_args()
    res_dir = Path(args.resource_dir)

    if not res_dir.is_dir():
        print(f"Error: resource directory not found at {res_dir}", file=sys.stderr)
        return 1

    if args.case.lower() == "all":
        case_dirs = sorted([d for d in res_dir.iterdir() if d.is_dir() and not d.name.startswith(".")])
    else:
        target_dir = res_dir / args.case
        if not target_dir.is_dir():
            # Try case-insensitive lookup
            matched = [d for d in res_dir.iterdir() if d.is_dir() and d.name.lower() == args.case.lower()]
            if matched:
                target_dir = matched[0]
            else:
                print(f"Error: case study '{args.case}' not found in {res_dir}", file=sys.stderr)
                return 1
        case_dirs = [target_dir]

    print("\n========================================================")
    print("🔍 PRE-FLIGHT CASE STUDY QUIZ BANK VALIDATOR")
    print("========================================================")
    print(f"Scanning {len(case_dirs)} case study folder(s) in {res_dir}...\n")

    all_passed = True

    for c_dir in case_dirs:
        passed, report = validate_case_quiz(c_dir)
        print(report)
        print("-" * 56)

        if "⚠️ No quiz.md found" in report:
            if args.strict:
                all_passed = False
        elif not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 Pre-flight quiz validation PASSED! All verified quiz banks are ready for class.\n")
        return 0
    else:
        print("\n❌ Pre-flight quiz validation FAILED. Please resolve the errors above before class.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
