"""
Resume Radar Service - Main functionality for AI-powered CV review and annotation
Adapted from resume-radar project for Smart AI Resume Analyzer
"""

import os
import io
import re
import json
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI
from datetime import datetime
import streamlit as st
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Silence MuPDF logs
os.environ["MUPDF_LOG_LEVEL"] = "0"

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
        """Extract text from PDF file using PyMuPDF (original method)"""
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
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
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
        Create annotated PDF using original overlay_pdf function - matches main.py workflow exactly
        Returns both PDF bytes and the output file path
        """
        try:
            # Create temporary input file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as input_tmp:
                if hasattr(pdf_file, 'read'):
                    pdf_bytes = pdf_file.read()
                    pdf_file.seek(0)  # Reset file pointer
                    input_tmp.write(pdf_bytes)
                    # Get original filename if available
                    original_name = getattr(pdf_file, 'name', 'resume')
                else:
                    with open(pdf_file, 'rb') as f:
                        input_tmp.write(f.read())
                    original_name = Path(pdf_file).stem
                
                input_path = Path(input_tmp.name)
            
            # Create output path in the desired directory
            if output_dir is None:
                output_dir = "G:/Info4Tech/resume-radar/outputs"
            
            output_dir_path = Path(output_dir)
            output_dir_path.mkdir(parents=True, exist_ok=True)
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{Path(original_name).stem}_reviewed_{timestamp}.pdf"
            output_path = output_dir_path / output_filename
            
            # CRITICAL: Filter feedback like main.py does - only keep items with tags
            section_feedback_list = [fb for fb in section_feedback if fb.get("tag")]
            
            # Use original overlay_pdf function with filtered data
            overlay_pdf(input_path, output_path, section_feedback_list, granular_feedback)
            
            # Read the annotated PDF bytes for Streamlit download
            with open(output_path, 'rb') as f:
                annotated_pdf_bytes = f.read()
            
            # Clean up temporary input file
            os.unlink(input_path)
            
            return annotated_pdf_bytes, str(output_path)
            
        except Exception as e:
            raise Exception(f"Error creating annotated PDF: {str(e)}")
    
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
            return {
                "error": f"Resume analysis failed: {str(e)}",
                "success": False
            }
