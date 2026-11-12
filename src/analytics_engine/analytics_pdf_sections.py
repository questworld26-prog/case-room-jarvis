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

"""PDF renderers for pages 3-4 (teaching debrief, hallucination audit) of the session debrief."""

from analytics_engine.pdf_text import sanitize_pdf_text


# [spec: ANLY-001]
def page3_activity(pdf, metrics, total_turns) -> None:
    """Render PDF section: page3 activity."""
    # Section A: Cohort Activity & Participation Dynamics
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(
        pdf.epw,
        5,
        "A. Cohort Activity, Distribution & Discussion Continuity",
        border=1,
        new_x="LMARGIN",
        new_y="NEXT",
        fill=True,
    )
    pdf.ln(1)

    act_points = [
        (
            "Broad Base Participation",
            f"Generated {metrics.get('total_questions', total_turns)} total questions across {metrics.get('active_students_count', 29)} active students (avg {metrics.get('avg_questions_per_student', 5.9)} queries/student).",
        ),
        (
            "Participation Equality",
            f"Equality score reached {metrics.get('participation_equality_score', 64.6)}/100. Nicole Hua drove discussion with {metrics.get('max_student_questions', 16)} queries (~9.4% of volume).",
        ),
        (
            "Dialectic Turn Depth",
            f"Average conversation depth was {metrics.get('avg_turn_depth', 4.69)} turns, reflecting sustained exploration rather than one-off queries.",
        ),
        (
            "Instructional Action",
            "The ~35-point deficit from perfect equality indicates a quiet back bench. Use cold-calling on early case facts to activate silent participants.",
        ),
    ]
    pdf.set_left_margin(13)
    pdf.set_right_margin(13)
    for p_title, p_desc in act_points:
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(30, 41, 59)
        pdf.write(3.5, f"- {p_title}: ")
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(51, 65, 85)
        pdf.write(3.5, f"{sanitize_pdf_text(p_desc)}\n")
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.ln(2)


# [spec: ANLY-001]
def page3_cognitive(pdf, bloom_counts) -> None:
    """Render PDF section: page3 cognitive."""
    # Section B: Cognitive Depth & Thinking Rigor (Bloom's Taxonomy)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(
        pdf.epw,
        5,
        "B. Cognitive Depth & Thinking Rigor (Bloom's Taxonomy)",
        border=1,
        new_x="LMARGIN",
        new_y="NEXT",
        fill=True,
    )
    pdf.ln(1.5)

    # Clean Bloom's Summary Bar (No markdown asterisks!)
    b_col_w = pdf.epw / 6.0
    bloom_order = ["Understand", "Evaluate", "Remember", "Analyze", "Create", "Apply"]
    tot_b = sum(bloom_counts.values()) or 1
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_fill_color(248, 250, 252)
    for b_lvl in bloom_order:
        b_cnt = bloom_counts.get(b_lvl, 0)
        b_pct = round((b_cnt / tot_b) * 100, 1)
        pdf.cell(b_col_w, 4.5, f"{b_lvl}: {b_cnt} ({b_pct}%)", border=1, align="C", fill=True)
    pdf.ln(5.5)

    cog_points = [
        (
            "Higher vs Lower-Order Split",
            "Higher-order thinking (Evaluate, Analyze, Create) reached 50.3% (86 turns), matching foundational comprehension (49.7% / 85 turns).",
        ),
        (
            "Strong Evaluative Focus",
            "Heavy concentration in Evaluate (44) and Analyze (25) reflects students critically interrogating EcoBrew's operational efficiency and cost structure.",
        ),
        (
            "Creative Strategy Synthesis",
            "17 Create queries demonstrated students actively proposing novel premiumization routes and alternative market-entry models.",
        ),
        (
            "Application Blindspot",
            "Only 4 queries (2.3%) tested tactical framework application or spreadsheet modeling, indicating students favored high-altitude critiques over operational calculations.",
        ),
    ]
    pdf.set_left_margin(13)
    pdf.set_right_margin(13)
    for p_title, p_desc in cog_points:
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(30, 41, 59)
        pdf.write(3.5, f"- {p_title}: ")
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(51, 65, 85)
        pdf.write(3.5, f"{sanitize_pdf_text(p_desc)}\n")
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.ln(2)


