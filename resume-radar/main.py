import io, contextlib
import os
os.environ["MUPDF_LOG_LEVEL"] = "0"  # attempt to silence MuPDF logs 

# PDF libraries

# ⚠️ ISSUE: Highlight annotations ignore custom fill colors in most PDF readers.
# This prints non-fatal warnings "Warning: fill color ignored for annot type 'Highlight'." 
# TODO: find a workaround or alternative annotation type.
import fitz  # PyMuPDF

import pypdf

from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import re
import json

from extract_pdf import extract_text_from_pdf
from parse_cv import split_into_sections_dynamic
from global_llm_reflection import global_llm_reflection
from sectional_llm_critique import section_feedback
from granular_llm_critique import granular_feedback
from overlay_pdf import overlay_pdf

import argparse

# Load environment variables from .env if it exists
load_dotenv()

# Configure OpenRouter client
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def extract_text_from_pdf(path: Path, method: str = "pymupdf") -> str:
    """Extract text from PDF using either pypdf or PyMuPDF (default)."""
    text = ""
    if method == "pypdf2":
        with open(path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
                text += "\n"
    elif method == "pymupdf":
        with fitz.open(path) as doc:
            for page in doc:
                text += page.get_text()
    else:
        raise ValueError("Unsupported method. Use 'pypdf2' or 'pymupdf'.")
    return text

def chunk_text(text: str, max_chars: int = 1500) -> list[str]:
    """Split text into chunks of up to max_chars."""
    chunks = []
    current = ""
    for line in text.splitlines():
        if len(current) + len(line) < max_chars:
            current += line + "\n"
        else:
            chunks.append(current.strip())
            current = line + "\n"
    if current:
        chunks.append(current.strip())
    return chunks

def clean_text(text: str) -> str:
    """Fix common PDF text extraction issues (extra spaces, linebreaks)."""
    # Collapse multiple spaces into one
    text = re.sub(r"\s+", " ", text)
    # Strip leading/trailing whitespace
    return text.strip()

def query_llm(chunk: str) -> dict:
    """Send chunk to OpenRouter API and return structured feedback with ratings and tags."""

    prompt = f"""
    You are a strict resume reviewer. Be critical and use the full rating scale.
    For each distinct section or element in the text, do the following:

    1. Give it a rating from 1 to 20 (integer only). Use the full scale:
       - 17-20: Exceptional quality, significantly stands out
       - 13-16: Good quality, solid and effective
       - 9-12: Average/adequate, meets basic requirements
       - 5-8: Below average, needs improvement
       - 1-4: Poor quality, significant issues

    2. Add one of these tags based on the rating:
       - [GOOD] if rating ≥ 17
       - [BAD] if rating ≤ 8
       - [CAUTION] if rating is between 9 and 12
       - Leave untagged if rating is between 13 and 16.

    3. Provide a brief justification (1–2 sentences max).

    Be critical - not everything should be rated highly!

    Respond in JSON format like this:
    [
      {{
        "snippet": "summary of text element",
        "rating": 18,
        "tag": "[GOOD]",
        "feedback": "Exceptionally clear and impactful professional summary."
      }},
      {{
        "snippet": "education section",
        "rating": 10,
        "tag": "[CAUTION]",
        "feedback": "Basic information provided but lacks detail on coursework or achievements."
      }}
    ]

    Resume text:
    {chunk}
    """

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    
    feedback = response.choices[0].message.content.strip()
    return {"chunk": chunk[:80], "feedback": feedback}

def parse_llm_feedback(raw_feedback: str) -> list[dict]:
    """Extract and parse JSON from LLM feedback safely."""
    # Remove Markdown code fences if present
    cleaned = re.sub(r"^```json|```$", "", raw_feedback.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print("⚠️ Could not parse feedback as JSON. Raw output returned.")
        return [{"raw_feedback": raw_feedback}]

# Map tags to colors (RGB format, 0–1 range)
# Updated to match new stricter rating criteria
TAG_COLORS = {
    "[GOOD]": (0.6, 0.9, 0.6),    # green - ratings 17-20
    "[CAUTION]": (1.0, 1.0, 0.6), # yellow - ratings 9-12  
    "[BAD]": (1.0, 0.6, 0.6),     # red - ratings 1-8
    "": (0.9, 0.9, 0.9)           # grey/neutral - ratings 13-16
}

def main():
    parser = argparse.ArgumentParser(description="Resume-Radar: CV reviewer & decorator")
    parser.add_argument("input_pdf", type=Path, help="Path to input CV PDF")
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Path to save annotated PDF (default: outputs/<input_basename>_reviewed.pdf)"
    )
    args = parser.parse_args()

    input_pdf = args.input_pdf
    output_pdf = args.output or Path("outputs") / f"{input_pdf.stem}_reviewed.pdf"

    print("⌖ resume-radar: starting full pipeline")

    # 1. Extract text
    cv_text = extract_text_from_pdf(input_pdf)
    print("\n--- Extracted CV Text ---")
    print(cv_text[:500], "...\n")  # preview only

    # 2. Global reflection
    reflection = global_llm_reflection(cv_text)
    print("\n--- Global Reflection ---")
    print(json.dumps(reflection, indent=2))

    # 3. Split into sections
    sections = split_into_sections_dynamic(cv_text)

    # 4. Per-section feedback (mark them as "section")
    section_results = section_feedback(sections)
    for fb in section_results:
        fb["level"] = "section"

    # 5. Granular feedback (mark them as "granular")
    granular_results = granular_feedback(sections)
    for fb in granular_results:
        fb["level"] = "granular"

    # 6. Collate for overlay:
    section_feedback_list = [fb for fb in section_results if fb.get("tag")]
#    granular_feedback_list = [fb for fb in granular_results if fb.get("tag")]

    # 7. Only keep valid dicts with snippets
#    annotated_feedback = [fb for fb in annotated_feedback if isinstance(fb, dict) and "snippet" in fb]

    # 8. Overlay PDF with annotations
    overlay_pdf(input_pdf, output_pdf, section_feedback_list, granular_results)
    print(f"\n📄 Pipeline complete: annotated CV written to {output_pdf}")

if __name__ == "__main__":
    main()