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

