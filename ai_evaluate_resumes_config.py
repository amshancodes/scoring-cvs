#!/usr/bin/env python3
"""
Resume evaluation script that uses the configuration system to evaluate candidate resumes.
"""

import os
import json
import re
import time
from pathlib import Path
import PyPDF2
from openai import OpenAI
from collections import defaultdict

# Import the configuration loader
class ConfigLoader:
    """Load and manage configuration from the 'configure' directory."""
    
    def __init__(self, base_dir="configure"):
        self.base_dir = Path(base_dir)
        self.must_configure_dir = self.base_dir / "must_configure"
        self.nice_to_configure_dir = self.base_dir / "nice_to_configure"
        
        # Load main config
        self.config = self._load_json(self.must_configure_dir / "config.json")
        
        # Load model options if available
        try:
            model_options = self._load_json(self.nice_to_configure_dir / "model_options.json")
            self.model_options = model_options.get("model_options", {})
            self.default_model = model_options.get("default_model", "gpt-4-turbo")
        except Exception:
            self.model_options = {}
            self.default_model = "gpt-4-turbo"
        
        # Load output templates if available
        try:
            self.output_templates = self._load_json(self.nice_to_configure_dir / "output_templates.json")
        except Exception:
            self.output_templates = {}
    
    def _load_json(self, file_path):
        """Load a JSON file."""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def _load_text(self, file_path):
        """Load a text file."""
        with open(file_path, 'r') as f:
            return f.read().strip()
    
    def get_system_prompt(self):
        """Get the system prompt from the configuration."""
        try:
            return self._load_text(self.must_configure_dir / "system_prompt.txt")
        except Exception:
            return "You are an expert HR professional specializing in evaluating technical resumes."
    
    def get_user_prompt_template(self):
        """Get the user prompt template from the configuration."""
        try:
            return self._load_text(self.must_configure_dir / "resume_prompt.txt")
        except Exception:
            return "Please evaluate the following resume: {resume_text}"
    
    def get_model_config(self, model_name=None):
        """Get the configuration for a specific model."""
        if not model_name:
            model_name = self.config.get("model", self.default_model)
        
        return self.model_options.get(model_name, {})
    
    def get_output_format(self):
        """Get the output format from the configuration."""
        output_path = self.config.get("output_path", "evaluation.md")
        _, ext = os.path.splitext(output_path)
        
        if ext == ".md":
            return "markdown_template"
        elif ext == ".json":
            return "json_template"
        elif ext == ".csv":
            return "csv_template"
        else:
            return None
    
    def format_output(self, output_format, evaluation, candidate_name):
        """Format the evaluation output according to the template."""
        if output_format not in self.output_templates or not self.output_templates[output_format]:
            # Default format is just the raw evaluation
            return json.dumps(evaluation, indent=4)
        
        template = self.output_templates[output_format]
        
        # Add candidate name to evaluation dict
        evaluation_with_name = evaluation.copy()
        evaluation_with_name["candidate_name"] = candidate_name
        
        # Helper function to handle nested dictionary access with format strings
        def nested_format(template_str, data_dict):
            result = template_str
            
            # Find all format placeholders like {field} or {field[subfield]}
            placeholders = re.findall(r'\{([^}]+)\}', template_str)
            
            for placeholder in placeholders:
                # Handle nested dictionary access with square brackets like flag_scores[ai_ml_experience][score]
                if '[' in placeholder and ']' in placeholder:
                    parts = re.split(r'[\[\]]', placeholder)
                    parts = [p for p in parts if p]  # Remove empty strings
                    
                    # Navigate the nested dictionary
                    try:
                        value = data_dict
                        for part in parts:
                            if isinstance(value, dict) and part in value:
                                value = value[part]
                            elif isinstance(value, list) and part.isdigit() and int(part) < len(value):
                                value = value[int(part)]
                            else:
                                value = "N/A"  # Set a default value for missing keys
                                break
                        
                        # Replace the placeholder with the value
                        result = result.replace(f"{{{placeholder}}}", str(value))
                    except Exception as e:
                        print(f"Error accessing nested field {placeholder}: {e}")
                        result = result.replace(f"{{{placeholder}}}", "N/A")
                else:
                    # Handle simple fields
                    try:
                        value = data_dict.get(placeholder, "N/A")
                        result = result.replace(f"{{{placeholder}}}", str(value))
                    except Exception as e:
                        print(f"Error accessing field {placeholder}: {e}")
                        result = result.replace(f"{{{placeholder}}}", "N/A")
            
            return result
        
        # Format the output
        try:
            return nested_format(template, evaluation_with_name)
        except Exception as e:
            print(f"Error formatting output: {e}")
            return json.dumps(evaluation, indent=4)
    
    def get_output_path(self, candidate_name):
        """Get the output path for a candidate's evaluation."""
        output_format = self.config.get("output_path", "{name}_evaluation.md")
        return output_format.replace("{name}", candidate_name.replace(" ", "_"))
    
    def get_pdf_path(self, candidate_name=None):
        """Get the PDF path from the configuration."""
        if candidate_name:
            # If candidate name is provided, use it to construct the PDF path
            
            # Check if this is a Profile filename
            if candidate_name.lower().startswith("profile"):
                # For Profile filenames, just match exactly
                pdf_dir = Path("PDF-PROJECTS") / self.config.get("current_project", "")
                for pdf_file in pdf_dir.glob("*.pdf"):
                    if candidate_name == pdf_file.stem:
                        return str(pdf_file)
            else:
                # For standard names, match by name parts (e.g., first_last)
                pdf_dir = Path("PDF-RESUMES")
                for pdf_file in pdf_dir.glob("*.pdf"):
                    if candidate_name.lower().replace(" ", "_") in pdf_file.stem.lower():
                        return str(pdf_file)
        
        # Otherwise return the path from config
        return self.config.get("pdf_path", "")

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def get_current_role(text):
    """Extract the current role from resume text."""
    # Try to find patterns like "Role at Company" or similar job titles
    role_patterns = [
        r"([A-Za-z\s]+) at ([A-Za-z\s]+)",
        r"([A-Za-z\s]+), ([A-Za-z\s]+)",
        r"Current Role:?\s*([A-Za-z\s&]+)",
        r"Title:?\s*([A-Za-z\s&]+)",
        r"Position:?\s*([A-Za-z\s&]+)"
    ]
    
    for pattern in role_patterns:
        match = re.search(pattern, text[:500])  # Look only in the first part of the resume
        if match:
            return match.group(1).strip()
    
    # Default if no role found
    return "Unknown Role"

