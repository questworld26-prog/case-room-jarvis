# Instructor Admin Controls & Live Broadcast Specifications

## ADMIN-001: Instructor Mode Staging, Broadcast and Runtime Configuration

The instructor admin handler module shall stage pedagogical mode changes, broadcast live mode transitions to students, and update runtime model parameters.

Acceptance Criteria:
- AC-ADMIN-001.1: When an instructor selects a pedagogical mode button, `set_pending_mode` shall stage `pending_mode` without mutating `active_mode` until `confirm_mode_broadcast` executes.
- AC-ADMIN-001.2: When `active_mode` changes between a student's turns, the chatbot engine shall prepend a live mode switch event card banner to the student's next response.
- AC-ADMIN-001.3: When an instructor updates the context cache TTL or Gemini model identifier, the admin handler module shall update `app_state` and return a confirmation status string.
- AC-ADMIN-001.4: When authenticating admin credentials or rendering HTML cards, the application shall verify passwords via `compare_digest` and escape untrusted HTML strings.
- AC-ADMIN-001.5: When a client requests a file from the static fallback endpoint, the server shall resolve the target path and block any path outside `static`.

