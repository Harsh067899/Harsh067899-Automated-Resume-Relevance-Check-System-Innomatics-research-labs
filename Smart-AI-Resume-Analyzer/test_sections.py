#!/usr/bin/env python3

"""
Test script to debug split_into_sections_dynamic function
"""

import sys
import os
sys.path.append('.')

from resume_radar.parse_cv import split_into_sections_dynamic

def main():
    print("🔍 Testing split_into_sections_dynamic function...")
    
    # Sample CV text from the debug output
    cv_text = """Afroz Khan HYDERABAD | afrozkhan7020@gmail.com |https://github.com/afrozkhan| https://www.linkedin.com/in/afrozkhan35b0822 CAREER OBJECTIVE To secure a challenging role that leverages analytical skills, statistical knowledge, and programming expertise to drive data-driven decisions, optimize strategies, and deliver actionable insights through reports and visualizations. EDUCATIONAL QUALIFICATIONS AURORA DEGREE AND PG COLLEGE -(2020-2022) Master of science (statistics) CGPA:6.39 ST.ANN'S DEGREE AND PG COLLEGE -(2017-2020) Bachelor of science (mathematics) CGPA:7.64 INTERMEDIATE COLLEGE -(2015-2017) Intermediate (MPC) Grade:8.0 HIGH SCHOOL -(2014-2015) SSC Grade:9.0"""
    
    print(f"📝 Input CV text length: {len(cv_text)}")
    print(f"📝 First 200 chars: {cv_text[:200]}...")
    
    try:
        sections = split_into_sections_dynamic(cv_text)
        print(f"📄 Sections detected: {len(sections)}")
        for i, (header, content) in enumerate(sections.items()):
            print(f"  Section {i+1}: '{header[:50]}...' ({len(content)} chars)")
    except Exception as e:
        print(f"❌ Error in split_into_sections_dynamic: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()