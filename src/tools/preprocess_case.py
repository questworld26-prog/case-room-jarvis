"""
Offline Business Case Study Preprocessor Script
Scans target case study folder(s) in `resource/`, extracts clean text, strips header/footer noise,
generates `extracted_context.txt` for instant sub-0.1s startup, and creates an Executive High-Value Case Summary if missing.

Usage:
  PYTHONPATH=src uv run python src/tools/preprocess_case.py --case EcoBrew
  PYTHONPATH=src uv run python src/tools/preprocess_case.py --case all
"""

import argparse
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()

RESOURCE_DIR = Path(__file__).resolve().parent.parent.parent / "resource"


# [spec: CACHE-001]
def clean_extracted_text(raw_text: str) -> str:
    """Clean up extracted text by removing repetitive page headers, footers, and redundant whitespace."""
    lines = raw_text.split("\n")
    cleaned_lines = []

    # Common noise patterns in case study PDFs
    header_footer_patterns = [
        r"COPIES MAY NOT BE MADE WITHOUT PERMISSION",
        r"NO PART OF THIS PUBLICATION MAY BE COPIED",
        r"To access INSEAD teaching materials",
        r"Do Not Copy or Post",
        r"This document is authorized for educator review",
        r"Permissions@hbsp\.harvard\.edu",
        r"©\s*HEC\s*Montréal.*",
        r"Copyright\s*©.*",
        r"REPRODUCED OR DISTRIBUTED IN ANY FORM OR MEDIUM WHATSOEVER.*",
        r"Distributed by The Case Centre.*",
        r"Educator copy - do not distribute.*",
        r"Page\s*\d+(\s*of\s*\d+)?",
        r"^\d+\s*$",
    ]

    for line in lines:
        l_strip = line.strip()
        if not l_strip:
            cleaned_lines.append("")
            continue

        # Check if line matches any noise pattern
        is_noise = any(re.search(pat, l_strip, re.IGNORECASE) for pat in header_footer_patterns)
        if not is_noise:
            cleaned_lines.append(l_strip)

    # Collapse multiple consecutive blank lines into single blank lines
    text_result = "\n".join(cleaned_lines)
    text_result = re.sub(r"\n{3,}", "\n\n", text_result)
    return text_result.strip()


# [spec: CACHE-001]
def csv_to_markdown_table(csv_text: str) -> str:
    """Convert raw CSV string into a formatted GitHub markdown table."""
    import csv
    import io

    reader = csv.reader(io.StringIO(csv_text))
    rows = [r for r in reader if any(cell.strip() for cell in r)]
    if not rows:
        return ""
    header = rows[0]
    md_lines = ["| " + " | ".join(cell.strip() for cell in header) + " |"]
    md_lines.append("| " + " | ".join("---" for _ in header) + " |")
    for r in rows[1:]:
        # Pad row if shorter than header
        padded = r + [""] * (len(header) - len(r))
        md_lines.append("| " + " | ".join(cell.strip() for cell in padded[: len(header)]) + " |")
    return "\n".join(md_lines)


# [spec: CACHE-001]
def detect_empty_image_exhibits(text: str) -> str | list[str]:
    """Scan extracted text for exhibit headings that lack numerical data (likely embedded images)."""
    warnings = []
    exhibit_pattern = re.compile(r"(Exhibit\s+\d+[^:\n]*[:\n]?[^\n]*)", re.IGNORECASE)
    matches = list(exhibit_pattern.finditer(text))
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else start + 300
        snippet = text[start:end].strip()
        # If the snippet has fewer than 2 digits or under 60 characters before the next exhibit or section
        digits = len(re.findall(r"\d", snippet))
        if digits < 2 or len(snippet) < 60:
            warnings.append(m.group(1).strip())
    return warnings


# [spec: CACHE-001]
def generate_case_manifest_header(
    case_name: str,
    primary_docs: list[str],
    supporting_docs: list[str],
    supplementary_files: list[str],
    empty_exhibit_warnings: list[str],
) -> str:
    """Generate an authoritative Case Knowledge Grounding Manifest preamble for extracted_context.txt."""
    lines = [
        f"=== CASE KNOWLEDGE MANIFEST: {case_name} ===",
        f"Active Business Case: {case_name}",
        f"Primary Case Document(s): {', '.join(primary_docs) if primary_docs else 'None'}",
        f"Supporting Document(s): {', '.join(supporting_docs) if supporting_docs else 'None'}",
        f"Curated Supplementary Exhibit Files: {', '.join(supplementary_files) if supplementary_files else 'None'}",
        "",
        "CRITICAL GROUNDING DIRECTIVES FOR ASSISTANT:",
        "1. All factual statements, operational data, and numerical figures must be strictly grounded in this context.",
        "2. If an exhibit or metric (e.g. EBITDA, 2017 Gross Profit, specific nuclear plants) is not explicitly present in the data tables below, explicitly state that it is not provided in the case materials rather than extrapolating or guessing.",
    ]
    if empty_exhibit_warnings and not supplementary_files:
        lines.append("3. NOTICE: The following exhibits in the case appear to be image/chart scans without raw data:")
        for w in empty_exhibit_warnings[:5]:
            lines.append(f"   - {w}")
        lines.append("   Do not invent exact numbers for these exhibits; refer to the qualitative discussion.")
    lines.append("=" * 50)
    return "\n".join(lines)


