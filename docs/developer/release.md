# Case-Room — Release Notes

All notable changes to Case-Room are documented in this file.

---

## [0.9.0] — 2026-11-12

### Added
- **Startup & Admin Case/Quiz Diagnostics (`CACHE-003`, `QUIZ-004`)**: Added bordered terminal and high-contrast Admin Panel alerts for invalid `quiz.md` files and empty/incomplete case folders missing source materials or `quiz.md`.
- **Quiz Bank Section & MCQ Answer Highlighting (`ADMIN-002`)**: Separated the Admin Quiz Bank preview into its own collapsible section with `✓ Correct Answer` MCQ highlighting.
- **Strict Quiz Edge-Case Validation**: Extended `validate_quiz_file` to catch duplicate question numbers, empty prompts, unrecognized types, duplicate/invalid A–D letters, blank option text, and empty official answers.

### Fixed
- **Admin Unlock & Live Quiz Synchronization**: Fixed Admin Panel recovery after an incorrect password (`gr.skip()`), cleared resolved top alerts on reload/broadcast, and mutated `PRE_AUTHORED_QUIZ_BANKS` in-place so student chatroom sessions see repaired quiz banks without restarting.
- **Light Mode Surface Parity (`UI-005`)**: Added consistent light slate canvas (`#E8EEF5`) and admin surface styling matching dark mode, plus clean text-wrapping layout for multi-line error alerts.
- **Empty Folder Handling**: Prevented duplicate empty extraction scans, stopped locking sessions on 0-char case loads, and cleared stale active context caches.

### Changed
- **Documentation**: Fixed `src/tools/validate_quiz.py` command paths in `docs/ADDING_A_CASE_STUDY.md` and `docs/TROUBLESHOOTING.md`, and added a Troubleshooting cross-reference table in `docs/ADDING_A_CASE_STUDY.md`.

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
