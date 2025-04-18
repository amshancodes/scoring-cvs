"""
Resume Evaluation System - Streamlit Web Application
"""

import os
import json
import time
import streamlit as st
from pathlib import Path
import re
import io # Import io for BytesIO
import zipfile
from datetime import datetime

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
    download_button,
    copy_button,
    show_markdown_content
)

# Set page configuration
set_page_config()
add_custom_css()

# Initialize session state if not already done
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""
if 'uploaded_resumes' not in st.session_state:
    st.session_state.uploaded_resumes = []
if 'evaluation_result' not in st.session_state:
    st.session_state.evaluation_result = None
if 'evaluation_results_list' not in st.session_state:
    st.session_state.evaluation_results_list = []
if 'markdown_result' not in st.session_state:
    st.session_state.markdown_result = ""
if 'raw_api_response' not in st.session_state:
    st.session_state.raw_api_response = ""
if 'filename' not in st.session_state:
    st.session_state.filename = ""
if 'selected_template_index' not in st.session_state:
    st.session_state.selected_template_index = 0
if 'selected_model_index' not in st.session_state:
    st.session_state.selected_model_index = 0
if 'show_password' not in st.session_state:
    st.session_state.show_password = False
# Add new session state variables for custom prompts
if 'custom_system_prompt' not in st.session_state:
    st.session_state.custom_system_prompt = None
if 'custom_user_prompt' not in st.session_state:
    st.session_state.custom_user_prompt = None

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
    st.session_state.uploaded_resumes = []
    st.session_state.evaluation_result = None
    st.session_state.evaluation_results_list = []
    st.session_state.markdown_result = ""
    st.session_state.raw_api_response = ""
    st.session_state.filename = ""
    # Also reset custom prompts
    st.session_state.custom_system_prompt = None
    st.session_state.custom_user_prompt = None

# Create markdown content from API response - modified to use the markdown directly
def create_markdown_from_api(response, filename):
    """
    Create markdown content from the API response.
    This now uses the markdown_content field directly if available.
    """
    try:
        # Check if we have the markdown content directly
        if isinstance(response, dict) and 'markdown_content' in response:
            # Return the markdown content directly
            return response['markdown_content']
        
        # If markdown_content is not available, check for raw_text
        if isinstance(response, dict) and 'raw_text' in response:
            return response['raw_text']
        
        # If neither markdown_content nor raw_text is available, handle as before
        if isinstance(response, dict):
            # Start with the resume name
            markdown = f"# Resume Evaluation: {filename}\n\n"
            
            # If response has a standard format, extract fields
            if 'total_score' in response or 'summary' in response:
                # Add summary if available
                if 'summary' in response:
                    markdown += f"## Summary\n{response['summary']}\n\n"
                
                # Add total score if available
                if 'total_score' in response:
                    markdown += f"## Overall Score: {response['total_score']}/50\n\n"
                
                # Add individual categories
                categories = [
                    ('overall_impression', 'Overall Impression'),
                    ('technical_skills', 'Technical Skills'), 
                    ('experience', 'Experience'),
                    ('education', 'Education'),
                    ('projects', 'Projects')
                ]
                
                for key, label in categories:
                    if key in response and isinstance(response[key], dict):
                        category = response[key]
                        score = category.get('score', '-')
                        explanation = category.get('explanation', 'No details provided.')
                        markdown += f"## {label}: {score}/10\n{explanation}\n\n"
            else:
                # If it doesn't match our expected format, just dump the entire response
                markdown += "## Evaluation Results\n"
                markdown += json.dumps(response, indent=2)
        else:
            # If not a dict, handle as string or raw content
            markdown = f"# Resume Evaluation: {filename}\n\n"
            markdown += str(response)
        
        return markdown.strip()
        
    except Exception as e:
        # If something goes wrong, return a basic evaluation
        return f"# Resume Evaluation: {filename}\n\nError generating formatted output: {str(e)}"

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
        if st.button("Login", key="login_button"):
            if entered_password == password:
                st.session_state.authenticated = True
                with st.spinner("Logging in..."):
                    st.rerun()
            else:
                st.error("Incorrect password")
    st.stop()

