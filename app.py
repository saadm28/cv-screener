import os, io, json, zipfile
from pathlib import Path

import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from parsing.extractor import load_files_from_uploader
from utils.text import clean_text
from cv_analyzer import analyze_cv_with_openai, to_dict, score_candidate_with_ai

load_dotenv()

st.set_page_config(
    page_title="KSEYE CV Screener", 
    page_icon="assets/kseye_logo.svg", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# KSEYE Brand Colors
KSEYE_RED = "#e42c2c"
KSEYE_DARK = "#2c3e50"
KSEYE_LIGHT = "#f8f9fa"

# Custom CSS with KSEYE branding
st.markdown(f"""
<style>
                      tab1, tab2, tab3 = st.tabs(["Analysis", "Experience", "Skills & Education"]) /* Import Google Fonts */
    @import u                    tab1, tab2, tab3 = st.tabs(["Analysis", "Experience", "Skills & Education"])l('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {{
        font-family: 'Inter', sans-serif !important;
    }}
    
    /* Hide Streamlit elements */
    #MainMenu {{visibility: hidden;}}
    .stDeployButton {{display: none;}}
    header {{visibility: hidden;}}
    
    /* Main container */
    .main .block-container {{
        padding-top: 1rem;
        max-width: 1200px;
    }}
    
    /* Sidebar styling */
    .css-1d391kg {{
        background-color: white;
        border-right: 2px solid {KSEYE_LIGHT};
    }}
    
    /* KSEYE Header */
    .kseye-header {{
        background: white;
        color: {KSEYE_DARK};
        padding: 2.5rem 2rem;
        border-radius: 12px;
        margin: 1rem 0 2rem 0;
        text-align: center;
        border: 1px solid {KSEYE_LIGHT};
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    
    .kseye-logo {{
        max-width: 180px;
        margin-bottom: 1.5rem;
    }}
    
    .page-title {{
        color: {KSEYE_DARK};
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
    }}
    
    .page-subtitle {{
        color: #6c757d;
        font-size: 1.1rem;
        margin: 0;
        opacity: 0.8;
    }}
    
    /* Cards */
    .feature-card {{
        background: white;
        border: 1px solid {KSEYE_LIGHT};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        text-align: center;
        height: 100%;
        min-height: 280px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    
    .feature-card:hover {{
        box-shadow: 0 8px 25px rgba(228, 44, 44, 0.15);
        transform: translateY(-3px);
        border-color: {KSEYE_RED};
    }}
    
    .feature-icon {{
        font-size: 3rem;
        margin-bottom: 1rem;
        color: {KSEYE_RED};
    }}
    
    .candidate-card {{
        background: white;
        border: 1px solid {KSEYE_LIGHT};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }}
    
    .candidate-summary-card {{
        background: white;
        border: 1px solid {KSEYE_LIGHT};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        cursor: pointer;
    }}
    
    .candidate-summary-card:hover {{
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        transform: translateY(-2px);
        border-color: {KSEYE_RED};
    }}
    
    .candidate-card:hover {{
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }}
    
    /* Score badge */
    .score-badge {{
        background: linear-gradient(45deg, {KSEYE_RED} 0%, #c82333 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 16px;
        display: inline-block;
        margin-bottom: 12px;
        text-align: center;
        min-width: 60px;
    }}
    
    /* Skill chips */
    .skill-chip {{
        background: {KSEYE_LIGHT};
        border: 1px solid #dee2e6;
        color: {KSEYE_DARK};
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 13px;
        margin-right: 8px;
        margin-bottom: 4px;
        display: inline-block;
    }}
    
    .skill-chip.must-have {{
        background: #dcfce7;
        border-color: #86efac;
        color: #15803d;
    }}
    
    /* Buttons */
    .stButton > button {{
        background: linear-gradient(45deg, {KSEYE_RED} 0%, #c82333 100%);
        color: white;
        border: none;
        padding: 12px 32px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 16px;
        width: 100%;
        margin-top: 16px;
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        background: linear-gradient(45deg, #c82333 0%, #a01e28 100%);
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(228, 44, 44, 0.4);
    }}
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        border: 2px solid {KSEYE_LIGHT};
        border-radius: 8px;
        transition: border-color 0.3s ease;
    }}
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {KSEYE_RED} !important;
        box-shadow: 0 0 0 3px rgba(228, 44, 44, 0.1) !important;
    }}
    
    /* Results header */
    .results-header {{
        text-align: center;
        margin: 2rem 0;
        padding: 2rem;
        background: white;
        border-radius: 12px;
        border: 1px solid {KSEYE_LIGHT};
    }}
    
    /* Text styles */
    h1, h2, h3 {{
        color: {KSEYE_DARK} !important;
    }}
    
    .subtitle {{
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }}
    
    /* Navigation */
    .nav-item {{
        margin: 8px 0;
    }}
    
    .nav-item.active {{
        background: {KSEYE_RED};
        color: white;
        border-radius: 8px;
        padding: 8px 12px;
        font-weight: 600;
    }}
</style>
""", unsafe_allow_html=True)

# Navigation
LOGO_BASE64 = "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4gPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxODAuMTE2IiBoZWlnaHQ9IjUzLjA3NCIgdmlld0JveD0iMCAwIDE4MC4xMTYgNTMuMDc0Ij48ZGVmcz48c3R5bGU+IC5jbHMtMXtmaWxsOm5vbmV9LmNscy0ye2NsaXAtcGF0aDp1cmwoI2NsaXAtcGF0aCl9LmNscy0ze2ZpbGw6I2U3MjkyYn0uY2xzLTR7ZmlsbDojZmZmfS5jbHMtNXtmaWxsOiMxYzFjMWN9IDwvc3R5bGU+PGNsaXBQYXRoIGlkPSJjbGlwLXBhdGgiPjxwYXRoIGlkPSJSZWN0YW5nbGVfOSIgZD0iTTAgMGg1My4yMTZ2NTMuMDc0SDB6IiBjbGFzcz0iY2xzLTEiIGRhdGEtbmFtZT0iUmVjdGFuZ2xlIDkiPjwvcGF0aD48L2NsaXBQYXRoPjwvZGVmcz48ZyBpZD0iTG9nbyI+PGcgaWQ9Ikdyb3VwXzE2OSIgZGF0YS1uYW1lPSJHcm91cCAxNjkiPjxnIGlkPSJHcm91cF8xNjgiIGNsYXNzPSJjbHMtMiIgZGF0YS1uYW1lPSJHcm91cCAxNjgiPjxwYXRoIGlkPSJQYXRoXzEwNzIiIGQ9Ik0xMDAyLjY2MyA3MjEuMjRhMjYuNTI1IDI2LjUyNSAwIDEgMSAyNi41MjQgMjYuNTY3IDI2LjU0NSAyNi41NDUgMCAwIDEtMjYuNTI0LTI2LjU2NyIgY2xhc3M9ImNscy0zIiBkYXRhLW5hbWU9IlBhdGggMTA3MiIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTEwMDIuNjYzIC02OTQuNjczKSI+PC9wYXRoPjwvZz48L2c+PHBhdGggaWQ9IlBhdGhfMTA3MyIgZD0iTTExNzcuODY4IDg3MC4xNjF2OC41aDIuMTIxdi00LjIzM2gyMy4zNDF2NC4yMzNoMi4xMjN2LTguNXoiIGNsYXNzPSJjbHMtNCIgZGF0YS1uYW1lPSJQYXRoIDEwNzMiIHRyYW5zZm9ybT0idHJhbnNsYXRlKC0xMTY1LjEzNSAtODU3LjQwOCkiPjwvcGF0aD48cGF0aCBpZD0iUGF0aF8xMDc0IiBkPSJNMTIwMy4zNDQgMTEzMy4zNzZ2NC4yMzVIMTE4MHYtNC4yMzVoLTIuMTJ2OC41aDI3LjU4NnYtOC41eiIgY2xhc3M9ImNscy00IiBkYXRhLW5hbWU9IlBhdGggMTA3NCIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTExNjUuMTQ4IC0xMTAxLjQ5NSkiPjwvcGF0aD48cGF0aCBpZD0iUGF0aF8xMDc1IiBkPSJNMTI1OC41MTMgMTAwMS45Mzh2Mi44MmgtMTUuNTYydi0yLjgyaC0xLjQxNHY4LjVoMS40MTR2LTIuODM4aDE1LjU2MnYyLjgzNWgxLjQxNXYtOC41eiIgY2xhc3M9ImNscy00IiBkYXRhLW5hbWU9IlBhdGggMTA3NSIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTEyMjQuMTc4IC05NzkuNjA5KSI+PC9wYXRoPjxnIGlkPSJHcm91cF8xNzEiIGRhdGEtbmFtZT0iR3JvdXAgMTcxIiB0cmFuc2Zvcm09InRyYW5zbGF0ZSg4Ny44NDYgMTAuMDA4KSI+PGcgaWQ9Ikdyb3VwXzE3MyIgZGF0YS1uYW1lPSJHcm91cCAxNzMiPjxwYXRoIGlkPSJQYXRoXzEwNzciIGQ9Ik0yMjE2LjQ4NiA4NTUuNDUyYzAgMS4wNzkuNTEyIDUuNzc4IDUuNTg1IDUuNzc4YTUuMTc2IDUuMTc2IDAgMCAwIDUuNTM3LTUuMzg5YzAtMy41OC0zLjE2NS00LjM1NS01LjUzNy01LjIxNy00LjYwOC0xLjYzNi01LjcyNC0yLjE1NC03LjMwNy0zLjU3N2E4LjExIDguMTEgMCAwIDEtMi4zMjUtNS45OTJjMC0zLjcgMy4xMTctOC42NjMgOS42MzMtOC42NjMgNS43MjMgMCA5Ljg2MyAzLjQ5MSA5Ljg2MyA4Ljg3OGgtNS4wMjNjMC0zLjUzMS0yLjc5My00LjYxMS00Ljg0LTQuNjExYTQuNTUzIDQuNTUzIDAgMCAwLTQuNjA4IDQuMzU2YzAgMy4wNTcgMy4xMTggMy44NzggNC42MDggNC4zOTQgNC4zMjcgMS41MSAxMC41NjEgMi43NjEgMTAuNTYxIDEwLjQzMiAwIDUuNTU5LTQuMjMzIDkuNjU0LTEwLjU2MSA5LjY1NC00Ljc0NSAwLTEwLjYwOS0yLjkyOS0xMC42MDktMTAuMDQzeiIgY2xhc3M9ImNscy01IiBkYXRhLW5hbWU9IlBhdGggMTA3NyIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTIyMTEuNDYxIC04MzIuMzkyKSI+PC9wYXRoPjwvZz48L2c+PHBhdGggaWQ9IlBhdGhfMTA3NiIgZD0iTTE4OTYuMDU5IDg3Mi42MThsLTEzLjA3Ni0xNi4wNzdoLS4wOTJ2MTYuMDc3aC01LjAyNnYtMzEuODk0aDUuMDI2djE1LjgxOGguMDkybDEzLjA3Ni0xNS44MThoNi4xODhsLTEzLjQ0NyAxNS44MTcgMTMuNDQ3IDE2LjA3N3oiIGNsYXNzPSJjbHMtNSIgZGF0YS1uYW1lPSJQYXRoIDEwNzYiIHRyYW5zZm9ybT0idHJhbnNsYXRlKC0xODE0LjI2MyAtODMwLjExKSI+PC9wYXRoPjxwYXRoIGlkPSJQYXRoXzEwNzgiIGQ9Ik0yNTQ1LjAzNyA4NzIuNjE4di0zMS44OTRoMTguNTYzdjQuMjY3aC0xMy41NHY5LjM5NWgxMy41NHY0LjI2N2gtMTMuNTR2OS43aDEzLjU0djQuMjY3eiIgY2xhc3M9ImNscy01IiBkYXRhLW5hbWU9IlBhdGggMTA3OCIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTI0MzIuOTUgLTgzMC4xMSkiPjwvcGF0aD48cGF0aCBpZD0iUGF0aF8xMDc5IiBkPSJNMjgzOS4zODEgODcyLjYxOHYtMTEuNTA5bC0xMC43LTIwLjM4Nmg1LjYzbDcuNTgzIDE0Ljk1NyA3LjUzOS0xNC45NTdoNS41ODdsLTEwLjYxMSAyMC4zODZ2MTEuNTA5eiIgY2xhc3M9ImNscy01IiBkYXRhLW5hbWU9IlBhdGggMTA3OSIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTI2OTUuOTc4IC04MzAuMTEpIj48L3BhdGg+PHBhdGggaWQ9IlBhdGhfMTA4MCIgZD0iTTMyMjUuNjYyIDg0MC43MjR2MzEuODk0aDE4LjU2N3YtNC4yNjZoLTEzLjU0NHYtOS43aDEzLjU0NHYtNC4yNjZoLTEzLjU0NHYtOS40aDEzLjU0NHYtNC4yNjZ6IiBjbGFzcz0iY2xzLTUiIGRhdGEtbmFtZT0iUGF0aCAxMDgwIiB0cmFuc2Zvcm09InRyYW5zbGF0ZSgtMzA2NC4xMTMgLTgzMC4xMSkiPjwvcGF0aD48L2c+PC9zdmc+"

st.sidebar.markdown(f"""
<div style="text-align: center; margin-bottom: 2rem;">
    <img src="data:image/svg+xml;base64,{LOGO_BASE64}" style="max-width: 150px;">
    <h3 style="color: {KSEYE_RED}; margin-top: 1rem;">CV Screener</h3>
</div>
""", unsafe_allow_html=True)

# Page selection
if "page" not in st.session_state:
    st.session_state.page = "Home"

page = st.sidebar.selectbox(
    "Navigation",
    ["Home", "CV Analyzer"],
    index=["Home", "CV Analyzer"].index(st.session_state.page),
    format_func=lambda x: x,
    label_visibility="hidden",
    key="page_selector"
)

# Update session state if selectbox changed
if page != st.session_state.page:
    st.session_state.page = page

# Home Page
if page == "Home":
    st.markdown(f"""
    <div class="kseye-header">
        <img src="data:image/svg+xml;base64,{LOGO_BASE64}" class="kseye-logo">
        <h1 class="page-title">CV Screener</h1>
        <p class="page-subtitle">AI-powered candidate ranking and analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 style="color: #2c3e50;">Streamline Your Hiring Process</h2>
        <p class="subtitle">Leverage AI to efficiently screen thousands of CVs and identify the best candidates for your roles</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h3>AI-Powered Analysis</h3>
            <p>Advanced AI technology analyzes CVs with human-like understanding, extracting key skills, experience, and qualifications automatically for accurate candidate evaluation.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <h3>Bulk Processing</h3>
            <p>Process thousands of CVs in minutes. Upload individual files for efficient batch analysis and get comprehensive results quickly.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Smart Ranking</h3>
            <p>Candidates are automatically ranked based on relevance to your job requirements, with detailed analysis and confidence scoring for informed decisions.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # How it works section
    st.markdown("""
    <div style="margin: 4rem 0 2rem 0;">
        <h2 style="text-align: center; color: #2c3e50;">How It Works</h2>
        <p style="text-align: center;" class="subtitle">Get started in 3 simple steps</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <div style="background: #e42c2c; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto; font-size: 1.5rem; font-weight: bold;">1</div>
            <h4>Define Your Role</h4>
            <p>Enter the job title and complete job description with requirements and qualifications.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <div style="background: #e42c2c; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto; font-size: 1.5rem; font-weight: bold;">2</div>
            <h4>Upload CVs</h4>
            <p>Upload multiple CV files (PDF, DOCX) containing all candidate resumes for analysis.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <div style="background: #e42c2c; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto; font-size: 1.5rem; font-weight: bold;">3</div>
            <h4>Get Results</h4>
            <p>Receive ranked candidate lists with detailed analysis, skills matching, and assessment notes.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Call to action
    st.markdown("""
    <div style="text-align: center; margin: 4rem 0;">
        <p style="font-size: 1.1rem; margin-bottom: 2rem;">Ready to transform your hiring process?</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Start CV Analysis", type="primary"):
            st.session_state.page = "CV Analyzer"
            st.rerun()

# CV Analyzer Page
elif page == "CV Analyzer":
    st.markdown(f"""
    <div class="kseye-header">
        <h1 class="page-title">CV Analyzer</h1>
        <p class="page-subtitle">Upload your job requirements and candidate CVs</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Input Section
    with st.container():
        st.markdown("### Job Details")
        
        job_title = st.text_input("Job Title", placeholder="e.g., Senior Python Developer")
        
        job_description = st.text_area(
            "Job Description", 
            height=200, 
            placeholder="Paste the complete job description including requirements, responsibilities, and qualifications...",
            help="Include all relevant details about the role"
        )
        
        st.markdown("### Upload CVs")
        uploaded_files = st.file_uploader(
            "Upload candidate CVs", 
            accept_multiple_files=True, 
            type=["pdf", "docx", "doc", "zip"],
            help="You can upload individual CV files or a ZIP containing multiple CVs"
        )
        
        # Full-width button styling
        st.markdown("""
        <style>
        .stButton > button {
            width: 100% !important;
            height: 50px !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            margin-top: 10px !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        analyze_button = st.button("Analyze Candidates", type="primary")
    
    # Analysis Section
    if analyze_button:
        if not job_title.strip():
            st.error("Please enter a job title")
            st.stop()
        
        if not job_description.strip():
            st.error("Please enter a job description")
            st.stop()
        
        if not uploaded_files:
            st.error("Please upload at least one CV")
            st.stop()
        
        # Check OpenAI availability
        openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not openai_key:
            st.error("OpenAI API key not configured. Please add OPENAI_API_KEY to your .env file.")
            st.stop()

        # Create a unique key for this analysis session
        analysis_key = f"{job_title}_{len(uploaded_files)}_{hash(job_description[:100])}"
        
        # Check if we already have results for this exact job/files combination
        if f"analysis_results_{analysis_key}" not in st.session_state:
            with st.spinner("Analyzing candidates... This may take a few moments."):
                try:
                    # Load and parse CVs
                    docs = load_files_from_uploader(uploaded_files)
                    
                    if not docs:
                        st.error("❌ No valid CV files found in the uploaded files.")
                        st.stop()
                    
                    # Prepare job context for AI
                    job_context = {
                        "job_title": job_title.strip(),
                        "job_description": job_description.strip(),
                        "analysis_instructions": "Analyze each CV against this job and provide detailed insights"
                    }
                    
                    # Analyze each CV with AI
                    candidates = []
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, (filename, cv_text) in enumerate(docs):
                        status_text.text(f"Analyzing {filename}... ({i+1}/{len(docs)})")
                        
                        cleaned_text = clean_text(cv_text)
                        analysis = analyze_cv_with_openai(cleaned_text, filename, job_context)
                        
                        candidates.append(analysis)
                        progress_bar.progress((i + 1) / len(docs))
                    
                    status_text.empty()
                    progress_bar.empty()
                    
                    if not candidates:
                        st.error("❌ Could not analyze any CVs. Please check the file formats.")
                        st.stop()
                    
                    # Calculate scores using AI analysis and rank candidates
                    scored_candidates = []
                    
                    progress_bar = st.progress(0)
                    total_candidates_to_score = len(candidates)
                    
                    for i, candidate in enumerate(candidates):
                        # Update progress
                        progress_bar.progress((i + 1) / total_candidates_to_score)
                        
                        # Get AI-powered score and reasoning
                        score, reasoning = score_candidate_with_ai(candidate, job_title, job_description)
                        
                        # Store score with reasoning for display
                        candidate.ai_score = score
                        candidate.ai_reasoning = reasoning
                        
                        scored_candidates.append((score, candidate))
                    
                    progress_bar.empty()
                    
                    # Sort by score (highest first)
                    scored_candidates.sort(key=lambda x: x[0], reverse=True)
                    
                    # Store results in session state
                    st.session_state[f"analysis_results_{analysis_key}"] = {
                        "scored_candidates": scored_candidates,
                        "job_title": job_title,
                        "total_candidates": len(candidates)
                    }
                    
                except Exception as e:
                    st.error("An error occurred during analysis: " + str(e))
                    st.exception(e)
                    st.stop()
        
        # Get results from session state
        results = st.session_state[f"analysis_results_{analysis_key}"]
        scored_candidates = results["scored_candidates"]
        job_title_display = results["job_title"]
        total_candidates = results["total_candidates"]
        
        # Display Results
        st.markdown(f"""
        <div class="results-header">
            <h2 style="color: #2c3e50; margin-bottom: 8px;">Analysis Results</h2>
            <p style="color: #6c757d; margin: 0;">Analyzed {total_candidates} candidates for <strong>{job_title_display}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display all candidates (up to 50 max for performance)
        max_display = 50
        display_candidates = scored_candidates[:max_display]
        
        if len(scored_candidates) > max_display:
            st.info(f"Showing top {max_display} candidates out of {len(scored_candidates)} total candidates.")
        
        # Display all candidates
        for i, (score, candidate) in enumerate(display_candidates):
            rank = i + 1
            candidate_key = f"candidate_{rank}"
            
            # Initialize expanded state
            if f"{candidate_key}_expanded" not in st.session_state:
                st.session_state[f"{candidate_key}_expanded"] = False
            
            # Candidate card with integrated details
            with st.container():
                st.markdown(f"""
                <div style="border: 1px solid #e5e7eb; border-radius: 12px; padding: 20px; margin: 12px 0; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <span style="background: #f1f5f9; color: #334155; padding: 6px 12px; border-radius: 20px; font-size: 14px; font-weight: 600;">#{rank}</span>
                            <span style="font-size: 20px; font-weight: 600; color: #2c3e50;">{candidate.candidate_name}</span>
                        </div>
                        <div style="background: {KSEYE_RED}; color: white; padding: 10px 18px; border-radius: 25px; font-weight: bold; font-size: 16px;">{score:.0f}%</div>
                    </div>
                    <div style="color: #6c757d; font-size: 15px; font-weight: 500; margin-bottom: 16px;">
                        {candidate.current_title} • {candidate.total_years} years total • {candidate.relevant_years} years relevant
                    </div>
                """, unsafe_allow_html=True)
                
                # Integrated expandable details within the card
                with st.expander("View Details", expanded=False):
                    # Get skills for use in tabs
                    must_have_skills = candidate.must_have_skills if isinstance(candidate.must_have_skills, list) else []
                    nice_to_have_skills = candidate.nice_to_have_skills if isinstance(candidate.nice_to_have_skills, list) else []
                    
                    st.markdown("""
                    <style>
                        .stTabs [data-baseweb="tab-list"] {
                            gap: 8px;
                            margin-bottom: 10px;
                        }
                        .stTabs [data-baseweb="tab"] {
                            height: 45px;
                            min-height: 45px;
                            padding-left: 20px;
                            padding-right: 20px;
                            background-color: #f8fafc;
                            border: 1px solid #e2e8f0;
                            color: #64748b;
                            border-radius: 6px 6px 0 0;
                        }
                        .stTabs [aria-selected="true"] {
                            background-color: #e42c2c;
                            color: white;
                            border-color: #e42c2c;
                        }
                        .tab-content {
                            padding: 16px 0 0 0;
                            margin: 0;
                        }
                        .detail-section {
                            margin-bottom: 16px;
                        }
                        .detail-header {
                            color: #1e293b;
                            font-weight: 600;
                            font-size: 17px;
                            margin-bottom: 8px;
                            padding-bottom: 4px;
                            border-bottom: 2px solid #f1f5f9;
                        }
                        .all-skills {
                            display: flex;
                            flex-wrap: wrap;
                            gap: 8px;
                            margin-top: 8px;
                        }
                        .experience-card {
                            background: #f8fafc;
                            padding: 12px;
                            border-radius: 8px;
                            margin-bottom: 12px;
                            border-left: 4px solid #e42c2c;
                        }
                        .experience-title {
                            color: #1e293b;
                            font-weight: 600;
                            font-size: 16px;
                            margin: 0 0 8px 0;
                        }
                        .experience-company {
                            color: #64748b;
                            font-weight: 500;
                            margin: 0 0 12px 0;
                            font-size: 15px;
                        }
                        .experience-desc {
                            color: #374151;
                            line-height: 1.6;
                            margin: 0;
                        }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    tab1, tab2, tab3 = st.tabs(["🎯 Analysis", "� Experience", "🎓 Skills & Education"])
                    
                    with tab1:
                        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
                        
                        # Candidate summary
                        st.markdown('<div class="detail-section">', unsafe_allow_html=True)
                        st.markdown('<div class="detail-header">Candidate Summary</div>', unsafe_allow_html=True)
                        st.markdown(f'<div style="color: #374151; line-height: 1.7; font-size: 15px;">{candidate.summary}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Combined AI Assessment (scoring + notes)
                        ai_reasoning = getattr(candidate, 'ai_reasoning', '')
                        ai_score = getattr(candidate, 'ai_score', 0)
                        confidence_notes = candidate.confidence_notes if candidate.confidence_notes else ''
                        
                        if ai_reasoning or confidence_notes:
                            st.markdown('<div class="detail-section">', unsafe_allow_html=True)
                            st.markdown('<div class="detail-header">AI Assessment</div>', unsafe_allow_html=True)
                            
                            # Build combined assessment content
                            assessment_content = ""
                            
                            if ai_reasoning:
                                assessment_content += f"<strong>Score: {ai_score:.0f}%</strong><br><br>"
                                assessment_content += f"<strong>Evaluation:</strong><br>{ai_reasoning}"
                            
                            if confidence_notes:
                                if ai_reasoning:
                                    assessment_content += "<br><br>"
                                assessment_content += f"<strong>Additional Notes:</strong><br>{confidence_notes}"
                            
                            st.markdown(f"""
                            <div style="padding: 16px; background: linear-gradient(135deg, #f0f9ff 0%, #e0f7fa 100%); border-radius: 8px; color: #374151; border-left: 4px solid {KSEYE_RED}; line-height: 1.6;">
                                {assessment_content}
                            </div>
                            """, unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with tab2:
                        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
                        
                        # Experience highlights first
                        highlights = candidate.experience_highlights if isinstance(candidate.experience_highlights, list) else []
                        if highlights:
                            st.markdown('<div class="detail-section">', unsafe_allow_html=True)
                            st.markdown('<div class="detail-header">Key Experience Highlights</div>', unsafe_allow_html=True)
                            for highlight in highlights[:6]:
                                st.markdown(f'<div style="padding: 8px 0; color: #374151; border-bottom: 1px solid #f1f5f9;">• {highlight}</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Detailed experience if available
                        if hasattr(candidate, 'experience') and candidate.experience:
                            st.markdown('<div class="detail-section">', unsafe_allow_html=True)
                            st.markdown('<div class="detail-header">Work Experience Details</div>', unsafe_allow_html=True)
                            for exp in candidate.experience:
                                st.markdown(f"""
                                <div class="experience-card">
                                    <h4 class="experience-title">{exp.get('title', 'N/A')}</h4>
                                    <p class="experience-company">{exp.get('company', 'N/A')} • {exp.get('duration', 'N/A')}</p>
                                    <p class="experience-desc">{exp.get('description', 'N/A')}</p>
                                </div>
                                """, unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                        elif not highlights:
                            st.info("No detailed experience information extracted from CV")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with tab3:
                        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
                        
                        # Skills section with better organization
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown('<div class="detail-section">', unsafe_allow_html=True)
                            st.markdown('<div class="detail-header">Required Skills Found</div>', unsafe_allow_html=True)
                            if must_have_skills:
                                skills_html = ""
                                for skill in must_have_skills:
                                    skills_html += f'<span class="skill-chip must-have">{skill}</span>'
                                st.markdown(f'<div class="all-skills">{skills_html}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div style="color: #9ca3af; font-style: italic;">None identified</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown('<div class="detail-section">', unsafe_allow_html=True)
                            st.markdown('<div class="detail-header">Additional Skills</div>', unsafe_allow_html=True)
                            if nice_to_have_skills:
                                skills_html = ""
                                for skill in nice_to_have_skills:
                                    skills_html += f'<span class="skill-chip">{skill}</span>'
                                st.markdown(f'<div class="all-skills">{skills_html}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div style="color: #9ca3af; font-style: italic;">None identified</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Education section
                        if hasattr(candidate, 'education') and candidate.education:
                            st.markdown('<div class="detail-section">', unsafe_allow_html=True)
                            st.markdown('<div class="detail-header">Education Background</div>', unsafe_allow_html=True)
                            for edu in candidate.education:
                                st.markdown(f"""
                                <div style="background: #f8fafc; padding: 14px; border-radius: 8px; margin-bottom: 10px; border-left: 3px solid #e42c2c;">
                                    <div style="color: #1e293b; font-weight: 600; margin-bottom: 4px;">{edu.get('degree', 'N/A')}</div>
                                    <div style="color: #64748b; font-size: 14px;">{edu.get('institution', 'N/A')} • {edu.get('year', 'N/A')}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Close the main card div
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<div style='margin-bottom: 60px;'></div>", unsafe_allow_html=True)
