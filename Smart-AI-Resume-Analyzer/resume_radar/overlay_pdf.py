from pathlib import Path
import os
import sys

# Add utils directory to Python path for cloud compatibility
utils_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils')
if utils_path not in sys.path:
    sys.path.insert(0, utils_path)

# Import cloud-compatible PDF utilities
try:
    from pdf_utils import create_simple_annotated_pdf, get_pdf_info
    print("✅ Using cloud-compatible PDF utilities")
except ImportError:
    # Fallback for local development with PyMuPDF
    try:
        import fitz  # PyMuPDF
        print("⚠️ Using PyMuPDF fallback (may not work on Streamlit Cloud)")
        
        def create_simple_annotated_pdf(original_pdf, annotations):
            """Fallback annotation using PyMuPDF"""
            if hasattr(original_pdf, 'read'):
                pdf_bytes = original_pdf.read()
            else:
                pdf_bytes = original_pdf
            
            doc = fitz.open("pdf", pdf_bytes)
            
            for annotation in annotations:
                page_num = annotation.get('page', 0)
                if page_num < len(doc):
                    page = doc[page_num]
                    
                    rect = annotation.get('rect', [50, 50, 150, 70])
                    highlight = page.add_highlight_annot(fitz.Rect(rect))
                    
                    color = annotation.get('color', [1, 1, 0])
                    highlight.set_colors(stroke=color)
                    
                    note = annotation.get('note', 'Feedback')
                    highlight.set_content(note)
                    highlight.update()
            
            annotated_bytes = doc.write()
            doc.close()
            return annotated_bytes
        
        def get_pdf_info():
            return {'annotation_support': True, 'primary_processor': 'fitz'}
            
    except ImportError:
        def create_simple_annotated_pdf(original_pdf, annotations):
            print("❌ PDF annotation not available. Returning original PDF.")
            return original_pdf
        
        def get_pdf_info():
            return {'annotation_support': False, 'primary_processor': None}

placed_sections = set()

# Traffic light colors - Updated to match stricter rating criteria
TAG_COLORS = {
    "[GOOD]": (0.6, 0.9, 0.6),    # green - ratings 17-20
    "[CAUTION]": (1.0, 1.0, 0.6), # yellow - ratings 9-12  
    "[BAD]": (1.0, 0.6, 0.6),     # red - ratings 1-8
    "": (0.9, 0.9, 0.9)           # grey/neutral - ratings 13-16
}

def flatten_feedback(feedback_list):
    """Flatten nested feedback into simple dicts with 'snippet'."""
    flattened = []
    for item in feedback_list:
        if isinstance(item, dict):
            if "snippet" in item:
                flattened.append(item)
            elif "result" in item and isinstance(item["result"], list):
                flattened.extend(item["result"])
            else:
                for v in item.values():
                    if isinstance(v, list):
                        flattened.extend(v)
        elif isinstance(item, list):
            flattened.extend(item)
    return flattened


def overlay_pdf(input_path, output_path, *feedback_sources):
    """
    Overlay feedback (sectional + granular) onto PDF using cloud-compatible approach.
    Falls back to text-based feedback if PDF annotation is not available.
    """
    try:
        # Check if we have annotation support
        pdf_info = get_pdf_info()
        
        if not pdf_info.get('annotation_support', False):
            print("⚠️ PDF annotation not available. Copying original file and providing text feedback.")
            # Copy original file
            import shutil
            shutil.copy2(input_path, output_path)
            
            # Generate text-based feedback summary
            feedback = []
            for source in feedback_sources:
                feedback.extend(flatten_feedback(source))
            
            _generate_text_feedback_summary(feedback, output_path)
            return

        # Use PyMuPDF-based annotation (legacy approach)
        return _overlay_pdf_legacy(input_path, output_path, *feedback_sources)
        
    except Exception as e:
        print(f"❌ PDF overlay failed: {str(e)}")
        # Fallback: copy original file
        import shutil
        shutil.copy2(input_path, output_path)


