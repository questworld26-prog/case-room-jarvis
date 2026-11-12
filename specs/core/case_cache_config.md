# Case Discovery, Preprocessing & Context Cache Specifications

## CACHE-001: Dynamic Case Discovery and Preprocessing Pipeline

The case preprocessing and configuration modules shall discover available case study folders and compile raw PDF and CSV files into a clean context document.

Acceptance Criteria:
- AC-CACHE-001.1: When scanning the data directory, the system shall return a sorted list of available case study folder names.
- AC-CACHE-001.2: When preprocessing a case study folder containing PDFs and CSVs, the preprocessing tool shall generate a consolidated clean text document with a manifest header.

## CACHE-002: Context Cache Lifecycle and Recovery

The cache manager shall load preprocessed case text into application state and manage the Gemini context cache lifecycle across server restarts.

Acceptance Criteria:
- AC-CACHE-002.1: When a case study is selected, the cache manager shall load the case text into `app_state.case_text_context` and initialize the active context cache.
- AC-CACHE-002.2: When initializing or reading the context cache without a forced refresh, the cache manager shall retain or restore the loaded case text context exceeding 1000 characters.

## CACHE-003: Empty or Incomplete Case Study Folder Diagnostics

While scanning case directories or loading a selected case study, the case management system shall detect empty or incomplete case study folders missing readable case materials or quiz banks and present prominent error diagnostics.

Acceptance Criteria:
- AC-CACHE-003.1: When scanning case study directories on startup or refresh, the validation scanner shall include folders missing readable case materials or missing a markdown quiz bank in the reported startup diagnostics.
- AC-CACHE-003.2: When an instructor loads or refreshes a case study directory containing zero characters of readable case text, the admin panel shall display an error diagnostic, prevent session locking, and clear any stale active context cache.
- AC-CACHE-003.3: When loading a case study directory that lacks readable case materials, the context loader shall avoid duplicate empty extraction scans and log one diagnostic warning.
- AC-CACHE-003.4: While any discovered case study directory lacks case materials or a markdown quiz bank, the admin panel top alert banner shall list each incomplete folder with setup instructions and clear automatically once resolved.

