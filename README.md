# Business Case Study Chatbot ("Jarvis") — Open-Core Edition

An AI-powered interactive teaching assistant designed for undergraduate business students exploring the **EcoBrew Sustainability & Global Strategy Case Study**  in a 3-hour classroom session (50 students).

---

## 🎯 Goal

Provide a **scalable, cost-effective, high-speed, and interactive AI chatbot** ("Jarvis") that acts as an authoritative case study companion during class. 

Jarvis grounds all answers strictly in the provided business case study documents, supporting free-form Q&A, knowledge assessment quizzes, and citation verification (with extensible plugin architecture for additional pedagogical modes) — with zero cloud infrastructure cost and sub-3 second response latency.

For technical design rationale and architectural records, see [Architecture Decision Records (docs/ADR.md)](docs/ADR.md).

---

## ✨ Features

### 1. High-Speed Knowledge Engine & Latency Optimization
- **Cleaned Text Pipeline**: Directly injects noise-reduced `extracted_context.txt` into system instructions, keeping response times consistently under **1.5s–3.5s** and hard-capping latency well under **7s**.
- **Instant Greeting Interceptor (<0.05s)**: Local memory short-circuit for pure greetings (`hi`, `hello`, `hey`) and quiz triggers (`k`, `ready`), providing instant mode-aware welcomes without API network overhead.
- **Initial Onboarding Welcome Card**: Renders a clean introductory welcome card upon first load prompting students to enter their Full Name and ask case-related questions.
- **Strict 200-Word & 350-Token Ceiling**: Enforces crisp, mobile-friendly responses and fast streaming throughput.
- **Thread-Safe Telemetry & Resilience**: Thread-locked JSONL telemetry logging and exponential backoff retry loops for handling API quota limits gracefully.

### 2. Pedagogical Operating Modes (Microkernel Architecture)
- **Mode 1: Standard Q&A (Built-in Plugin)**: Direct, factual answers based strictly on case documents, delivered in a polite, professional tone.
- **Mode 2: Interactive Quiz & Assessment (Built-in Plugin)**: Bloom's taxonomy sequential quiz progression with MCQs and open-ended questions. Features a **2-attempt rule**, hint generation, and instant scorecard.
- **Extensible Pedagogical Plugins**: Additional custom pedagogical modes can be plugged in seamlessly via `src/plugins/` adhering to the `ModePlugin` protocol in `src/core/plugin_protocol.py`.

### 3. Student Chat & Redesigned Instructor Admin Interface
- **🔐 Redesigned Instructor Admin Panel**: Password-authenticated control center (default password: `admin123`). Password input fields automatically hide upon successful unlock for a clean, distraction-free UI.
- **⚡ Active Session Overview Header**: High-visibility dark-glass summary card at top of admin panel displaying Active Case Study, Active Mode, Selected Framework, Gemini Model ID, and Cache TTL / Duration in real time.
- **📊 Live Class Dashboard**: Positioned at top of admin panel with **10-second auto-refresh timer** (no manual refresh button needed).
- **📈 Dual Live Matplotlib Plots**: Side-by-side real-time charts displaying **Student Activity Timeline (Messages / Min)** and **Response Latency Tracker (Sec)** across the last 30 minutes.
- **📢 Staged Classroom Mode Broadcast**: 2-step mode selection (radio button stage -> `📢 Broadcast Mode to Students` confirmation button) pushing mode announcements and Quiz Question #1 directly into all active student browsers without requiring page reloads.
- **Screen Projection QR Code**: Automatically generates `static/classroom_qr.png` on launch, linking directly to the public Gradio `share=True` URL for projection on classroom screens.
- **Unified Classroom Evaluation Pipeline & Executive PDF Debrief (`src/tools/eval_classroom_logs.py`)**: Unified offline evaluation CLI computing Gini participation equality scores, Bloom's Taxonomy cognitive breakdowns, question frequency histograms, AI accuracy/hallucination audits, and publication-grade multi-page executive PDF debrief reports (`Session_Debrief_Report_*.pdf`).

---

## 🛠️ Prerequisites

