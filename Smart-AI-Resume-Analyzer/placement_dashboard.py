"""
Placement Team Dashboard - Automated Resume Relevance Check System
Streamlit interface for Innomatics Research Labs placement team
"""

import streamlit as st
import pandas as pd
import json
import tempfile
from pathlib import Path
from datetime import datetime
import os
import sqlite3
from typing import Dict, List, Optional, Tuple

# Import our custom modules
from resume_radar.jd_parser import JobDescriptionParser
from resume_radar.matching_engine import ResumeJDMatcher
from resume_radar.resume_radar_service import ResumeRadarService

# Page configuration
st.set_page_config(
    page_title="Innomatics Placement Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 1rem;
    }
    
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    
    .high-score {
        color: #28a745;
        font-weight: bold;
    }
    
    .medium-score {
        color: #ffc107;
        font-weight: bold;
    }
    
    .low-score {
        color: #dc3545;
        font-weight: bold;
    }
    
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'jd_parsed' not in st.session_state:
    st.session_state.jd_parsed = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []
if 'current_job_id' not in st.session_state:
    st.session_state.current_job_id = None

def initialize_database():
    """Initialize SQLite database for storing results"""
    db_path = "placement_dashboard.db"
    conn = sqlite3.connect(db_path)
    
    # Create tables
    conn.execute('''
        CREATE TABLE IF NOT EXISTS job_descriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            must_have_skills TEXT,
            good_to_have_skills TEXT,
            qualifications TEXT,
            experience_years INTEGER,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            raw_jd TEXT
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS resume_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            candidate_name TEXT,
            resume_filename TEXT,
            relevance_score REAL,
            verdict TEXT,
            matched_skills TEXT,
            missing_skills TEXT,
            semantic_score REAL,
            analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            full_analysis TEXT,
            FOREIGN KEY (job_id) REFERENCES job_descriptions (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    return db_path

def save_jd_to_db(parsed_jd: Dict) -> int:
    """Save job description to database and return job ID"""
    conn = sqlite3.connect("placement_dashboard.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO job_descriptions 
        (role_title, company, location, must_have_skills, good_to_have_skills, 
         qualifications, experience_years, raw_jd)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        parsed_jd.get('role_title', ''),
        parsed_jd.get('company', ''),
        parsed_jd.get('location', ''),
        json.dumps(parsed_jd.get('must_have_skills', [])),
        json.dumps(parsed_jd.get('good_to_have_skills', [])),
        json.dumps(parsed_jd.get('qualifications', [])),
        parsed_jd.get('experience_years'),
        str(parsed_jd)
    ))
    
    job_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return job_id

def save_analysis_to_db(job_id: int, candidate_name: str, filename: str, analysis: Dict):
    """Save resume analysis to database"""
    conn = sqlite3.connect("placement_dashboard.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO resume_analysis 
        (job_id, candidate_name, resume_filename, relevance_score, verdict, 
         matched_skills, missing_skills, semantic_score, full_analysis)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        job_id,
        candidate_name,
        filename,
        analysis['relevance_score'],
        analysis['verdict'],
        json.dumps(analysis['matched_skills']),
        json.dumps(analysis['missing_skills']),
        analysis['semantic_score'],
        json.dumps(analysis)
    ))
    
    conn.commit()
    conn.close()

def get_score_color_class(score: float) -> str:
    """Get CSS class for score coloring"""
    if score >= 75:
        return "high-score"
    elif score >= 50:
        return "medium-score"
    else:
        return "low-score"

def extract_candidate_name_from_resume(resume_text: str) -> str:
    """Extract candidate name from resume text using simple heuristics"""
    lines = resume_text.strip().split('\n')
    
    # Look for name in first few lines
    for line in lines[:5]:
        line = line.strip()
        if len(line) > 0 and len(line.split()) <= 4:  # Names are usually 1-4 words
            # Skip common headers
            if not any(word.lower() in line.lower() for word in 
                      ['resume', 'cv', 'curriculum', 'profile', 'contact', 'email', 'phone']):
                if any(char.isalpha() for char in line):  # Contains letters
                    return line
    
    return "Unknown Candidate"

def main():
    # Initialize database
    initialize_database()
    
    # Header
    st.markdown('<h1 class="main-header">🎯 Innomatics Placement Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Automated Resume Relevance Check System</p>', unsafe_allow_html=True)
    
    # Sidebar for job management
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.header("📋 Job Management")
    
    # Job Description Upload
    st.sidebar.subheader("1. Upload Job Description")
    jd_upload_method = st.sidebar.radio(
        "Choose upload method:",
        ["Upload File (PDF/DOCX)", "Paste Text"]
    )
    
    if jd_upload_method == "Upload File (PDF/DOCX)":
        jd_file = st.sidebar.file_uploader(
            "Upload JD File",
            type=['pdf', 'docx', 'txt'],
            key="jd_file"
        )
        
        if jd_file and st.sidebar.button("Parse Job Description", key="parse_jd_file"):
            with st.spinner("Parsing job description..."):
                try:
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{jd_file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(jd_file.read())
                        tmp_path = tmp_file.name
                    
                    # Parse JD
                    jd_parser = JobDescriptionParser()
                    parsed_jd = jd_parser.parse_job_description(tmp_path)
                    
                    # Save to session and database
                    st.session_state.jd_parsed = parsed_jd
                    job_id = save_jd_to_db(parsed_jd)
                    st.session_state.current_job_id = job_id
                    
                    # Cleanup
                    os.unlink(tmp_path)
                    
                    st.sidebar.success("✅ Job description parsed successfully!")
                    
                except Exception as e:
                    st.sidebar.error(f"❌ Error parsing JD: {e}")
    
    else:  # Paste text method
        jd_text = st.sidebar.text_area(
            "Paste Job Description:",
            height=200,
            placeholder="Paste the complete job description here..."
        )
        
        if jd_text and st.sidebar.button("Parse Job Description", key="parse_jd_text"):
            with st.spinner("Parsing job description..."):
                try:
                    jd_parser = JobDescriptionParser()
                    parsed_jd = jd_parser.parse_job_description(text=jd_text)
                    
                    st.session_state.jd_parsed = parsed_jd
                    job_id = save_jd_to_db(parsed_jd)
                    st.session_state.current_job_id = job_id
                    
                    st.sidebar.success("✅ Job description parsed successfully!")
                    
                except Exception as e:
                    st.sidebar.error(f"❌ Error parsing JD: {e}")
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Resume Upload Section
    if st.session_state.jd_parsed:
        st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.sidebar.subheader("2. Upload Resumes")
        
        resume_files = st.sidebar.file_uploader(
            "Upload Resume Files",
            type=['pdf', 'docx'],
            accept_multiple_files=True,
            key="resume_files"
        )
        
        if resume_files and st.sidebar.button("Analyze Resumes", key="analyze_resumes"):
            analyze_resumes(resume_files)
        
        st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Main content area
    if st.session_state.jd_parsed:
        display_job_details()
        
        if st.session_state.analysis_results:
            display_analysis_results()
    else:
        st.info("👆 Please upload and parse a job description to get started.")

def analyze_resumes(resume_files):
    """Analyze uploaded resumes against the current JD"""
    if not st.session_state.jd_parsed or not st.session_state.current_job_id:
        st.error("Please parse a job description first!")
        return
    
    matcher = ResumeJDMatcher()
    resume_service = ResumeRadarService()
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, resume_file in enumerate(resume_files):
        try:
            status_text.text(f"Analyzing {resume_file.name}... ({i+1}/{len(resume_files)})")
            
            # Extract resume text
            resume_text = resume_service.extract_text_from_pdf(resume_file)
            
            # Perform matching analysis
            analysis = matcher.analyze_resume_jd_match(resume_text, st.session_state.jd_parsed)
            
            # Extract candidate name
            candidate_name = extract_candidate_name_from_resume(resume_text)
            
            # Add metadata
            analysis['candidate_name'] = candidate_name
            analysis['filename'] = resume_file.name
            analysis['analysis_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            results.append(analysis)
            
            # Save to database
            save_analysis_to_db(
                st.session_state.current_job_id,
                candidate_name,
                resume_file.name,
                analysis
            )
            
            progress_bar.progress((i + 1) / len(resume_files))
            
        except Exception as e:
            st.error(f"Error analyzing {resume_file.name}: {e}")
    
    st.session_state.analysis_results = results
    progress_bar.empty()
    status_text.empty()
    st.success(f"✅ Analyzed {len(results)} resumes successfully!")

def display_job_details():
    """Display parsed job description details"""
    st.header("📋 Current Job Requirements")
    
    jd = st.session_state.jd_parsed
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Role", jd.get('role_title', 'Unknown'))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Company", jd.get('company', 'Not specified'))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Experience", f"{jd.get('experience_years', 'Not specified')} years")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Skills breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Must-Have Skills")
        must_have = jd.get('must_have_skills', [])
        if must_have:
            for skill in must_have:
                st.write(f"• {skill}")
        else:
            st.write("None specified")
    
    with col2:
        st.subheader("⭐ Good-to-Have Skills")
        good_to_have = jd.get('good_to_have_skills', [])
        if good_to_have:
            for skill in good_to_have:
                st.write(f"• {skill}")
        else:
            st.write("None specified")
    
    st.divider()

def display_analysis_results():
    """Display resume analysis results in a comprehensive dashboard"""
    st.header("📊 Resume Analysis Results")
    
    results = st.session_state.analysis_results
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    high_count = len([r for r in results if r['verdict'] == 'High'])
    medium_count = len([r for r in results if r['verdict'] == 'Medium'])
    low_count = len([r for r in results if r['verdict'] == 'Low'])
    avg_score = sum(r['relevance_score'] for r in results) / len(results)
    
    with col1:
        st.metric("Total Resumes", len(results))
    
    with col2:
        st.metric("High Suitability", high_count, delta=f"{(high_count/len(results)*100):.1f}%")
    
    with col3:
        st.metric("Medium Suitability", medium_count, delta=f"{(medium_count/len(results)*100):.1f}%")
    
    with col4:
        st.metric("Average Score", f"{avg_score:.1f}/100")
    
    # Results table
    st.subheader("📋 Detailed Results")
    
    # Prepare data for table
    table_data = []
    for result in results:
        table_data.append({
            'Candidate': result.get('candidate_name', 'Unknown'),
            'File': result.get('filename', ''),
            'Score': result['relevance_score'],
            'Verdict': result['verdict'],
            'Matched Skills': len(result['matched_skills']),
            'Missing Skills': len(result['missing_skills']),
            'Semantic Score': result['semantic_score']
        })
    
    df = pd.DataFrame(table_data)
    
    # Sort by score descending
    df = df.sort_values('Score', ascending=False)
    
    # Display with custom styling
    def color_verdict(val):
        if val == 'High':
            return 'color: #28a745; font-weight: bold'
        elif val == 'Medium':
            return 'color: #ffc107; font-weight: bold'
        else:
            return 'color: #dc3545; font-weight: bold'
    
    def color_score(val):
        if val >= 75:
            return 'color: #28a745; font-weight: bold'
        elif val >= 50:
            return 'color: #ffc107; font-weight: bold'
        else:
            return 'color: #dc3545; font-weight: bold'
    
    styled_df = df.style.applymap(color_verdict, subset=['Verdict'])\
                       .applymap(color_score, subset=['Score'])
    
    st.dataframe(styled_df, use_container_width=True)
    
    # Detailed analysis for selected candidate
    st.subheader("🔍 Detailed Analysis")
    
    candidate_names = [r.get('candidate_name', 'Unknown') for r in results]
    selected_candidate = st.selectbox("Select candidate for detailed view:", candidate_names)
    
    if selected_candidate:
        selected_result = next((r for r in results if r.get('candidate_name') == selected_candidate), None)
        
        if selected_result:
            display_detailed_analysis(selected_result)
    
    # Download results
    if st.button("📥 Download Results as CSV"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

def display_detailed_analysis(result: Dict):
    """Display detailed analysis for a selected candidate"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Scores:**")
        st.write(f"Overall Relevance: **{result['relevance_score']}/100**")
        st.write(f"Semantic Match: **{result['semantic_score']}/100**")
        st.write(f"Verdict: **{result['verdict']}**")
        
        st.markdown("**✅ Matched Skills:**")
        if result['matched_skills']:
            for skill in result['matched_skills']:
                st.write(f"• {skill}")
        else:
            st.write("None")
        
        if result['fuzzy_matched_skills']:
            st.markdown("**⚡ Fuzzy Matched Skills:**")
            for skill in result['fuzzy_matched_skills']:
                st.write(f"• {skill}")
    
    with col2:
        st.markdown("**❌ Missing Skills:**")
        if result['missing_skills']:
            for skill in result['missing_skills']:
                st.write(f"• {skill}")
        else:
            st.write("None")
        
        st.markdown("**📈 Score Breakdown:**")
        breakdown = result['score_breakdown']
        st.write(f"Must-Have Skills: {breakdown['must_have_score']}/100")
        st.write(f"Good-to-Have Skills: {breakdown['good_to_have_score']}/100")
        st.write(f"Semantic Similarity: {breakdown['semantic_score']}/100")

if __name__ == "__main__":
    main()