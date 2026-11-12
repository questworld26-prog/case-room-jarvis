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
