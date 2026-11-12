---
title: "Classroom Flow"
layout: default
nav_order: 4
---

# Instructor Classroom Operating Workflow & Architecture Context

This document captures the exact operational pattern and requirements for using the Business Case Chatbot in a live classroom environment. Agents and contributors should reference this document for all future reviews, test setups, and architectural decisions.

---

## 1. Operating Profile & Context

- **Event Type**: Live 3-Hour Interactive Executive / MBA Classroom Workshop.
- **Audience**: ~50 Students using heterogeneous personal devices (macOS, Windows, iOS Safari, Android Chrome, iPadOS).
- **Host**: Single instructor laptop (macOS / Apple Silicon) running the server locally, closed and powered down immediately after class.
- **Access Model**: Students connect over classroom Wi-Fi or local network via a scanned QR code to the student UI.

---

## 2. Instructor Pre-Class & Live Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Instructor
    participant App as Instructor Laptop (Gradio Server)
    participant Gemini as Google Gemini Context API
    actor Students as 50 Students (Mobile/Laptop)

    Note over Instructor,App: Step 1: Pre-Class Start (10 min before)
    Instructor->>App: Launch app (`uv run python src/chatbot.py`)
    App-->>Instructor: Prints public https://xxxx.gradio.live URL + QR code
    Instructor->>App: Open Admin Panel tab, enter password, press Enter
    
    Note over Instructor,Gemini: Step 2: Case Selection & Cache Loading
    Instructor->>App: Select Case Study (e.g. EcoBrew) & set Session ID
    Instructor->>App: Click "🚀 Load Selected Case Study"
    App->>Gemini: Prime cache / load clean context
    Gemini-->>App: Cache Name / ID + Status Active
    App-->>Instructor: Green Badge: "✅ Active Case Study set to..."

    Note over Instructor,App: Step 3: Mode Setting & Broadcast
    Instructor->>App: Select Pedagogical Mode (Q&A or Quiz)
    Instructor->>App: Click "📢 Broadcast Mode to Students"
    
    Note over Instructor,Students: Step 4: Classroom Onboarding
    Instructor->>Students: Project QR code from Admin screen or static/classroom_qr.png
    Students->>App: Scan QR Code on mobile/laptop -> Enters Student Chatroom
    Students->>App: Enter Full Name
    
    Note over Students,Gemini: Step 5: Live 3-Hour Class Breakouts
    Students->>App: 50 concurrent students query the case study
    App->>Gemini: Stream content with context cache (Sub-3s latency)
    Gemini-->>Students: Responsive, grounded Socratic answers
    
    Note over Instructor,App: Step 6: Post-Class Teardown
    Note over App: Every message auto-logged to logs/classroom_chats_YYYYMMDD_HHMM.jsonl
    Instructor->>App: Stop local server (Ctrl + C) / close laptop
```

---

## 3. Detailed Step-by-Step Operating Flow

### Step 1: Launch App
- Instructor starts the server on laptop before class (`uv run python src/chatbot.py`).
- Terminal verifies `GOOGLE_API_KEY`, spins up Gradio with a public tunnel, and prints `https://xxxx.gradio.live`.

### Step 2: Access Admin Section
- Instructor opens the `gradio.live` link in their browser.
- Switch to the **🔐 Instructor Admin Panel** tab.
- Type `ADMIN_PASSWORD` (default `admin123`, configured in `.env`) and **press Enter** to unlock controls.

### Step 3: Select Case & Load Context
- Set the **Active Classroom Session Identifier** (e.g., `Section_A` or `Week5_Tue`) before loading.
- Select the active case folder from **Available Case Studies**.
- Verify or adjust Cache TTL (default: **4 hours** / `14400s`).
- Click **🚀 Load Selected Case Study**:
  - The server loads preprocessed text context (or auto-extracts from PDFs).
  - Warmed Gemini cache handle is established with ~95% token savings.
  - Active session locks to protect log consistency.

### Step 4: Set Class Mode & Broadcast
- Select desired pedagogical mode:
  - **Mode 1 — Standard Q&A (Default)**
  - **Mode 2 — Interactive Quiz & Assessment**
- Click **📢 Broadcast Mode to Students**. All connected student screens instantly receive the mode update card (and Quiz Question #1 if Quiz mode).

### Step 5: Share QR Code with the Class
- Project the high-contrast QR code directly from the Admin Panel or open `static/classroom_qr.png`.
- Students scan with phone or laptop cameras, enter their **Full Name**, and begin asking questions.

### Step 6: Post-Class Shutdown
- Every student interaction, timestamp, latency, and reply is automatically written to `logs/classroom_chats_YYYYMMDD_HHMM.jsonl` with student PII redacted.
- Instructor stops the local server by pressing `Ctrl + C` in the terminal.
