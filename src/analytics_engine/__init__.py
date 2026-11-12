# Copyright 2026 Sukti Ghosh and Prithis Samaddar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
