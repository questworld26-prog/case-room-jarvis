# Telemetry Logging & Student PII Privacy Specifications

## PRIV-001: Student PII Redaction and Custom Detectors

The chatbot engine and privacy scrubber shall prevent student personally identifiable information from leaking into language model responses or quiz evaluations.

Acceptance Criteria:
- AC-PRIV-001.1: When scrubbing text containing an 8-digit student identifier, the custom University ID detector shall replace the identifier with a redaction placeholder.
- AC-PRIV-001.2: When a student includes personal phone numbers, emails, or student IDs in a QA prompt, the chatbot engine shall exclude those raw identifiers from the generated response.
- AC-PRIV-001.3: When a student includes personal identifiers in an interactive quiz answer, the quiz engine shall evaluate the answer without echoing the raw identifiers.

## PRIV-002: Telemetry Log Sanitization and Environment Isolation

The telemetry logger shall scrub personally identifiable information before writing JSONL interaction records and isolate automated test logs from classroom logs.

Acceptance Criteria:
- AC-PRIV-002.1: When recording a chat turn to disk, the telemetry logger shall redact student emails, phone numbers, and 8-digit IDs from the logged prompt before writing JSONL.
- AC-PRIV-002.2: When writing a telemetry entry, the telemetry logger shall record the active `case_study` name alongside the timestamp, mode, and latency fields.
- AC-PRIV-002.3: While running inside a pytest execution environment, the telemetry logger shall route all interaction records to `logs/test_interactions.jsonl`.

