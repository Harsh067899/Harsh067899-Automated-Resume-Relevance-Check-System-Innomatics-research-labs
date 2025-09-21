"""
Bridge to run the original resume-radar pipeline from the hosted app.
This mirrors resume-radar/main.py behavior to produce annotated PDFs.
"""

from __future__ import annotations

import io
import os
import sys
import json
import tempfile
from pathlib import Path
from typing import Tuple


def _add_resume_radar_to_path():
    """Ensure the sibling resume-radar package is importable."""
    # Smart-AI-Resume-Analyzer/resume_radar/ -> project root
    here = Path(__file__).resolve()
    project_root = here.parents[2]
    rr_path = project_root / "resume-radar"
    if str(rr_path) not in sys.path:
        sys.path.insert(0, str(rr_path))
    return rr_path


def run_resume_radar_pipeline(pdf_input, output_dir: str | None = None) -> Tuple[bytes, str]:
    """
    Run the original resume-radar pipeline on the given PDF input and return (bytes, output_path).

    pdf_input: file-like object with .read() or a filesystem path to a PDF
    output_dir: directory to write the annotated PDF (temp dir if None)
    """
    rr_path = _add_resume_radar_to_path()

    # Lazy imports after path updated
    from extract_pdf import extract_text_from_pdf
    from parse_cv import split_into_sections_dynamic
    from global_llm_reflection import global_llm_reflection
    from sectional_llm_critique import section_feedback
    from granular_llm_critique import granular_feedback
    from overlay_pdf import overlay_pdf

    os.environ.setdefault("MUPDF_LOG_LEVEL", "0")

    # Prepare input temp file if needed
    if hasattr(pdf_input, "read"):
        original_name = getattr(pdf_input, "name", "resume")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_in:
            pdf_input.seek(0)
            tmp_in.write(pdf_input.read())
            input_path = Path(tmp_in.name)
    else:
        input_path = Path(pdf_input)
        original_name = input_path.stem

    # Output location
    out_dir = Path(output_dir or tempfile.gettempdir())
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / f"{Path(original_name).stem}_reviewed.pdf"

    # Mirror CLI print for parity with local run
    print("⌖ resume-radar: starting full pipeline")

    # 1) Extract text
    cv_text = extract_text_from_pdf(input_path)

    # 2) Global reflection
    _ = global_llm_reflection(cv_text)

    # 3) Split into sections
    sections = split_into_sections_dynamic(cv_text)

    # 4) Section feedback (tagged ones used for overlay)
    section_results = section_feedback(sections)
    section_feedback_list = [fb for fb in section_results if fb.get("tag")]

    # 5) Granular feedback (full list passed so snippet search can try)
    granular_results = granular_feedback(sections)

    # 6) Overlay and save
    overlay_pdf(input_path, output_path, section_feedback_list, granular_results)

    # Read bytes back
    with open(output_path, "rb") as f:
        annotated_bytes = f.read()

    return annotated_bytes, str(output_path)