# [spec: CACHE-001]
def generate_ai_case_summary(case_name: str, full_text: str) -> str:
    """Generate a structured 1-2 page High-Value Case Summary using Gemini AI (with extractive fallback)."""
    print(f"Generating AI High-Value Summary for '{case_name}'...")

    prompt = f"""
You are a senior business school professor preparing an executive case study high-value summary for MBA students.

Case Study Name: {case_name}
Full Case Text (Snippet):
{full_text[:15000]}

Generate a concise, highly structured 2-page High-Value Executive Summary containing:
1. **Executive Overview & Core Dilemma**: Company background, industry context, and primary strategic challenge.
2. **Key Strategic Drivers & Operations**: Products, technology, supply chain, market position, and growth initiatives.
3. **Financial & Operational Performance Highlights**: Key revenue, profit, unit economics, or sustainability metrics mentioned in the case.
4. **Key Case Study Discussion Questions**: 4 critical analytical questions for class discussion.

Format cleanly with clear headings and bullet points.
"""
    try:
        from google import genai

        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt, config={"temperature": 0.2}
            )
            if response and response.text:
                clean_text = re.sub(r"^```[a-z]*\s*", "", response.text.strip(), flags=re.MULTILINE)
                clean_text = re.sub(r"\s*```$", "", clean_text, flags=re.MULTILINE)
                return clean_text
    except Exception as e:
        print(f"Notice: AI summary generation notice ({e}). Using structured extractive summary fallback.")

    # Extractive Fallback Summary
    return f"""# Executive High-Value Summary: {case_name}

## 1. Executive Overview & Strategic Dilemma
This case study examines '{case_name}', detailing key strategic shifts, competitive market positioning, and operational decisions.

## 2. Key Case Content & Data Points
{full_text[:3000]}...

## 3. Recommended Discussion Questions
1. What are the key competitive advantages and core capabilities of {case_name}?
2. How should management navigate strategic pivots or market shifts presented in the case?
3. What financial and operational trade-offs exist in the proposed strategic plan?
4. How can leadership balance long-term innovation with short-term financial performance?
"""


def _extract_pdf_text_block(pdf_path: Path, header_prefix: str = "DOCUMENT") -> str | None:
    try:
        reader = PdfReader(pdf_path)
        pages = [page.extract_text() or "" for page in reader.pages]
        cleaned = clean_extracted_text("\n\n".join(p for p in pages if p))
        return f"=== {header_prefix}: {pdf_path.name} ===\n\n{cleaned}"
    except Exception as e:
        print(f" ❌ Error processing {pdf_path.name}: {e}")
        return None


def _collect_case_documents(
    case_dir: Path, case_name: str, pdf_files: list[Path]
) -> tuple[list[Path], list[Path], list[Path], list[Path], list[str]]:
    primary_pdfs, supporting_pdfs, auxiliary_pdfs = [], [], []
    for p in pdf_files:
        lower_name = p.name.lower()
        if any(w in lower_name for w in ["question", "quiz", "rubric", "outline"]):
            auxiliary_pdfs.append(p)
        elif "case" in lower_name or case_name.lower() in lower_name:
            primary_pdfs.append(p)
        else:
            supporting_pdfs.append(p)

    ordered_pdfs = sorted(primary_pdfs, key=lambda p: p.name) + sorted(supporting_pdfs, key=lambda p: p.name)
    print(f"Found {len(pdf_files)} PDF file(s): {[p.name for p in ordered_pdfs]}")
    if auxiliary_pdfs:
        print(f"ℹ️ Auxiliary pedagogical files segregated: {[p.name for p in auxiliary_pdfs]}")

    extracted_parts: list[str] = []
    for pdf_path in ordered_pdfs:
        print(f" - Extracting text from {pdf_path.name}...")
        block = _extract_pdf_text_block(pdf_path, "DOCUMENT")
        if block:
            extracted_parts.append(block)

    supp_files: list[Path] = []
    for ext in ("*.txt", "*.md", "*.csv", "*.json"):
        supp_files.extend(case_dir.glob(f"supplementary_{ext}"))
        supp_files.extend(case_dir.glob(f"exhibit_{ext}"))
    supp_files = sorted(set(supp_files), key=lambda p: p.name)

    for supp_path in supp_files:
        print(f" - Ingesting supplementary exhibit data from {supp_path.name}...")
        try:
            supp_text = supp_path.read_text(encoding="utf-8").strip()
            if supp_path.suffix.lower() == ".csv":
                supp_text = csv_to_markdown_table(supp_text)
            if supp_text:
                extracted_parts.append(
                    f"=== CURATED SUPPLEMENTARY DATA & EXHIBITS: {supp_path.name} ===\n\n{supp_text}"
                )
        except Exception as e:
            print(f" ❌ Error reading {supp_path.name}: {e}")

    for aux_path in sorted(auxiliary_pdfs, key=lambda p: p.name):
        block = _extract_pdf_text_block(aux_path, "AUXILIARY PEDAGOGICAL REFERENCE (NOT CORE CASE STUDY FACTS)")
        if block:
            extracted_parts.append(block)

    return primary_pdfs, supporting_pdfs, auxiliary_pdfs, supp_files, extracted_parts