def evaluate_resume_with_ai(resume_text, candidate_name, config_loader):
    """Use OpenAI to evaluate the resume using the provided configuration."""
    # Get OpenAI API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return None
    
    # Initialize the OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Get system prompt from config
    system_prompt = config_loader.get_system_prompt()
    
    # Get user prompt from config
    try:
        user_prompt_template = config_loader.get_user_prompt_template()
        user_prompt = user_prompt_template.format(resume_text=resume_text)
        print("Using prompt template from config file")
    except Exception as e:
        print(f"Error loading prompt template: {e}")
        print("Using default prompt")
        user_prompt = f"Please evaluate this resume: {resume_text}"
    
    # Get model config
    model_name = config_loader.config.get("model", "gpt-4-turbo")
    model_config = config_loader.get_model_config(model_name)
    
    # Set defaults if not in config
    temperature = model_config.get("temperature", 0.2)
    max_tokens = model_config.get("max_tokens", 4000)
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt+1}: Sending request to OpenAI API...")
            
            # Check if we need JSON response format or not
            if "json" in user_prompt.lower() or "json" in system_prompt.lower():
                print("Using JSON response format")
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"}
                )
            else:
                # Use standard text response for Markdown
                print("Using standard text response format")
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            
            # Get the response text
            response_text = response.choices[0].message.content
            
            # Debug the response
            print(f"Debug - Raw response first 100 chars: {response_text[:100]}...")
            
            # Save raw response to debug directory
            debug_dir = Path("debug")
            debug_dir.mkdir(exist_ok=True)
            debug_file = debug_dir / f"{candidate_name.replace(' ', '_')}_response.txt"
            with open(debug_file, 'w') as f:
                f.write(response_text)
            
            # Simply return the raw response text - no parsing needed
            return response_text
            
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Error: {e}. Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print(f"Failed after {max_retries} attempts: {e}")
                return f"Error: {e}"

