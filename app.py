"""
Resume Evaluation System - Streamlit Web Application
"""

import os
import json
import time
import streamlit as st
from pathlib import Path

# Import utility modules
from utils.resume_processor import (
    extract_text_from_pdf_bytes,
    extract_text_from_pdf_file,
    evaluate_resume_with_ai,
    get_available_templates,
    read_prompt_file,
    get_available_models
)
from utils.ui_components import (
    set_page_config,
    add_custom_css,
    show_header,
    show_template_card,
    show_evaluation_summary,
    show_footer,
    show_api_key_input,
    download_button
)

# Set page configuration
set_page_config()
add_custom_css()

# Initialize session state if not already done
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""
if 'evaluation_result' not in st.session_state:
    st.session_state.evaluation_result = None
if 'filename' not in st.session_state:
    st.session_state.filename = ""
if 'selected_template_index' not in st.session_state:
    st.session_state.selected_template_index = 0
if 'selected_model_index' not in st.session_state:
    st.session_state.selected_model_index = 0
if 'show_password' not in st.session_state:
    st.session_state.show_password = False

# Get API key from Streamlit secrets or environment variable
def get_api_key():
    # Try to get from secrets
    if 'openai' in st.secrets and 'api_key' in st.secrets['openai']:
        return st.secrets['openai']['api_key']
    # Fallback to environment variable
    return os.environ.get('OPENAI_API_KEY', '')

# Navigation functions
def go_to_step(step_number):
    st.session_state.step = step_number
    
def go_to_next_step():
    st.session_state.step += 1

def go_to_previous_step():
    st.session_state.step -= 1
    
def reset_app():
    st.session_state.step = 1
    st.session_state.resume_text = ""
    st.session_state.evaluation_result = None
    st.session_state.filename = ""

# App header
show_header()

# Simple authentication (MVP version)
password = "demo123"  # Simple password for MVP
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Authentication check
if not st.session_state.authenticated:
    auth_col1, auth_col2 = st.columns([3, 1])
    with auth_col1:
        entered_password = st.text_input("Enter password to access the application", type="password")
    with auth_col2:
        if st.button("Login"):
            if entered_password == password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")
    st.stop()

# Main content area - based on current step
if st.session_state.step == 1:
    # Step 1: Resume Input
    st.markdown("## Step 1: Resume Input")
    st.markdown("Upload a resume file or paste the resume text below.")
    
    # Input tabs for different input methods
    tab1, tab2, tab3 = st.tabs(["📤 Upload PDF", "📝 Paste Text", "🔍 Sample Resume"])
    
    with tab1:
        uploaded_file = st.file_uploader("Upload a resume PDF file", type=['pdf'])
        if uploaded_file is not None:
            try:
                st.session_state.filename = uploaded_file.name
                st.session_state.resume_text = extract_text_from_pdf_bytes(uploaded_file)
                st.success(f"Successfully extracted text from {uploaded_file.name}")
                
                with st.expander("Preview Extracted Text"):
                    st.text_area("Resume Text", st.session_state.resume_text, height=300)
                    
            except Exception as e:
                st.error(f"Error processing PDF: {e}")
    
    with tab2:
        pasted_text = st.text_area("Paste resume text here", height=300)
        if st.button("Use this text"):
            if pasted_text.strip():
                st.session_state.resume_text = pasted_text
                st.session_state.filename = "pasted_resume"
                st.success("Resume text saved")
            else:
                st.warning("Please paste some text first")
    
    with tab3:
        st.info("Load a sample resume for demonstration purposes")
        if st.button("Load Sample Resume"):
            # Try to load the sample text file
            sample_txt_path = Path("samples/sample_resume.txt")
            
            if sample_txt_path.exists():
                try:
                    with open(sample_txt_path, 'r') as file:
                        sample_text = file.read()
                        
                    st.session_state.resume_text = sample_text
                    st.session_state.filename = "sample_resume"
                    st.success(f"Loaded sample resume")
                    
                    with st.expander("Preview Sample Resume"):
                        st.text_area("Sample Resume", sample_text, height=300)
                        
                except Exception as e:
                    st.error(f"Error loading sample text: {e}")
                    
            else:
                # If text file doesn't exist, try PDF files
                sample_paths = [
                    Path("samples/sample_resume.pdf"),
                    Path("samples/resume_sample.pdf"),
                    Path("PDF-RESUMES/Adam_Jinnah_JuiceboxExport_2025-04-16_10.pdf")
                ]
                
                sample_found = False
                for sample_path in sample_paths:
                    if sample_path.exists():
                        try:
                            st.session_state.resume_text = extract_text_from_pdf_file(sample_path)
                            st.session_state.filename = sample_path.name
                            st.success(f"Loaded sample resume: {sample_path.name}")
                            sample_found = True
                            
                            with st.expander("Preview Sample Resume Text"):
                                st.text_area("Sample Resume", st.session_state.resume_text, height=300)
                            
                            break
                        except Exception as e:
                            st.error(f"Error loading sample PDF: {e}")
                
                if not sample_found:
                    st.error("No sample resume files found. Please add a sample to the 'samples' directory.")
                    # Provide a dummy text as fallback
                    if st.button("Use Dummy Sample Instead"):
                        dummy_text = """
                        John Doe
                        AI Researcher & Machine Learning Engineer
                        
                        EXPERIENCE
                        Senior Machine Learning Engineer
                        TechCorp, Inc. (2020-Present)
                        • Led development of NLP models for text classification
                        • Improved model accuracy by 25% using transformer architectures
                        • Deployed ML pipelines to production serving 10M+ users
                        
                        AI Research Associate
                        University of Technology (2018-2020)
                        • Published 3 papers on deep learning techniques
                        • Developed novel approaches for computer vision tasks
                        
                        EDUCATION
                        Ph.D. in Computer Science
                        University of Technology (2018)
                        
                        B.S. in Computer Science
                        State University (2014)
                        
                        SKILLS
                        Python, TensorFlow, PyTorch, NLP, Computer Vision, 
                        MLOps, Git, Docker, Kubernetes, SQL, AWS
                        """
                        st.session_state.resume_text = dummy_text
                        st.session_state.filename = "dummy_sample_resume"
                        st.success("Loaded dummy sample resume text")
                        
                        with st.expander("Preview Dummy Sample Resume"):
                            st.text_area("Dummy Sample", dummy_text, height=300)
    
    # Navigation
    col1, col2, col3 = st.columns([2, 2, 6])
    with col2:
        if st.button("Next: Configure Evaluation", disabled=not st.session_state.resume_text):
            go_to_next_step()