# [spec: CACHE-001]
def preprocess_case_folder(case_name: str) -> bool:
    """Preprocess a single business case study folder in resource/."""
    case_dir = RESOURCE_DIR / case_name
    if not case_dir.exists() or not case_dir.is_dir():
        print(f"❌ Error: Case directory '{case_dir}' does not exist.")
        return False

    print("\n==================================================")
    print(f"🔍 Preprocessing Case Study: '{case_name}'")
    print("==================================================")

    pdf_files = list(case_dir.glob("*.pdf")) or list(case_dir.glob("**/*.pdf"))
    if not pdf_files:
        print(f"⚠️ Warning: No PDF files found in '{case_dir}'.")
        return False

    primary_pdfs, supporting_pdfs, _, supp_files, all_extracted_parts = _collect_case_documents(
        case_dir, case_name, pdf_files
    )
    full_case_text = "\n\n\n".join(all_extracted_parts)

    warnings = detect_empty_image_exhibits(full_case_text)
    if warnings and not supp_files:
        print(f"⚠️ Warning: Found {len(warnings)} potentially empty image-based exhibit(s) without text:")
        for w in warnings[:5]:
            print(f"   • {w}")
        print("   💡 Tip: Add numerical tables to 'supplementary_exhibits.txt' to eliminate AI chart guessing.")
    elif supp_files:
        print(f"ℹ️ Curated supplementary exhibits attached: {[sf.name for sf in supp_files]}")

    manifest_header = generate_case_manifest_header(
        case_name=case_name,
        primary_docs=[p.name for p in primary_pdfs],
        supporting_docs=[p.name for p in supporting_pdfs],
        supplementary_files=[sf.name for sf in supp_files],
        empty_exhibit_warnings=warnings,
    )
    final_context_text = f"{manifest_header}\n\n\n{full_case_text}"
    (case_dir / "extracted_context.txt").write_text(final_context_text, encoding="utf-8")

    char_count = len(final_context_text)
    print(f"✅ Generated 'extracted_context.txt' ({char_count:,} characters, ~{char_count // 4:,} tokens).")

    summary_files = list(case_dir.glob("*[S|s]ummary*"))
    if not summary_files:
        print(f"No existing summary file found for '{case_name}'. Creating High-Value Case Summary...")
        summary_content = generate_ai_case_summary(case_name, final_context_text)
        summary_path = case_dir / f"{case_name}_Case_Study_High_Value_Summary.txt"
        summary_path.write_text(summary_content, encoding="utf-8")
        print(f"✅ Saved High-Value Summary to '{summary_path.name}'.")
    else:
        print(f"ℹ️ High-Value Summary file already present: {[s.name for s in summary_files]}")

    print(f"🎉 Preprocessing for '{case_name}' completed successfully!\n")
    return True


def main():
    parser = argparse.ArgumentParser(description="Offline Business Case Study Preprocessor Tool")
    parser.add_argument(
        "--case", type=str, default="all", help="Case study folder name in resource/ (e.g. EcoBrew, or 'all')"
    )
    args = parser.parse_args()

    if not RESOURCE_DIR.exists():
        print(f"Error: Resource directory '{RESOURCE_DIR}' not found.")
        sys.exit(1)

    if args.case.lower() == "all":
        case_dirs = [d.name for d in RESOURCE_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")]
        print(f"Preprocessing all discovered case studies: {case_dirs}")
        for cname in sorted(case_dirs):
            preprocess_case_folder(cname)
    else:
        preprocess_case_folder(args.case)


if __name__ == "__main__":
    main()
