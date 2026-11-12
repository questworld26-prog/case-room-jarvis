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

"""
Classroom Engagement Analytics Engine
Processes classroom chat telemetry logs (multi-select or single datestamped), computes participation metrics (Gini index, depth, temporal trends, question count histogram),
classifies prompts via Gemini AI (Bloom's Taxonomy, Case Topics), generates pedagogical debrief reports, and exports PDF reports.
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from analytics_engine.analytics_charts import BLOOM_COLOR_MAP, BLOOM_LEVELS, generate_analytics_charts
from analytics_engine.analytics_pdf import ReportPDF
from analytics_engine.analytics_pdf import generate_pdf_report as _generate_pdf_report
from analytics_engine.mode_relevance import evaluate_mode_relevance
from config import app_state
from core.cache_manager import get_genai_client

__all__ = [
    "CASE_TOPICS",
    "BLOOM_LEVELS",
    "BLOOM_COLOR_MAP",
    "get_available_log_files",
    "load_telemetry_logs",
    "compute_gini_coefficient",
    "classify_prompts_ai",
    "compute_metrics",
    "evaluate_mode_relevance",
    "generate_ai_teaching_debrief",
    "generate_analytics_charts",
    "generate_pdf_report",
    "ReportPDF",
]


LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
REPORTS_DIR = LOG_DIR / "reports"
ANALYTICS_CACHE_FILE = LOG_DIR / "analytics_cache.json"


CASE_TOPICS = [
    "Carbon & Net Zero",
    "Water Stewardship",
    "Circular Packaging & CircularGrain",
    "Financial Performance",
    "Strategy & Growth",
    "Supply Chain & Scope 3",
    "Governance & ESG",
]


# [spec: ANLY-001]
# [spec: PRIV-002]
def get_available_log_files(include_test_logs: bool = False):
    """List JSONL log files in the logs directory sorted by modification time."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    files = list(LOG_DIR.glob("*.jsonl"))
    if not include_test_logs:
        files = [f for f in files if not f.name.startswith("test_")]
    files.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    return [f.name for f in files]


