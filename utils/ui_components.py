"""
UI components for the Streamlit app
"""

import streamlit as st
import base64
import hashlib
import re
from pathlib import Path
import json
import html # Import html for escaping

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
    # Remove clipboard.js CDN link and initialization
    st.markdown(f"""
    <style>
        .main {{
            padding: 1rem 1rem;
        }}
        .stAlert {{
            border-radius: 10px;
        }}
        .stProgress > div > div {{
            border-radius: 10px;
        }}
        .stButton button {{
            border-radius: 5px;
            height: 3em;
            width: 100%;
        }}
        .card {{
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            background-color: #f7f7f7;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .top-score-card {{
            background-color: #f0f7ff;
            border-left: 5px solid #4A90E2;
        }}
        h1, h2, h3, h4 {{
            font-weight: 600;
        }}
        .footer {{
            text-align: center;
            margin-top: 2rem;
            opacity: 0.7;
            font-size: 0.8rem;
        }}
        .score-badge {{
            background-color: #4A90E2;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-weight: bold;
        }}
        .sidebar-section {{
            background-color: #f1f3f6;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
        }}
        .copy-btn {{
            background-color: #cccccc; /* Grey out button */
            color: #666666;
            border: none;
            border-radius: 5px;
            padding: 8px 16px;
            font-size: 14px;
            cursor: not-allowed; /* Indicate non-interactive */
            display: inline-flex;
            align-items: center;
            margin: 10px 0;
            transition: background-color 0.3s;
            width: 100%;
            /* max-width: 300px; */ /* Removed to allow full width in container */
        }}
        .copy-btn:hover {{
            background-color: #cccccc; /* No hover effect */
        }}
        .copy-btn svg {{
            margin-right: 8px;
        }}
        .evaluation-md {{
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 5px;
            margin-bottom: 20px;
            font-family: 'Helvetica', sans-serif;
            line-height: 1.6;
            max-height: 500px;
            overflow-y: auto;
        }}
        .toast-message {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background-color: #4CAF50;
            color: white;
            padding: 16px;
            border-radius: 5px;
            z-index: 9999;
            opacity: 0;
            transition: opacity 0.5s;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .show-toast {{
            opacity: 1;
        }}
        /* Class to properly hide elements */
        .visually-hidden {{
            position: absolute;
            width: 1px;
            height: 1px;
            margin: -1px;
            padding: 0;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            border: 0;
            white-space: nowrap; /* Added for robustness */
        }}
        /* Style for button container */
        .button-container {{
            display: flex;
            gap: 10px; /* Space between buttons */
            margin-top: 15px;
            margin-bottom: 10px;
        }}
        .button-container .stMarkdown {{
            width: 100%; /* Make markdown containers take full width */
        }}
        .button-container button, .button-container a {{
             width: 100% !important; /* Make buttons/links take full width */
             max-width: none !important; /* Override max-width from copy-btn */
        }}
    </style>
    """, unsafe_allow_html=True)

def show_header():
    """Display the application header"""
    col1, col2 = st.columns([10, 1])
    with col1:
        st.markdown("# 📄 Resume Evaluation System")
        st.markdown("Internal Tool: Upload a resume or paste text to evaluate candidates using AI")
    with col2:
        with st.popover("ℹ️", use_container_width=True):
            st.markdown("### About This Tool")
            st.markdown("""
            This is an internal MVP tool created for efficiency in candidate evaluation.
            - **Purpose**: Streamline resume assessment
            - **Status**: MVP v1.0.0
            - **Feedback**: Please report any issues to the dev team
            """)
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
    
    # Check if total_score exists, otherwise try to calculate it
    if 'total_score' not in evaluation:
        try:
            # Try to calculate total score from individual scores
            total = 0
            for category in ['overall_impression', 'technical_skills', 'experience', 'education', 'projects']:
                if category in evaluation and 'score' in evaluation[category]:
                    total += evaluation[category]['score']
            evaluation['total_score'] = total
        except:
            # If calculation fails, set a placeholder
            evaluation['total_score'] = "-"
    
    # Same for summary
    if 'summary' not in evaluation:
        evaluation['summary'] = "No summary provided in the evaluation."
    
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
    
    # Individual scores - with error handling for each section
    categories = [
        ('overall_impression', 'Overall Impression'),
        ('technical_skills', 'Technical Skills'),
        ('experience', 'Experience'),
        ('education', 'Education'),
        ('projects', 'Projects')
    ]
    
    for category_key, category_label in categories:
        if category_key in evaluation and isinstance(evaluation[category_key], dict):
            category = evaluation[category_key]
            score = category.get('score', '-')
            explanation = category.get('explanation', 'No details provided.')
            show_score_section(score, 10, category_label, explanation)
        else:
            # Show placeholder if category is missing
            show_score_section('-', 10, category_label, 'Information not available.')

def show_footer():
    """Display the application footer"""
    st.markdown("""
    <div class="footer">
        Built by Hire AI, for Hire AI. Internal Tool. Version 1.0.0.
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

def copy_button(text_to_copy="", button_text="📋 Copy (Not Working)"):
    """Render a disabled-looking copy button placeholder"""
    # Create a unique ID just for rendering
    button_id = f"copy_btn_placeholder_{hashlib.md5(button_text.encode()).hexdigest()[:10]}"

    # Button HTML - styled as disabled, no JS functionality
    button_html = f"""
    <button id="{button_id}" class="copy-btn" disabled title="Copy functionality currently disabled">
        {button_text}
    </button>
    """
    return button_html # Return raw HTML string

def show_markdown_content(markdown_content, download_info=None, with_copy=True):
    """Display markdown content with optional (non-functional) copy and download buttons side-by-side"""
    # Display the markdown content in a styled container
    st.markdown("<div class='evaluation-md'>", unsafe_allow_html=True)
    st.markdown(markdown_content)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Button Row
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        # Add non-functional copy button if requested
        if with_copy:
            copy_button_html = copy_button() 
            st.markdown(copy_button_html, unsafe_allow_html=True)
        else:
            st.markdown("<div></div>", unsafe_allow_html=True) # Placeholder

    with col2:
        # Add download button if info provided
        if download_info and isinstance(download_info, dict):
            download_button(
                object_to_download=markdown_content,
                download_filename=download_info.get("filename", "evaluation.md"),
                button_text=download_info.get("text", "📥 Download Markdown")
            )
        else:
            st.markdown("<div></div>", unsafe_allow_html=True) # Placeholder
    
    st.markdown('</div>', unsafe_allow_html=True) 