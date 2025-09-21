#!/usr/bin/env python3
"""Test full annotation pipeline with a real PDF"""

import sys
import os
from pathlib import Path
import tempfile

# Add current directory to path
sys.path.append('.')

def test_full_annotation():
    from resume_radar.resume_radar_service import ResumeRadarService
    
    service = ResumeRadarService()
    
    # Use a sample PDF
    pdf_path = r"g:\Info4Tech\resume-radar\inputs\CV_RobinDoe.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    # Sample feedback
    sample_section_feedback = [
        {
            'tag': '[GOOD]',
            'section_title': 'Education',
            'feedback': 'Strong educational background with relevant degree'
        },
        {
            'tag': '[CAUTION]',
            'section_title': 'Experience',
            'feedback': 'Consider adding more quantifiable achievements and metrics'
        }
    ]

    sample_granular_feedback = [
        {
            'snippet': 'Software Engineer',
            'feedback': 'Good job title that clearly describes your role in tech'
        },
        {
            'snippet': 'University',
            'feedback': 'Educational background shows strong foundation'
        }
    ]

    print(f'📄 Testing with PDF: {pdf_path}')
    print(f'📋 Section feedback items: {len(sample_section_feedback)}')
    print(f'📝 Granular feedback items: {len(sample_granular_feedback)}')
    
    try:
        # Test the full annotation process
        with open(pdf_path, 'rb') as pdf_file:
            annotated_bytes, output_path = service.create_annotated_pdf(
                pdf_file,
                sample_section_feedback,
                sample_granular_feedback,
                tempfile.gettempdir()
            )
        
        print(f'✅ Successfully created annotated PDF!')
        print(f'📁 Output path: {output_path}')
        print(f'📊 Annotated PDF size: {len(annotated_bytes):,} bytes')
        
        # Check if file was created
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f'📁 Output file confirmed: {file_size:,} bytes')
        else:
            print('⚠️ Output file not found on disk')
            
    except Exception as e:
        print(f'❌ Annotation failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_annotation()