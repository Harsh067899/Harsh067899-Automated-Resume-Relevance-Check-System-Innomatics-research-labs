"""
Resume Radar Service - Main functionality for AI-powered CV review and annotation
Adapted from resume-radar project for Smart AI Resume Analyzer
"""

import os
import io
import re
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI
from datetime import datetime
import streamlit as st
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add utils directory to Python path for cloud compatibility
utils_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils')
if utils_path not in sys.path:
    sys.path.insert(0, utils_path)

# Import cloud-compatible PDF utilities
try:
    from pdf_utils import extract_text_from_pdf as extract_pdf_text_util, get_pdf_info
    print("✅ Using cloud-compatible PDF utilities for Resume Radar Service")
except ImportError:
    # Fallback for local development
    try:
        import fitz  # PyMuPDF
        print("⚠️ Using PyMuPDF fallback for Resume Radar Service")
        # Silence MuPDF logs
        os.environ["MUPDF_LOG_LEVEL"] = "0"
        
        def extract_pdf_text_util(pdf_file):
            """Fallback PDF extraction"""
            if isinstance(pdf_file, (str, Path)):
                with fitz.open(pdf_file) as doc:
                    return "\n".join([page.get_text() for page in doc])
            else:
                doc = fitz.open("pdf", pdf_file.read())
                text = "\n".join([page.get_text() for page in doc])
                doc.close()
                return text
        
        def get_pdf_info():
            return {'annotation_support': True, 'primary_processor': 'fitz'}
            
    except ImportError:
        def extract_pdf_text_util(pdf_file):
            raise RuntimeError("No PDF processing libraries available")
        
        def get_pdf_info():
            return {'annotation_support': False, 'primary_processor': None}

# Import the original resume-radar modules
from .extract_pdf import extract_text_from_pdf as extract_text_from_pdf_original
from .parse_cv import split_into_sections_dynamic
from .overlay_pdf import overlay_pdf, TAG_COLORS

