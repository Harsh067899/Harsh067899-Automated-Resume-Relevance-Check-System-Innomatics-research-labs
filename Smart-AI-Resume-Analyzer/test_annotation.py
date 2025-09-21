#!/usr/bin/env python3
"""Test script for the reverted annotation system"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append('.')

# Test the annotation preparation
def test_annotation_preparation():
    from resume_radar.resume_radar_service import ResumeRadarService
    
    service = ResumeRadarService()
    
    # Sample feedback
    sample_section_feedback = [
        {
            'tag': '[GOOD]',
            'section_title': 'Education',
            'feedback': 'Strong educational background'
        },
        {
            'tag': '[CAUTION]',
            'section_title': 'Experience',
            'feedback': 'Consider adding more quantifiable achievements'
        }
    ]

    sample_granular_feedback = [
        {
            'snippet': 'Software Engineer',
            'feedback': 'This is a good job title that clearly describes your role'
        },
        {
            'snippet': 'Python',
            'feedback': 'Great technical skill to highlight'
        }
    ]

    print('Testing annotation preparation...')
    annotations = service._prepare_annotations_for_original_overlay(
        sample_section_feedback, 
        sample_granular_feedback
    )
    
    print(f'Generated {len(annotations)} annotations:')
    for i, ann in enumerate(annotations, 1):
        print(f'  {i}. Snippet: "{ann["snippet"]}"')
        print(f'     Note: "{ann["note"]}"')
        print(f'     Tag: {ann["tag"]}')
        print()
    
    print('✅ Annotation preparation test completed')
    return annotations

if __name__ == "__main__":
    test_annotation_preparation()