elif st.session_state.step == 2:
    # Step 2: Configure Evaluation
    st.markdown("## Step 2: Configure Evaluation")
    st.markdown("Configure how you want the resume to be evaluated.")
    
    # Get available templates
    templates = get_available_templates()
    
    # Template selection
    st.markdown("### Evaluation Template")
    for i, template in enumerate(templates):
        col1, col2 = st.columns([9, 1])
        with col1:
            show_template_card(template, selected=(i == st.session_state.selected_template_index))
        with col2:
            if st.button("Select", key=f"template_{i}"):
                st.session_state.selected_template_index = i
    
    # Advanced options expander
    with st.expander("Advanced Options"):
        # Custom prompt editing
        st.markdown("### Customize Prompts")
        if st.checkbox("Edit evaluation prompts", value=False):
            selected_template = templates[st.session_state.selected_template_index]
            
            # Read current prompts
            system_prompt = read_prompt_file(selected_template['system_prompt'])
            user_prompt = read_prompt_file(selected_template['user_prompt'])
            
            # Edit prompts
            st.markdown("#### System Prompt")
            system_prompt_edited = st.text_area("System Prompt", system_prompt, height=200)
            
            st.markdown("#### User Prompt")
            user_prompt_edited = st.text_area("User Prompt Template", user_prompt, height=300)
            
            # Save edited prompts (in-memory for MVP)
            if system_prompt_edited != system_prompt or user_prompt_edited != user_prompt:
                if st.button("Save Custom Prompts"):
                    # In a full implementation, we'd save these to files or database
                    # For the MVP, we'll just update the template object in memory
                    templates[st.session_state.selected_template_index]['custom_system_prompt'] = system_prompt_edited
                    templates[st.session_state.selected_template_index]['custom_user_prompt'] = user_prompt_edited
                    st.success("Custom prompts saved")
    
    # Navigation
    col1, col2, col3, col4 = st.columns([2, 2, 2, 4])
    with col1:
        if st.button("← Previous"):
            go_to_previous_step()
    with col2:
        if st.button("Next: Evaluate"):
            # Check if API key is available before proceeding
            api_key = get_api_key()
            if not api_key:
                st.error("OpenAI API key not found. Please contact the administrator.")
            else:
                go_to_next_step()