# [spec: ANLY-001]
# [spec: PRIV-002]
def load_telemetry_logs(target_logfiles=None):
    """Load and normalize telemetry records from one or multiple datestamped log files."""
    if not LOG_DIR.exists() or not target_logfiles:
        return []

    if isinstance(target_logfiles, str):
        target_logfiles = [target_logfiles]

    target_files = []
    for item in target_logfiles:
        if item == "All Log Files (Combined)":
            target_files.extend([f for f in LOG_DIR.glob("*.jsonl") if not f.name.startswith("test_")])
        else:
            p = Path(item)
            if p.exists() and p.is_file():
                target_files.append(p)
            elif (LOG_DIR / item).exists():
                target_files.append(LOG_DIR / item)

    unique_files = list(dict.fromkeys(target_files))

    records = []
    for fpath in unique_files:
        try:
            with open(fpath, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                        if "session_id" not in rec or not rec["session_id"]:
                            rec["session_id"] = "Session_1"
                        if "case_study" not in rec or not rec["case_study"]:
                            rec["case_study"] = "EcoBrew"
                        if "student_name" not in rec or not rec["student_name"]:
                            rec["student_name"] = "Anonymous Student"
                        if "turn_number" not in rec:
                            rec["turn_number"] = 1
                        if "history_depth" not in rec:
                            rec["history_depth"] = 0
                        if "prompt_word_count" not in rec:
                            rec["prompt_word_count"] = len(rec.get("prompt", "").split())
                        rec["source_file"] = fpath.name
                        records.append(rec)
                    except Exception as e:
                        print(f"Notice: skipped invalid log line in {fpath.name}: {e}")
        except Exception as err:
            print(f"Warning: unable to open log file {fpath.name}: {err}")
    return records


# [spec: ANLY-001]
def compute_gini_coefficient(counts):
    """
    Compute Gini coefficient of inequality for participation.
    0.0 = perfect equality (everyone asked same number of questions)
    1.0 = total inequality (one student asked all questions)
    """
    if not counts or len(counts) <= 1:
        return 0.0
    sorted_counts = sorted(counts)
    n = len(sorted_counts)
    mean = sum(sorted_counts) / n
    if mean == 0:
        return 0.0

    diff_sum = sum(abs(x - y) for x in sorted_counts for y in sorted_counts)
    gini = diff_sum / (2 * n * n * mean)
    return round(gini, 3)


def _empty_length_stats() -> dict:
    return {
        "avg_words": 0.0,
        "min_words": 0,
        "max_words": 0,
        "median_words": 0,
        "avg_chars": 0,
        "min_chars": 0,
        "max_chars": 0,
    }


def _empty_metrics() -> dict:
    return {
        "total_questions": 0,
        "active_students_count": 0,
        "avg_questions_per_student": 0,
        "avg_turn_depth": 0,
        "avg_word_count": 0,
        "gini_coefficient": 0.0,
        "participation_equality_score": 100.0,
        "max_student_name": "N/A",
        "max_student_questions": 0,
        "avg_latency": 0.0,
        "median_latency": 0.0,
        "p95_latency": 0.0,
        "min_latency": 0.0,
        "max_latency": 0.0,
        "avg_words_per_sec": 0.0,
        "latency_histogram": {},
        "question_length_stats": _empty_length_stats(),
        "answer_length_stats": _empty_length_stats(),
        "mode_breakdown": {},
        "mode_stats": {},
        "overall_mode_relevance_score": 100.0,
        "case_study_breakdown": {},
        "student_counts": {},
        "question_histogram": {},
        "timeline_data": [],
        "records": [],
    }


def _calc_stats(arr):
    if not arr:
        return {"avg": 0.0, "min": 0, "max": 0, "median": 0}
    s = sorted(arr)
    return {"avg": round(sum(s) / len(s), 1), "min": s[0], "max": s[-1], "median": s[len(s) // 2]}


def _latency_metrics(records) -> dict:
    latencies = [r.get("latency_seconds", 0.0) for r in records if r.get("latency_seconds") is not None]
    out = dict(avg=0.0, median=0.0, p95=0.0, min=0.0, max=0.0, wps=0.0)
    if latencies:
        s = sorted(latencies)
        out["avg"] = round(sum(latencies) / len(latencies), 2)
        out["min"] = round(s[0], 2)
        out["max"] = round(s[-1], 2)
        out["median"] = round(s[int(len(s) * 0.50)], 2)
        out["p95"] = round(s[min(int(len(s) * 0.95), len(s) - 1)], 2)
        total_words = sum(len(r.get("response", "").split()) for r in records)
        total_lat = sum(latencies)
        out["wps"] = round(total_words / total_lat, 1) if total_lat > 0 else 0.0

    raw = Counter()
    for lat in latencies:
        if lat < 1.0:
            raw["< 1.0s"] += 1
        elif lat < 2.0:
            raw["1.0s - 2.0s"] += 1
        elif lat < 4.0:
            raw["2.0s - 4.0s"] += 1
        elif lat < 8.0:
            raw["4.0s - 8.0s"] += 1
        else:
            raw["> 8.0s"] += 1
    bins = ["< 1.0s", "1.0s - 2.0s", "2.0s - 4.0s", "4.0s - 8.0s", "> 8.0s"]
    out["histogram"] = {b: raw[b] for b in bins if b in raw}
    return out


def _length_stats(records) -> tuple[dict, dict]:
    q_words = [r.get("prompt_word_count") or len(r.get("prompt", "").split()) for r in records if r.get("prompt")]
    q_chars = [len(r.get("prompt", "")) for r in records if r.get("prompt")]
    a_words = [len(r.get("response", "").split()) for r in records if r.get("response")]
    a_chars = [len(r.get("response", "")) for r in records if r.get("response")]

    def pack(words, chars):
        w, c = _calc_stats(words), _calc_stats(chars)
        return {
            "avg_words": w["avg"],
            "min_words": w["min"],
            "max_words": w["max"],
            "median_words": w["median"],
            "avg_chars": int(c["avg"]),
            "min_chars": c["min"],
            "max_chars": c["max"],
        }

    return pack(q_words, q_chars), pack(a_words, a_chars)


def _mode_metrics(records, total_questions) -> tuple[dict, dict, dict, float]:
    mode_counts = dict(Counter(r.get("mode", "qa") for r in records))
    case_counts = dict(Counter(r.get("case_study", "EcoBrew") for r in records))
    rel_counts = defaultdict(Counter)
    for r in records:
        m = r.get("mode", "qa")
        rel_counts[m][evaluate_mode_relevance(r.get("prompt", ""), m)] += 1

    mode_stats = {}
    total_rel = 0.0
    for m, cnt in mode_counts.items():
        rels = rel_counts[m]
        h, med, low = rels.get("High", 0), rels.get("Medium", 0), rels.get("Low", 0)
        total_rel += h + med * 0.6
        mode_stats[m] = {
            "count": cnt,
            "pct_of_total": round((cnt / total_questions) * 100, 1) if total_questions > 0 else 0.0,
            "high": h,
            "medium": med,
            "low": low,
            "relevance_score": round(((h + med * 0.6) / cnt) * 100, 1) if cnt > 0 else 100.0,
        }
    overall = round((total_rel / total_questions) * 100, 1) if total_questions > 0 else 100.0
    return mode_counts, case_counts, mode_stats, overall


def _timeline(records) -> list:
    bins = defaultdict(int)
    for r in records:
        ts = r.get("timestamp", "")
        if len(ts) >= 15:
            bins[ts[:15] + "0"] += 1
    return sorted(bins.items(), key=lambda x: x[0])


# [spec: ANLY-001]
def compute_metrics(target_logfiles=None, records=None):
    """Calculate quantitative engagement metrics across selected log file(s) or preloaded records."""
    if records is None:
        records = load_telemetry_logs(target_logfiles)
    if not records:
        return _empty_metrics()

    total = len(records)
    student_counts = Counter(r["student_name"] for r in records)
    active = len(student_counts)
    counts_list = list(student_counts.values())
    gini = compute_gini_coefficient(counts_list)
    max_name, max_q = student_counts.most_common(1)[0] if student_counts else ("N/A", 0)

    lat = _latency_metrics(records)
    q_stats, a_stats = _length_stats(records)
    mode_counts, case_counts, mode_stats, overall_rel = _mode_metrics(records, total)

    max_count = max(counts_list)
    freq = Counter(counts_list)
    question_histogram = {
        (f"{k} Question" if k == 1 else f"{k} Questions"): freq.get(k, 0) for k in range(1, max_count + 1)
    }

    return {
        "total_questions": total,
        "active_students_count": active,
        "avg_questions_per_student": round(total / active, 2) if active > 0 else 0,
        "avg_turn_depth": round(sum(r.get("turn_number", 1) for r in records) / total, 2),
        "avg_word_count": round(sum(r.get("prompt_word_count", 0) for r in records) / total, 1),
        "gini_coefficient": gini,
        "participation_equality_score": round((1.0 - gini) * 100, 1),
        "max_student_name": max_name,
        "max_student_questions": max_q,
        "avg_latency": lat["avg"],
        "median_latency": lat["median"],
        "p95_latency": lat["p95"],
        "min_latency": lat["min"],
        "max_latency": lat["max"],
        "avg_words_per_sec": lat["wps"],
        "latency_histogram": lat["histogram"],
        "question_length_stats": q_stats,
        "answer_length_stats": a_stats,
        "mode_breakdown": mode_counts,
        "mode_stats": mode_stats,
        "overall_mode_relevance_score": overall_rel,
        "case_study_breakdown": case_counts,
        "student_counts": dict(student_counts),
        "question_histogram": question_histogram,
        "timeline_data": _timeline(records),
        "records": records,
    }


# [spec: ANLY-001]
def load_analytics_cache():
    """Load local JSON cache of AI-classified prompts."""
    if ANALYTICS_CACHE_FILE.exists():
        try:
            with open(ANALYTICS_CACHE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Notice loading analytics cache: {e}")
    return {}


# [spec: ANLY-001]
def save_analytics_cache(cache_data):
    """Save AI-classified prompt annotations to local JSON cache."""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(ANALYTICS_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        print(f"Notice saving analytics cache: {e}")


_CLASSIFY_PROMPT_TEMPLATE = """
You are an expert educational taxonomist analyzing student questions in an MBA/undergraduate business case study class on EcoBrew strategy & sustainability.
Classify each question into:
1. "bloom": One of ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]
2. "topic": One of ["Carbon & Net Zero", "Water Stewardship", "Circular Packaging & CircularGrain", "Financial Performance", "Strategy & Growth", "Supply Chain & Scope 3", "Governance & ESG"]

Questions:
{questions}

Respond strictly in valid JSON format as a list of objects with keys: "prompt", "bloom", "topic".
"""


def _classify_batches_with_gemini(prompts: list[str], cache: dict) -> None:
    client = get_genai_client()
    batch_size = 25
    for i in range(0, len(prompts), batch_size):
        batch = prompts[i : i + batch_size]
        response = client.models.generate_content(
            model=app_state.analytics_model_id,
            contents=_CLASSIFY_PROMPT_TEMPLATE.format(questions=json.dumps(batch, indent=2)),
            config={"temperature": 0.1, "response_mime_type": "application/json"},
        )
        if response and response.text:
            clean = re.sub(r"^```[a-z]*\s*", "", response.text.strip(), flags=re.MULTILINE)
            clean = re.sub(r"\s*```$", "", clean, flags=re.MULTILINE)
            for item in json.loads(clean):
                p = item.get("prompt", "").strip()
                if p:
                    cache[p] = {
                        "bloom": item.get("bloom", "Understand"),
                        "topic": item.get("topic", "Strategy & Growth"),
                    }


def _classify_prompt_heuristic(prompt: str) -> dict:
    p_lower = prompt.lower()
    topic = "Strategy & Growth"
    if "water" in p_lower:
        topic = "Water Stewardship"
    elif "carbon" in p_lower or "emission" in p_lower or "scope" in p_lower:
        topic = "Carbon & Net Zero"
    elif "packaging" in p_lower or "CircularGrain" in p_lower or "glass" in p_lower:
        topic = "Circular Packaging & CircularGrain"
    elif "revenue" in p_lower or "financial" in p_lower or "profit" in p_lower:
        topic = "Financial Performance"
    bloom = "Remember" if any(w in p_lower for w in ["what", "who", "when", "show", "list"]) else "Understand"
    return {"bloom": bloom, "topic": topic}


# [spec: ANLY-001]
def classify_prompts_ai(records):
    """
    Classify prompts into Bloom's Taxonomy and Case Topics using Gemini AI with local caching and keyword heuristic fallback.
    """
    if not records:
        return {}, {}, []

    cache = load_analytics_cache()
    unique_unclassified = list(
        {r.get("prompt", "").strip() for r in records if r.get("prompt", "").strip()} - set(cache)
    )

    if unique_unclassified:
        print(f"Classifying {len(unique_unclassified)} new prompts via Gemini AI...")
        try:
            _classify_batches_with_gemini(unique_unclassified, cache)
        except Exception as gemini_err:
            print(f"Notice: Gemini classification unavailable ({gemini_err}). Using fallback taxonomy mapping...")
            for p in unique_unclassified:
                cache[p] = _classify_prompt_heuristic(p)
        save_analytics_cache(cache)

    bloom_counts = Counter()
    topic_counts = Counter()
    for r in records:
        ann = cache.get(r.get("prompt", "").strip(), {"bloom": "Understand", "topic": "Strategy & Growth"})
        bloom_counts[ann["bloom"]] += 1
        topic_counts[ann["topic"]] += 1

    gap_topics = [t for t in CASE_TOPICS if topic_counts[t] == 0]
    return dict(bloom_counts), dict(topic_counts), gap_topics


# [spec: ANLY-001]
def generate_ai_teaching_debrief(log_label, metrics, bloom_counts, topic_counts, gap_topics):
    """Generate executive debrief report using Gemini AI with friendly notice if unavailable."""
    q_stats = metrics.get("question_length_stats", {})
    a_stats = metrics.get("answer_length_stats", {})
    mode_stats = metrics.get("mode_stats", {})
    max_stu = metrics.get("max_student_name", "N/A")
    max_q_cnt = metrics.get("max_student_questions", 0)

    summary_prompt = f"""
You are a senior business professor summarizing classroom engagement telemetry for a case study discussion on EcoBrew.

Log Source: {log_label}
Key Quantitative Metrics:
- Total Questions Asked: {metrics["total_questions"]}
- Active Students: {metrics["active_students_count"]}
- Avg Questions per Student: {metrics["avg_questions_per_student"]}
- Most Active Contributor: {max_stu} ({max_q_cnt} questions)
- Participation Equality Score (100 = perfectly equal): {metrics["participation_equality_score"]}
- Avg Conversation Turn Depth: {metrics["avg_turn_depth"]}

Question & Answer Length Dynamics:
- Student Questions: Avg {q_stats.get("avg_words", 0)} words (Median {q_stats.get("median_words", 0)}w, Range {q_stats.get("min_words", 0)}-{q_stats.get("max_words", 0)}w)
- AI Answers: Avg {a_stats.get("avg_words", 0)} words (Median {a_stats.get("median_words", 0)}w, Range {a_stats.get("min_words", 0)}-{a_stats.get("max_words", 0)}w)

Pedagogical Modes & Relevance:
- Mode Distribution: {json.dumps(metrics.get("mode_breakdown", {}))}
- Mode Quality & Relevance Score: {metrics.get("overall_mode_relevance_score", 100)}%
- Mode Details: {json.dumps(mode_stats)}

Cognitive Depth (Bloom's Taxonomy): {json.dumps(bloom_counts)}
Case Topic Coverage: {json.dumps(topic_counts)}
Unexplored/Gap Topics: {json.dumps(gap_topics)}

Provide a polished, 4-section Executive Teaching Debrief containing:
1. **Engagement Overview & Participation Balance**: Comment on student active participation, equality score, and most active student contribution.
2. **Cognitive Depth & Thinking Rigor**: Evaluate the Bloom's taxonomy distribution (higher-order vs lower-order thinking).
3. **Pedagogical Mode Alignment & Dialogue Dynamics**: Evaluate how students engaged across modes (e.g., QA vs Quiz) and the substantive length of student questions vs model responses.
4. **Key Strengths & Gap Areas for Class Debrief**: Highlight top explored themes vs unexplored gap topics that the instructor should cover in the debrief.

Keep formatting clear with clean Markdown headings and bullet points.
"""
    try:
        client = get_genai_client()
        response = client.models.generate_content(
            model=app_state.analytics_model_id, contents=summary_prompt, config={"temperature": 0.3}
        )
        if response and response.text:
            return response.text
    except Exception as gemini_err:
        err_msg = str(gemini_err)
        print(f"Notice: Gemini AI debrief generation unavailable ({err_msg}).")
        return (
            "### ⚠️ Gemini AI Service Notice\n\n"
            f"Unable to generate the AI Executive Teaching Debrief at this time: Gemini API returned `{err_msg[:120]}`.\n\n"
            "*Note*: All quantitative telemetry metrics, participation distribution charts, Bloom's cognitive taxonomy, question/answer length stats, mode alignment metrics, and case topic coverage plots above have been rendered from your log files. Please check your Google GenAI API key or retry shortly."
        )


# [spec: ANLY-001]
def generate_pdf_report(selected_logfiles, metrics, bloom_counts, topic_counts, gap_topics, debrief_text):
    """Generate a clean, multi-page PDF report file delegating to analytics_pdf with chart generation callback."""
    return _generate_pdf_report(
        selected_logfiles,
        metrics,
        bloom_counts,
        topic_counts,
        gap_topics,
        debrief_text,
        generate_charts_fn=generate_analytics_charts,
    )
