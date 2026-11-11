"""Classroom engagement analytics and debrief report generation."""

from analytics_engine.analytics import (
    classify_prompts_ai,
    compute_metrics,
    generate_ai_teaching_debrief,
    generate_analytics_charts,
    get_available_log_files,
    load_telemetry_logs,
)
from analytics_engine.analytics_pdf import (
    ReportPDF,
    generate_pdf_report,
    generate_unified_session_report_pdf,
)

__all__ = [
    "classify_prompts_ai",
    "compute_metrics",
    "generate_ai_teaching_debrief",
    "generate_analytics_charts",
    "get_available_log_files",
    "load_telemetry_logs",
    "ReportPDF",
    "generate_pdf_report",
    "generate_unified_session_report_pdf",
]
