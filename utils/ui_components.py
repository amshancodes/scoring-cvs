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
        .copy-btn {
            background-color: #4A90E2;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 16px;
            font-size: 14px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            margin: 10px 0;
            transition: background-color 0.3s;
        }
        .copy-btn:hover {
            background-color: #3a7abd;
        }
        .copy-btn svg {
            margin-right: 8px;
        }
        .evaluation-md {
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 5px;
            margin-bottom: 20px;
            font-family: 'Helvetica', sans-serif;
            line-height: 1.6;
            max-height: 500px;
            overflow-y: auto;
        }
        /* Animation for copy feedback */
        @keyframes fadeInOut {
            0% { opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { opacity: 0; }
        }
        .copy-success {
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: #4caf50;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            z-index: 9999;
            animation: fadeInOut 2s forwards;
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

def copy_button(text_to_copy, button_text="📋 Copy to Clipboard"):
    """Create a button that copies text to clipboard using JavaScript"""
    # Generate a unique ID for this button
    button_id = f"copy_button_{hash(text_to_copy)}"[-10:]
    
    # Process the text to make it safe for JavaScript
    # Replace line breaks with explicit newlines for JS
    js_safe_text = text_to_copy.replace("\n", "\\n").replace("\r", "").replace("'", "\\'").replace('"', '\\"')
    
    # Create the JavaScript function to handle copying
    copy_js = f"""
    <script>
    function copyToClipboard{button_id}() {{
        navigator.clipboard.writeText('{js_safe_text}')
            .then(() => {{
                // Show success message
                const successMsg = document.createElement('div');
                successMsg.className = 'copy-success';
                successMsg.textContent = '✓ Copied to clipboard!';
                document.body.appendChild(successMsg);
                
                // Change button text to show success
                document.getElementById('{button_id}').innerHTML = '✓ Copied!';
                
                // Remove success message after animation
                setTimeout(() => {{
                    if (successMsg.parentNode) {{
                        document.body.removeChild(successMsg);
                    }}
                }}, 2000);
                
                // Reset button text
                setTimeout(() => {{
                    document.getElementById('{button_id}').innerHTML = '{button_text}';
                }}, 2000);
            }})
            .catch(err => {{
                console.error('Failed to copy: ', err);
                // Show error message briefly
                document.getElementById('{button_id}').innerHTML = '❌ Failed to copy';
                setTimeout(() => {{
                    document.getElementById('{button_id}').innerHTML = '{button_text}';
                }}, 2000);
            }});
    }}
    </script>
    """
    
    # Create the button HTML
    button_html = f"""
    <button id="{button_id}" class="copy-btn" onclick="copyToClipboard{button_id}()">
        {button_text}
    </button>
    {copy_js}
    """
    
    return st.markdown(button_html, unsafe_allow_html=True)

def show_markdown_content(markdown_content, with_copy=True):
    """Display markdown content in a nice format with optional copy button"""
    # Display the markdown content in a styled container
    st.markdown("<div class='evaluation-md'>", unsafe_allow_html=True)
    st.markdown(markdown_content)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add copy button if requested
    if with_copy:
        copy_button(markdown_content) 