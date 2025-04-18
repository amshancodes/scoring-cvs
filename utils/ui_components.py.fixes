"""
UI components for the Streamlit app
"""

import streamlit as st
import base64
from pathlib import Path

def set_page_config():
    """Set the page configuration"""
    st.set_page_config(
        page_title="Resume Evaluation System",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def add_custom_css():
    """Add custom CSS for better styling"""
    st.markdown("""
    <style>
        .main {
            padding: 1rem 1rem;
        }
        .stAlert {
            border-radius: 10px;
        }
        .stProgress > div > div {
            border-radius: 10px;
        }
        .stButton button {
            border-radius: 5px;
            height: 3em;
            width: 100%;
        }
        .card {
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            background-color: #f7f7f7;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .top-score-card {
            background-color: #f0f7ff;
            border-left: 5px solid #4A90E2;
        }
        h1, h2, h3, h4 {
            font-weight: 600;
        }
        .footer {
            text-align: center;
            margin-top: 2rem;
            opacity: 0.7;
            font-size: 0.8rem;
        }
        .score-badge {
            background-color: #4A90E2;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-weight: bold;
        }
        .sidebar-section {
            background-color: #f1f3f6;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
        }
    </style>
    """, unsafe_allow_html=True)

def show_header():
    """Display the application header"""
    st.markdown("# 📄 Resume Evaluation System")
    st.markdown("Upload a resume or paste text to evaluate candidates using AI")
    st.markdown("---")

def show_template_card(template, selected=False):
    """Show a template selection card"""
    bg_color = "#e6f3ff" if selected else "#f7f7f7"
    border = "3px solid #4A90E2" if selected else "1px solid #e0e0e0"
    
    st.markdown(f"""
    <div style="background-color: {bg_color}; padding: 15px; border-radius: 10px; 
        margin-bottom: 10px; border: {border};">
        <h3>{template['name']}</h3>
        <p>{template['description']}</p>
    </div>
    """, unsafe_allow_html=True)

def show_score_section(score, max_score, label, explanation):
    """Display a score section with label and explanation"""
    col1, col2 = st.columns([1, 5])
    with col1:
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="font-size: 1.8rem; font-weight: bold; color: #4A90E2;">{score}</div>
            <div style="font-size: 1rem; color: #666;">/{max_score}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"**{label}**")
        st.markdown(explanation)
    st.markdown("---")

def show_evaluation_summary(evaluation):
    """Display the evaluation summary in a nice format"""
    # Top summary card
    st.markdown("""
    <div class="card top-score-card">
        <h2>Evaluation Summary</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Total score
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="font-size: 3rem; font-weight: bold; color: #4A90E2;">
                {evaluation['total_score']}
            </div>
            <div style="font-size: 1.2rem; color: #666;">/50</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("### Overall Assessment")
        st.markdown(evaluation['summary'])
    
    st.markdown("---")
    
    # Individual scores
    show_score_section(
        evaluation['overall_impression']['score'], 10, 
        "Overall Impression", 
        evaluation['overall_impression']['explanation']
    )
    
    show_score_section(
        evaluation['technical_skills']['score'], 10, 
        "Technical Skills", 
        evaluation['technical_skills']['explanation']
    )
    
    show_score_section(
        evaluation['experience']['score'], 10, 
        "Experience", 
        evaluation['experience']['explanation']
    )
    
    show_score_section(
        evaluation['education']['score'], 10, 
        "Education", 
        evaluation['education']['explanation']
    )
    
    show_score_section(
        evaluation['projects']['score'], 10, 
        "Projects", 
        evaluation['projects']['explanation']
    )

def show_footer():
    """Display the application footer"""
    st.markdown("""
    <div class="footer">
        Resume Evaluation System • Powered by OpenAI • v1.0.0
    </div>
    """, unsafe_allow_html=True)

def show_api_key_input():
    """Display the API key input section"""
    st.sidebar.markdown("### 🔑 OpenAI API Key")
    api_key = st.sidebar.text_input(
        "Enter your OpenAI API key",
        type="password",
        help="Your API key will not be stored permanently",
        placeholder="sk-..."
    )
    st.sidebar.markdown("""
    <div style="font-size: 0.8rem; color: #666;">
        Your API key is only used for this session and not stored.
    </div>
    """, unsafe_allow_html=True)
    
    return api_key

def download_button(object_to_download, download_filename, button_text):
    """Generate a download button for any object"""
    if isinstance(object_to_download, str):
        b64 = base64.b64encode(object_to_download.encode()).decode()
    else:
        b64 = base64.b64encode(object_to_download).decode()
        
    button_uuid = "download_button"
    custom_css = f""" 
        <style>
            #{button_uuid} {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                background-color: #4A90E2;
                color: white;
                padding: 0.5em 1em;
                border-radius: 5px;
                text-decoration: none;
                font-weight: 500;
                border: none;
                cursor: pointer;
                width: 100%;
            }}
            #{button_uuid}:hover {{
                background-color: #3a7abd;
            }}
        </style>
    """
    
    dl_link = custom_css + f'<a href="data:file/txt;base64,{b64}" id="{button_uuid}" download="{download_filename}">{button_text}</a>'
    return st.markdown(dl_link, unsafe_allow_html=True) 