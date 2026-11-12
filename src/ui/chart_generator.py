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
High-Performance Local Matplotlib Chart Generator for Case Study Data.
Generates dark-themed, responsive full-width PNG charts saved locally in static/generated_plots/.
"""

import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.patches import Circle

PLOTS_DIR = Path("./static/generated_plots")
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def _save_fig_and_get_tag(fig: Figure, prefix: str) -> str:
    """Save matplotlib figure to static/generated_plots and return an HTML img tag with file path."""
    filename = f"{prefix}_{int(time.time() * 1000)}.png"
    filepath = PLOTS_DIR / filename
    FigureCanvasAgg(fig)
    fig.savefig(str(filepath), format="png", bbox_inches="tight", facecolor="#0F172A")
    return f'\n\n### Visual Data Chart\n<img src="/gradio_api/file={filepath.as_posix()}" alt="Visual Data Chart" style="width:100% !important; max-width:100% !important; border-radius:10px; margin-top:12px; display:block;" />\n'


# [spec: CHAT-004]
def generate_water_stewardship_chart() -> str:
    """Generate dual-axis full-width chart for EcoBrew Water Stewardship (2017-2025)."""
    fig = Figure(figsize=(10, 4.5), dpi=140, facecolor="#0F172A")
    ax1 = fig.add_subplot(111, facecolor="#1E293B")

    years = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
    water_use = [3.08, 2.94, 2.79, 2.68, 2.64, 2.64, 2.53, 2.47, 2.38]
    high_stress_pct = [0, 0, 0, 0, 8, 17, 56, 89, 100]

    line1 = ax1.plot(years, water_use, color="#38BDF8", marker="o", linewidth=2.5, label="Water Use (hl/hl)")
    ax1.set_ylabel("Water Use Efficiency (hl/hl)", color="#38BDF8", fontsize=10, fontweight="bold")
    ax1.tick_params(axis="y", labelcolor="#38BDF8")
    ax1.set_ylim(1.8, 3.5)

    ax2 = ax1.twinx()
    line2 = ax2.plot(
        years,
        high_stress_pct,
        color="#F59E0B",
        marker="s",
        linewidth=2.5,
        linestyle="--",
        label="High-Stress Communities (%)",
    )
    ax2.set_ylabel("High-Stress Communities Improved (%)", color="#F59E0B", fontsize=10, fontweight="bold")
    ax2.tick_params(axis="y", labelcolor="#F59E0B")
    ax2.set_ylim(-5, 110)

    ax1.set_title(
        "EcoBrew Water Stewardship Performance (2017-2025)", color="#F8FAFC", fontsize=12, fontweight="bold", pad=12
    )
    ax1.set_xlabel("Year", color="#94A3B8", fontsize=10)
    ax1.tick_params(axis="x", colors="#94A3B8")
    ax1.grid(True, linestyle=":", alpha=0.3, color="#475569")

    lines = line1 + line2
    labels = [line_item.get_label() for line_item in lines]
    ax1.legend(lines, labels, loc="upper right", facecolor="#1E293B", edgecolor="#475569", labelcolor="#F8FAFC")

    return _save_fig_and_get_tag(fig, "water_stewardship")


# [spec: CHAT-004]
def generate_scope_emissions_chart() -> str:
    """Generate full-width donut chart for EcoBrew Scopes 1, 2, 3 carbon footprint."""
    fig = Figure(figsize=(9, 4.2), dpi=140, facecolor="#0F172A")
    ax = fig.add_subplot(111, facecolor="#1E293B")

    labels = ["Scope 3 (Supply Chain & Packaging)", "Scope 1 (Direct Operations)", "Scope 2 (Purchased Electricity)"]
    sizes = [85.0, 9.0, 6.0]
    colors = ["#EF4444", "#3B82F6", "#10B981"]
    explode = (0.05, 0, 0)

    _, _, autotexts = ax.pie(
        sizes,
        explode=explode,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.75,
        textprops=dict(color="#F8FAFC", fontsize=9),
    )
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_weight("bold")

    centre_circle = Circle((0, 0), 0.50, fc="#0F172A")
    ax.add_artist(centre_circle)
    ax.set_title("EcoBrew GHG Emissions Breakdown by Scope", color="#F8FAFC", fontsize=12, fontweight="bold", pad=12)

    return _save_fig_and_get_tag(fig, "scope_emissions")


# [spec: CHAT-004]
def generate_generic_chart(prompt: str) -> str:
    """Intelligently select or generate high-res full-width Matplotlib PNG chart for prompt."""
    prompt_lower = prompt.lower()
    if "water" in prompt_lower or "stewardship" in prompt_lower or "hl/hl" in prompt_lower:
        return generate_water_stewardship_chart()
    if "carbon" in prompt_lower or "scope" in prompt_lower or "footprint" in prompt_lower or "emission" in prompt_lower:
        return generate_scope_emissions_chart()
    return generate_water_stewardship_chart()
