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

"""Matplotlib chart builders for the classroom engagement analytics report (8 subplots, 4x2 grid)."""

import io

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

BLOOM_LEVELS = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]

BLOOM_COLOR_MAP = {
    "Remember": "#94A3B8",  # Slate Gray
    "Understand": "#60A5FA",  # Sky Blue
    "Apply": "#34D399",  # Emerald Green
    "Analyze": "#FBBF24",  # Amber Yellow
    "Evaluate": "#F87171",  # Rose Red
    "Create": "#A78BFA",  # Purple
}

_TITLE = {"fontsize": 11, "fontweight": "bold"}


def _empty(ax, message: str, title: str) -> None:
    ax.text(0.5, 0.5, message, ha="center", va="center")
    ax.set_title(title, **_TITLE)


def _label_bars(ax, bars, offset: float, bold: bool = False, skip_zero: bool = False) -> None:
    for bar in bars:
        yval = bar.get_height()
        if skip_zero and yval <= 0:
            continue
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            yval + offset,
            str(yval),
            ha="center",
            va="bottom",
            fontsize=8,
            fontweight="bold" if bold else "normal",
        )


# [spec: ANLY-001]
def _plot_top_students(ax, metrics) -> None:
    student_counts = metrics.get("student_counts", {})
    if not student_counts:
        return _empty(ax, "No Student Data", "Top Participating Students")
    top = sorted(student_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    names = [x[0][:15] for x in top][::-1]
    ax.barh(names, [x[1] for x in top][::-1], color="#3B82F6", edgecolor="#1D4ED8")
    ax.set_title("Top Participating Students", pad=8, **_TITLE)
    ax.set_xlabel("Number of Questions Asked", fontsize=9)
    ax.grid(axis="x", linestyle="--", alpha=0.5)


# [spec: ANLY-001]
def _plot_question_histogram(ax, metrics) -> None:
    q_hist = metrics.get("question_histogram", {})
    if not q_hist:
        return _empty(ax, "No Histogram Data", "Student Question Frequency Histogram")
    labels = [k.replace(" Questions", "").replace(" Question", "") for k in q_hist]
    bars = ax.bar(labels, list(q_hist.values()), color="#6366F1", edgecolor="#4338CA")
    ax.set_title("Full Student Question Frequency Histogram", pad=8, **_TITLE)
    ax.set_xlabel("Questions Asked per Student", fontsize=9)
    ax.set_ylabel("Student Count", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    if len(labels) > 10:
        ax.tick_params(axis="x", rotation=45, labelsize=8)
    _label_bars(ax, bars, 0.1, skip_zero=True)


# [spec: ANLY-001]
def _plot_bloom_donut(ax, bloom_counts) -> None:
    if not bloom_counts:
        return _empty(ax, "No Cognitive Data", "Cognitive Depth")
    labels = [b for b in BLOOM_LEVELS if bloom_counts.get(b, 0) > 0]
    ax.pie(
        [bloom_counts[b] for b in labels],
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        colors=[BLOOM_COLOR_MAP.get(b, "#94A3B8") for b in labels],
        wedgeprops=dict(width=0.4, edgecolor="w"),
    )
    ax.set_title("Cognitive Depth (Bloom's Taxonomy)", pad=8, **_TITLE)


# [spec: ANLY-001]
def _plot_topic_coverage(ax, topic_counts) -> None:
    if not topic_counts:
        return _empty(ax, "No Topic Data", "Case Topic Coverage")
    sorted_topics = sorted(topic_counts.items(), key=lambda x: (x[1], x[0]))
    ax.barh([t[0] for t in sorted_topics], [t[1] for t in sorted_topics], color="#10B981", edgecolor="#047857")
    ax.set_title("Case Study Topic Coverage", pad=8, **_TITLE)
    ax.set_xlabel("Question Count", fontsize=9)
    ax.grid(axis="x", linestyle="--", alpha=0.5)


# [spec: ANLY-001]
def _plot_mode_quality(ax, metrics) -> None:
    mode_stats = metrics.get("mode_stats", {})
    if not mode_stats:
        return _empty(ax, "No Mode Data", "Questions per Mode")
    names = list(mode_stats.keys())
    labels = [f"{m.upper()}\n({mode_stats[m]['relevance_score']}%)" for m in names]
    bars = ax.bar(labels, [mode_stats[m]["count"] for m in names], color="#0EA5E9", edgecolor="#0284C7")
    ax.set_title("Questions per Mode & Alignment Quality", pad=8, **_TITLE)
    ax.set_ylabel("Question Count", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    _label_bars(ax, bars, 0.3, bold=True)


# [spec: ANLY-001]
def _plot_length_dynamics(ax, metrics) -> None:
    ql = metrics.get("question_length_stats", {})
    al = metrics.get("answer_length_stats", {})
    if not (ql and al):
        return _empty(ax, "No Length Data", "Question vs Answer Length")
    categories = ["Average", "Median", "Max"]
    keys = ("avg_words", "median_words", "max_words")
    indices = list(range(len(categories)))
    width = 0.35
    ax.bar(
        [i - width / 2 for i in indices],
        [ql.get(k, 0) for k in keys],
        width=width,
        label="Student Q",
        color="#F59E0B",
        edgecolor="#D97706",
    )
    ax.bar(
        [i + width / 2 for i in indices],
        [al.get(k, 0) for k in keys],
        width=width,
        label="AI Answer",
        color="#10B981",
        edgecolor="#059669",
    )
    ax.set_title("Question vs Answer Word Length Dynamics", pad=8, **_TITLE)
    ax.set_xticks(indices)
    ax.set_xticklabels(categories, fontsize=9)
    ax.set_ylabel("Word Count", fontsize=9)
    ax.legend(fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.5)


# [spec: ANLY-001]
def _plot_timeline(ax, metrics) -> None:
    timeline_data = metrics.get("timeline_data", [])
    if not timeline_data:
        return _empty(ax, "No Timeline Data", "Activity Timeline")
    times = [x[0][-5:] for x in timeline_data]
    counts = [x[1] for x in timeline_data]
    ax.plot(times, counts, marker="o", color="#8B5CF6", linewidth=2, markersize=5)
    ax.fill_between(times, counts, color="#8B5CF6", alpha=0.2)
    ax.set_title("Classroom Activity Timeline", pad=8, **_TITLE)
    ax.set_xlabel("Time (10-Min Intervals)", fontsize=9)
    ax.set_ylabel("Questions Asked", fontsize=9)
    ax.tick_params(axis="x", rotation=45)
    ax.grid(True, linestyle="--", alpha=0.5)


# [spec: ANLY-001]
def _plot_latency_histogram(ax, metrics) -> None:
    lat_hist = metrics.get("latency_histogram", {})
    if not lat_hist:
        return _empty(ax, "No Latency Data", "Response Latency Distribution")
    colors = ["#10B981", "#3B82F6", "#8B5CF6", "#F59E0B", "#EF4444"][: len(lat_hist)]
    ax.bar(list(lat_hist.keys()), list(lat_hist.values()), color=colors, edgecolor="#1F2937")
    ax.set_title("Response Latency Distribution", pad=8, **_TITLE)
    ax.set_xlabel("Latency Range (Seconds)", fontsize=9)
    ax.set_ylabel("Turn Count", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.5)


# [spec: ANLY-001]
def generate_analytics_charts(metrics, bloom_counts, topic_counts):
    """Generate high-res Matplotlib visualizations for engagement reporting (8 subplots in 4x2 grid)."""
    fig = Figure(figsize=(14, 17))
    FigureCanvasAgg(fig)
    fig.patch.set_facecolor("#F8FAFC")
    axes = fig.subplots(4, 2)

    _plot_top_students(axes[0, 0], metrics)
    _plot_question_histogram(axes[0, 1], metrics)
    _plot_bloom_donut(axes[1, 0], bloom_counts)
    _plot_topic_coverage(axes[1, 1], topic_counts)
    _plot_mode_quality(axes[2, 0], metrics)
    _plot_length_dynamics(axes[2, 1], metrics)
    _plot_timeline(axes[3, 0], metrics)
    _plot_latency_histogram(axes[3, 1], metrics)

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120)
    buf.seek(0)
    return buf
