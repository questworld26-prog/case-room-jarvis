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
Admin event handlers, session control actions, and live classroom dashboard plotting.
Encapsulates instructor mode changes, framework updates, cache lifecycle triggers,
and 10-second auto-refreshing telemetry plots.
"""

import html
import json
import secrets
import time
import traceback

import gradio as gr
import matplotlib

matplotlib.use("Agg")
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from config import app_state
from core.cache_manager import get_or_create_cache
from core.logger import get_log_file_path


# [spec: ADMIN-001]
def verify_admin_password(input_password: str) -> bool:
    """Verify instructor password using constant-time digest comparison."""
    if not input_password or not isinstance(input_password, str):
        return False
    candidate = input_password.strip().encode("utf-8")
    expected = str(app_state.admin_password or "").encode("utf-8")
    return bool(expected) and secrets.compare_digest(candidate, expected)


# [spec: ADMIN-001]
def set_pending_mode(new_mode):
    """Stage mode change without mutating live student mode until Broadcast is clicked."""
    app_state.pending_mode = new_mode
    app_state._has_staged_mode = new_mode != app_state.active_mode
    status_msg = f"🔄 Mode staged: **{new_mode.upper()}** — Click **'📢 Broadcast Mode to Students'** to apply."
    plugin = app_state.get_active_plugin(new_mode)
    if plugin.requires_framework:
        status_msg += f" (Framework: {app_state.selected_framework})"
    return status_msg


# [spec: ADMIN-001]
def confirm_mode_broadcast():
    """Confirm and broadcast the staged mode change to all connected students."""
    if getattr(app_state, "_has_staged_mode", False) and getattr(app_state, "pending_mode", None):
        app_state.active_mode = app_state.pending_mode
        app_state._has_staged_mode = False
    else:
        app_state.pending_mode = app_state.active_mode
    app_state.notify_mode_change()
    mode_name = app_state.get_mode_display_name()
    return f"✅ **{mode_name}** is now live for all students!"


# [spec: ADMIN-001]
def update_framework(new_framework):
    app_state.selected_framework = new_framework
    app_state.notify_mode_change()
    return f"✅ Active Framework updated to: **{new_framework}**"


# [spec: ADMIN-001]
def add_custom_fw(name, desc):
    if not name or not desc:
        return gr.Dropdown(choices=list(app_state.get_all_frameworks().keys())), "⚠️ Name and description required."
    app_state.add_custom_framework(name, desc)
    all_fw = list(app_state.get_all_frameworks().keys())
    app_state.selected_framework = name
    app_state.notify_mode_change()
    return gr.Dropdown(choices=all_fw, value=name), f"✅ Added custom framework: **{name}**"


# [spec: ADMIN-001]
def update_model_id(new_model):
    if new_model and new_model.strip():
        app_state.model_id = new_model.strip()
    return get_admin_status()


# [spec: ADMIN-001]
def update_ttl(new_ttl):
    if new_ttl and new_ttl.strip():
        app_state.cache_ttl = new_ttl.strip()
    return get_admin_status()


# [spec: ADMIN-001]
def refresh_cache_action():
    try:
        case = app_state.active_case_study or "EcoBrew"
        get_or_create_cache(case, force_refresh=True, ttl=app_state.cache_ttl)
        app_state.notify_mode_change()
        cache_msg = ""
        if app_state.active_cache_name:
            cache_msg = f" | ⚡ **Gemini Context Cache ACTIVE** ({app_state.active_cache_name[-18:]}, TTL: {app_state.cache_ttl})"
        return f"✅ Cleaned text context reloaded successfully for '{case}'! ({len(app_state.case_text_context):,} chars){cache_msg}"
    except Exception as e:
        print(f"❌ Context reload error: {e}")
        traceback.print_exc()
        return f"❌ Context reload failed: {str(e)}"


def _admin_stat_box(label: str, value: str, border_color: str, value_color: str, extra_style: str = "") -> str:
    return (
        f'<div style="background: rgba(255, 255, 255, 0.04); padding: 8px 12px; border-radius: 8px; border-left: 3px solid {border_color};">'
        f'<div style="font-size: 11px; color: #94A3B8; font-weight: 600; text-transform: uppercase; margin-bottom: 2px;">{label}</div>'
        f'<div style="font-size: 13px; font-weight: 700; color: {value_color}; {extra_style}">{value}</div>'
        f"</div>"
    )


# [spec: ADMIN-001]
def get_admin_status():
    is_live = bool(app_state.active_case_study and app_state.session_locked)
    has_gemini_cache = bool(getattr(app_state, "active_cache_name", None))

    case_display = html.escape(str(app_state.active_case_study or "— (Not Loaded)"), quote=True)
    mode_raw = app_state.get_mode_display_name()
    if getattr(app_state, "_has_staged_mode", False) and getattr(app_state, "pending_mode", None):
        mode_raw += f" (⏳ Staged: {app_state.pending_mode.upper()} — Click Broadcast)"
    mode_display = html.escape(str(mode_raw), quote=True)
    fw_display = html.escape(str(app_state.selected_framework), quote=True)
    model_display = html.escape(str(app_state.model_id), quote=True)
    ttl_display = html.escape(str(app_state.cache_ttl), quote=True)

    badge_bg = "rgba(16, 185, 129, 0.2)" if is_live else "rgba(245, 158, 11, 0.2)"
    badge_color = "#34D399" if is_live else "#FBBF24"
    badge_border = "rgba(52, 211, 153, 0.3)" if is_live else "rgba(251, 191, 36, 0.3)"
    badge_text = "● LIVE SESSION" if is_live else "⏳ READY (LOAD CASE STUDY)"

    cache_bg = "rgba(16, 185, 129, 0.2)" if has_gemini_cache else "rgba(245, 158, 11, 0.15)"
    cache_color = "#34D399" if has_gemini_cache else "#F59E0B"
    cache_border = "rgba(52, 211, 153, 0.4)" if has_gemini_cache else "rgba(245, 158, 11, 0.3)"
    cache_text = "⚡ GEMINI CACHE ACTIVE (95% TOKEN SAVINGS)" if has_gemini_cache else "📄 IN-MEMORY TEXT PIPELINE"

    stat_items = [
        _admin_stat_box("Active Case Study", case_display, "#38BDF8", "#F8FAFC" if is_live else "#94A3B8"),
        _admin_stat_box("Active Mode", mode_display, "#F59E0B", "#F59E0B"),
    ]
    if app_state.has_framework_modes():
        stat_items.append(
            _admin_stat_box(
                "Selected Framework",
                fw_display,
                "#A855F7",
                "#E9D5FF",
                "white-space: nowrap; overflow: hidden; text-overflow: ellipsis;",
            )
        )
    stat_items.extend(
        [
            _admin_stat_box("Gemini Model ID", model_display, "#10B981", "#6EE7B7"),
            _admin_stat_box("Cache TTL / Duration", ttl_display, "#EC4899", "#F472B6"),
        ]
    )
    boxes = "".join(stat_items)

    return (
        '<div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); border: 1px solid rgba(56, 189, 248, 0.3); '
        'border-radius: 12px; padding: 16px 20px; margin-bottom: 16px; box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25); color: #F8FAFC; font-family: system-ui, -apple-system, sans-serif;">'
        '<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 8px;">'
        '<span style="font-weight: 700; font-size: 14px; letter-spacing: 0.5px; text-transform: uppercase; color: #38BDF8; display: flex; align-items: center; gap: 6px;">⚡ Active Session Overview</span>'
        '<div style="display: flex; gap: 8px; align-items: center;">'
        f'<span style="background: {cache_bg}; color: {cache_color}; font-size: 11px; font-weight: 600; padding: 3px 9px; border-radius: 20px; border: 1px solid {cache_border};">{cache_text}</span>'
        f'<span style="background: {badge_bg}; color: {badge_color}; font-size: 12px; font-weight: 600; padding: 3px 10px; border-radius: 20px; border: 1px solid {badge_border};">{badge_text}</span>'
        "</div></div>"
        f'<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px;">{boxes}</div></div>'
    )


def _collect_dashboard_telemetry() -> tuple[int, list[str], list[int], list[float]]:
    log_path = get_log_file_path(is_test=False)
    now = time.time()
    cutoff_5m = now - 300
    active_names = set()
    time_buckets = [now - (i * 300) for i in range(5, -1, -1)]
    bucket_labels = [time.strftime("%H:%M", time.localtime(t)) for t in time_buckets]
    msg_counts = [0] * 6
    latencies_sum = [0.0] * 6
    latencies_count = [0] * 6

    if log_path.exists():
        try:
            with open(log_path, encoding="utf-8") as lf:
                for line in lf:
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    if rec.get("is_test_run", False):
                        continue
                    epoch = rec.get("epoch", 0)
                    name = rec.get("student_name", "").strip()
                    if epoch >= cutoff_5m and name and name not in ("Anonymous Student", "Anonymous"):
                        active_names.add(name)
                    for idx in range(6):
                        if (time_buckets[idx] - 300) <= epoch < time_buckets[idx]:
                            msg_counts[idx] += 1
                            lat = rec.get("latency_seconds", rec.get("response_time_seconds", 0.0))
                            if lat > 0:
                                latencies_sum[idx] += lat
                                latencies_count[idx] += 1
        except Exception as err:
            print(f"Notice reading live dashboard telemetry: {err}")

    avg_latencies = [(latencies_sum[i] / latencies_count[i]) if latencies_count[i] > 0 else 0.0 for i in range(6)]
    return len(active_names), bucket_labels, msg_counts, avg_latencies


# [spec: ADMIN-001]
def generate_live_dashboard_data():
    """Calculate active student count and generate thread-safe live activity + latency figures."""
    count, bucket_labels, msg_counts, avg_latencies = _collect_dashboard_telemetry()
    signal = "🟢" if count > 0 else "🔴"
    status_text = (
        f"{signal} **Students Active (last 5 min):** `{count}`  \n"
        f"*{'Class is live! Students are engaging.' if count > 0 else 'No recent activity — waiting for student interaction.'}*"
    )

    fig_act = Figure(figsize=(5, 2.5), dpi=100, facecolor="#0F172A")
    FigureCanvasAgg(fig_act)
    ax_act = fig_act.add_subplot(111, facecolor="#1E293B")
    ax_act.bar(bucket_labels, msg_counts, color="#38BDF8", alpha=0.85, width=0.5)
    ax_act.set_title("Messages Sent (Last 30m)", color="#F8FAFC", fontsize=10, fontweight="bold")
    ax_act.set_ylabel("Messages", color="#94A3B8", fontsize=8)
    ax_act.tick_params(colors="#94A3B8", labelsize=8)
    ax_act.grid(True, linestyle=":", alpha=0.2, color="#475569")
    fig_act.tight_layout()

    fig_lat = Figure(figsize=(5, 2.5), dpi=100, facecolor="#0F172A")
    FigureCanvasAgg(fig_lat)
    ax_lat = fig_lat.add_subplot(111, facecolor="#1E293B")
    ax_lat.plot(bucket_labels, avg_latencies, color="#F59E0B", marker="o", linewidth=2.0)
    ax_lat.set_title("Avg Response Latency (Sec)", color="#F8FAFC", fontsize=10, fontweight="bold")
    ax_lat.set_ylabel("Seconds", color="#94A3B8", fontsize=8)
    ax_lat.tick_params(colors="#94A3B8", labelsize=8)
    ax_lat.grid(True, linestyle=":", alpha=0.2, color="#475569")
    fig_lat.tight_layout()

    return status_text, fig_act, fig_lat