def _overlay_pdf_legacy(input_path, output_path, *feedback_sources):
    """Legacy PDF overlay using PyMuPDF (when available)"""
    import fitz
    
    doc = fitz.open(input_path)

    # Flatten everything into a single list of dicts with 'snippet'
    feedback = []
    for source in feedback_sources:
        feedback.extend(flatten_feedback(source))

    for fb in feedback:
        _place_annotation(doc, fb)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    print(f"📄 Annotated PDF saved to {output_path}")


def _generate_text_feedback_summary(feedback, output_path):
    """Generate a text-based feedback summary when PDF annotation is not available"""
    summary_path = output_path.with_suffix('.txt')
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("RESUME FEEDBACK SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        
        good_feedback = [fb for fb in feedback if fb.get('tag') == '[GOOD]']
        caution_feedback = [fb for fb in feedback if fb.get('tag') == '[CAUTION]']
        bad_feedback = [fb for fb in feedback if fb.get('tag') == '[BAD]']
        
        if good_feedback:
            f.write("✅ STRENGTHS:\n")
            f.write("-" * 20 + "\n")
            for fb in good_feedback:
                f.write(f"• {fb.get('feedback', '')}\n")
                if fb.get('snippet'):
                    f.write(f"  Related to: \"{fb.get('snippet')[:50]}...\"\n")
                f.write(f"  Rating: {fb.get('rating', '?')}/20\n\n")
        
        if caution_feedback:
            f.write("⚠️ AREAS FOR IMPROVEMENT:\n")
            f.write("-" * 30 + "\n")
            for fb in caution_feedback:
                f.write(f"• {fb.get('feedback', '')}\n")
                if fb.get('snippet'):
                    f.write(f"  Related to: \"{fb.get('snippet')[:50]}...\"\n")
                f.write(f"  Rating: {fb.get('rating', '?')}/20\n\n")
        
        if bad_feedback:
            f.write("❌ CRITICAL ISSUES:\n")
            f.write("-" * 25 + "\n")
            for fb in bad_feedback:
                f.write(f"• {fb.get('feedback', '')}\n")
                if fb.get('snippet'):
                    f.write(f"  Related to: \"{fb.get('snippet')[:50]}...\"\n")
                f.write(f"  Rating: {fb.get('rating', '?')}/20\n\n")
    
    print(f"📄 Text-based feedback saved to {summary_path}")

def _place_annotation(doc, fb, single_hit=True):
    """Helper to place a highlight+tooltip annotation."""
    try:
        snippet = fb.get("snippet", "")
        tag = fb.get("tag", "")
        feedback_text = fb.get("feedback", "")
        rating = fb.get("rating", "?")

        # Skip neutral/empty feedback
        if tag.strip().upper() in ["", "[NEUTRAL]"]:
            return
            
        color = TAG_COLORS.get(tag, (0.9, 0.9, 0.9))

        placed = False
        for page_num, page in enumerate(doc):
            rects = page.search_for(snippet)
            if rects:
                if single_hit:   # section-level feedback
                    rects = rects[:1]   # 🔑 only take the first hit

                for rect in rects:
                    highlight = page.add_highlight_annot(rect)
                    highlight.set_colors(stroke=color, fill=color)
                    highlight.update()
                    highlight.set_popup(rect)
                    highlight.set_info(
                        title="resume-radar",
                        content=f"{feedback_text}"
                    )
                    page.insert_text(
                        (rect.x0, rect.y1 + 10),
                        "⌖",
                        fontsize=12,
                        color=(0, 0, 0)
                    )
                    placed = True

                if placed:
                    print(f"✅ Annotated '{snippet}' on page {page_num+1}")
                    break

        if not placed:
            print(f"⚠️ Snippet not found in PDF: {snippet}")
            
    except Exception as e:
        print(f"❌ Annotation failed for snippet '{fb.get('snippet', '')}': {str(e)}")