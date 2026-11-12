# Case-Room — Developer & Architecture Guide

Welcome to the internal engineering guide for **Case-Room**. This document details the system design, microkernel plugin model, Spec-Driven Development (SDD) governance, and the 5-Level Testing Pyramid.

For general setup and classroom operations, refer back to the **[Main README](../../README.md)**, **[Setup Guide](../SETUP_GUIDE.md)**, and **[User Guide](../USER_GUIDE.md)**.

---

## 🗺️ Interactive System & Testing Diagrams

Case-Room includes standalone, interactive HTML diagrams authored with [Archify](https://github.com/tt-a1i/archify). Open them directly in your browser:

| Diagram | Format | Description |
| :--- | :--- | :--- |
| 🏛️ **[System Architecture](architecture.html)** | Standalone HTML | Interactive component topology mapping student mobile ingress, Gradio TLS tunneling, dialogue guardrails, microkernel plugins, context cache management, and Google Gemini API integration. Supports dark/light themes, live connection tracing, and SVG export. |
| 🧪 **[Testing & SDD Pipeline](testing.html)** | Standalone HTML | Interactive workflow diagram illustrating the 5-Level Testing Pyramid, dual-layer golden dataset grader, Ollama user simulator, and the Spec Guardian audit loop. |

> [!TIP]
> **Semantic Passport & IDE Jumping**: Clicking any component or node in either interactive HTML diagram opens its **Semantic Passport** panel with source links and direct IDE jumping (`⚡ Open in IDE`).

---

## 📚 Architectural Records & Release History

Key architectural decisions, trade-offs, and version release notes are formally documented in:

- **[Architecture Decision Records (ADR.md)](ADR.md)**: 16 approved ADRs covering context caching (ADR 002), restart recovery (ADR 003), staged mode broadcasting (ADR 014), microkernel plugins (ADR 016), and tiered evaluation (ADR 011).
- **[Release Notes & History (release.md)](release.md)**: The single canonical release log detailing version milestones, migrations, and quality gates from v0.5.0 to v0.8.0.

---

## 📐 Spec-Driven Development (SDD) Workflow

Case-Room enforces a strict **Spec-First** development methodology aligned with ISO/IEC/IEEE 29148 and EARS (Easy Approach to Requirements Syntax).

### The Red → Green → Audit Cycle

1. **Spec First**: Define or update requirements in `specs/**/*.md` before touching code:
   ```bash
   python3 ~/.gemini/config/skills/ears-spec-validator/scripts/ears_validator.py validate --strict
   ```
2. **Red**: Write a failing deterministic test in `tests/` tagged with `# [verifies: REQ-ID/AC-ID]` (strictly enforces `1-Test-to-1-AC` cardinality).
3. **Green**: Implement the minimal code in `src/` tagged with `# [spec: REQ-ID]`.
4. **Audit**: Verify bidirectional traceability between specs, code AST, and test functions:
   ```bash
   python3 ~/.gemini/config/skills/spec-driven-development/scripts/guardian.py audit --strict
   ```

---

## 🧪 The 5-Level Testing Pyramid

Our testing strategy guarantees speed, privacy, pedagogical accuracy, and concurrency resilience using the bundled synthetic **EcoBrew** reference case (`resource/EcoBrew/`):

> [!NOTE]
> **Synthetic Test Fixtures**: **EcoBrew** is an entirely fictional, synthetic corporate case study created to enable hermetic, automated testing across all five pyramid levels without relying on proprietary courseware.

```text
               ▲
              / \     Level 5: 50-Student Concurrency & Load (Manual on-demand)
             /---\
            /     \    Level 4: Agentic User Simulator (Ollama qwen2.5:3b)
           /-------\
          /         \   Level 3: Golden Dataset & Adaptive LLM Judge (50 cases)
         /-----------\
        /             \  Level 2: Semantic Proximity, Privacy (PII) & Analytics
       /---------------\
      /                 \ Level 1: Unit & Guardrails Suite (<10s, deterministic)
     ---------------------
```

### Level 1: Unit & Guardrail Test Suite (Fast, <10s)
Covers input guardrails, regex greeting fastpaths (<50ms), Gradio payload extraction polymorphism, history sanitization, and the Bloom quiz state machine:
```bash
uv run pytest tests/test_chatbot.py tests/test_chat_guardrails.py tests/test_quiz_engine.py tests/test_multi_case.py tests/test_ui_theme.py -v
```

> **Telemetry Log Isolation**: Test executions automatically write to `test_classroom_chats_YYYYMMDD_HHMM.jsonl`, ensuring production classroom analytics dashboards remain 100% free of synthetic test data.

### Level 2: Semantic Proximity, Privacy & Analytics
Validates factual response embeddings (`all-MiniLM-L6-v2`), regex student ID / matriculation scrubbing, and Gini coefficient calculations:
```bash
uv run pytest tests/test_semantic_proximity.py tests/test_pii_sanitization.py tests/test_analytics.py -v
```

### Level 3: Golden Dataset Benchmarking & Dual-Layer Grader
Evaluates chatbot accuracy, pedagogical fidelity, and safety boundaries across 50 verified golden benchmark test cases using **Deterministic Heuristics (Layer 1)** + **`gemini-2.5-flash` LLM-as-a-Judge (Layer 2)**:
```bash
# Cost-optimized run (reuses cache, skips judge on clean heuristic passes):
PYTHONPATH=src uv run python src/tools/eval_golden_dataset.py --use-cache --judge-mode adaptive

# Run via Pytest:
uv run pytest tests/test_golden_dataset.py -v -s
```

### Level 4: Agentic User Simulator (Local Ollama LLM)
Simulates dynamic multi-turn dialogues across 4 student personas (*Fast Learner*, *Struggling Student*, *Adversarial Student*, *Off-Topic Drifter*) using a local `qwen2.5:3b` model:
```bash
uv run pytest tests/test_user_simulator.py -v -s
```

### Level 5: 50-Student Concurrency & Load Testing (On-Demand)
Simulates 50 concurrent students querying the case simultaneously, mid-class Quiz mode switching, and server restart recovery:
```bash
uv run pytest tests/test_load.py -v -s
```
*(Per workspace rules, Level 5 is executed only when explicitly instructed).*

---

## 🛡️ Pre-Commit Security Firewall

Every commit must pass 5 automated verification gates:
1. **Positive Path Allowlist / Blocklist**: Ensures forbidden temporary and private scratch paths are excluded.
2. **Secrets & Environment Integrity**: Confirms `.env` and API credentials are never committed.
3. **Data Integrity**: Ensures quiz banks and test fixtures are properly formatted.
4. **Token Leak Detection**: Verifies no internal private university/course names leak into public code.
5. **Spec Guardian Strict Audit**: Enforces 100% bi-directional AST traceability.

---

## 🔌 Adding a New Pedagogical Mode Plugin

To add a new operating mode to Jarvis:

1. Create a new module in `src/plugins/` (or extend `src/plugins/standard_modes.py`).
2. Implement the `ModePlugin` dataclass defined in `src/core/plugin_protocol.py`:
   ```python
   from core.plugin_protocol import ModePlugin


   def register_plugins(registry: dict[str, ModePlugin], frameworks: dict[str, str]) -> None:
       registry["socratic"] = ModePlugin(
           key="socratic",
           radio_label="Mode 3 — Socratic Inquiry",
           order=3,
           requires_framework=False,
           max_history_turns=3,
           max_output_tokens=250,
           display_name_fn=lambda state: "Mode 3 — Socratic Inquiry",
           instruction_fn=lambda state: "Guide the student through Socratic questioning...",
           event_card_fn=lambda state, name, case, format_fn: format_fn(...),
       )
   ```
3. The plugin registry automatically discovers and exposes the new mode in the Instructor Admin Panel.

---

## 🏗️ Codebase Layout & Subsystem Ownership

```text
case-room/
├── src/                               # Application source code
│   ├── core/                          # Domain engines & infrastructure
│   │   ├── cache_manager.py           # Gemini context cache lifecycle & in-memory fallback
│   │   ├── dialogue_utils.py          # Message extraction, history sanitization & fastpaths
│   │   ├── logger.py                  # Thread-safe JSONL telemetry & regex PII redaction
│   │   ├── plugin_protocol.py         # Microkernel ModePlugin protocol & registry
│   │   └── quiz_engine.py             # Bloom's quiz progression, hints & scorecard rendering
│   │
│   ├── ui/                            # Presentation & admin controls
│   │   ├── admin_handlers.py          # Admin authentication, mode staging & dashboard feeds
│   │   ├── chart_generator.py         # Matplotlib timeline & latency visualizations
│   │   ├── client_scripts.py          # Client-side JavaScript hooks & theme toggling
│   │   ├── event_cards.py             # Mode switch cards & post-quiz waiting cards
│   │   ├── gradio_app.py              # Gradio 6 Blocks layout & component binding
│   │   ├── qr_generator.py            # Screen projection QR code generator
│   │   └── ui_theme.py                # Mobile CSS, touch styling, tokens & color contrasts
│   │
│   ├── plugins/                       # Pedagogical operating modes
│   │   └── standard_modes.py          # Built-in Mode 1 (Q&A) and Mode 2 (Interactive Quiz)
│   │
│   ├── analytics_engine/              # Telemetry analysis & reporting
│   │   ├── analytics.py               # Gini participation equality, turn stats & Bloom counts
│   │   └── analytics_pdf.py           # FPDF2 4-page executive debrief PDF generation
│   │
│   ├── tools/                         # Offline utilities & evaluation harnesses
│   │   ├── eval_golden_dataset.py     # 50-case benchmark harness with LLM-as-a-judge
│   │   ├── golden_scorecard.py        # Markdown scorecard generator for benchmarks
│   │   └── preprocess_case.py         # Case PDF text extractor & noise scrubber
│   │
│   ├── chatbot.py                     # Main Gradio application & streaming loop
│   ├── config.py                      # Global AppState singleton & case study discovery
│   └── main.py                        # Alternative launcher entrypoint
│
├── specs/                             # EARS requirements & AST traceability
│   ├── analytics/                     # Telemetry & reporting specs
│   ├── core/                          # Dialogue, cache, mode & privacy specs
│   ├── eval/                          # Evaluation tools specs
│   ├── ui/                            # Theme, contrast & admin specs
│   └── traceability.json              # Normalized SHA-256 AST audit lockfile
│
├── tests/                             # 5-Level Testing Pyramid test suites
│   ├── conftest.py                    # Pytest fixtures & environment setup
│   ├── test_chatbot.py                # Level 1: Unit & pre-flight guardrail suite
│   ├── test_chat_guardrails.py        # Level 1: Input edge cases & payload parsing
│   ├── test_quiz_engine.py            # Level 1: MCQ options, hints & scorecards
│   ├── test_multi_case.py             # Level 1: Case discovery & preprocessor
│   ├── test_ui_theme.py               # Level 1: WCAG AA/AAA contrast ratios
│   ├── test_semantic_proximity.py     # Level 2: Cosine factual embeddings
│   ├── test_pii_sanitization.py       # Level 2: Student ID & phone redaction
│   ├── test_analytics.py              # Level 2: Gini index & PDF report generation
│   ├── test_golden_dataset.py         # Level 3: 50-case golden benchmark suite
│   ├── test_user_simulator.py         # Level 4: Ollama agentic multi-turn simulator
│   └── test_load.py                   # Level 5: 50-student concurrency stress test
│
└── docs/                              # Project documentation
    ├── developer/                     # Developer guides, ADRs & architecture HTML
    │   ├── ADR.md                     # Architectural Decision Records
    │   ├── README.md                  # Developer & architecture guide
    │   ├── architecture.html          # Interactive system architecture diagram
    │   ├── release.md                 # Single consolidated release log & version history
    │   └── testing.html               # Interactive testing pyramid & SDD diagram
    ├── ADDING_A_CASE_STUDY.md         # Case onboarding guide
    ├── SETUP_GUIDE.md                 # End-user setup guide
    ├── TROUBLESHOOTING.md             # Common issues & recovery
    └── USER_GUIDE.md                  # Screen-by-screen operations guide
```

