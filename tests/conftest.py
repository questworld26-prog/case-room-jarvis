"""
Shared Pytest Configuration & Test Fixtures.
Provides dynamic case study resolution across Private ('EcoBrew') and Open-Source ('EcoBrew') repositories.
"""

from pathlib import Path

import pytest

from config import app_state, get_default_case_study

RESOURCE_DIR = Path(__file__).resolve().parent.parent / "resource"


def is_private_repo() -> bool:
    """Return True if running in the supervisor repository with multi-case studies."""
    if not RESOURCE_DIR.exists():
        return False
    case_dirs = [d for d in RESOURCE_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")]
    return len(case_dirs) > 1


def get_test_case_study() -> str:
    """Return 'EcoBrew' if present in resource/ (Private repo), otherwise 'EcoBrew' (OSS repo)."""
    return get_default_case_study()


@pytest.fixture(autouse=True)
def setup_default_test_case():
    """Ensure app_state defaults to the active repository's case study."""
    case = get_test_case_study()
    app_state.active_case_study = case
    return case