class ResumeRadarService:
    """
    Main service class for Resume Radar functionality
    Uses original resume-radar logic with OpenRouter API integration
    """
    
    def __init__(self, api_key: str = None):
        """Initialize Resume Radar Service with OpenRouter configuration"""
        try:
            self.api_key = api_key or st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))
        except:
            self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        
        # Initialize OpenRouter client
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1"
            )
        else:
            self.client = None
        
        # Use original tag colors
        self.tag_colors = TAG_COLORS
        
        # LLM Prompts (adapted from original)
        self.global_reflection_prompt = """You are a professional CV reviewer.
Read the CV in full and provide a JSON object with these fields:
- rating: integer out of 20
- strengths: list of 3 concise bullet points
- weaknesses: list of 3 concise bullet points
- feedback: a short paragraph of overall impressions

CV:
{cv_text}
"""
        
        self.section_critique_prompt = """You are a strict CV reviewer. Rate this section of a CV out of 20.
Be critical but fair. Use the full scale from 1-20.

Rating Guidelines:
- 17-20: Exceptional quality, stands out significantly
- 13-16: Good quality, solid content
- 9-12: Average/adequate, meets basic requirements
- 5-8: Below average, needs improvement
- 1-4: Poor quality, significant issues

Tagging Rules:
- If score >= 17 → tag = [GOOD]
- If score <= 8 → tag = [BAD] 
- If 9 <= score <= 12 → tag = [CAUTION]
- Else tag = ""

Return ONLY JSON with keys: snippet, rating, tag, feedback.

Section Header: {header}
Section Content:
{content}
"""
        
        self.granular_critique_prompt = """You are a strict CV reviewer. Analyze the following CV section in detail.
Be critical and use the full rating scale. Not everything should be rated highly.

Rating Guidelines:
- 17-20: Exceptional quality, significantly stands out
- 13-16: Good quality, solid and effective
- 9-12: Average/adequate, meets basic requirements  
- 5-8: Below average, needs improvement
- 1-4: Poor quality, significant issues

For each key sentence or phrase in this section, provide:
- snippet: the exact phrase (as it appears in the text)
- rating: an integer from 1 to 20 (be critical, use full scale)
- tag: "[GOOD]" if rating >= 17, "[BAD]" if rating <= 8, "[CAUTION]" if 9-16, otherwise ""
- feedback: short constructive comment

You must return a valid JSON array. Example format:
[
    {{"snippet": "example phrase", "rating": 15, "tag": "[CAUTION]", "feedback": "comment here"}},
    {{"snippet": "another phrase", "rating": 18, "tag": "[GOOD]", "feedback": "why it's good"}}
]

Section Header: {header}
Section Content:
{content}

Return only the JSON array, no other text:"""
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF file using cloud-compatible approach"""
        try:
            # Use the cloud-compatible PDF utility
            return extract_pdf_text_util(pdf_file)
            
        except Exception as e:
            # Fallback to original method if available
            try:
                # Handle Streamlit uploaded file objects
                if hasattr(pdf_file, 'read'):
                    # Create temporary file for the original function
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        pdf_bytes = pdf_file.read()
                        pdf_file.seek(0)  # Reset file pointer for potential future use
                        tmp_file.write(pdf_bytes)
                        tmp_path = Path(tmp_file.name)
                    
                    # Use original extraction function
                    text = extract_text_from_pdf_original(tmp_path)
                    
                    # Clean up temporary file
                    os.unlink(tmp_path)
                    
                    return text
                else:
                    # Direct file path
                    return extract_text_from_pdf_original(Path(pdf_file))
            except Exception as fallback_error:
                raise Exception(f"Error extracting text from PDF (primary: {str(e)}, fallback: {str(fallback_error)})")
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text while preserving line breaks for section detection"""
        # Split into lines first
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Clean each line individually (collapse multiple spaces but keep line breaks)
            cleaned_line = re.sub(r"[ \t]+", " ", line).strip()
            if cleaned_line:  # Only keep non-empty lines
                cleaned_lines.append(cleaned_line)
        
        # Rejoin with line breaks
        return '\n'.join(cleaned_lines)
    
    def global_llm_reflection(self, cv_text: str) -> Dict[str, Any]:
        """
        First pass: Global reflection on the entire CV (adapted from original)
        Returns overall rating, strengths, weaknesses, and feedback
        """
        if not self.client:
            return {"error": "No AI client available - please configure OPENROUTER_API_KEY"}
        
        prompt = self.global_reflection_prompt.format(cv_text=cv_text)
        
        try:
            response = self.client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            content = response.choices[0].message.content
            
            # Clean potential markdown code blocks
            content = re.sub(r'^```json\s*|\s*```$', '', content.strip(), flags=re.MULTILINE)
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse JSON response: {str(e)}", "raw_output": content}
        except Exception as e:
            return {"error": f"Failed to get global reflection: {str(e)}"}
    
    def section_feedback(self, sections: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Second pass: Section-level critique (adapted from original)
        """
        if not self.client:
            return [{"error": "No AI client available"}]
        
        feedback = []
        
        for header, content in sections.items():
            try:
                prompt = self.section_critique_prompt.format(header=header, content=content)
                response = self.client.chat.completions.create(
                    model="openai/gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a precise CV analysis assistant. Return only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.4
                )
                fb = response.choices[0].message.content
                
                # Clean potential markdown code blocks
                fb = re.sub(r'^```json\s*|\s*```$', '', fb.strip(), flags=re.MULTILINE)
                
                fb_parsed = json.loads(fb)
                
                # Force snippet to be the section header
                fb_parsed["snippet"] = header.strip().split("\n")[0]
                fb_parsed["level"] = "section"
                
                feedback.append(fb_parsed)
                
            except Exception as e:
                feedback.append({
                    "snippet": header.strip().split("\n")[0],
                    "rating": "?",
                    "tag": "",
                    "feedback": f"Section analysis failed: {str(e)}",
                    "level": "section"
                })
        
        return feedback
    
    def granular_feedback(self, sections: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Third pass: Granular line-by-line critique (fixed version)
        """
        if not self.client:
            return [{"error": "No AI client available"}]
        
        all_feedback = []
        
        for header, content in sections.items():
            # Skip very short sections that don't have much to analyze
            if len(content.strip()) < 30:
                continue
                
            try:
                prompt = self.granular_critique_prompt.format(header=header, content=content)
                response = self.client.chat.completions.create(
                    model="openai/gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a precise CV analysis assistant. Always return valid JSON arrays only. Do not include any explanatory text."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=800
                )
                
                fb = response.choices[0].message.content.strip()
                
                # Debug: Print raw response for the first few sections
                if len(all_feedback) < 3:  # Only debug first 3 sections to avoid spam
                    print(f"\n=== DEBUG GRANULAR for '{header}' ===")
                    print(f"Raw response: '{fb}'")
                    print("=" * 50)
                
                # Clean markdown code blocks
                fb = re.sub(r'^```json\s*', '', fb, flags=re.MULTILINE | re.IGNORECASE)
                fb = re.sub(r'\s*```$', '', fb, flags=re.MULTILINE)
                fb = fb.strip()
                
                # Try to fix common JSON issues
                if not fb:
                    raise ValueError("Empty response from AI")
                
                # Ensure it's a proper JSON array
                if not fb.startswith('['):
                    # Sometimes AI returns a single object instead of array
                    if fb.startswith('{') and fb.endswith('}'):
                        fb = '[' + fb + ']'
                    else:
                        raise ValueError(f"Response doesn't start with [ or {{: '{fb[:50]}...'")
                
                if not fb.endswith(']'):
                    fb = fb + ']'
                
                try:
                    fb_parsed = json.loads(fb)
                except json.JSONDecodeError as json_err:
                    print(f"JSON Error for '{header}': {json_err}")
                    print(f"Problematic JSON: '{fb}'")
                    
                    # Try to fix common JSON issues
                    fb_fixed = fb.replace("'", '"')  # Replace single quotes
                    fb_fixed = re.sub(r',\s*}', '}', fb_fixed)  # Remove trailing commas
                    fb_fixed = re.sub(r',\s*]', ']', fb_fixed)  # Remove trailing commas in arrays
                    
                    try:
                        fb_parsed = json.loads(fb_fixed)
                        print(f"✅ Fixed JSON for '{header}'")
                    except:
                        raise json_err
                
                # Process the parsed response
                if isinstance(fb_parsed, dict):
                    fb_parsed["level"] = "granular"
                    # Validate required fields
                    if "snippet" not in fb_parsed:
                        fb_parsed["snippet"] = content[:50] + "..."
                    if "rating" not in fb_parsed:
                        fb_parsed["rating"] = 10
                    if "tag" not in fb_parsed:
                        fb_parsed["tag"] = "[CAUTION]"
                    if "feedback" not in fb_parsed:
                        fb_parsed["feedback"] = "Analysis incomplete"
                    all_feedback.append(fb_parsed)
                    
                elif isinstance(fb_parsed, list):
                    for item in fb_parsed:
                        if isinstance(item, dict):
                            item["level"] = "granular"
                            # Validate required fields
                            if "snippet" not in item:
                                item["snippet"] = content[:50] + "..."
                            if "rating" not in item:
                                item["rating"] = 10
                            if "tag" not in item:
                                item["tag"] = "[CAUTION]"
                            if "feedback" not in item:
                                item["feedback"] = "Analysis incomplete"
                    all_feedback.extend(fb_parsed)
                else:
                    print(f"⚠️ Unexpected response format for {header}: {type(fb_parsed)}")
                
            except Exception as e:
                print(f"❌ Error processing granular feedback for '{header}': {e}")
                all_feedback.append({
                    "snippet": header[:30] + "...",
                    "rating": 10,
                    "tag": "[CAUTION]",
                    "feedback": f"Analysis failed: {str(e)[:100]}",
                    "level": "granular"
                })
        
        print(f"✅ Granular feedback completed: {len(all_feedback)} items generated")
        return all_feedback
    
    def create_annotated_pdf(self, pdf_file, section_feedback: List[Dict[str, Any]], granular_feedback: List[Dict[str, Any]], output_dir: str = None) -> Tuple[bytes, str]:
        """
        Create annotated PDF with GUARANTEED fallback - ALWAYS returns a PDF
        Returns both PDF bytes and the output file path
        """
        # Get original PDF data first (for guaranteed fallback)
        if hasattr(pdf_file, 'read'):
            pdf_file.seek(0)
            original_pdf_bytes = pdf_file.read()
            pdf_file.seek(0)  # Reset for further processing
            original_name = getattr(pdf_file, 'name', 'resume')
        else:
            with open(pdf_file, 'rb') as f:
                original_pdf_bytes = f.read()
            original_name = Path(pdf_file).stem

        # Setup output path
        if output_dir is None:
            output_dir = tempfile.gettempdir()
        
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{Path(original_name).stem}_reviewed_{timestamp}.pdf"
        output_path = output_dir_path / output_filename

        # Try annotation methods in order of preference
        try:
            print("🔄 Attempting cloud-compatible PDF annotation...")
            return self._create_annotated_pdf_cloud_compatible(pdf_file, section_feedback, granular_feedback, output_dir)
            
        except Exception as e:
            print(f"⚠️ Cloud-compatible PDF annotation failed: {str(e)}")
            
            try:
                print("🔄 Attempting original PDF annotation method...")
                return self._create_annotated_pdf_original(pdf_file, section_feedback, granular_feedback, output_dir)
                
            except Exception as e2:
                print(f"⚠️ Original PDF annotation failed: {str(e2)}")
                
                try:
                    print("🔄 Using fallback: Original PDF with summary...")
                    return self._create_fallback_pdf_with_summary(pdf_file, section_feedback, granular_feedback, output_dir)
                
                except Exception as e3:
                    print(f"⚠️ Fallback with summary failed: {str(e3)}")
                    
                    # FINAL GUARANTEE: Return original PDF no matter what
                    print("📄 FINAL FALLBACK: Returning original PDF")
                    with open(output_path, 'wb') as f:
                        f.write(original_pdf_bytes)
                    
                    return original_pdf_bytes, str(output_path)

    def _create_annotated_pdf_cloud_compatible(self, pdf_file, section_feedback: List[Dict[str, Any]], granular_feedback: List[Dict[str, Any]], output_dir: str = None) -> Tuple[bytes, str]:
        """Try cloud-compatible PDF annotation using utils/pdf_utils.py"""
        try:
            from pdf_utils import create_simple_annotated_pdf
        except ImportError:
            # Try alternative import path
            import sys
            utils_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils')
            if utils_path not in sys.path:
                sys.path.insert(0, utils_path)
            from pdf_utils import create_simple_annotated_pdf
        
        # Get PDF bytes
        if hasattr(pdf_file, 'read'):
            pdf_bytes = pdf_file.read()
            pdf_file.seek(0)  # Reset file pointer
            original_name = getattr(pdf_file, 'name', 'resume')
        else:
            with open(pdf_file, 'rb') as f:
                pdf_bytes = f.read()
            original_name = Path(pdf_file).stem

        # Prepare annotations for the cloud-compatible utility
        annotations = []
        for feedback in section_feedback + granular_feedback:
            if feedback.get("tag"):
                annotations.append({
                    'page': 0,  # Default to first page
                    'rect': [50, 50, 400, 70],  # Default rectangle
                    'note': f"{feedback.get('tag', '')} - {feedback.get('feedback', '')}",
                    'color': [1, 1, 0]  # Yellow highlight
                })

        # Create annotated PDF
        annotated_pdf_bytes = create_simple_annotated_pdf(pdf_bytes, annotations)
        
        # Save to output directory
        if output_dir is None:
            output_dir = tempfile.gettempdir()
        
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{Path(original_name).stem}_reviewed_{timestamp}.pdf"
        output_path = output_dir_path / output_filename
        
        with open(output_path, 'wb') as f:
            f.write(annotated_pdf_bytes)
        
        return annotated_pdf_bytes, str(output_path)

    def _create_annotated_pdf_original(self, pdf_file, section_feedback: List[Dict[str, Any]], granular_feedback: List[Dict[str, Any]], output_dir: str = None) -> Tuple[bytes, str]:
        """Original PDF annotation method using overlay_pdf"""
        # Create temporary input file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as input_tmp:
            if hasattr(pdf_file, 'read'):
                pdf_bytes = pdf_file.read()
                pdf_file.seek(0)  # Reset file pointer
                input_tmp.write(pdf_bytes)
                original_name = getattr(pdf_file, 'name', 'resume')
            else:
                with open(pdf_file, 'rb') as f:
                    input_tmp.write(f.read())
                original_name = Path(pdf_file).stem
            
            input_path = Path(input_tmp.name)
        
        # Create output path
        if output_dir is None:
            output_dir = tempfile.gettempdir()
        
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{Path(original_name).stem}_reviewed_{timestamp}.pdf"
        output_path = output_dir_path / output_filename
        
        # Filter feedback with tags
        section_feedback_list = [fb for fb in section_feedback if fb.get("tag")]
        
        # Use original overlay_pdf function
        overlay_pdf(input_path, output_path, section_feedback_list, granular_feedback)
        
        # Read annotated PDF bytes
        with open(output_path, 'rb') as f:
            annotated_pdf_bytes = f.read()
        
        # Clean up
        os.unlink(input_path)
        
        return annotated_pdf_bytes, str(output_path)

    def _create_fallback_pdf_with_summary(self, pdf_file, section_feedback: List[Dict[str, Any]], granular_feedback: List[Dict[str, Any]], output_dir: str = None) -> Tuple[bytes, str]:
        """Fallback: Return original PDF and create a text summary file"""
        print("📄 Using fallback: Original PDF + Text Summary")
        
        # Get original PDF bytes
        if hasattr(pdf_file, 'read'):
            pdf_bytes = pdf_file.read()
            pdf_file.seek(0)
            original_name = getattr(pdf_file, 'name', 'resume')
        else:
            with open(pdf_file, 'rb') as f:
                pdf_bytes = f.read()
            original_name = Path(pdf_file).stem

        # Create output path
        if output_dir is None:
            output_dir = tempfile.gettempdir()
        
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{Path(original_name).stem}_reviewed_{timestamp}.pdf"
        output_path = output_dir_path / output_filename
        
        # Save original PDF
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        # Create summary text file alongside
        summary_path = output_path.with_suffix('.txt')
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"Resume Analysis Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("SECTION FEEDBACK:\n")
            f.write("-" * 20 + "\n")
            for feedback in section_feedback:
                if feedback.get("tag"):
                    f.write(f"• {feedback.get('tag', '')} - {feedback.get('feedback', '')}\n")
            
            f.write("\nGRANULAR FEEDBACK:\n")
            f.write("-" * 20 + "\n")
            for feedback in granular_feedback:
                if feedback.get("tag"):
                    f.write(f"• {feedback.get('tag', '')} - {feedback.get('feedback', '')}\n")
            
            f.write(f"\nNote: PDF annotation not available in cloud environment.")
            f.write(f"\nFeedback provided as text summary alongside original PDF.")
        
        return pdf_bytes, str(output_path)
    
    def analyze_resume(self, pdf_file) -> Dict[str, Any]:
        """
        Complete resume analysis following the exact main.py workflow
        """
        try:
            print("⌖ resume-radar: starting full pipeline")
            
            # Step 1: Extract text from PDF 
            cv_text = self.extract_text_from_pdf(pdf_file)
            cv_text = self.clean_text(cv_text)
            
            if not cv_text.strip():
                raise Exception("No text could be extracted from the PDF")
            
            # Step 2: Global reflection (first pass)
            global_reflection = self.global_llm_reflection(cv_text)
            
            # Step 3: Split into sections
            sections = split_into_sections_dynamic(cv_text)
            
            # Step 4: Per-section feedback (mark them as "section") 
            section_feedback_results = self.section_feedback(sections)
            for fb in section_feedback_results:
                fb["level"] = "section"
            
            # Step 5: Granular feedback (mark them as "granular")
            granular_feedback_results = self.granular_feedback(sections)
            for fb in granular_feedback_results:
                fb["level"] = "granular"
            
            # Step 6: Create annotated PDF - pass only feedback that has tags (like main.py)
            annotated_pdf_bytes, output_file_path = self.create_annotated_pdf(
                pdf_file, 
                section_feedback_results, 
                granular_feedback_results
            )
            
            print(f"\n📄 Pipeline complete: annotated CV written to {output_file_path}")
            
            # Prepare results (following original structure)
            all_feedback = section_feedback_results + granular_feedback_results
            
            results = {
                "global_reflection": global_reflection,
                "sections": sections,
                "section_feedback": section_feedback_results,
                "granular_feedback": granular_feedback_results,
                "all_feedback": all_feedback,
                "annotated_pdf": annotated_pdf_bytes,  # PDF bytes for Streamlit download
                "annotated_pdf_path": output_file_path,  # File path for reference
                "analysis_timestamp": datetime.now().isoformat(),
                "total_feedback_items": len(all_feedback),
                "success": True
            }
            
            return results
            
        except Exception as e:
            print(f"❌ Resume analysis failed: {str(e)}")
            
            # CRITICAL: Always provide a downloadable PDF, even on failure
            try:
                # Extract the original PDF bytes for fallback
                if hasattr(pdf_file, 'read'):
                    pdf_file.seek(0)  # Reset file pointer
                    original_pdf_bytes = pdf_file.read()
                    original_name = getattr(pdf_file, 'name', 'resume')
                else:
                    with open(pdf_file, 'rb') as f:
                        original_pdf_bytes = f.read()
                    original_name = Path(pdf_file).stem

                # Create a fallback output path
                output_dir = tempfile.gettempdir()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                fallback_filename = f"{Path(original_name).stem}_analysis_failed_{timestamp}.pdf"
                fallback_path = Path(output_dir) / fallback_filename
                
                # Save original PDF as fallback
                with open(fallback_path, 'wb') as f:
                    f.write(original_pdf_bytes)

                return {
                    "error": f"Resume analysis failed: {str(e)}",
                    "success": False,
                    "annotated_pdf": original_pdf_bytes,  # Return original PDF for download
                    "annotated_pdf_path": str(fallback_path),
                    "global_reflection": "Analysis failed, but your original resume is available for download.",
                    "sections": {},
                    "section_feedback": [],
                    "granular_feedback": [],
                    "all_feedback": [],
                    "analysis_timestamp": datetime.now().isoformat(),
                    "total_feedback_items": 0,
                    "fallback_mode": True
                }
            
            except Exception as fallback_error:
                print(f"❌ Even fallback PDF creation failed: {str(fallback_error)}")
                return {
                    "error": f"Resume analysis and PDF fallback failed: {str(e)}",
                    "success": False,
                    "annotated_pdf": None,
                    "annotated_pdf_path": None
                }
