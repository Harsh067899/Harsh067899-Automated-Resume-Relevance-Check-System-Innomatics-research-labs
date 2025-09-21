"""
PDF Processing Utilities for Streamlit Cloud Compatibility
Provides fallback PDF processing when PyMuPDF is not available
"""

import io
from typing import Optional, Dict, Any, List, Tuple

# Try multiple PDF processing libraries for cloud compatibility
PDF_PROCESSORS = []

# Primary: pdfplumber (most reliable for text extraction)
try:
    import pdfplumber
    PDF_PROCESSORS.append('pdfplumber')
except ImportError:
    pass

# Secondary: pypdf (good for basic text extraction)
try:
    import pypdf
    PDF_PROCESSORS.append('pypdf')
except ImportError:
    pass

# Tertiary: pdfminer (robust for complex PDFs)  
try:
    from pdfminer.high_level import extract_text as pdfminer_extract_text
    from pdfminer.layout import LAParams
    PDF_PROCESSORS.append('pdfminer')
except ImportError:
    pass

# Legacy: PyMuPDF/fitz (if available)
try:
    import fitz
    PDF_PROCESSORS.append('fitz')
except ImportError:
    pass


def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract text from PDF using available processors
    Tries multiple libraries for maximum compatibility
    """
    if not PDF_PROCESSORS:
        raise RuntimeError("No PDF processing libraries available")
    
    # Reset file pointer
    if hasattr(pdf_file, 'seek'):
        pdf_file.seek(0)
    
    # Try each processor in order of preference
    for processor in PDF_PROCESSORS:
        try:
            if processor == 'pdfplumber':
                return _extract_with_pdfplumber(pdf_file)
            elif processor == 'pypdf':
                return _extract_with_pypdf(pdf_file)
            elif processor == 'pdfminer':
                return _extract_with_pdfminer(pdf_file)
            elif processor == 'fitz':
                return _extract_with_fitz(pdf_file)
        except Exception as e:
            print(f"❌ Failed to extract with {processor}: {str(e)}")
            continue
    
    raise RuntimeError("All PDF processors failed to extract text")


def _extract_with_pdfplumber(pdf_file) -> str:
    """Extract text using pdfplumber"""
    text = ""
    
    # Handle both file-like objects and bytes
    if hasattr(pdf_file, 'read'):
        pdf_bytes = pdf_file.read()
    else:
        pdf_bytes = pdf_file
    
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    
    return text.strip()


def _extract_with_pypdf(pdf_file) -> str:
    """Extract text using pypdf"""
    text = ""
    
    # Handle both file-like objects and bytes
    if hasattr(pdf_file, 'read'):
        pdf_bytes = pdf_file.read()
    else:
        pdf_bytes = pdf_file
    
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    return text.strip()


def _extract_with_pdfminer(pdf_file) -> str:
    """Extract text using pdfminer"""
    # Handle both file-like objects and bytes
    if hasattr(pdf_file, 'read'):
        pdf_bytes = pdf_file.read()
    else:
        pdf_bytes = pdf_file
    
    laparams = LAParams(
        boxes_flow=0.5,
        word_margin=0.1,
        char_margin=2.0,
        line_margin=0.5
    )
    
    return pdfminer_extract_text(io.BytesIO(pdf_bytes), laparams=laparams)


def _extract_with_fitz(pdf_file) -> str:
    """Extract text using PyMuPDF/fitz (if available)"""
    text = ""
    
    # Handle both file-like objects and bytes
    if hasattr(pdf_file, 'read'):
        pdf_bytes = pdf_file.read()
    else:
        pdf_bytes = pdf_file
    
    doc = fitz.open("pdf", pdf_bytes)
    for page in doc:
        text += page.get_text() + "\n"
    doc.close()
    
    return text.strip()


def create_simple_annotated_pdf(original_pdf, annotations: List[Dict]) -> bytes:
    """
    Create a simple annotated PDF without PyMuPDF
    Falls back to text-based feedback when PDF annotation is not available
    """
    try:
        if 'fitz' in PDF_PROCESSORS:
            return _create_fitz_annotated_pdf(original_pdf, annotations)
        else:
            # Fallback: return original PDF with a note about text-based feedback
            print("⚠️ PDF annotation not available without PyMuPDF. Providing text-based feedback.")
            return original_pdf
    except Exception as e:
        print(f"❌ PDF annotation failed: {str(e)}")
        return original_pdf


def _create_fitz_annotated_pdf(original_pdf, annotations: List[Dict]) -> bytes:
    """Create annotated PDF using PyMuPDF if available"""
    if hasattr(original_pdf, 'read'):
        pdf_bytes = original_pdf.read()
    else:
        pdf_bytes = original_pdf
    
    doc = fitz.open("pdf", pdf_bytes)
    
    for annotation in annotations:
        page_num = annotation.get('page', 0)
        if page_num < len(doc):
            page = doc[page_num]
            
            # Add highlight annotation
            rect = annotation.get('rect', [50, 50, 150, 70])
            highlight = page.add_highlight_annot(fitz.Rect(rect))
            
            # Set color based on feedback type
            color = annotation.get('color', [1, 1, 0])  # Default yellow
            highlight.set_colors(stroke=color)
            
            # Add note
            note = annotation.get('note', 'Feedback')
            highlight.set_content(note)
            highlight.update()
    
    # Save annotated PDF
    annotated_bytes = doc.write()
    doc.close()
    
    return annotated_bytes


def get_available_processors() -> List[str]:
    """Get list of available PDF processors"""
    return PDF_PROCESSORS.copy()


def get_pdf_info() -> Dict[str, Any]:
    """Get information about PDF processing capabilities"""
    return {
        'available_processors': PDF_PROCESSORS,
        'primary_processor': PDF_PROCESSORS[0] if PDF_PROCESSORS else None,
        'annotation_support': 'fitz' in PDF_PROCESSORS,
        'total_processors': len(PDF_PROCESSORS)
    }


# Test function for debugging
def test_pdf_processing():
    """Test PDF processing capabilities"""
    info = get_pdf_info()
    print("📄 PDF Processing Capabilities:")
    print(f"   Available processors: {info['available_processors']}")
    print(f"   Primary processor: {info['primary_processor']}")
    print(f"   Annotation support: {info['annotation_support']}")
    print(f"   Total processors: {info['total_processors']}")
    
    if not info['available_processors']:
        print("❌ No PDF processors available!")
        return False
    
    print("✅ PDF processing ready!")
    return True


if __name__ == "__main__":
    test_pdf_processing()