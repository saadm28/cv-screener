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
    /* Import Google Fonts */                    tab1, tab2, tab3 = st.tabs(["Analysis", "Experience", "Skills & Education"])    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
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
        
        # Full-width button styling with higher specificity
        st.markdown("""
        <style>
        div[data-testid="stButton"] > button,
        .stButton > button,
        button[kind="primary"] {
            width: 100% !important;
            height: 50px !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            margin-top: 10px !important;
            display: block !important;
        }
        
        /* Fix expander display issues */
        .streamlit-expanderHeader {
            font-size: 14px !important;
            font-weight: 500 !important;
        }
        
        details[open] > summary {
            margin-bottom: 10px !important;
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
                        
                        # Get AI-powered score, reasoning, and brief summary
                        score, reasoning, brief_summary = score_candidate_with_ai(candidate, job_title, job_description)
                        
                        # Store score with reasoning and summary for display
                        candidate.ai_score = score
                        candidate.ai_reasoning = reasoning
                        candidate.brief_summary = brief_summary
                        
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
        
        # Create candidate summary table
        candidate_data = []
        for i, (score, candidate) in enumerate(display_candidates):
            rank = i + 1
            # Get brief summary - either from AI or create a fallback
            brief_summary = getattr(candidate, 'brief_summary', f"{candidate.current_title} with {candidate.relevant_years}y relevant experience")
            
            candidate_data.append({
                "rank": rank,
                "name": candidate.candidate_name,
                "summary": brief_summary,
                "score": score,
                "candidate_obj": candidate
            })
        
        st.markdown("### 📊 Candidate Rankings")
        
        # Custom modern table with click functionality
        st.markdown("""
        <style>
            .modern-table {
                background: white;
                border-radius: 16px;
                border: 1px solid #e5e7eb;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                margin: 20px 0;
            }
            .table-header {
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                border-bottom: 2px solid #e5e7eb;
                padding: 0;
            }
            .table-header-cell {
                padding: 20px 24px;
                font-weight: 700;
                font-size: 14px;
                color: #374151;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                border-right: 1px solid #e5e7eb;
            }
            .table-header-cell:last-child {
                border-right: none;
            }
            .table-row {
                border-bottom: 1px solid #f3f4f6;
                transition: all 0.2s ease;
                cursor: pointer;
                padding: 0;
            }
            .table-row:hover {
                background: #f8fafc;
                transform: scale(1.001);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .table-row:last-child {
                border-bottom: none;
            }
            .table-cell {
                padding: 20px 24px;
                vertical-align: middle;
                border-right: 1px solid #f3f4f6;
                font-size: 15px;
            }
            .table-cell:last-child {
                border-right: none;
            }
            .rank-cell {
                width: 80px;
                text-align: center;
                font-weight: 700;
                color: #6b7280;
            }
            .name-cell {
                width: 200px;
                font-weight: 600;
                color: #1f2937;
            }
            .summary-cell {
                color: #4b5563;
                line-height: 1.6;
                max-width: 400px;
            }
            .score-cell {
                width: 120px;
                text-align: center;
            }
            .score-badge {
                display: inline-block;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: 700;
                font-size: 14px;
                color: white;
                background: linear-gradient(135deg, #e42c2c 0%, #c82333 100%);
                box-shadow: 0 2px 4px rgba(228, 44, 44, 0.2);
            }
            
            /* Modal styles */
            .modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(4px);
                z-index: 9999;
                display: flex;
                align-items: center;
                justify-content: center;
                animation: fadeIn 0.2s ease;
            }
            .modal-content {
                background: white;
                border-radius: 20px;
                width: 90%;
                max-width: 800px;
                max-height: 90vh;
                overflow-y: auto;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                animation: slideIn 0.3s ease;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes slideIn {
                from { transform: translateY(-50px) scale(0.9); opacity: 0; }
                to { transform: translateY(0) scale(1); opacity: 1; }
            }
            .modal-header {
                background: linear-gradient(135deg, #e42c2c 0%, #c82333 100%);
                color: white;
                padding: 32px;
                border-radius: 20px 20px 0 0;
                position: relative;
            }
            .close-btn {
                position: absolute;
                top: 24px;
                right: 24px;
                background: rgba(255, 255, 255, 0.2);
                border: none;
                color: white;
                font-size: 24px;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.2s ease;
            }
            .close-btn:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: scale(1.1);
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Create markdown table - much cleaner and more reliable
        markdown_table = """
| Rank | Candidate | Score | Summary |
|------|-----------|-------|---------|
"""
        
        for candidate_info in candidate_data:
            # Clean the summary text for markdown (escape pipes and limit length)
            clean_summary = candidate_info['summary'].replace('|', '\\|')
            if len(clean_summary) > 150:
                clean_summary = clean_summary[:150] + "..."
            markdown_table += f"| **{candidate_info['rank']}** | **{candidate_info['name']}** | **{candidate_info['score']:.0f}%** | {clean_summary} |\n"
        
        st.subheader("Candidate Rankings")
        st.markdown(markdown_table)
        
        # Simple candidate selection using selectbox
        candidate_names = [c['name'] for c in candidate_data]
        selected_name = st.selectbox("Select a candidate for detailed analysis:", [""] + candidate_names, key="candidate_select")
        
        # Show candidate details when selected
        if selected_name:
            # Find the selected candidate
            selected_candidate = next((c for c in candidate_data if c['name'] == selected_name), None)
            if selected_candidate:
                candidate = selected_candidate["candidate_obj"]
                score = selected_candidate["score_value"]
            
            # Clean candidate details card
            st.markdown(f"""
            <div style="
                background: white; 
                border: 1px solid #e5e7eb; 
                border-radius: 8px; 
                padding: 0; 
                margin: 24px 0; 
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            ">
                <div style="
                    background: {KSEYE_RED}; 
                    color: white; 
                    padding: 24px; 
                    display: flex; 
                    justify-content: space-between; 
                    align-items: center;
                ">
                    <div>
                        <h2 style="margin: 0 0 8px 0; font-size: 24px; font-weight: 600;">{candidate.candidate_name}</h2>
                        <p style="margin: 0; font-size: 16px; opacity: 0.9;">{getattr(candidate, 'current_title', 'Professional')}</p>
                    </div>
                    <div style="
                        background: rgba(255,255,255,0.2); 
                        padding: 12px 24px; 
                        border-radius: 6px; 
                        text-align: center;
                    ">
                        <div style="font-size: 28px; font-weight: 700; margin-bottom: 4px;">{score:.0f}%</div>
                        <div style="font-size: 11px; opacity: 0.8;">MATCH</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # CSS for clean tabs
            st.markdown("""
            <style>
                .stTabs [data-baseweb="tab-list"] {
                    background: #f8f9fa;
                    border-radius: 8px;
                    padding: 4px;
                }
                .stTabs [data-baseweb="tab"] {
                    background: transparent;
                    border-radius: 6px;
                    color: #6b7280;
                    font-weight: 500;
                }
                .stTabs [data-baseweb="tab"]:hover {
                    background: rgba(255,255,255,0.5);
                }
                .stTabs [aria-selected="true"] {
                    background: white;
                    color: #374151;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                }
                .stTabs [data-baseweb="tab-panel"] {
                    padding: 24px 0;
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Details tabs
            tab1, tab2, tab3 = st.tabs(["Analysis", "Experience", "Skills"])
            
            with tab1:
                if hasattr(candidate, 'ai_reasoning') and candidate.ai_reasoning:
                    st.markdown("#### � AI Assessment")
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #fef7ff 0%, #fdf4ff 100%); 
                        padding: 24px; 
                        border-radius: 16px; 
                        border-left: 6px solid {KSEYE_RED};
                        margin-bottom: 24px;
                        box-shadow: 0 4px 16px rgba(228, 44, 44, 0.1);
                    ">
                        <p style="margin: 0; color: #374151; line-height: 1.8; font-size: 16px;">
                            {candidate.ai_reasoning}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                if hasattr(candidate, 'summary') and candidate.summary:
                    st.markdown("#### � Professional Summary")
                    st.markdown(f"""
                    <div style="
                        background: #ffffff; 
                        padding: 24px; 
                        border-radius: 16px; 
                        border: 1px solid #e5e7eb;
                        margin-bottom: 24px;
                        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
                    ">
                        <p style="margin: 0; color: #374151; line-height: 1.8; font-size: 16px;">
                            {candidate.summary}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                if hasattr(candidate, 'strengths') and candidate.strengths:
                    st.markdown("#### ⭐ Key Strengths")
                    strengths_html = '<div style="display: flex; flex-wrap: wrap; gap: 12px; margin-top: 16px;">'
                    for strength in candidate.strengths:
                        strengths_html += f"""
                        <div style="
                            background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); 
                            border: 2px solid #86efac; 
                            color: #15803d; 
                            padding: 12px 20px; 
                            border-radius: 24px; 
                            font-size: 14px;
                            font-weight: 600;
                            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                            display: inline-flex;
                            align-items: center;
                            gap: 8px;
                            transition: transform 0.2s ease;
                        " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                            <span style="font-size: 14px;">✓</span> {strength}
                        </div>
                        """
                    strengths_html += '</div>'
                    st.markdown(strengths_html, unsafe_allow_html=True)
            
            with tab2:
                if hasattr(candidate, 'experience_highlights') and candidate.experience_highlights:
                    st.markdown("#### 💼 Experience Highlights")
                    for i, highlight in enumerate(candidate.experience_highlights):
                        st.markdown(f"""
                        <div style="
                            background: #ffffff; 
                            padding: 24px; 
                            border-radius: 16px; 
                            margin-bottom: 16px; 
                            border-left: 5px solid {KSEYE_RED};
                            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
                            border: 1px solid #f1f5f9;
                            transition: transform 0.2s ease;
                        " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                            <div style="display: flex; align-items: flex-start; gap: 16px;">
                                <div style="
                                    background: {KSEYE_RED}; 
                                    color: white; 
                                    width: 32px; 
                                    height: 32px; 
                                    border-radius: 50%; 
                                    display: flex; 
                                    align-items: center; 
                                    justify-content: center; 
                                    font-size: 14px; 
                                    font-weight: bold;
                                    flex-shrink: 0;
                                    margin-top: 2px;
                                    box-shadow: 0 2px 8px rgba(228, 44, 44, 0.3);
                                ">
                                    {i+1}
                                </div>
                                <p style="margin: 0; color: #374151; line-height: 1.7; font-size: 16px;">
                                    {highlight}
                                </p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="
                        text-align: center; 
                        padding: 60px 20px; 
                        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                        border-radius: 16px;
                        border: 2px dashed #d1d5db;
                    ">
                        <div style="font-size: 48px; margin-bottom: 16px;">�</div>
                        <h4 style="color: #6b7280; margin: 0; font-weight: 500;">
                            No detailed experience highlights available
                        </h4>
                    </div>
                    """, unsafe_allow_html=True)
            
            with tab3:
                col1, col2 = st.columns(2)
                
                with col1:
                    if hasattr(candidate, 'must_have_skills') and candidate.must_have_skills:
                        st.markdown("#### ✅ Must-Have Skills")
                        skills_html = '<div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px;">'
                        for skill in candidate.must_have_skills:
                            skills_html += f"""
                            <span style="
                                background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); 
                                border: 2px solid #86efac; 
                                color: #15803d; 
                                padding: 10px 16px; 
                                border-radius: 20px; 
                                font-size: 13px; 
                                font-weight: 600;
                                box-shadow: 0 3px 6px rgba(0,0,0,0.1);
                                display: inline-block;
                                margin-bottom: 8px;
                                transition: transform 0.2s ease;
                            " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                                {skill}
                            </span>
                            """
                        skills_html += '</div>'
                        st.markdown(skills_html, unsafe_allow_html=True)
                
                with col2:
                    if hasattr(candidate, 'nice_to_have_skills') and candidate.nice_to_have_skills:
                        st.markdown("#### 💡 Nice-to-Have Skills")
                        skills_html = '<div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px;">'
                        for skill in candidate.nice_to_have_skills:
                            skills_html += f"""
                            <span style="
                                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); 
                                border: 2px solid #d1d5db; 
                                color: #374151; 
                                padding: 10px 16px; 
                                border-radius: 20px; 
                                font-size: 13px; 
                                font-weight: 500;
                                box-shadow: 0 3px 6px rgba(0,0,0,0.08);
                                display: inline-block;
                                margin-bottom: 8px;
                                transition: all 0.2s ease;
                            " onmouseover="this.style.transform='scale(1.05)'; this.style.borderColor='#9ca3af'" onmouseout="this.style.transform='scale(1)'; this.style.borderColor='#d1d5db'">
                                {skill}
                            </span>
                            """
                        skills_html += '</div>'
                        st.markdown(skills_html, unsafe_allow_html=True)
                
                # Education section
                if hasattr(candidate, 'education') and candidate.education:
                    st.markdown("#### 🎓 Education Background")
                    for edu in candidate.education:
                        st.markdown(f"""
                        <div style="
                            background: #ffffff; 
                            padding: 24px; 
                            border-radius: 16px; 
                            margin-bottom: 16px; 
                            border-left: 4px solid {KSEYE_RED};
                            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
                            border: 1px solid #f1f5f9;
                            transition: transform 0.2s ease;
                        " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                            <div style="color: #1e293b; font-weight: 700; margin-bottom: 12px; font-size: 18px;">
                                {edu.get('degree', 'N/A')}
                            </div>
                            <div style="color: #64748b; font-size: 15px; display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
                                <span style="display: flex; align-items: center; gap: 6px;">
                                    <span>🏛️</span> {edu.get('institution', 'N/A')}
                                </span>
                                <span style="display: flex; align-items: center; gap: 6px;">
                                    <span>📅</span> {edu.get('year', 'N/A')}
                                </span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        
        else:
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); 
                border: 3px dashed #0ea5e9; 
                border-radius: 20px; 
                padding: 50px 30px; 
                text-align: center; 
                margin: 40px 0;
                box-shadow: 0 8px 32px rgba(14, 165, 233, 0.1);
            ">
                <div style="font-size: 64px; margin-bottom: 20px;">👆</div>
                <h2 style="color: #0c4a6e; margin: 0 0 16px 0; font-weight: 700; font-size: 24px;">
                    Select a Candidate to View Details
                </h2>
                <p style="color: #075985; margin: 0; font-size: 18px; font-weight: 500;">
                    Click on any row in the table above to view comprehensive analysis,<br>
                    skills assessment, and detailed experience breakdown.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin-bottom: 60px;'></div>", unsafe_allow_html=True)
