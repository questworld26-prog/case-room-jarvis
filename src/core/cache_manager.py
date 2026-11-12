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
High-Speed Cleaned Text Pipeline & Case Context Manager.
Loads preprocessed extracted_context.txt text directly for sub-3s response latency.
"""

import asyncio
import os
import re
import sys
from pathlib import Path
from typing import Any

from google import genai

from config import app_state, get_default_case_study

RESOURCE_ROOT = Path(__file__).resolve().parent.parent.parent / "resource"
_GENAI_CLIENT_CACHE: dict[tuple[str, Any], genai.Client] = {}


# [spec: CACHE-004]
def validate_gemini_api_key() -> tuple[bool, str]:
    """Verify GOOGLE_API_KEY is non-empty and authenticates against the Gemini API."""
    api_key = (os.getenv("GOOGLE_API_KEY") or "").strip()
    if not api_key:
        return False, "GOOGLE_API_KEY environment variable is missing or empty."
    try:
        client = genai.Client(api_key=api_key)
        client.models.get(model=app_state.model_id)
        return True, ""
    except Exception as exc:
        return False, f"Google Gemini API key validation failed: {exc}"


# [spec: CACHE-004]
def format_api_key_startup_alert(reason: str, use_color: bool | None = None) -> str:
    """Format a prominent bordered terminal banner explaining why startup halted on API key failure."""
    if use_color is None:
        use_color = hasattr(sys.stderr, "isatty") and sys.stderr.isatty()

    red = "\033[1;31m" if use_color else ""
    yellow = "\033[1;33m" if use_color else ""
    cyan = "\033[1;36m" if use_color else ""
    reset = "\033[0m" if use_color else ""

    bar = "=" * 72
    lines = [
        f"{red}{bar}{reset}",
        f"{red}🚨 STARTUP HALTED: GOOGLE GEMINI API KEY MISSING OR INVALID{reset}",
        f"{red}{bar}{reset}",
        f"{red}❌ Reason: {reason}{reset}",
        "",
        f"{cyan}🔧 How to fix:{reset}",
        "   1. Create or check your key at https://aistudio.google.com/apikey",
        "   2. Set GOOGLE_API_KEY=your_actual_key in your .env file (no quotes or spaces)",
        "   3. See docs/TROUBLESHOOTING.md ('API key not valid', '403', or 'PERMISSION_DENIED')",
        f"{yellow}⚠️ Application startup aborted. Server will not start without a valid Gemini API key.{reset}",
        f"{red}{bar}{reset}",
    ]
    return "\n".join(lines)


# [spec: CACHE-002]
def get_genai_client() -> genai.Client:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is missing.")
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    cache_key = (api_key, loop)
    client = _GENAI_CLIENT_CACHE.get(cache_key)
    if client is None or (loop is not None and loop.is_closed()):
        client = genai.Client(api_key=api_key)
        _GENAI_CLIENT_CACHE[cache_key] = client
    return client


# [spec: CACHE-001]
# [spec: CACHE-002]
def load_case_text_context(case_name: str | None = None) -> str:
    """Load clean preprocessed case text context from extracted_context.txt."""
    target_case = case_name or app_state.active_case_study or get_default_case_study()
    root_resource = RESOURCE_ROOT
    resource_dir = root_resource / target_case

    if not resource_dir.exists():
        resource_dir = root_resource

    preprocessed_file = resource_dir / "extracted_context.txt"
    if preprocessed_file.exists():
        try:
            with open(preprocessed_file, encoding="utf-8") as f:
                extracted = f.read()
            print(
                f"✅ Loaded preprocessed text context for '{target_case}' ({len(extracted):,} characters, ~{len(extracted) // 4:,} tokens)."
            )
            return extracted
        except Exception as e:
            print(f"Notice reading preprocessed context for {target_case}: {e}")

    # Fallback to direct PDF text extraction if extracted_context.txt missing
    from pypdf import PdfReader

    pdf_files = list(resource_dir.glob("*.pdf"))
    if not pdf_files and resource_dir != root_resource:
        pdf_files = list(resource_dir.glob("**/*.pdf"))

    text_parts = []
    for pdf_path in sorted(pdf_files, key=lambda p: p.name):
        try:
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                txt = page.extract_text()
                if txt:
                    text_parts.append(txt)
        except Exception as e:
            print(f"Warning extracting text from {pdf_path.name}: {e}")

    # Also include any curated supplementary exhibits
    supp_files = list(resource_dir.glob("supplementary_*.*")) + list(resource_dir.glob("exhibit_*.*"))
    for sf in sorted(supp_files, key=lambda p: p.name):
        try:
            with open(sf, encoding="utf-8") as f:
                supp_txt = f.read().strip()
            if supp_txt:
                text_parts.append(f"=== CURATED SUPPLEMENTARY DATA & EXHIBITS: {sf.name} ===\n\n{supp_txt}")
        except Exception as e:
            print(f"Warning reading supplementary file {sf.name}: {e}")

    extracted = "\n\n".join(text_parts)
    print(
        f"Loaded case text context for '{target_case}' ({len(extracted):,} characters, ~{len(extracted) // 4:,} tokens across {len(pdf_files)} PDFs and {len(supp_files)} supplementary files)."
    )

    if extracted and resource_dir.exists() and resource_dir.is_dir():
        try:
            with open(preprocessed_file, "w", encoding="utf-8") as f:
                f.write(extracted)
            print(f"✅ Auto-persisted 'extracted_context.txt' for '{target_case}'.")
        except Exception as e:
            print(f"Notice auto-persisting text context: {e}")

    return extracted


# [spec: CACHE-002]
# [spec: ADMIN-001]
def parse_ttl_string(ttl_str: str) -> str:
    """Normalize TTL string to Google GenAI format (e.g. '14400s' or '300s')."""
    val = str(ttl_str).strip().lower()
    m = re.match(r"^(\d+)\s*(s|m|h)?$", val)
    if not m:
        return "300s"
    num = int(m.group(1))
    unit = m.group(2)
    if unit == "h":
        return f"{num * 3600}s"
    elif unit == "m":
        return f"{num * 60}s"
    return f"{num}s"


# [spec: CACHE-002]
def create_gemini_context_cache(case_name: str | None = None, ttl: str | None = None) -> Any | None:
    """
    Creates or refreshes a Gemini Context Cache using the SDK caches API.
    Caches the case study text so subsequent student requests avoid resending 28k tokens.
    """
    target_case = case_name or app_state.active_case_study or get_default_case_study()
    app_state.active_case_study = target_case

    # Ensure local text context is loaded
    if not app_state.case_text_context or app_state.active_case_study != target_case:
        app_state.case_text_context = load_case_text_context(target_case)

    if not app_state.case_text_context or not app_state.case_text_context.strip():
        app_state.active_cache_name = None
        app_state.cache_info = {}
        print(f"⚠️ No text context available to cache for '{target_case}'.")
        return None

    ttl_formatted = parse_ttl_string(ttl or app_state.cache_ttl or "14400s")

    try:
        from google.genai import types

        client = get_genai_client()

        # Prepare content part for context cache
        content_text = (
            f"### BUSINESS CASE STUDY KNOWLEDGE BASE GROUND TRUTH ###\n"
            f"Case Study: {target_case}\n\n"
            f"{app_state.case_text_context}"
        )

        system_instruction = app_state.get_base_system_instruction()

        cache_config = types.CreateCachedContentConfig(
            contents=[types.Content(role="user", parts=[types.Part.from_text(text=content_text)])],
            system_instruction=system_instruction,
            display_name=f"case_study_{target_case.lower()}_{app_state.session_id}",
            ttl=ttl_formatted,
        )

        print(f"🚀 Creating Gemini Context Cache for '{target_case}' with TTL={ttl_formatted}...")
        cache_obj = client.caches.create(model=app_state.model_id, config=cache_config)

        app_state.active_cache_name = cache_obj.name
        expire_str = str(getattr(cache_obj, "expire_time", ""))
        app_state.cache_info = {
            "name": cache_obj.name,
            "display_name": getattr(cache_obj, "display_name", target_case),
            "expire_time": expire_str,
            "ttl": ttl_formatted,
            "case_study": target_case,
            "status": "active",
        }
        print(
            f"✅ Gemini Context Cache Created Successfully: {cache_obj.name} (TTL: {ttl_formatted}, Expire: {expire_str})"
        )
        return cache_obj
    except Exception as e:
        print(f"Notice: Gemini Context Cache creation failed ({e}). Falling back to in-memory context injection.")
        app_state.active_cache_name = None
        app_state.cache_info = {"status": "fallback", "error": str(e)}
        return None


# [spec: CACHE-002]
# [spec: CACHE-003]
# [spec: EVAL-001]
def get_or_create_cache(
    case_name: str | None = None, force_refresh: bool = False, ttl: str | None = None
) -> Any | None:
    """
    Initializes case text context and creates a Gemini server-side context cache.
    Falls back gracefully to local in-memory text if cache creation is unavailable.
    """
    target_case = case_name or app_state.active_case_study or get_default_case_study()
    app_state.active_case_study = target_case

    print(f"\nInitializing Case Study Knowledge: '{target_case}'...")
    app_state.case_text_context = load_case_text_context(target_case)

    if not app_state.case_text_context or not app_state.case_text_context.strip():
        app_state.active_cache_name = None
        app_state.cache_info = {}
        print(f"⚠️ No text context available to cache for '{target_case}'.")
        return app_state.case_text_context

    # Attempt to prime Gemini Context Cache with configured TTL
    create_gemini_context_cache(target_case, ttl=ttl or app_state.cache_ttl)
    return app_state.case_text_context
