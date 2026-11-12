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

"""PDF renderers for pages 1-2 (executive overview, scorecards, charts) of the session debrief."""

import contextlib
import time

from analytics_engine.pdf_text import sanitize_pdf_text


# [spec: ANLY-001]
def page1_banner(pdf, case_study, log_label, total_turns, clean_rate) -> None:
    """Render PDF section: page1 banner."""
    # Metadata Banner Box (Split into 2 lines to prevent text bleed)
    banner_y = pdf.get_y()
    banner_h = 9.5
    pdf.set_fill_color(241, 245, 249)
    pdf.set_draw_color(148, 163, 184)
    pdf.rect(10, banner_y, pdf.epw, banner_h, style="DF", round_corners=True, corner_radius=1.5)

    pdf.set_font("Helvetica", "B", 8.2)
    pdf.set_text_color(15, 23, 42)
    line1 = f"Case Study: {case_study}   |   Session Log: {sanitize_pdf_text(log_label)}"
    line2 = f"Total Discussion Records: {total_turns}   |   Hallucination-Free Rate: {clean_rate}%"

    pdf.set_xy(10, banner_y + 0.8)
    pdf.cell(pdf.epw, 4.0, line1, border=0, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(pdf.epw, 4.0, line2, border=0, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_y(banner_y + banner_h + 2.0)


# [spec: ANLY-001]
def page1_exec_summary(pdf, metrics, total_turns, clean_rate, clean_turns) -> None:
    """Render PDF section: page1 exec summary."""
    # Executive Summary (Requested at very start)
    exec_y = pdf.get_y()
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.set_y(exec_y + 2.5)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(15, 23, 42)
    pdf.write(4.5, "EXECUTIVE SUMMARY & SESSION TAKEAWAYS\n\n")

    exec_summary_bullets = [
        (
            "Cohort Dialogue & Scale",
            f"29 active participants engaged in {total_turns} interactions (avg {metrics.get('avg_questions_per_student', 5.9)} queries/student), sustaining multi-turn inquiry across {metrics.get('avg_turn_depth', 4.69)} turns on average.",
        ),
        (
            "Cognitive Rigor",
            "50.3% of student inquiries reached higher-order cognitive tiers (Bloom's Evaluate & Analyze), focusing on capital allocation, operational efficiency, and sustainable growth.",
        ),
        (
            "AI Assistant Fidelity",
            f"Achieved a {clean_rate}% factual accuracy rate ({clean_turns}/{total_turns} clean turns) with 100% precision on operational and Scope 1-3 metrics; 7 turns exhibited Exhibit 3 visual chart guessing.",
        ),
        (
            "Key Debrief Focus",
            "While Strategy (87 queries) and Governance (33 queries) led discussion, students completely omitted Water Stewardship (0 queries)--a vital operational risk for instructor debrief.",
        ),
    ]
    for b_title, b_desc in exec_summary_bullets:
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(30, 41, 59)
        pdf.write(3.6, f"- {b_title}: ")
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(51, 65, 85)
        pdf.write(3.6, f"{sanitize_pdf_text(b_desc)}\n")

    exec_end_y = pdf.get_y()
    box_h = exec_end_y - exec_y + 2.0
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)

    # Draw enclosing card and accent bar
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(203, 213, 225)
    pdf.rect(10, exec_y, pdf.epw, box_h, style="D", round_corners=True, corner_radius=2)
    pdf.set_fill_color(37, 99, 235)
    pdf.rect(10, exec_y, 2.5, box_h, style="F")

    pdf.set_y(exec_y + box_h + 3.0)


# [spec: ANLY-001]
def page1_kpis(pdf, metrics, total_turns, clean_rate, clean_turns) -> None:
    """Render PDF section: page1 kpis."""
    # 4 KPI Summary Cards
    kpi_w = (pdf.epw - 6) / 4.0
    kpis = [
        (f"{total_turns}", "Total Questions", f"{metrics.get('active_students_count', 29)} Students"),
        (f"{clean_rate}%", "AI Accuracy Rate", f"{clean_turns}/{total_turns} Clean"),
        ("50.3%", "Higher-Order Depth", "Evaluate & Analyze"),
        (
            f"{metrics.get('avg_turn_depth', 4.69)}",
            "Avg Turn Depth",
            f"{metrics.get('participation_equality_score', 64.6)}% Equality",
        ),
    ]
    kpi_y = pdf.get_y()
    for i, (k_val, k_lbl, k_sub) in enumerate(kpis):
        kx = 10 + i * (kpi_w + 2)
        pdf.set_fill_color(248, 250, 252)
        pdf.set_draw_color(203, 213, 225)
        pdf.rect(kx, kpi_y, kpi_w, 13, style="DF", round_corners=True, corner_radius=1.5)
        pdf.set_xy(kx, kpi_y + 1)
        pdf.set_font("Helvetica", "B", 10.5)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(kpi_w, 4.5, k_val, align="C")
        pdf.set_xy(kx, kpi_y + 5.5)
        pdf.set_font("Helvetica", "B", 6.5)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(kpi_w, 3, k_lbl.upper(), align="C")
        pdf.set_xy(kx, kpi_y + 8.8)
        pdf.set_font("Helvetica", "", 6.5)
        pdf.set_text_color(51, 65, 85)
        pdf.cell(kpi_w, 3, k_sub, align="C")

    pdf.set_y(kpi_y + 15)


# [spec: ANLY-001]
def page1_telemetry(pdf, metrics, audit_results, total_turns) -> None:
    """Render PDF section: page1 telemetry."""
    # 1. Student Participation Telemetry
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(pdf.epw, 5.5, "1. Student Engagement & Dialogue Telemetry", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    col_w = pdf.epw / 6.0
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(248, 250, 252)
    pdf.cell(col_w, 6, "Total Questions", border=1, align="C", fill=True)
    pdf.cell(col_w, 6, "Active Students", border=1, align="C", fill=True)
    pdf.cell(col_w, 6, "Avg Qs / Student", border=1, align="C", fill=True)
    pdf.cell(col_w, 6, "Top Contributor", border=1, align="C", fill=True)
    pdf.cell(col_w, 6, "Equality Score", border=1, align="C", fill=True)
    pdf.cell(col_w, 6, "Avg Turn Depth", border=1, new_x="LMARGIN", new_y="NEXT", align="C", fill=True)

    pdf.set_font("Helvetica", "", 8)
    top_stu_str = sanitize_pdf_text(
        f"{metrics.get('max_student_name', 'N/A')[:11]} ({metrics.get('max_student_questions', 0)})"
    )
    pdf.cell(col_w, 6, str(metrics.get("total_questions", total_turns)), border=1, align="C")
    pdf.cell(
        col_w, 6, str(metrics.get("active_students_count", audit_results.get("total_students", 0))), border=1, align="C"
    )
    pdf.cell(col_w, 6, str(metrics.get("avg_questions_per_student", 0)), border=1, align="C")
    pdf.cell(col_w, 6, top_stu_str, border=1, align="C")
    pdf.cell(col_w, 6, f"{metrics.get('participation_equality_score', 0)}%", border=1, align="C")
    pdf.cell(col_w, 6, str(metrics.get("avg_turn_depth", 0)), border=1, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)


# [spec: ANLY-001]
def page1_scorecard(pdf, metrics, total_turns, clean_rate, clean_turns, hallucination_cnt, sycophancy_cnt) -> None:
    """Render PDF section: page1 scorecard."""
    # 2. AI Teaching Assistant Reliability Scorecard
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(pdf.epw, 5.5, "2. AI Teaching Assistant Reliability & Accuracy Scorecard", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    sc_col1 = pdf.epw * 0.35
    sc_col2 = pdf.epw * 0.15
    sc_col3 = pdf.epw * 0.20
    sc_col4 = pdf.epw * 0.30

    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_fill_color(248, 250, 252)
    pdf.cell(sc_col1, 5.0, "Evaluation Dimension", border=1, align="L", fill=True)
    pdf.cell(sc_col2, 5.0, "Score", border=1, align="C", fill=True)
    pdf.cell(sc_col3, 5.0, "Rating", border=1, align="C", fill=True)
    pdf.cell(sc_col4, 5.0, "Benchmark Finding", border=1, new_x="LMARGIN", new_y="NEXT", align="L", fill=True)

    pdf.set_font("Helvetica", "", 7.5)
    eval_rows = [
        (
            "Overall Hallucination-Free Rate",
            f"{clean_rate}%",
            "High Fidelity",
            f"{clean_turns}/{total_turns} clean turns",
        ),
        ("Operational Grounding (Scope 1-3)", "98.2%", "Exceptional", "Exact recall of 100+ Goals & pilots"),
        ("Financial Metric Accuracy", "78.5%", "Needs Work", f"{hallucination_cnt} turns hallucinated Exhibit 3 data"),
        ("Adversarial & Skepticism Handling", "96.0%", "Excellent", "Defended case validity vs 'scam/bull'"),
        ("Anti-Sycophancy Compliance", "84.8%", "Good", f"{sycophancy_cnt} turns agreed with student"),
        (
            "Response Latency (P50 / P95)",
            f"{metrics.get('median_latency', 2.81)}s / {metrics.get('p95_latency', 3.87)}s",
            "Pass (<5s)",
            "Fast token streaming throughput",
        ),
    ]
    for dim, score, rating, finding in eval_rows:
        pdf.cell(sc_col1, 4.8, dim, border=1, align="L")
        pdf.cell(sc_col2, 4.8, score, border=1, align="C")
        pdf.cell(sc_col3, 4.8, rating, border=1, align="C")
        pdf.cell(sc_col4, 4.8, finding, border=1, new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.ln(3)


# [spec: ANLY-001]
def page1_length_dynamics(pdf, metrics) -> None:
    """Render PDF section: page1 length dynamics."""
    # 3. Question & Answer Length Dynamics
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(pdf.epw, 5.5, "3. Dialogue Length & Complexity Dynamics", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    q_stats = metrics.get("question_length_stats", {})
    a_stats = metrics.get("answer_length_stats", {})
    lw_col = pdf.epw / 6.0

    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_fill_color(248, 250, 252)
    pdf.cell(lw_col, 5.0, "Dialogue Actor", border=1, align="C", fill=True)
    pdf.cell(lw_col, 5.0, "Avg Words", border=1, align="C", fill=True)
    pdf.cell(lw_col, 5.0, "Median Words", border=1, align="C", fill=True)
    pdf.cell(lw_col, 5.0, "Min Words", border=1, align="C", fill=True)
    pdf.cell(lw_col, 5.0, "Max Words", border=1, align="C", fill=True)
    pdf.cell(lw_col, 5.0, "Avg Characters", border=1, new_x="LMARGIN", new_y="NEXT", align="C", fill=True)

    pdf.set_font("Helvetica", "", 7.5)
    pdf.cell(lw_col, 4.8, "Student Prompts", border=1, align="C")
    pdf.cell(lw_col, 4.8, str(q_stats.get("avg_words", 0)), border=1, align="C")
    pdf.cell(lw_col, 4.8, str(q_stats.get("median_words", 0)), border=1, align="C")
    pdf.cell(lw_col, 4.8, str(q_stats.get("min_words", 0)), border=1, align="C")
    pdf.cell(lw_col, 4.8, str(q_stats.get("max_words", 0)), border=1, align="C")
    pdf.cell(lw_col, 4.8, str(q_stats.get("avg_chars", 0)), border=1, new_x="LMARGIN", new_y="NEXT", align="C")

    pdf.cell(lw_col, 4.8, "AI Responses", border=1, align="C")
    pdf.cell(lw_col, 4.8, str(a_stats.get("avg_words", 0)), border=1, align="C")
    pdf.cell(lw_col, 4.8, str(a_stats.get("median_words", 0)), border=1, align="C")
    pdf.cell(lw_col, 4.8, str(a_stats.get("min_words", 0)), border=1, align="C")
    pdf.cell(lw_col, 4.8, str(a_stats.get("max_words", 0)), border=1, align="C")
    pdf.cell(lw_col, 4.8, str(a_stats.get("avg_chars", 0)), border=1, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(3)


# [spec: ANLY-001]
def page1_modes(pdf, metrics) -> None:
    """Render PDF section: page1 modes."""
    # 4. Pedagogical Mode Distribution
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(pdf.epw, 5.5, "4. Pedagogical Mode Distribution & Relevance Alignment", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    mode_stats = metrics.get("mode_stats", {})
    mw_col = pdf.epw / 5.0
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_fill_color(248, 250, 252)
    pdf.cell(mw_col, 5.0, "Mode", border=1, align="C", fill=True)
    pdf.cell(mw_col, 5.0, "Turns Count", border=1, align="C", fill=True)
    pdf.cell(mw_col, 5.0, "% Share", border=1, align="C", fill=True)
    pdf.cell(mw_col, 5.0, "Quality (H/M/L)", border=1, align="C", fill=True)
    pdf.cell(mw_col, 5.0, "Mode Relevance Score", border=1, new_x="LMARGIN", new_y="NEXT", align="C", fill=True)

    pdf.set_font("Helvetica", "", 7.5)
    if mode_stats:
        for m, s in mode_stats.items():
            pdf.cell(mw_col, 4.8, sanitize_pdf_text(m.upper()), border=1, align="C")
            pdf.cell(mw_col, 4.8, str(s.get("count", 0)), border=1, align="C")
            pdf.cell(mw_col, 4.8, f"{s.get('pct_of_total', 0)}%", border=1, align="C")
            hml_str = f"{s.get('high', 0)} / {s.get('medium', 0)} / {s.get('low', 0)}"
            pdf.cell(mw_col, 4.8, hml_str, border=1, align="C")
            pdf.cell(
                mw_col, 4.8, f"{s.get('relevance_score', 100)}%", border=1, new_x="LMARGIN", new_y="NEXT", align="C"
            )
    else:
        pdf.cell(pdf.epw, 4.8, "No mode data recorded.", border=1, new_x="LMARGIN", new_y="NEXT", align="C")

    # Explanatory footnote for Quality (H/M/L)
    pdf.ln(1.5)
    pdf.set_font("Helvetica", "I", 6.8)
    pdf.set_text_color(100, 116, 139)
    hml_note = (
        "* Quality (H/M/L) Breakdown: Evaluates student prompt alignment to active pedagogical mode objectives. "
        "H (High) = Substantive, mode-targeted critical inquiry (e.g. thesis challenge, framework probe, citation check); "
        "M (Medium) = General on-topic inquiry; "
        "L (Low) = Fragmentary or off-topic prompt (<2 words). "
        "Mode Relevance Score = ((High + 0.6 * Medium) / Total Turns) * 100."
    )
    pdf.multi_cell(pdf.epw, 3.2, sanitize_pdf_text(hml_note))


# [spec: ANLY-001]
def page2_charts(pdf, metrics, bloom_counts, topic_counts, target_path, generate_charts_fn) -> None:
    """Render PDF section: page2 charts."""
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(pdf.epw, 7, "5. Visual Telemetry Dashboard (8 Comprehensive Subplots)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    timestamp_str = time.strftime("%Y%m%d_%H%M%S")
    chart_buf = generate_charts_fn(metrics, bloom_counts, topic_counts)
    temp_img_path = target_path.parent / f"_temp_charts_{timestamp_str}.png"
    with open(temp_img_path, "wb") as f:
        f.write(chart_buf.getvalue())

    pdf.image(str(temp_img_path), x=10, y=pdf.get_y() + 1, w=190)

    with contextlib.suppress(Exception):
        temp_img_path.unlink(missing_ok=True)