def process_single_resume(candidate_name, config_loader, evaluations_dir=None):
    """Process a single resume."""
    # Check if we should output to project folder
    output_in_project = config_loader.config.get("output_in_project_folder", False)
    projects_folder = config_loader.config.get("projects_folder", "PDF-PROJECTS")
    current_project = config_loader.config.get("current_project", "")
    
    # Set up output directory
    if output_in_project and current_project:
        # Use project folder for output
        project_dir = Path(projects_folder) / current_project
        project_dir.mkdir(exist_ok=True, parents=True)
        evaluations_dir = project_dir
        print(f"Using project folder for output: {evaluations_dir}")
    elif evaluations_dir is None:
        # Use default evaluations folder
        evaluations_dir = Path("evaluations")
        evaluations_dir.mkdir(exist_ok=True)
    
    # Get PDF path for this candidate - first try in project folder
    pdf_path = None
    if current_project:
        project_pdf_dir = Path(projects_folder) / current_project
        for pdf_file in project_pdf_dir.glob("*.pdf"):
            if candidate_name.lower().replace(" ", "_") in pdf_file.stem.lower():
                pdf_path = str(pdf_file)
                break
    
    # If not found in project folder, try the default path
    if not pdf_path:
        pdf_path = config_loader.get_pdf_path(candidate_name)
    
    if not pdf_path or not os.path.exists(pdf_path):
        print(f"Error: PDF file not found for {candidate_name}")
        return False
    
    # Extract text from PDF
    print(f"Extracting text from {pdf_path}...")
    resume_text = extract_text_from_pdf(pdf_path)
    
    # Get AI evaluation
    print(f"Evaluating resume for {candidate_name}...")
    try:
        # Get evaluation as raw text (markdown)
        evaluation_text = evaluate_resume_with_ai(resume_text, candidate_name, config_loader)
        
        # Define output path
        output_path = evaluations_dir / f"{candidate_name.replace(' ', '_')}_evaluation.md"
        
        # Write the markdown evaluation directly to the file
        with open(output_path, 'w') as f:
            f.write(evaluation_text)
        
        print(f"Completed evaluation for {candidate_name}")
        print(f"Output saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error processing {candidate_name}: {e}")
        return False

def process_resumes(test_mode=False, limit=None):
    """Process resumes using the configuration system."""
    # Initialize the config loader
    config_loader = ConfigLoader()
    
    # Get project configuration
    projects_folder = config_loader.config.get("projects_folder", "PDF-PROJECTS")
    current_project = config_loader.config.get("current_project", "")
    
    # Setup directories
    pdf_dir = None
    if current_project:
        # Use project folder for PDFs
        pdf_dir = Path(projects_folder) / current_project
        if not pdf_dir.exists():
            pdf_dir.mkdir(exist_ok=True, parents=True)
            print(f"Created project directory: {pdf_dir}")
        print(f"Using project folder for PDFs: {pdf_dir}")
    else:
        # Use default PDF directory
        pdf_dir = Path("PDF-RESUMES")
    
    evaluations_dir = Path("evaluations")
    evaluations_dir.mkdir(exist_ok=True)
    
    # Get the list of PDF files
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {pdf_dir}")
        return 0
    
    # In test mode, only process a few resumes
    if test_mode:
        if limit and limit > 0:
            pdf_files = pdf_files[:limit]
        else:
            pdf_files = pdf_files[:3]  # Default to 3 files in test mode
    
    total_resumes = len(pdf_files)
    processed_count = 0
    success_count = 0
    
    print(f"Found {total_resumes} resumes to process")
    
    for pdf_file in pdf_files:
        # Extract candidate name from filename
        filename = pdf_file.stem
        
        # Handle generic profile filenames
        if filename.lower().startswith("profile"):
            # Use filename as candidate name
            candidate_name = filename  # Example: "Profile (42)"
            print(f"Using filename as candidate name: {candidate_name}")
        # Original name extraction for FirstName_LastName format
        elif "_" in filename:
            candidate_name = " ".join(filename.split("_")[:2])  # First two parts of filename
        else:
            print(f"Skipping {filename}: cannot determine candidate name")
            continue
            
        # Check if output already exists
        if config_loader.config.get("output_in_project_folder", False) and current_project:
            # Check in project folder
            project_dir = Path(projects_folder) / current_project
            eval_file = project_dir / f"{candidate_name.replace(' ', '_')}_evaluation.md"
        else:
            # Check in evaluations folder
            eval_file = evaluations_dir / f"{candidate_name.replace(' ', '_')}_evaluation.md"
        
        if eval_file.exists() and not test_mode:
            print(f"Evaluation already exists for {candidate_name}, skipping...")
            processed_count += 1
            continue
        
        # Process the resume
        if process_single_resume(candidate_name, config_loader):
            success_count += 1
        
        processed_count += 1
        print(f"Progress: {processed_count}/{total_resumes}")
        
        # Sleep to prevent API rate limiting
        time.sleep(1)
    
    print(f"Completed {success_count}/{processed_count} evaluations.")
    return success_count

if __name__ == "__main__":
    # Process all resumes
    process_resumes(test_mode=False) 