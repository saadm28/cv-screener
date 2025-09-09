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
    <div class=\"kseye-header\">\n        <h1 class=\"page-title\">CV Analyzer</h1>\n        <p class=\"page-subtitle\">Upload your job requirements and candidate CVs</p>\n    </div>
    """, unsafe_allow_html=True)

    # Helper to render analysis results (table + details below)
    def render_analysis_results(results_key: str):
        results = st.session_state.get(f"analysis_results_{results_key}")
        if not results:
            return

        scored_candidates = results["scored_candidates"]
        job_title_display = results["job_title"]
        total_candidates = results["total_candidates"]

        st.markdown(f"""
        <div class=\"results-header\">\n            <h2 style=\"color: #2c3e50; margin-bottom: 8px;\">Analysis Results</h2>\n            <p style=\"color: #6c757d; margin: 0;\">Analyzed {total_candidates} candidates for <strong>{job_title_display}</strong></p>\n        </div>
        """, unsafe_allow_html=True)

        # Prepare table rows (cap at 50)
        max_display = 50
        display_candidates = scored_candidates[:max_display]
        if len(scored_candidates) > max_display:
            st.info(f"Showing top {max_display} candidates out of {len(scored_candidates)} total candidates.")

        candidate_data = []
        for i, (score, candidate) in enumerate(display_candidates):
            candidate_data.append({
                "rank": i + 1,
                "name": candidate.candidate_name,
                "summary": getattr(candidate, 'brief_summary', f"{getattr(candidate, 'current_title', 'Professional')} with {getattr(candidate, 'relevant_years', 'N/A')}y relevant experience"),
                "score": score,
                "candidate_obj": candidate,
            })

        st.subheader("Candidate Rankings")
        st.caption("Click View details to see full analysis below")

        # Table header
        h1, h2, h3, h4, h5 = st.columns([0.8, 3, 1, 6, 1.4])
        with h1: st.markdown("**Rank**")
        with h2: st.markdown("**Name**")
        with h3: st.markdown("**Score**")
        with h4: st.markdown("**Summary**")
        with h5: st.markdown("**Action**")

        # Table rows with a View button per row
        for idx, row in enumerate(candidate_data):
            summary = row["summary"]
            summary = (summary[:120] + "...") if isinstance(summary, str) and len(summary) > 120 else summary
            c1, c2, c3, c4, c5 = st.columns([0.8, 3, 1, 6, 1.4])
            c1.write(row["rank"]) 
            c2.write(row["name"]) 
            c3.write(f"{row['score']:.0f}%") 
            c4.write(summary)
            if c5.button("View details", key=f"view_{idx}"):
                st.session_state["selected_candidate_idx"] = idx
                st.rerun()

        selected_idx = st.session_state.get("selected_candidate_idx")

        # Details panel
        if selected_idx is not None and 0 <= selected_idx < len(candidate_data):
            chosen = candidate_data[selected_idx]
            candidate = chosen["candidate_obj"]
            score = chosen["score"]

            # Simple header and tabs (no extra CSS)
            st.markdown(f"### {candidate.candidate_name}")
            st.caption(getattr(candidate, 'current_title', 'Professional'))
            st.write(f"Match score: {score:.0f}%")

            tab1, tab2, tab3 = st.tabs(["Analysis", "Experience", "Skills"])

            with tab1:
                if hasattr(candidate, 'ai_reasoning') and candidate.ai_reasoning:
                    st.markdown("#### AI Assessment")
                    st.write(candidate.ai_reasoning)
                if hasattr(candidate, 'summary') and candidate.summary:
                    st.markdown("#### Professional Summary")
                    st.write(candidate.summary)
                if hasattr(candidate, 'strengths') and candidate.strengths:
                    st.markdown("#### Key Strengths")
                    for s in candidate.strengths:
                        st.markdown(f"- {s}")

            with tab2:
                if hasattr(candidate, 'experience_highlights') and candidate.experience_highlights:
                    st.markdown("#### Experience Highlights")
                    for i, h in enumerate(candidate.experience_highlights):
                        st.markdown(f"- {h}")
                else:
                    st.info("No detailed experience highlights available.")

            with tab3:
                col1, col2 = st.columns(2)
                with col1:
                    if hasattr(candidate, 'must_have_skills') and candidate.must_have_skills:
                        st.markdown("#### Must-Have Skills")
                        for sk in candidate.must_have_skills:
                            st.markdown(f"- {sk}")
                with col2:
                    if hasattr(candidate, 'nice_to_have_skills') and candidate.nice_to_have_skills:
                        st.markdown("#### Nice-to-Have Skills")
                        for sk in candidate.nice_to_have_skills:
                            st.markdown(f"- {sk}")
                if hasattr(candidate, 'education') and candidate.education:
                    st.markdown("#### Education Background")
                    for edu in candidate.education:
                        degree = edu.get('degree', 'N/A')
                        institution = edu.get('institution', 'N/A')
                        year = edu.get('year', 'N/A')
                        st.markdown(f"- {degree} — {institution} ({year})")

        else:
            st.info("Use the selector above to choose a candidate and view details.")

        st.markdown("<div style='margin-bottom: 60px;'></div>", unsafe_allow_html=True)

    # Input Section
    with st.container():
        st.markdown("### Job Details")

        job_title = st.text_input("Job Title", placeholder="e.g., Senior Python Developer")
        job_description = st.text_area(
            "Job Description",
            height=200,
            placeholder="Paste the complete job description including requirements, responsibilities, and qualifications...",
            help="Include all relevant details about the role",
        )

        st.markdown("### Upload CVs")
        uploaded_files = st.file_uploader(
            "Upload candidate CVs",
            accept_multiple_files=True,
            type=["pdf", "docx", "doc", "zip"],
            help="You can upload individual CV files or a ZIP containing multiple CVs",
        )

        # Full-width button styling with higher specificity
        st.markdown(
            """
        <style>
        div[data-testid=\"stButton\"] > button,
        .stButton > button,
        button[kind=\"primary\"] {
            width: 100% !important;
            height: 50px !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            margin-top: 10px !important;
            display: block !important;
        }
        .streamlit-expanderHeader { font-size: 14px !important; font-weight: 500 !important; }
        details[open] > summary { margin-bottom: 10px !important; }
        </style>
            """,
            unsafe_allow_html=True,
        )

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

        analysis_key = f"{job_title}_{len(uploaded_files)}_{hash(job_description[:100])}"
        if f"analysis_results_{analysis_key}" not in st.session_state:
            with st.spinner("Analyzing candidates... This may take a few moments."):
                try:
                    docs = load_files_from_uploader(uploaded_files)
                    if not docs:
                        st.error("❌ No valid CV files found in the uploaded files.")
                        st.stop()

                    job_context = {
                        "job_title": job_title.strip(),
                        "job_description": job_description.strip(),
                        "analysis_instructions": "Analyze each CV against this job and provide detailed insights",
                    }

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

                    scored_candidates = []
                    progress_bar = st.progress(0)
                    total_candidates_to_score = len(candidates)
                    for i, candidate in enumerate(candidates):
                        progress_bar.progress((i + 1) / total_candidates_to_score)
                        score, reasoning, brief_summary = score_candidate_with_ai(candidate, job_title, job_description)
                        candidate.ai_score = score
                        candidate.ai_reasoning = reasoning
                        candidate.brief_summary = brief_summary
                        scored_candidates.append((score, candidate))
                    progress_bar.empty()
                    scored_candidates.sort(key=lambda x: x[0], reverse=True)

                    st.session_state[f"analysis_results_{analysis_key}"] = {
                        "scored_candidates": scored_candidates,
                        "job_title": job_title,
                        "total_candidates": len(candidates),
                    }
                    st.session_state["current_analysis_key"] = analysis_key
                    st.session_state.pop("selected_candidate_idx", None)
                except Exception as e:
                    st.error("An error occurred during analysis: " + str(e))
                    st.exception(e)
                    st.stop()

        render_analysis_results(analysis_key)

    # If already analyzed previously in this session, show results even on rerun
    if (not analyze_button) and st.session_state.get("current_analysis_key") and \
       f"analysis_results_{st.session_state['current_analysis_key']}" in st.session_state:
        render_analysis_results(st.session_state["current_analysis_key"])
