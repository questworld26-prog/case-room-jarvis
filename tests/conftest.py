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
    case_dirs = [
        d
        for d in RESOURCE_DIR.iterdir()
        if d.is_dir()
        and not d.name.startswith(".")
        and (any(d.glob("*.pdf")) or (d / "extracted_context.txt").exists())
    ]
    return len(case_dirs) >= 3


def get_test_case_study() -> str:
    """Return 'EcoBrew' if present in resource/ (Private repo), otherwise 'EcoBrew' (OSS repo)."""
    return get_default_case_study()


@pytest.fixture(autouse=True)
def setup_default_test_case():
    """Ensure app_state defaults to the active repository's case study."""
    case = get_test_case_study()
    app_state.active_case_study = case
    return case
