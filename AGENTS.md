# Workspace Rules & Directives

## 1. Testing Policy
* **Routine Verification**: Run only the unit test suite (`uv run pytest tests/test_chatbot.py -v`).
* **Concurrency Load Tests (`tests/test_load.py`)**: **DO NOT run automatically** for every build or code edit. Only execute the 50-student load test when the user explicitly instructs to do so.
* **Ollama User Simulator Tests (`tests/test_user_simulator.py`)**: **DO NOT run automatically** for every build or code edit. Only execute when the user explicitly instructs to do so.

## 2. Spec-Driven Development (SDD) & TDD Workflow
* **Spec-First Rule**: Author or update EARS requirements in `specs/**/*.md` before modifying `src/` or `tests/`, and validate with `python3 ~/.gemini/config/skills/ears-spec-validator/scripts/ears_validator.py validate --strict`.
* **Red → Green → Audit Loop**:
  1. **Red**: Write a failing deterministic test in `tests/` tagged with `# [verifies: REQ-ID/AC-ID]` (`1-Test-to-1-AC` cardinality).
  2. **Green**: Implement the minimal code in `src/` tagged with `# [spec: REQ-ID]`.
  3. **Audit**: Lock and verify bi-directional traceability via `python3 ~/.gemini/config/skills/spec-driven-development/scripts/guardian.py audit --update-hashes && python3 ~/.gemini/config/skills/spec-driven-development/scripts/guardian.py audit --strict`.