# Main content area - based on current step
if st.session_state.step == 1:
    # Step 1: Resume Input
    st.markdown("## Step 1: Resume Input")
    st.markdown("Upload one or more resume PDF files, paste text, or load a sample.")
    
    # Input tabs for different input methods
    tab1, tab2, tab3 = st.tabs(["📤 Upload PDF(s)", "📝 Paste Text", "🔍 Sample Resume"])
    
    with tab1:
        # Allow multiple file uploads
        uploaded_files = st.file_uploader(
            "Upload resume PDF files", 
            type=['pdf'], 
            accept_multiple_files=True
        )
        if uploaded_files:
            # Clear previous uploads if new ones are added
            st.session_state.uploaded_resumes = []
            st.session_state.resume_text = "" # Clear single text if files are uploaded
            st.session_state.filename = "" 
            
            processed_files = []
            error_files = []
            
            for uploaded_file in uploaded_files:
                try:
                    # Store file info (name and bytes) for later processing
                    file_info = {
                        "filename": uploaded_file.name,
                        "bytes": uploaded_file.read() # Read bytes here
                    }
                    st.session_state.uploaded_resumes.append(file_info)
                    processed_files.append(uploaded_file.name)
                except Exception as e:
                    error_files.append(uploaded_file.name)
                    st.error(f"Error reading {uploaded_file.name}: {e}")
            
            if processed_files:
                st.success(f"Successfully queued {len(processed_files)} file(s) for evaluation: {', '.join(processed_files)}")
            if error_files:
                 st.warning(f"Could not read {len(error_files)} file(s): {', '.join(error_files)}")

            # Optional: Preview filenames
            with st.expander("Uploaded Files"):
                for file_info in st.session_state.uploaded_resumes:
                    st.text(file_info["filename"])
                    
    with tab2:
        pasted_text = st.text_area("Paste resume text here", height=300)
        if st.button("Use this text"):
            if pasted_text.strip():
                st.session_state.resume_text = pasted_text
                st.session_state.filename = "pasted_resume"
                st.session_state.uploaded_resumes = [] # Clear file uploads if text is pasted
                st.success("Pasted resume text saved")
            else:
                st.warning("Please paste some text first")
    
    with tab3:
        st.info("Load a sample resume for demonstration purposes")
        if st.button("Load Sample Resume"):
            # Try to load the sample text file
            sample_txt_path = Path("samples/sample_resume.txt")
            sample_loaded = False
            if sample_txt_path.exists():
                try:
                    with open(sample_txt_path, 'r') as file:
                        sample_text = file.read()
                        
                    st.session_state.resume_text = sample_text
                    st.session_state.filename = "sample_resume"
                    st.success(f"Loaded sample resume")
                    
                    with st.expander("Preview Sample Resume"):
                        st.text_area("Sample Resume", sample_text, height=300)
                        
                    st.session_state.uploaded_resumes = [] # Clear file uploads
                    sample_loaded = True
                    
                except Exception as e:
                    st.error(f"Error loading sample text: {e}")
            else:
                # If text file doesn't exist, try PDF files
                sample_paths = [
                    Path("samples/sample_resume.pdf"),
                    Path("samples/resume_sample.pdf"),
                    Path("PDF-RESUMES/Adam_Jinnah_JuiceboxExport_2025-04-16_10.pdf")
                ]
                
                for sample_path in sample_paths:
                    if sample_path.exists():
                        try:
                            st.session_state.resume_text = extract_text_from_pdf_file(sample_path)
                            st.session_state.filename = sample_path.name
                            st.success(f"Loaded sample resume: {sample_path.name}")
                            
                            with st.expander("Preview Sample Resume Text"):
                                st.text_area("Sample Resume", st.session_state.resume_text, height=300)
                            
                            st.session_state.uploaded_resumes = [] # Clear file uploads
                            sample_loaded = True
                            break
                        except Exception as e:
                            st.error(f"Error loading sample PDF: {e}")
                
                if not sample_loaded:
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
                            st.session_state.uploaded_resumes = [] # Clear file uploads
    
    # Determine if ready for next step
    ready_to_proceed = bool(st.session_state.resume_text or st.session_state.uploaded_resumes)
    
    # Navigation
    col1, col2, col3 = st.columns([2, 2, 6])
    with col2:
        # Instead of checking condition within button, check it after button is clicked
        if st.button("Next: Configure Evaluation", disabled=not ready_to_proceed, key="next_button_step1"):
            go_to_next_step()
            # Force the app to rerun to show the new state
            st.rerun()

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
        edit_prompts_checkbox = st.checkbox("Edit evaluation prompts", value=False)
        if edit_prompts_checkbox:
            selected_template = templates[st.session_state.selected_template_index]
            
            # Read current prompts
            system_prompt = read_prompt_file(selected_template['system_prompt'])
            user_prompt = read_prompt_file(selected_template['user_prompt'])
            
            # Edit prompts
            st.markdown("#### System Prompt")
            system_prompt_edited = st.text_area("System Prompt", system_prompt, height=200)
            
            st.markdown("#### User Prompt")
            st.markdown('<div style="padding: 1em; border-radius: 0.5em; background-color: #cfe2ff; color: #084298;"><p>Make sure to keep the <span style="color:red; font-weight:bold;">{resume_text}</span> placeholder in your prompt - this is where the actual resume content will be inserted.</p></div>', unsafe_allow_html=True)
            user_prompt_edited = st.text_area("User Prompt Template", user_prompt, height=300)
            
            # Save edited prompts (in-memory for MVP)
            if system_prompt_edited != system_prompt or user_prompt_edited != user_prompt:
                st.markdown("<div style='color:red;'>Your custom prompts will be automatically saved when you click 'Start Evaluation'</div>", unsafe_allow_html=True)
                if st.button("Save Custom Prompts", type="primary"):
                    # Make sure the user prompt contains the resume_text placeholder
                    if "{resume_text}" not in user_prompt_edited:
                        st.error("The user prompt must contain the {resume_text} placeholder where the resume content will be inserted.")
                    else:
                        # Store in session state to persist between steps
                        st.session_state.custom_system_prompt = system_prompt_edited
                        st.session_state.custom_user_prompt = user_prompt_edited
                        # Also update the template object in memory for the current session
                        templates[st.session_state.selected_template_index]['custom_system_prompt'] = system_prompt_edited
                        templates[st.session_state.selected_template_index]['custom_user_prompt'] = user_prompt_edited
                        st.success("Custom prompts saved")
    
    # Navigation
    col1, col2, col3, col4 = st.columns([2, 2, 2, 4])
    with col1:
        if st.button("← Previous", key="prev_button_step2"):
            go_to_previous_step()
            st.rerun()
    with col2:
        # Check if API key is available
        api_key = get_api_key()
        button_disabled = not api_key
        
        if st.button("Start Evaluation", disabled=button_disabled, key="eval_button_step2"):
            if not api_key:
                st.error("OpenAI API key not found. Please contact the administrator.")
            else:
                # If "Edit evaluation prompts" checkbox is on, automatically save the custom prompts
                if edit_prompts_checkbox:
                    # Check if user prompt contains the resume_text placeholder
                    if "{resume_text}" not in user_prompt_edited:
                        st.error("The user prompt must contain the {resume_text} placeholder where the resume content will be inserted.")
                        st.stop()
                    else:
                        # Store in session state to persist between steps
                        st.session_state.custom_system_prompt = system_prompt_edited
                        st.session_state.custom_user_prompt = user_prompt_edited
                        # Also update the template object in memory for the current session
                        templates[st.session_state.selected_template_index]['custom_system_prompt'] = system_prompt_edited
                        templates[st.session_state.selected_template_index]['custom_user_prompt'] = user_prompt_edited
                        st.success("Custom prompts automatically saved")
                        time.sleep(1)  # Brief pause to show the success message
                        
                # Show a spinner to indicate processing
                with st.spinner("Transitioning to evaluation..."):
                    go_to_next_step()
                    st.rerun()

