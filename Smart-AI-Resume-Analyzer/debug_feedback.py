#!/usr/bin/env python3

"""
Debug script to test ResumeRadarService feedback generation
"""

import sys
import os
sys.path.append('.')

from resume_radar.resume_radar_service import ResumeRadarService
from pathlib import Path

def main():
    print("🔍 Debugging ResumeRadarService feedback generation...")
    
    # Initialize service
    service = ResumeRadarService()
    
    # Test with a PDF file
    pdf_path = Path("inputs/Resume - 10.pdf")
    if not pdf_path.exists():
        pdf_path = Path("../resume-radar/inputs/Resume - 10.pdf")
    
    if not pdf_path.exists():
        print("❌ No test PDF found")
        return
    
    print(f"📄 Testing with: {pdf_path}")
    
    try:
        # Analyze the resume
        with open(pdf_path, 'rb') as f:
            results = service.analyze_resume(f)
            
        if results.get('success'):
            print("✅ Analysis completed")
            print(f"📊 Results:")
            print(f"  - Section feedback: {len(results.get('section_feedback', []))}")
            print(f"  - Granular feedback: {len(results.get('granular_feedback', []))}")
            print(f"  - PDF saved to: {results.get('annotated_pdf_path', 'None')}")
        else:
            print(f"❌ Analysis failed: {results.get('error')}")
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()