"""
Utility functions for processing resumes
"""

import os
import json
import PyPDF2
import pdfplumber
from openai import OpenAI
from pathlib import Path

def extract_text_from_pdf_bytes(pdf_bytes):
    """Extract text from PDF bytes (for Streamlit file uploader)"""
    text = ""
    try:
        # Using PyPDF2
        pdf_reader = PyPDF2.PdfReader(pdf_bytes)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
            
        # If PyPDF2 extraction is poor, try pdfplumber as backup
        if len(text.strip()) < 100:  # Arbitrary threshold
            with pdfplumber.open(pdf_bytes) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                    
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {e}")

def extract_text_from_pdf_file(pdf_path):
    """Extract text from a PDF file path"""
    try:
        with open(pdf_path, 'rb') as file:
            return extract_text_from_pdf_bytes(file)
    except Exception as e:
        raise Exception(f"Error opening PDF file: {e}")

def evaluate_resume_with_ai(resume_text, system_prompt, user_prompt_template, model_name, api_key):
    """Evaluate the resume using OpenAI API"""
    client = OpenAI(api_key=api_key)
    
    # Format the user prompt with the resume text
    user_prompt = user_prompt_template.format(resume_text=resume_text)
    
    # Add JSON keyword if not present to ensure compatibility with response_format
    if "json" not in user_prompt.lower():
        user_prompt += "\n\nPlease format your response as JSON."
    
    # Also ensure system prompt mentions JSON
    if "json" not in system_prompt.lower():
        system_prompt += " Provide your evaluation in JSON format."
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise Exception(f"Error evaluating resume with AI: {e}")

def get_available_templates():
    """Get list of available templates from the configure directory"""
    templates = []
    
    # Default template
    templates.append({
        "name": "Standard AI/ML Evaluation",
        "description": "Evaluates technical skills, experience, and projects for AI/ML roles",
        "system_prompt": "configure/must_configure/system_prompt.txt",
        "user_prompt": "configure/must_configure/resume_prompt.txt"
    })
    
    # You can add custom template discovery logic here
    
    return templates

def read_prompt_file(file_path):
    """Read prompt from a file"""
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except Exception as e:
        raise Exception(f"Error reading prompt file {file_path}: {e}")

def get_available_models():
    """Get list of available OpenAI models"""
    return [
        {"name": "GPT-4.1-Turbo", "value": "gpt-4-turbo", "description": "Latest model with best performance"},
        {"name": "GPT-4o", "value": "gpt-4o", "description": "Balanced performance and speed"},
        {"name": "GPT-3.5 Turbo", "value": "gpt-3.5-turbo", "description": "Faster but less accurate"}
    ] 