elif st.session_state.step == 3:
    # Step 3: Evaluation Process
    st.markdown("## Step 3: Processing")
    
    if st.session_state.evaluation_result is None:
        # Get API key
        api_key = get_api_key()
        if not api_key:
            st.error("OpenAI API key not found. Please contact the administrator.")
            if st.button("← Go Back to Configuration"):
                go_to_previous_step()
                st.rerun()
            st.stop()
            
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        result_area = st.empty()
        
        # Show progress updates
        status_text.text("Extracting resume information...")
        progress_bar.progress(20)
        time.sleep(0.5) # Simulate processing time
        
        status_text.text("Analyzing candidate profile...")
        progress_bar.progress(40)
        time.sleep(0.5)
        
        status_text.text("Evaluating technical skills...")
        progress_bar.progress(60)
        time.sleep(0.5)
        
        status_text.text("Generating comprehensive assessment...")
        progress_bar.progress(80)
        time.sleep(0.5)
        
        try:
            # Get the selected template
            templates = get_available_templates()
            selected_template = templates[st.session_state.selected_template_index]
            
            # Use default model (GPT-4.1)
            models = get_available_models()
            selected_model = models[0]  # Always use the first (best) model
            
            # Get prompts (including any custom ones)
            if 'custom_system_prompt' in selected_template:
                system_prompt = selected_template['custom_system_prompt']
            else:
                system_prompt = read_prompt_file(selected_template['system_prompt'])
                
            if 'custom_user_prompt' in selected_template:
                user_prompt = selected_template['custom_user_prompt']
            else:
                user_prompt = read_prompt_file(selected_template['user_prompt'])
            
            # Update status
            status_text.text("Making API request to OpenAI...")
            progress_bar.progress(90)
            
            # Run the evaluation
            evaluation_result = evaluate_resume_with_ai(
                st.session_state.resume_text,
                system_prompt,
                user_prompt,
                selected_model['value'],
                api_key
            )
            
            # Update progress
            status_text.text("Evaluation complete!")
            progress_bar.progress(100)
            
            # Store the result
            st.session_state.evaluation_result = evaluation_result
            
            # Show partial result preview
            with result_area.container():
                st.success("Evaluation completed successfully!")
                st.markdown(f"**Overall Score:** {evaluation_result['total_score']}/50")
                st.markdown(f"**Summary:** {evaluation_result['summary']}")
                
                if st.button("View Full Evaluation"):
                    go_to_next_step()
                    st.rerun()
            
            # Add a button to view full results
            if st.button("Continue to Results"):
                go_to_next_step()
                st.rerun()
                
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"Error during evaluation: {e}")
            
            # More detailed error information for easier debugging
            with st.expander("Error Details"):
                st.code(str(e))
                
            # Add retry button
            if st.button("Retry Evaluation"):
                st.rerun()
                
            # Add back button
            if st.button("← Go Back to Configuration"):
                go_to_previous_step()
                st.rerun()

elif st.session_state.step == 4:
    # Step 4: Results
    st.markdown("## Step 4: Evaluation Results")
    
    if st.session_state.evaluation_result:
        # Display the evaluation summary
        show_evaluation_summary(st.session_state.evaluation_result)
        
        # Export options
        st.markdown("### Export Options")
        col1, col2, col3 = st.columns(3)
        
        # Create the markdown content
        markdown_content = f"""# Resume Evaluation: {st.session_state.filename}

## Overall Score: {st.session_state.evaluation_result['total_score']}/50

### Summary
{st.session_state.evaluation_result['summary']}

### Overall Impression: {st.session_state.evaluation_result['overall_impression']['score']}/10
{st.session_state.evaluation_result['overall_impression']['explanation']}

### Technical Skills: {st.session_state.evaluation_result['technical_skills']['score']}/10
{st.session_state.evaluation_result['technical_skills']['explanation']}

### Experience: {st.session_state.evaluation_result['experience']['score']}/10
{st.session_state.evaluation_result['experience']['explanation']}

### Education: {st.session_state.evaluation_result['education']['score']}/10
{st.session_state.evaluation_result['education']['explanation']}

### Projects: {st.session_state.evaluation_result['projects']['score']}/10
{st.session_state.evaluation_result['projects']['explanation']}
"""
        
        with col1:
            download_button(
                markdown_content,
                f"{st.session_state.filename.split('.')[0]}_evaluation.md",
                "📥 Download as Markdown"
            )
            
        with col2:
            download_button(
                json.dumps(st.session_state.evaluation_result, indent=2),
                f"{st.session_state.filename.split('.')[0]}_evaluation.json",
                "📥 Download as JSON"
            )
            
        # Navigation
        st.markdown("### Actions")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("← Back to Configuration"):
                go_to_step(2)
        with col2:
            if st.button("Evaluate Another Resume"):
                reset_app()
    else:
        st.error("No evaluation results available")
        if st.button("Return to Start"):
            reset_app()

# Footer
show_footer()

# Side information about current step
with st.sidebar:
    st.markdown("### Progress")
    st.progress((st.session_state.step - 1) / 3)
    
    current_step_name = {
        1: "Resume Input",
        2: "Configuration",
        3: "Processing",
        4: "Results"
    }.get(st.session_state.step, "")
    
    st.markdown(f"**Current Step:** {st.session_state.step}. {current_step_name}")
    
    # Info about the current file
    if st.session_state.filename:
        st.markdown(f"**Current File:** {st.session_state.filename}")
    
    # Add info about using internal OpenAI API
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ About This System")
    st.sidebar.markdown("""
    This is an internal candidate evaluation system that leverages AI to provide
    consistent assessments of technical resumes. It uses our organization's 
    API key and custom evaluation criteria.
    """)
    
    # Help section at the bottom of sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Need Help?")
    with st.sidebar.expander("How to use this app"):
        st.markdown("""
        1. **Upload Resume**: Upload a PDF or paste text
        2. **Configure**: Select evaluation template
        3. **Process**: Wait for AI evaluation
        4. **Review**: See detailed assessment and download results
        """)

if __name__ == "__main__":
    # This will run when the script is executed directly
    pass 