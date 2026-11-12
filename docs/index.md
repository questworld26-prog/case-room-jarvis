---
title: "Overview"
layout: default
nav_order: 1
has_children: false
permalink: /
---

# Case-Room — Classroom AI Copilot

Case-Room is a real-time classroom AI assistant designed for business school professors and students. It answers student questions strictly from assigned business case studies, runs Socratic multiple-choice and open-ended quizzes, and delivers live session telemetry to instructors.

---

## 🌟 Interactive Diagrams

Explore the system topologies directly in your browser:

- 🏛️ **[Interactive System Architecture](developer/architecture.html)**: Interactive component topology mapping student mobile ingress, Gradio TLS tunneling, dialogue guardrails, microkernel plugins, context cache management, and Gemini 2.5 Flash LLM integration.
- 🧪 **[Testing & Verification Pipeline](developer/testing.html)**: Interactive visual tour of the 5-Level Testing Pyramid, ISO/IEC/IEEE 29148 EARS audit loops, and dual-layer LLM-as-a-judge grader.

---

## 📖 Documentation Sections

| Guide | Description |
| :--- | :--- |
| **[Setup Guide](SETUP_GUIDE)** | Step-by-step instructions for installation, UV package setup, and Gemini API keys. |
| **[User Guide](USER_GUIDE)** | Detailed operational guide for instructors, teaching assistants, and students. |
| **[Classroom Flow](CLASSROOM_FLOW)** | Pedagogical runbook for running Case-Room live in lectures and breakout groups. |
| **[Adding a Case Study](ADDING_A_CASE_STUDY)** | Tutorial on authoring case packs, markdown quiz banks (`quiz.md`), and metadata. |
| **[Troubleshooting](TROUBLESHOOTING)** | Solutions for common network, caching, quota, and authentication issues. |
| **[Developer Guide](developer/)** | Architectural deep dive, microkernel plugin model, and Spec-Driven Development (SDD). |

---

## 🛡️ Privacy & Compliance

Chat logs are stored **strictly locally on the instructor's laptop** in the `logs/` directory. Student identifiers (emails, phone numbers, student IDs) are automatically masked before writing to telemetry. No student conversation data is persisted to public cloud storage or shared across classes.