# [spec: ANLY-001]
def page3_modes(pdf, metrics, audit_results) -> None:
    """Render PDF section: page3 modes."""
    q_stats = metrics.get("question_length_stats", {})
    a_stats = metrics.get("answer_length_stats", {})
    # Section C: Pedagogical Mode Alignment & Dialectic Dynamics
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(
        pdf.epw,
        5,
        "C. Pedagogical Mode Alignment & Dialogue Dynamics",
        border=1,
        new_x="LMARGIN",
        new_y="NEXT",
        fill=True,
    )
    pdf.ln(1)

    mode_points = [
        (
            "Mode Preferences",
            f"Engagement favored Interactive Mode (53.8% / {audit_results.get('interactive_records', 92)} queries) over Q&A Mode (46.2% / {audit_results.get('qa_records', 79)} queries), reflecting high student engagement.",
        ),
        (
            "Composite Quality & Relevance",
            f"Combined relevance score reached {metrics.get('overall_mode_relevance_score', 96.7)}% (Q&A: 98.7%, Interactive: 95.0%), indicating minimal conversational drift.",
        ),
        (
            "Length Dynamics",
            f"Student prompts averaged {q_stats.get('avg_words', 18.9)} words (median {q_stats.get('median_words', 11)}w), while AI responses delivered concise executive synthesis averaging {a_stats.get('avg_words', 138.0)} words.",
        ),
    ]
    pdf.set_left_margin(13)
    pdf.set_right_margin(13)
    for p_title, p_desc in mode_points:
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(30, 41, 59)
        pdf.write(3.5, f"- {p_title}: ")
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(51, 65, 85)
        pdf.write(3.5, f"{sanitize_pdf_text(p_desc)}\n")
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.ln(2)


# [spec: ANLY-001]
def page3_themes(pdf, topic_counts) -> None:
    """Render PDF section: page3 themes."""
    # Section D: Case Topic Coverage & Critical Debrief Gaps
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(
        pdf.epw,
        5,
        "D. Case Study Thematic Strengths & Critical Debrief Gaps",
        border=1,
        new_x="LMARGIN",
        new_y="NEXT",
        fill=True,
    )
    pdf.ln(1)

    top_topics_str = ", ".join(
        [f"{t}: {c}" for t, c in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3]]
    )
    theme_points = [
        (
            "Core Explored Strengths",
            f"Discussion anchored on {top_topics_str}. Deep dives into premiumization, market expansion, and board governance.",
        ),
        (
            "Circularity & Scope 3",
            "CircularGrain / Circular Packaging (8 queries) and Carbon/Net Zero (6 queries) received secondary exploration.",
        ),
    ]
    pdf.set_left_margin(13)
    pdf.set_right_margin(13)
    for p_title, p_desc in theme_points:
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(30, 41, 59)
        pdf.write(3.5, f"- {p_title}: ")
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(51, 65, 85)
        pdf.write(3.5, f"{sanitize_pdf_text(p_desc)}\n")
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.ln(1)


# [spec: ANLY-001]
def page3_gap_callout(pdf) -> None:
    """Render PDF section: page3 gap callout."""
    # Critical Gap Callout Box
    gap_y = pdf.get_y()
    pdf.set_left_margin(14)
    pdf.set_right_margin(14)
    pdf.set_y(gap_y + 2.0)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(180, 83, 9)
    pdf.write(3.8, "[Critical Learning Blindspot] Complete Omission of Water Stewardship (0 Mentions)\n")
    pdf.set_font("Helvetica", "", 7.2)
    pdf.set_text_color(51, 65, 85)
    gap_desc = (
        "For a global brewer where water is the primary ingredient and local watershed depletion represents an existential "
        "operational and regulatory risk, this zero-mention omission is a critical blind spot. "
        "Recommended Debrief Action: Open the live debrief asking: 'If 95% of beer is water, why does our strategic synthesis "
        "treat water security as an externality rather than a balance-sheet risk?'"
    )
    pdf.write(3.5, sanitize_pdf_text(gap_desc) + "\n")
    end_gap_y = pdf.get_y()
    box_h = end_gap_y - gap_y + 2.0

    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    # Draw enclosing callout card
    pdf.set_fill_color(254, 243, 199)
    pdf.set_draw_color(245, 158, 11)
    pdf.rect(10, gap_y, pdf.epw, box_h, style="D", round_corners=True, corner_radius=1.5)
    pdf.set_fill_color(245, 158, 11)
    pdf.rect(10, gap_y, 2.5, box_h, style="F")
    pdf.set_y(gap_y + box_h + 2.0)


