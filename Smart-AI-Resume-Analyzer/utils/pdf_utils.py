"""
PDF Processing Utilities for Streamlit Cloud Compatibility
Provides fallback PDF processing when PyMuPDF is not available
"""

import io
import os
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
    Create annotated PDF - prefer original resume-radar overlay method
    This is a simplified interface that delegates to the original overlay system
    """
    try:
        # If PyMuPDF is available, use it (best quality)
        if 'fitz' in PDF_PROCESSORS:
            return _create_fitz_annotated_pdf(original_pdf, annotations)
        else:
            # Cloud fallback: return original PDF
            print("⚠️ PDF annotation not available without PyMuPDF. Returning original PDF.")
            if hasattr(original_pdf, 'read'):
                original_pdf.seek(0)
                return original_pdf.read()
            return original_pdf
    except Exception as e:
        print(f"❌ PDF annotation failed: {str(e)}")
        # Return original PDF if annotation fails
        if hasattr(original_pdf, 'read'):
            original_pdf.seek(0)
            return original_pdf.read()
        return original_pdf


def _create_fitz_annotated_pdf(original_pdf, annotations: List[Dict]) -> bytes:
    """Create annotated PDF using PyMuPDF (fitz) - Original resume-radar overlay system"""
    try:
        import fitz
        
        # Get PDF bytes
        if hasattr(original_pdf, 'read'):
            original_pdf.seek(0)
            pdf_bytes = original_pdf.read()
        else:
            pdf_bytes = original_pdf
        
        # Open PDF with fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # TAG colors mapping from original resume-radar system
        TAG_COLORS = {
            "[GOOD]": [0.0, 0.7, 0.0],      # Green
            "[CAUTION]": [1.0, 0.7, 0.0],   # Yellow
            "[BAD]": [1.0, 0.2, 0.2],       # Red
            "[INFO]": [0.0, 0.5, 1.0],      # Blue
            "default": [1.0, 1.0, 0.0]      # Yellow default
        }
        
        # Process annotations using original overlay method
        for annotation in annotations:
            snippet = annotation.get('snippet', '')
            note = annotation.get('note', '')
            tag = annotation.get('tag', '[INFO]')
            
            if snippet and note:
                color = TAG_COLORS.get(tag, TAG_COLORS['default'])
                _place_annotation_original(doc, snippet, note, tag, color)
        
        # Get annotated PDF bytes
        annotated_pdf_bytes = doc.write()
        doc.close()
        
        print("✅ Original resume-radar PDF annotation completed")
        return annotated_pdf_bytes
        
    except Exception as e:
        print(f"❌ PyMuPDF annotation failed: {str(e)}")
        # Return original PDF
        if hasattr(original_pdf, 'read'):
            original_pdf.seek(0)
            return original_pdf.read()
        return original_pdf


def _place_annotation_original(doc, snippet: str, feedback_content: str, tag: str, color: List[float]):
    """
    Place annotation on PDF using original resume-radar method with text snippet search
    """
    try:
        import fitz
        
        # Search for snippet in all pages
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Search for the text snippet
            text_instances = page.search_for(snippet)
            
            for rect in text_instances:
                try:
                    # Create highlight annotation
                    highlight = page.add_highlight_annot(rect)
                    highlight.set_colors(stroke=color)
                    highlight.update()
                    
                    # Create popup annotation with feedback
                    popup_rect = fitz.Rect(rect.x0, rect.y1 + 5, rect.x0 + 200, rect.y1 + 50)
                    popup = page.add_text_annot(popup_rect.tl, f"{tag}: {feedback_content}")
                    popup.set_info(content=f"{tag}: {feedback_content}")
                    popup.update()
                    
                    # Add radar icon if available
                    try:
                        icon_rect = fitz.Rect(rect.x1 + 5, rect.y0, rect.x1 + 20, rect.y0 + 15)
                        icon = page.add_text_annot(icon_rect.tl, "📡")
                        icon.set_info(content=f"Resume Radar: {tag}")
                        icon.update()
                    except:
                        pass  # Icon placement is optional
                        
                except Exception as e:
                    print(f"⚠️ Could not place annotation for snippet '{snippet[:30]}...': {e}")
                    continue
    
    except Exception as e:
        print(f"❌ Annotation placement failed: {e}")


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


def extract_text_from_docx(docx_file) -> str:
    """
    Extract text from DOCX file
    Compatible with Streamlit Cloud environment
    """
    try:
        from docx import Document
        
        # Handle both file-like objects and bytes
        if hasattr(docx_file, 'read'):
            doc = Document(docx_file)
        else:
            doc = Document(io.BytesIO(docx_file))
        
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text.strip()
    
    except ImportError:
        raise RuntimeError("python-docx package not available for DOCX processing")
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from DOCX: {str(e)}")


if __name__ == "__main__":
    test_pdf_processing()