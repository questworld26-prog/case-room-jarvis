# Case-Room — Release Notes

All notable changes to Case-Room are documented in this file.

---

## [0.8.0] — 2026-11-12

### Added
- **Apache License 2.0**: Added root `LICENSE`, `NOTICE`, and SPDX headers across core Python modules.
- **Synthetic Case Study Disclaimers**: Added `resource/EcoBrew/DISCLAIMER.md` and explicit fictional case notices across UI banners, data files, PDF debrief reports, and documentation.
- **Consolidated Release Notes**: Added `docs/developer/release.md` as the project's single release log.

### Changed
- **Asset Sanitization**: Renamed `EcoBrew_Case_Study_HBS_2024.pdf` to `EcoBrew_Case_Study_2024.pdf` and refreshed extracted context.
- **Packaging**: Bumped `pyproject.toml` to `0.8.0` with Apache-2.0 metadata and classifiers.
- **Developer Docs**: Updated `docs/developer/testing.html` with distinct boxes for Levels 1–5 and reordered `docs/developer/README.md`.

---

## [0.7.0] — 2026-11-12

### Added
- **Markdown Quiz Engine**: Added `src/core/quiz_parser.py` for YAML-frontmatter Markdown quizzes (`resource/<case>/quiz.md`).
- **Pre-Flight Validator**: Added `src/tools/validate_quiz.py` CLI and `tests/test_quiz_parser.py` suite.

### Changed
- **Quiz Bank Migration**: Replaced `data/quiz_banks.json` with co-located `quiz.md` files and dynamic loading in `src/ui/gradio_app.py`.
- **Documentation**: Updated `docs/ADDING_A_CASE_STUDY.md` and `docs/TROUBLESHOOTING.md` for Markdown quiz authoring.

---

## [0.6.0] — 2026-11-12

### Added
- **Developer Workspace**: Created `docs/developer/` with `README.md` and interactive Archify diagrams (`architecture.html`, `testing.html`).
- **Modular Guides**: Split documentation into `SETUP_GUIDE.md`, `USER_GUIDE.md`, `ADDING_A_CASE_STUDY.md`, and `TROUBLESHOOTING.md`.

### Changed
- **Documentation Restructure**: Streamlined root `README.md` and moved `ADR.md` into `docs/developer/`.

---

## [0.5.0] — 2026-11-11

### Added
- **Initial Release**: Case-Room (Jarvis) AI Business Case Companion.
- **Core Platform**: Gemini context caching with fallback, Gradio 6 mobile UI with QR onboarding, Mode 1 (Q&A) and Mode 2 (Bloom Quiz) plugins, and Instructor Admin Dashboard.
- **Privacy & Analytics**: Local-only JSONL telemetry with regex/Scrubadub PII redaction, Gini participation scoring, and 4-page executive PDF reports.
- **5-Level Testing Pyramid**: Unit/guardrail tests, semantic proximity & PII tests, 50-case golden benchmark with LLM judge, Ollama user simulator, and 50-student concurrency load suite.
