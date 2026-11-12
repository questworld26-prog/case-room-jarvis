# Classroom Telemetry Analytics & PDF Reporting Specifications

## ANLY-001: Classroom Telemetry Analytics and PDF Report Generation

The analytics engine shall parse classroom JSONL telemetry logs, compute participation and latency metrics, classify student prompts, and export PDF reports.

Acceptance Criteria:
- AC-ANLY-001.1: When given a list of per-student message counts, the analytics engine shall return 0.0 for equal participation and a bounded value between 0.0 and 1.0 for unequal distributions.
- AC-ANLY-001.2: When loading telemetry logs from a directory, the analytics engine shall parse valid JSONL lines, skip malformed lines, and exclude automated test telemetry logs by default.
- AC-ANLY-001.3: When computing classroom metrics from telemetry logs, the analytics engine shall aggregate total prompts, unique students, mean and P95 latency, mode counts, and quiz pass rates.
- AC-ANLY-001.4: When generating a classroom debrief report, the analytics engine shall classify prompts into Bloom's taxonomy tiers, render PNG charts, and export a valid PDF document.