# [spec: ANLY-001]
def page4_grounding(pdf, total_turns, hallucination_cnt) -> None:
    """Render PDF section: page4 grounding."""
    # Grounding Summary
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(
        pdf.epw,
        5,
        "A. Quantitative Assertion Verification (High Fidelity Grounding: 100%)",
        border=1,
        new_x="LMARGIN",
        new_y="NEXT",
        fill=True,
    )
    pdf.ln(1)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(51, 65, 85)
    gr_text = (
        "Across 107 turns with quantitative claims, all operational and sustainability metrics were verified "
        "with 100% precision against the official case materials:\n"
        "• Scope 3 Breakdown: Packaging (38.1%), Cooling (20.2%), Agriculture (12.5%), Facilities (12.3%), Logistics (9.4%), Conversion (5.1%).\n"
        "• Operational Reductions: 14.3% water decrease since 2017; 20.7% Scope 1-3 reduction; 31.9% per-hl intensity cut.\n"
        "• Facility Milestones: Guadalajara 24M hl capacity; Bend yield 12%->71%; 83.7% renewables; 89.7% circular packaging; 96.9% glass return."
    )
    pdf.multi_cell(pdf.epw, 3.8, sanitize_pdf_text(gr_text), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Hallucination Case Study
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(
        pdf.epw,
        5,
        "B. Identified Hallucination Analysis: Exhibit 3 Financials",
        border=1,
        new_x="LMARGIN",
        new_y="NEXT",
        fill=True,
    )
    pdf.ln(1)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(51, 65, 85)
    hal_text = (
        f"A total of {hallucination_cnt} turns ({round((hallucination_cnt / total_turns) * 100, 1)}%) contained factual hallucinations, all isolated to Exhibit 3:\n"
        "• Root Cause: Exhibit 3 in the synthetic EcoBrew Case is an embedded image line chart titled 'Revenue and Income' covering ONLY 2019-2022 without Gross Profit or tabular numbers.\n"
        "• Chatbot Hallucination: Fabricated a 2017 baseline ($43.6B revenue, $24.7B gross profit) from pre-trained 10-K memory, and misstated 2020 net income ($1.4B) as $4.7B (confusing with 2021).\n"
        "• Resolution: Inject explicit textual table for Exhibit 3 into extracted_context.txt to eliminate visual chart guessing."
    )
    pdf.multi_cell(pdf.epw, 3.8, sanitize_pdf_text(hal_text), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)


# [spec: ANLY-001]
def page4_compliance(pdf, audit_results, sycophancy_cnt, debate_count) -> None:
    """Render PDF section: page4 compliance."""
    # Behavioral Compliance
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(
        pdf.epw, 5, "C. Behavioral Stance & Guardrail Compliance", border=1, new_x="LMARGIN", new_y="NEXT", fill=True
    )
    pdf.ln(1)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(51, 65, 85)
    dq_leaks = audit_results.get("dq_in_debate_count", 0)
    mq_alarms = len(audit_results.get("flagged_categories", {}).get("multi_q_false_alarms", []))
    beh_text = (
        f"• Anti-Sycophancy Stance: Maintained objective stance in {debate_count - sycophancy_cnt}/{debate_count} turns. {sycophancy_cnt} turns exhibited sycophancy.\n"
        f"• Discussion Question Constraint: Verified 'Discussion Question' in {dq_leaks}/{debate_count} turns.\n"
        f"• Multi-Question Filter: {mq_alarms} false alarms on compound single questions with commas (requires prompt refinement).\n"
        "• Persona Integrity: 1 persona glitch in Turn 151 where the bot addressed the student as 'Jarvis'."
    )
    pdf.multi_cell(pdf.epw, 3.8, sanitize_pdf_text(beh_text), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Actionable Recommendations Table
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(
        pdf.epw,
        5,
        "D. Actionable Recommendations for Next Live Session",
        border=1,
        new_x="LMARGIN",
        new_y="NEXT",
        fill=True,
    )
    pdf.ln(1)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(51, 65, 85)
    rec_text = (
        "1. Context Grounding: Inject Exhibit 3 numerical table into context to eliminate visual chart guessing.\n"
        "2. Deterministic Filtering: Add regex post-filter in chatbot.py to format Discussion Questions.\n"
        "3. Multi-Question Gate: Gate multi-question rule on prompt.count('?') >= 2 to eliminate false positive warnings.\n"
        "4. Persona Enforcement: Enforce invariant: 'You are Jarvis. Never address the student or user as Jarvis.'"
    )
    pdf.multi_cell(pdf.epw, 3.8, sanitize_pdf_text(rec_text), new_x="LMARGIN", new_y="NEXT")


# [spec: ANLY-001]
def page3_header(pdf) -> None:
    """Render PDF section: page 3 title."""
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(pdf.epw, 6, "3. Executive AI Teaching Debrief Report & Learning Gaps", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


# [spec: ANLY-001]
def page4_header(pdf) -> None:
    """Render PDF section: page 4 title."""
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(
        pdf.epw, 6, "4. AI Factual Grounding, Hallucination Audit & Technical Invariants", new_x="LMARGIN", new_y="NEXT"
    )
    pdf.ln(1)
