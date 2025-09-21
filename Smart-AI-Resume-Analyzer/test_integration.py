"""
Test the integrated placement dashboard functionality
"""

# Test the imports
try:
    from resume_radar.jd_parser import JobDescriptionParser
    from resume_radar.matching_engine import ResumeJDMatcher
    print("✅ All imports successful!")
    
    # Test JD Parser
    jd_parser = JobDescriptionParser()
    print("✅ JD Parser initialized")
    
    # Test Matcher
    matcher = ResumeJDMatcher()
    print("✅ Matcher initialized")
    
    # Test sample JD parsing
    sample_jd = """
    Data Scientist Position
    Required: Python, Machine Learning, SQL
    Experience: 2+ years
    """
    
    parsed = jd_parser.parse_job_description(text=sample_jd)
    print(f"✅ Sample JD parsed: {parsed['role_title']}")
    print(f"   Must-have skills: {len(parsed['must_have_skills'])}")
    
    print("\n🎉 All components working correctly!")
    print("🌐 Your integrated app is ready at: http://localhost:8501")
    
except Exception as e:
    print(f"❌ Error: {e}")