- **Python**: `>=3.13`
- **Package Manager**: [`uv`](https://github.com/astral-sh/uv) (recommended)
- **API Key**: Google GenAI API Key (`GOOGLE_API_KEY`) set in `.env`

---

## 🚀 How to Run the App

### 1. Environment Setup
Clone the repository and install dependencies using `uv`:
```bash
uv sync
```

### 2. Configure Environment Variables
Ensure `.env` exists in the root directory:
```env
GOOGLE_API_KEY=AIzaSy...
MODEL_ID=gemini-2.5-flash
CACHE_TTL=30s
ADMIN_PASSWORD=admin123
```

### 3. Launch Application
Launch the application using either entrypoint:
```bash
# Option A: Package main entrypoint (recommended)
PYTHONPATH=src uv run python src/main.py

# Option B: Chatbot entrypoint
PYTHONPATH=src uv run python src/chatbot.py
```

Upon launching:
1. The public Gradio URL (e.g. `https://xxxx.gradio.live`) will be printed in the terminal.
2. A QR Code image will be generated at `static/classroom_qr.png`. Project this QR code on the classroom screen for students to scan.

### 4. Multi-Case Preprocessor (`src/tools/preprocess_case.py`)
To add a new business case study:
1. Create a folder in `resource/` (e.g., `resource/NewCase/`, `resource/AnotherCase/`).
2. Add your case study PDF files inside that folder.
3. Run the preprocessor:
```bash
PYTHONPATH=src uv run python src/tools/preprocess_case.py --case EcoBrew
# Or preprocess all:
PYTHONPATH=src uv run python src/tools/preprocess_case.py --case all
```

---

## 🧪 Testing Strategy & Execution

Our automated testing strategy is structured across a **5-Level Testing Pyramid** to guarantee correctness, speed, privacy, and high-concurrency resilience:

### Level 1: Unit & Guardrail Test Suite (Deterministic, Fast, <10s)
Covers input guardrails, regex instant fastpaths (<50ms), Gradio payload extraction polymorphism, history sanitizers, and Bloom's quiz engine:
```bash
uv run pytest tests/test_chatbot.py tests/test_chat_guardrails.py tests/test_quiz_engine.py tests/test_multi_case.py -v
```
> **Telemetry Log Isolation**: Automated test and build executions automatically write to separate `test_classroom_chats_YYYYMMDD_HHMM.jsonl` log files, ensuring real classroom analytics dashboards remain 100% free of synthetic test data.

### Level 2: Semantic Proximity, Privacy & Analytics
Validates factual response embeddings (`all-MiniLM-L6-v2`), PII redaction (University Student ID & Scrubadub), and Gini participation metric calculation:
```bash
uv run pytest tests/test_semantic_proximity.py tests/test_pii_sanitization.py tests/test_analytics.py -v
```

### Level 3: Golden Dataset Benchmarking & Multi-Rubric Dual-Layer Grader
Evaluates chatbot accuracy, pedagogical fidelity, and safety boundaries across 50 verified golden benchmark test cases (factual metrics, strategic synthesis, quiz comprehension, anti-sycophancy, jailbreak deflection, and negative fictional traps) using **Deterministic Heuristics (Layer 1)** + **`gemini-3.5-flash` LLM-as-a-Judge (Layer 2)**:
```bash
# Option A: Cost-Optimized Run (Strategy 2 Cache + Strategy 3 Adaptive Judge) -> ~$0.0072 cost:
PYTHONPATH=src uv run python src/tools/eval_golden_dataset.py --use-cache --judge-mode adaptive

# Option B: Live Adaptive Benchmark (Refreshes completions, skips judge on clean factual passes):
PYTHONPATH=src uv run python src/tools/eval_golden_dataset.py --judge-mode adaptive --threshold 95

# Option C: Non-determinism validation with Pass@3 sampling:
PYTHONPATH=src uv run python src/tools/eval_golden_dataset.py --pass-at-k 3 --threshold 95

# Option D: Fast Deterministic Evaluation (Zero LLM Tokens):
PYTHONPATH=src uv run python src/tools/eval_golden_dataset.py --no-judge

# Option E: Run via Automated Pytest Suite:
uv run pytest tests/test_golden_dataset.py -v -s
```
> **Cost Optimization & Telemetry**: Evaluates fuzzy oracles with full LLM rigor while bypassing redundant judge calls on clean factual matches. Automatically exports snapshot cache to `data/golden_response_cache.json`, JSON telemetry to `data/eval_results.json`, and a Markdown scorecard to `docs/eval_scorecard.md`.

### Level 4: Agentic User Simulator (Ollama Local LLM)
Simulates dynamic multi-turn dialogues across 4 student personas (Fast Learner, Struggling Student, Adversarial Student, Off-Topic Drifter) evaluated via a local `qwen2.5:3b` model:
```bash
uv run pytest tests/test_user_simulator.py -v -s
```

### Level 5: 50-Student Concurrency & Load Testing (Manual On-Demand Only)
Simulates 50 concurrent students asking diverse multi-turn questions, mid-class Quiz mode switching, and supervisor server restart recovery:
```bash
uv run pytest tests/test_load.py -v -s
```
*(Note: Per workspace directives, execute Level 5 load tests only when explicitly requested).*

---

## 📁 Repository Structure

```text
case-room/
├── src/                               # 📁 Application & library source code
│   ├── core/                          # Domain services & engines
│   │   ├── cache_manager.py           # Gemini context cache manager
│   │   ├── dialogue_utils.py          # Message extraction & prompt cleaning
│   │   ├── quiz_engine.py             # Bloom's quiz progression & scoring
│   │   │   ├── logger.py                  # Thread-safe JSONL telemetry logger
│   │   └── __init__.py
│   ├── ui/                            # Presentation & admin controls
│   │   ├── ui_theme.py                # Mobile CSS, touch styling & glowing cards
│   │   ├── admin_handlers.py          # Admin controls & live telemetry charts
│   │   ├── chart_generator.py         # Matplotlib visualizations
│   │   ├── qr_generator.py            # Projection QR code generator
│   │   └── __init__.py
│   ├── analytics_engine/              # Telemetry analysis & reporting
│   │   ├── analytics.py               # Engagement metrics, Gini & log parsing
│   │   ├── analytics_pdf.py           # FPDF2 report generation
│   │   └── __init__.py
│   ├── tools/                         # Offline preprocessing & evaluations
│   │   ├── preprocess_case.py         # Case PDF text extractor & builder
│   │   ├── eval_golden_dataset.py     # Multi-case benchmark harness
│   │   ├── eval_classroom_logs.py     # Standalone live classroom audit engine
│   │   └── __init__.py
│   ├── chatbot.py                     # Main Gradio application
│   ├── config.py                      # Global configuration & app state
│   └── main.py                        # Launcher entrypoint
│
│
│
├── docs/                              # 📁 Documentation & architectural artifacts
│   ├── ADR.md                         # Architecture Decision Records (ADR 001–013)
│   ├── CLASSROOM_FLOW.md              # Live classroom operations guide
├── RELEASE.md                         # Version history & release notes
│
├── tests/                             # 📁 5-Tier Testing Pyramid test suites
├── data/                              # 📁 Quiz banks, prompts, eval datasets
├── resource/                          # 📁 Case study source PDFs & texts
├── logs/                              # 📁 Telemetry logs
├── static/                            # 📁 Generated QR & chart images
├── pyproject.toml                     # 📁 Project metadata & tool settings
├── README.md                          # 📁 Setup & execution guide
└── AGENTS.md                          # 📁 Workspace directives
```

---

## 🛠️ Classroom Troubleshooting & Recovery Guide

| Symptom / Issue | Root Cause | Recovery Step |
| :--- | :--- | :--- |
| **Student UI displays "Disconnected" or red error banner** | Browser tab went idle (>5 mins) or student mobile Wi-Fi dropped, closing the Gradio WebSocket connection. | **Refresh Browser Page (F5 / Pull-to-Refresh)**. The student tab will instantly reconnect to the active server session without losing context. |
| **"⚠️ No Case Study Selected" message** | The chatbot server was restarted and the case study hasn't been initialized in the Admin Panel yet. | Instructor opens **🔐 Instructor Admin Panel** tab -> Selects active case study -> Clicks **🚀 Load Selected Case Study**. |
| **"⚠️ Student Name Required"** | Student attempted to send a question before entering their name. | Enter Full Name in the top textbox. |
| **"Resource Exhausted / 429 Rate Limit"** | Peak student submissions hit Google GenAI free-tier API quota limit. | System automatically retries with exponential backoff. If persistent, configure a billing-enabled `GOOGLE_API_KEY` in `.env`. |
| **Server Crash or Unresponsive Laptop** | Server process terminated or memory full. | Re-run application: `PYTHONPATH=src uv run python src/main.py`. The app will automatically resume. |


