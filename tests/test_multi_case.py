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
Automated Pytest Suite for Multi-Case Study Architecture & Offline Preprocessor Tool.
Verifies dynamic case study discovery, case preprocessing, deferred cache loading, and telemetry tracking.
"""

from pathlib import Path

from analytics import compute_metrics, get_available_log_files
from cache_manager import get_or_create_cache
from conftest import is_private_repo
from logger import log_interaction
from preprocess_case import preprocess_case_folder

from config import app_state, get_available_case_studies


# [verifies: CACHE-001/AC-CACHE-001.1]
def test_dynamic_case_discovery():
    cases = get_available_case_studies()
    assert isinstance(cases, list)
    assert len(cases) >= 1
    assert any(c.lower() == "ecobrew" for c in cases)
    if is_private_repo():
        assert len(cases) >= 3


# [verifies: CACHE-001/AC-CACHE-001.2]
def test_preprocess_case():
    target_case = get_available_case_studies()[0]
    success = preprocess_case_folder(target_case)
    assert success is True

    context_file = Path(__file__).parent.parent / "resource" / target_case / "extracted_context.txt"
    assert context_file.exists()

    with open(context_file, encoding="utf-8") as f:
        text = f.read()
    assert len(text) > 5000


# [verifies: CACHE-002/AC-CACHE-002.1]
def test_case_selection_and_cache_loading():
    target_case = get_available_case_studies()[0]
    get_or_create_cache(target_case)
    assert app_state.active_case_study == target_case
    assert len(app_state.case_text_context) > 5000


# [verifies: PRIV-002/AC-PRIV-002.2]
def test_telemetry_logging_case_study_field():
    target_case = get_available_case_studies()[0]
    app_state.active_case_study = target_case
    log_interaction(
        mode="qa",
        framework=None,
        prompt=f"What is {target_case}'s strategic vision?",
        response=f"{target_case} focuses on circularity and sustainability.",
        latency_seconds=1.2,
        student_name="Test Student",
        session_id="Test_Session_MultiCase",
    )

    log_files = get_available_log_files()
    metrics = compute_metrics(log_files[:1])
    assert "case_study_breakdown" in metrics
    assert isinstance(metrics["case_study_breakdown"], dict)


# [verifies: CACHE-003/AC-CACHE-003.1]
def test_startup_scanner_flags_empty_and_missing_quiz_folders(tmp_path):
    """Verify startup diagnostics catch completely empty folders and folders missing quiz.md."""
    from core.quiz_parser import collect_case_setup_errors, format_quiz_startup_alert

    (tmp_path / "EmptyCase").mkdir()
    docs_only = tmp_path / "DocsOnlyCase"
    docs_only.mkdir()
    (docs_only / "extracted_context.txt").write_text("Valid case body text.", encoding="utf-8")

    errors_by_case = collect_case_setup_errors(tmp_path)
    by_name = {entry["case_name"]: entry for entry in errors_by_case}
    assert set(by_name.keys()) == {"DocsOnlyCase", "EmptyCase"}
    assert any("case materials" in e.lower() for e in by_name["EmptyCase"]["errors"])
    assert any("quiz.md" in e.lower() for e in by_name["EmptyCase"]["errors"])
    assert any("quiz.md" in e.lower() for e in by_name["DocsOnlyCase"]["errors"])
    assert not any("case materials" in e.lower() for e in by_name["DocsOnlyCase"]["errors"])

    banner = format_quiz_startup_alert(errors_by_case, use_color=False)
    assert "EmptyCase" in banner
    assert "DocsOnlyCase" in banner
    assert "ADDING_A_CASE_STUDY.md" in banner


# [verifies: CACHE-003/AC-CACHE-003.2]
def test_loading_or_refreshing_empty_case_shows_error_unlocks_and_clears_cache(tmp_path, monkeypatch):
    """Verify loading or refreshing a 0-char folder reports error, avoids locking session, and clears stale cache."""
    import config
    from core import cache_manager
    from ui import admin_handlers, gradio_app

    (tmp_path / "EmptyCase").mkdir()
    monkeypatch.setattr(cache_manager, "RESOURCE_ROOT", tmp_path)
    monkeypatch.setattr(gradio_app, "RESOURCE_ROOT", tmp_path)
    monkeypatch.setattr("core.quiz_parser.get_case_resource_dir", lambda name: tmp_path / name)
    monkeypatch.setattr(config.app_state, "active_cache_name", "cachedModels/stale-123")
    monkeypatch.setattr(config.app_state, "cache_info", {"name": "cachedModels/stale-123"})
    monkeypatch.setattr(config.app_state, "session_locked", False)
    monkeypatch.setattr(config.app_state, "case_text_context", "stale previous text")

    status, locked_input, _summary, preview_html, alert_html = gradio_app._load_selected_case_study("EmptyCase")
    assert "✅ Active Case Study set to" not in status
    assert "❌" in status or "0 chars" in status
    assert config.app_state.session_locked is False
    assert locked_input.get("interactive") is not False
    assert config.app_state.active_cache_name is None
    assert config.app_state.cache_info == {}
    assert "is-error" in preview_html
    assert "EmptyCase" in alert_html

    refresh_msg = admin_handlers.refresh_cache_action()
    assert "✅ Cleaned text context reloaded successfully" not in refresh_msg
    assert "❌" in refresh_msg


# [verifies: CACHE-003/AC-CACHE-003.3]
def test_empty_case_context_loader_avoids_duplicate_scan_and_logs_once(tmp_path, monkeypatch, capsys):
    """Verify get_or_create_cache scans an empty case folder only once and prints one cache warning."""
    import config
    from core import cache_manager

    (tmp_path / "EmptyCase").mkdir()
    monkeypatch.setattr(cache_manager, "RESOURCE_ROOT", tmp_path)
    monkeypatch.setattr(config.app_state, "case_text_context", "stale context")

    cache_manager.get_or_create_cache("EmptyCase", force_refresh=True)
    captured = capsys.readouterr().out
    assert captured.count("Loaded case text context for 'EmptyCase'") == 1
    assert captured.count("⚠️ No text context available to cache for 'EmptyCase'.") == 1


# [verifies: CACHE-003/AC-CACHE-003.4]
def test_admin_top_alert_lists_incomplete_folders_and_clears_when_resolved(tmp_path, monkeypatch):
    """Verify Admin top alert banner surfaces incomplete case folders and clears after adding files and reloading."""
    import config
    from core import cache_manager
    from core.quiz_parser import load_case_quiz_bank
    from ui import gradio_app

    case_dir = tmp_path / "EmptyCase"
    case_dir.mkdir()
    monkeypatch.setattr(gradio_app, "RESOURCE_ROOT", tmp_path)
    monkeypatch.setattr(cache_manager, "RESOURCE_ROOT", tmp_path)
    monkeypatch.setattr("core.quiz_parser.get_case_resource_dir", lambda name: tmp_path / name)
    monkeypatch.setattr(
        config,
        "load_all_case_quiz_banks",
        lambda: {"EmptyCase": load_case_quiz_bank(case_dir)} if load_case_quiz_bank(case_dir) else {},
    )
    monkeypatch.setattr(config.app_state, "session_locked", False)

    initial_alert = gradio_app._build_startup_quiz_alert_html()
    assert 'class="quiz-bank-alert-banner"' in initial_alert
    assert "EmptyCase" in initial_alert
    assert "docs/ADDING_A_CASE_STUDY.md" in initial_alert
    assert "preprocess_case.py" not in initial_alert
    assert "validate_quiz.py" not in initial_alert

    (case_dir / "extracted_context.txt").write_text("Complete case text body " * 20, encoding="utf-8")
    (case_dir / "quiz.md").write_text(
        "## Q1: Ready\n"
        "- **Type**: MCQ\n"
        "- **Official Answer**: A.\n\n"
        "### Question\n"
        "Prompt?\n\n"
        "- [x] A) Yes\n"
        "- [ ] B) No\n"
        "- [ ] C) Maybe\n"
        "- [ ] D) Unknown\n",
        encoding="utf-8",
    )

    _status, _locked, _summary, _preview, final_alert = gradio_app._load_selected_case_study("EmptyCase")
    assert final_alert == ""


# [verifies: CACHE-004/AC-CACHE-004.1]
def test_validate_gemini_api_key_rejects_missing_or_blank(monkeypatch):
    """Verify startup credential validation fails fast when GOOGLE_API_KEY is missing or blank without network calls."""
    from core import cache_manager

    def _forbid_client(*args, **kwargs):
        raise AssertionError("genai.Client should not be called when GOOGLE_API_KEY is missing")

    monkeypatch.setattr(cache_manager.genai, "Client", _forbid_client)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    is_ok, reason = cache_manager.validate_gemini_api_key()
    assert is_ok is False
    assert "missing or empty" in reason.lower()

    monkeypatch.setenv("GOOGLE_API_KEY", "   ")
    is_ok_blank, reason_blank = cache_manager.validate_gemini_api_key()
    assert is_ok_blank is False
    assert "missing or empty" in reason_blank.lower()


# [verifies: CACHE-004/AC-CACHE-004.2]
def test_validate_gemini_api_key_rejects_invalid_credentials(monkeypatch):
    """Verify startup credential validation rejects invalid Gemini API keys with diagnostic failure reason."""
    from core import cache_manager

    monkeypatch.setenv("GOOGLE_API_KEY", "AIzaInvalidTestKey000")

    class _FakeModelsFail:
        def get(self, **_kwargs):
            raise RuntimeError("400 API_KEY_INVALID: API key not valid.")

    class _FakeClientFail:
        models = _FakeModelsFail()

    monkeypatch.setattr(cache_manager.genai, "Client", lambda api_key: _FakeClientFail())
    is_ok, reason = cache_manager.validate_gemini_api_key()
    assert is_ok is False
    assert "API_KEY_INVALID" in reason

    class _FakeModelsOk:
        def get(self, **_kwargs):
            return {"name": "models/gemini-2.5-flash"}

    class _FakeClientOk:
        models = _FakeModelsOk()

    monkeypatch.setattr(cache_manager.genai, "Client", lambda api_key: _FakeClientOk())
    is_valid_ok, ok_reason = cache_manager.validate_gemini_api_key()
    assert is_valid_ok is True
    assert ok_reason == ""


# [verifies: CACHE-004/AC-CACHE-004.3]
def test_launch_app_halts_and_prints_banner_when_api_key_invalid(monkeypatch, capsys):
    """Verify launch_app prints a prominent warning banner and halts before starting Gradio on invalid key."""
    import pytest

    import chatbot

    monkeypatch.setattr("core.cache_manager.validate_gemini_api_key", lambda: (False, "400 API_KEY_INVALID"))
    monkeypatch.setattr(
        chatbot.demo, "launch", lambda *args, **kwargs: pytest.fail("Gradio server must not launch on invalid key")
    )

    with pytest.raises(SystemExit) as exc_info:
        chatbot.launch_app(share=False)

    assert exc_info.value.code == 1
    captured_err = capsys.readouterr().err
    assert "STARTUP HALTED" in captured_err
    assert "GOOGLE GEMINI API KEY" in captured_err
    assert "400 API_KEY_INVALID" in captured_err
    assert "aistudio.google.com/apikey" in captured_err
    assert "aborted" in captured_err.lower()