elif st.session_state.step == 3:
    # Step 3: Evaluation Process (Modified for Bulk)
    st.markdown("## Evaluating Resume(s)")
    
    # Get API key
    api_key = get_api_key()
    if not api_key:
        st.error("OpenAI API key not found. Please contact the administrator.")
        if st.button("← Go Back", key="back_no_api"):
            go_to_previous_step()
            st.rerun()
        st.stop()
    
    # Determine if processing single text or multiple files
    is_bulk_mode = bool(st.session_state.uploaded_resumes)
    is_single_mode = bool(st.session_state.resume_text) and not is_bulk_mode
    
    # Check if we need to run evaluation
    run_evaluation = False
    if is_single_mode and not st.session_state.evaluation_result:
        run_evaluation = True
    elif is_bulk_mode and not st.session_state.evaluation_results_list:
        run_evaluation = True
        
    if run_evaluation:
        # Get common evaluation parameters (template, model)
        templates = get_available_templates()
        selected_template = templates[st.session_state.selected_template_index]
        models = get_available_models()
        selected_model = models[0] # Always use the first (best) model
        
        # Get prompts (including any custom ones)
        if st.session_state.custom_system_prompt is not None:
            # Use custom system prompt from session state (highest priority)
            system_prompt = st.session_state.custom_system_prompt
            st.info("Using custom system prompt")
        elif 'custom_system_prompt' in selected_template:
            # Use custom system prompt from template
            system_prompt = selected_template['custom_system_prompt']
        else:
            # Use default system prompt from file
            system_prompt = read_prompt_file(selected_template['system_prompt'])
            
        if st.session_state.custom_user_prompt is not None:
            # Use custom user prompt from session state (highest priority)
            user_prompt_template = st.session_state.custom_user_prompt
            st.info("Using custom user prompt")
        elif 'custom_user_prompt' in selected_template:
            # Use custom user prompt from template
            user_prompt_template = selected_template['custom_user_prompt']
        else:
            # Use default user prompt from file
            user_prompt_template = read_prompt_file(selected_template['user_prompt'])
        
        # Prepare list of items to evaluate
        items_to_evaluate = []
        if is_single_mode:
            items_to_evaluate.append({"filename": st.session_state.filename, "text": st.session_state.resume_text})
        elif is_bulk_mode:
            for resume_info in st.session_state.uploaded_resumes:
                try:
                    # Extract text from bytes stored earlier, wrapping in BytesIO
                    resume_bytes_stream = io.BytesIO(resume_info["bytes"])
                    resume_text = extract_text_from_pdf_bytes(resume_bytes_stream)
                    items_to_evaluate.append({"filename": resume_info["filename"], "text": resume_text})
                except Exception as e:
                    # Store error instead of text for this file
                    items_to_evaluate.append({"filename": resume_info["filename"], "error": f"Text extraction failed: {e}"})
        
        total_items = len(items_to_evaluate)
        results_list = []
        errors_list = []
        # Add a configurable delay between API calls (in seconds)
        # Increased delay to 10s to stay within likely TPM limits
        API_CALL_DELAY = 10 
        
        # Progress tracking
        st.markdown(f"Processing {total_items} resume(s)...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        phase_indicator = st.empty()  # New element for showing the current phase
        
        for i, item in enumerate(items_to_evaluate):
            filename = item["filename"]
            status_text.text(f"Evaluating: {filename} ({i+1}/{total_items})")
            
            if "error" in item:
                # Handle extraction errors
                error_msg = f"Could not extract text from {filename}: {item['error']}"
                results_list.append({"filename": filename, "error": error_msg, "_raw_response": error_msg})
                errors_list.append(filename)
                progress_bar.progress((i + 1) / total_items)
                continue # Skip evaluation if text extraction failed

            resume_text = item["text"]
            
            try:
                # Show evaluation phases
                phase_indicator.info("📋 Phase 1/3: Preparing resume content for analysis...")
                time.sleep(0.5)  # Brief pause for UI update
                
                # Run the evaluation for this item
                phase_indicator.warning("🔍 Phase 2/3: Analyzing candidate qualifications and experience...")
                
                evaluation_result = evaluate_resume_with_ai(
                    resume_text,
                    system_prompt,
                    user_prompt_template,
                    selected_model['value'],
                    api_key
                )
                
                phase_indicator.success("✅ Phase 3/3: Generating comprehensive evaluation report...")
                time.sleep(0.5)  # Brief pause for UI update
                
                # Store result (including filename)
                result_item = {"filename": filename, **evaluation_result}
                results_list.append(result_item)
                
            except Exception as e:
                # Handle evaluation errors
                error_msg = f"Error evaluating {filename}: {e}"
                raw_error_details = str(e)
                # Try to get more details if available (e.g., from OpenAI error response)
                if hasattr(e, 'response') and hasattr(e.response, 'text'):
                    raw_error_details = e.response.text 
                elif hasattr(e, 'message'): # Some OpenAI errors have a message attribute
                     raw_error_details = e.message
                     
                results_list.append({"filename": filename, "error": error_msg, "_raw_response": raw_error_details})
                errors_list.append(filename)
            
            # Update progress bar
            progress_bar.progress((i + 1) / total_items)
            # Add delay between calls if not the last item
            if i < total_items - 1:
                 time.sleep(API_CALL_DELAY) 
        
        # Store results in session state
        if is_single_mode:
            st.session_state.evaluation_result = results_list[0] if results_list else None
            st.session_state.markdown_result = results_list[0].get("markdown_content", "") if results_list and "error" not in results_list[0] else ""
            st.session_state.raw_api_response = results_list[0].get("_raw_response", "") if results_list else ""
        elif is_bulk_mode:
            st.session_state.evaluation_results_list = results_list
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        phase_indicator.empty()  # Clear the phase indicator
        st.success(f"Evaluation complete for {total_items - len(errors_list)} out of {total_items} resume(s).")
        if errors_list:
            st.warning(f"Errors occurred for: {', '.join(errors_list)}")

    # --- Display Results --- 
    st.markdown("--- ")
    st.subheader("Evaluation Results")
    
    results_to_display = []
    if is_single_mode and st.session_state.evaluation_result:
        results_to_display = [st.session_state.evaluation_result]
    elif is_bulk_mode and st.session_state.evaluation_results_list:
        results_to_display = st.session_state.evaluation_results_list
        
    if not results_to_display:
        st.info("No evaluation results to display.")
    else:
        # Add Download All button for multiple evaluations
        if len(results_to_display) > 1:
            st.markdown("### Batch Download")
            
            # Filter out only successful evaluations
            successful_evals = [result for result in results_to_display if "markdown_content" in result]
            
            # Only show download button if there are successful evaluations
            if successful_evals:
                # Create a zipfile with all evaluations
                with st.spinner("Preparing ZIP file with all evaluations..."):
                    # Create a buffer for the zip file
                    zip_buffer = io.BytesIO()
                    
                    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                        for result in successful_evals:
                            if "markdown_content" in result:
                                filename = f"{result['filename'].split('.')[0]}_evaluation.md"
                                # Add markdown content to the zip file
                                zip_file.writestr(filename, result["markdown_content"])
                    
                    # Create timestamp for the zip filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # Reset buffer position
                    zip_buffer.seek(0)
                
                # Display info and download button
                st.success(f"**{len(successful_evals)}** evaluation(s) ready for download.")
                
                # Use columns for better layout
                col1, col2, col3 = st.columns([2, 3, 2])
                with col2:
                    st.download_button(
                        label="📥 Download All Evaluations as ZIP",
                        data=zip_buffer,
                        file_name=f"evaluations_{timestamp}.zip",
                        mime="application/zip",
                        key="download_all_button",
                        use_container_width=True,
                    )
            
            st.markdown("---")
        
        # Display results using expanders
        for result in results_to_display:
            filename = result.get("filename", "Unknown File")
            header = f"📄 {filename}"
            
            recommendation = ""
            status = "" # Add status indicator
            if "markdown_content" in result:
                status = " - Status: Success"
                match = re.search(r"🏆\s*RECOMMENDATION:\s*([\w\s]+)", result["markdown_content"])
                if match:
                    recommendation = f" - Recommendation: {match.group(1).strip()}"
            elif "error" in result:
                status = " - Status: Error"
                
            with st.expander(f"{header}{status}{recommendation}", expanded= (len(results_to_display) == 1) ): 
                if "error" in result:
                    st.error(f"Evaluation Error for {filename}:")
                    # Show the raw error details directly
                    st.code(result.get("_raw_response", "No details available."), language='text')
                elif "markdown_content" in result:
                    markdown_content = result["markdown_content"]
                    download_info = {
                        "filename": f"{filename.split('.')[0]}_evaluation.md",
                        "text": "📥 Download Markdown"
                    }
                    # Display the markdown content with buttons (copy is non-functional)
                    show_markdown_content(markdown_content, download_info=download_info, with_copy=True)
                    
                    # Debug info specific to this result
                    with st.popover("Debug Info"):
                        st.markdown("**Raw API Response**")
                        st.code(result.get("_raw_response", "Not available."), language="text")
                else:
                     st.warning("No content available for this item.")

    # --- Navigation Actions --- 
    st.markdown("--- ")
    st.markdown("### Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Configuration", key="back_config_step3"):
            go_to_step(2)
            st.rerun()
    with col2:
        if st.button("Evaluate Another Resume/Batch", key="restart_step3"):
            reset_app()
            st.rerun() # Already has rerun but keeping for clarity

# Footer
show_footer()

# Add branding in the main content area instead of sidebar
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
    <p style="margin-bottom: 0; color: #666; font-size: 0.9rem;">
        This is an internal resume evaluation system that leverages AI to provide consistent assessments.
    </p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    # This will run when the script is executed directly
    pass 