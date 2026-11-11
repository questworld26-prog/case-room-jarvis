import json
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from config import app_state

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
_log_lock = threading.Lock()
_log_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="jarvis_log_writer")

# Datestamp log file name capturing startup date, hour, and minute (e.g. classroom_chats_20260809_1854.jsonl)
SESSION_START_STAMP = time.strftime("%Y%m%d_%H%M")
ACTIVE_LOG_FILE = LOG_DIR / f"classroom_chats_{SESSION_START_STAMP}.jsonl"
TEST_LOG_FILE = LOG_DIR / f"test_classroom_chats_{SESSION_START_STAMP}.jsonl"

_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_STUDENT_MATRIC_RE = re.compile(r"\b[STGstg]\d{7}[A-Za-z]\b")
_EIGHT_DIGIT_ID_RE = re.compile(r"\b0\d{7}\b")
_PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s\-]?)?(?:\(?\d{3}\)?[\s\-]?)\d{3,4}[\s\-]?\d{4}\b")


# [spec: PRIV-001]
# [spec: PRIV-002]
def sanitize_pii(text: str) -> str:
    """Scrub student emails, phone numbers, University IDs, and 8-digit IDs from telemetry text."""
    if not text:
        return ""
    cleaned = _EMAIL_RE.sub("{{EMAIL}}", text)
    cleaned = _STUDENT_MATRIC_RE.sub("{{STUDENT_ID}}", cleaned)
    cleaned = _EIGHT_DIGIT_ID_RE.sub("{{STUDENT_ID}}", cleaned)
    cleaned = _PHONE_RE.sub("{{PHONE}}", cleaned)
    return cleaned


# [spec: PRIV-002]
def is_test_environment() -> bool:
    """Detect if execution is running under pytest, CI build, or explicit test environment."""
    return (
        bool(os.getenv("PYTEST_CURRENT_TEST"))
        or bool(os.getenv("IS_TESTING"))
        or bool(os.getenv("TESTING"))
        or bool(os.getenv("CI"))
    )


# [spec: PRIV-002]
def get_log_file_path(is_test: bool = False) -> Path:
    """Ensure logs directory exists and return active datestamped log file path (separate for tests)."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if is_test or is_test_environment():
        if not TEST_LOG_FILE.exists():
            TEST_LOG_FILE.touch()
        return TEST_LOG_FILE

    if not ACTIVE_LOG_FILE.exists():
        ACTIVE_LOG_FILE.touch()
    return ACTIVE_LOG_FILE


# [spec: PRIV-002]
def list_all_log_files(include_test_logs: bool = False) -> list[Path]:
    """List all JSONL log files in the logs directory sorted by timestamp/modification time."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    files = list(LOG_DIR.glob("*.jsonl"))
    if not include_test_logs:
        files = [f for f in files if not f.name.startswith("test_")]
    files.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    return files


def _write_to_disk(path: Path, line: str) -> None:
    with _log_lock, open(path, "a", encoding="utf-8") as f:
        f.write(line)


# [spec: PRIV-001]
# [spec: PRIV-002]
def log_interaction(
    mode: str,
    framework: str | None,
    prompt: str,
    response: str,
    latency_seconds: float,
    student_name: str = "Anonymous Student",
    session_id: str = "Session_1",
    turn_number: int = 1,
    history_depth: int = 0,
    prompt_word_count: int = 0,
) -> None:
    """Log structured, PII-sanitized interaction record to terminal and datestamped JSONL log file."""
    is_test = is_test_environment() or session_id.lower().startswith("test_") or student_name.lower().startswith("test")
    timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")
    word_cnt = prompt_word_count if prompt_word_count > 0 else len(prompt.split())
    safe_prompt = sanitize_pii(prompt)
    safe_response = sanitize_pii(response)
    safe_student = sanitize_pii(student_name)

    fw_str = f" | Framework: {framework}" if mode == "framework" and framework else ""
    prompt_snippet = safe_prompt.replace("\n", " ")[:50] + ("..." if len(safe_prompt) > 50 else "")
    tag_str = " [TEST/BUILD]" if is_test else ""
    print(
        f'[{timestamp_str}] 💬 [{session_id}]{tag_str} {safe_student} (Turn {turn_number}) | Mode: {mode.upper()}{fw_str} | ⏱️ {latency_seconds:.2f}s | Q: "{prompt_snippet}"'
    )

    try:
        log_file = get_log_file_path(is_test=is_test)
        record = {
            "timestamp": timestamp_str,
            "epoch": time.time(),
            "session_id": session_id,
            "case_study": app_state.active_case_study or "EcoBrew",
            "student_name": safe_student,
            "turn_number": turn_number,
            "history_depth": history_depth,
            "prompt_word_count": word_cnt,
            "mode": mode,
            "framework": framework if mode in ["framework", "teachback"] else None,
            "latency_seconds": round(latency_seconds, 3),
            "prompt": safe_prompt,
            "response": safe_response,
            "is_test_run": is_test,
        }
        line_to_write = json.dumps(record) + "\n"
        if is_test:
            _write_to_disk(log_file, line_to_write)
        else:
            _log_executor.submit(_write_to_disk, log_file, line_to_write)
    except Exception as e:
        print(f"Notice: logging error for {safe_student}: {e}")


# Alias for backward compatibility
LOG_FILE = ACTIVE_LOG_FILE
