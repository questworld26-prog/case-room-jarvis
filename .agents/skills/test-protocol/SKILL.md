---
name: case-room-test-protocol
description: >-
  Defines the testing methodology, runner commands, test tiering, and isolation rules
  for the case companion. Enforced during [Gate 5] Test Suite Execution in release management.
---

# Test Protocol: Case-Room Companion

This skill defines the official testing process for the Case-Room companion.

## 1. Test Command & Execution
Execute routine verification and release test suite via `uv run pytest tests/test_chatbot.py -v`.

## 2. Test Execution Tiers
- **Fast Unit Tests**: Deterministic fast tests validating pure logic, schemas, and math. Must run in `< 5s`.
- **Integration Tests**: Tests database, file I/O, or local service boundaries.
- **Heavy / Live Inference (Opt-In)**: Heavy multi-model, UI emulator, or network tests isolated from standard pre-commit runs.

## 3. Anti-Mirage Assertion & Traceability Rules
- Every test function (`def test_*`, `it(...)`, `@Test fun ...`) must carry a `[verifies: REQ-ID/AC-ID]` annotation when `specs/` is present.
- All test assertions must verify deterministic outputs and exact numeric/factual anchors.
- Vacuous assertions (`assert result is not None`, `expect(x).toBeDefined()`, `assertTrue(true)`) are strictly forbidden.
- Every code/test change must pass `python3 ~/.gemini/config/skills/ears-spec-validator/scripts/ears_validator.py validate --strict` and `python3 ~/.gemini/config/skills/spec-driven-development/scripts/guardian.py audit --strict`.
