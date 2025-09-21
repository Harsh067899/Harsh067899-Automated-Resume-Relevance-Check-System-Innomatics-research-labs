from pathlib import Path
import os
import sys

# Add utils directory to Python path for cloud compatibility
utils_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils')
if utils_path not in sys.path:
    sys.path.insert(0, utils_path)

# Import cloud-compatible PDF utilities
try:
    from pdf_utils import extract_text_from_pdf as extract_pdf_text
except ImportError:
    # Fallback for local development
    try:
        import fitz  # PyMuPDF
        def extract_pdf_text(pdf_file):
            """Fallback PDF extraction using PyMuPDF"""
            text = []
            if isinstance(pdf_file, (str, Path)):
                with fitz.open(pdf_file) as doc:
                    for page in doc:
                        text.append(page.get_text("text"))
            else:
                # Handle file-like objects
                doc = fitz.open("pdf", pdf_file.read())
                for page in doc:
                    text.append(page.get_text("text"))
                doc.close()
            return "\n".join(text)
    except ImportError:
        def extract_pdf_text(pdf_file):
            raise RuntimeError("No PDF processing libraries available. Please install pdfplumber, pypdf, or PyMuPDF.")

def extract_text_from_pdf(path: Path) -> str:
    """Extract text from a PDF using available PDF processors."""
    try:
        # For file paths, read the file first
        if isinstance(path, (str, Path)):
            with open(path, 'rb') as f:
                return extract_pdf_text(f)
        else:
            # For file-like objects
            return extract_pdf_text(path)
    except Exception as e:
        print(f"❌ PDF extraction failed for {path}: {str(e)}")
        return ""