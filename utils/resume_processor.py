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
        user_prompt += "\n\nPlease format your response as JSON with the following structure:\n"
        user_prompt += """{
  "overall_impression": {
    "score": 7,
    "explanation": "Detailed explanation here"
  },
  "technical_skills": {
    "score": 8,
    "explanation": "Detailed explanation here"
  },
  "experience": {
    "score": 6,
    "explanation": "Detailed explanation here"
  },
  "education": {
    "score": 7,
    "explanation": "Detailed explanation here"
  },
  "projects": {
    "score": 8,
    "explanation": "Detailed explanation here"
  },
  "total_score": 36,
  "summary": "Overall assessment summary here"
}"""
    
    # Also ensure system prompt mentions JSON
    if "json" not in system_prompt.lower():
        system_prompt += " Provide your evaluation in JSON format with the exact structure requested in the user message."
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        # Make API request
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            response_format={"type": "json_object"}
        )
        
        # Parse the response content
        response_content = response.choices[0].message.content
        
        # Parse as JSON
        try:
            evaluation = json.loads(response_content)
            # Save the raw response for debugging
            evaluation['_raw_response'] = response_content
            return evaluation
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract JSON from text
            try:
                # Look for JSON between curly braces
                json_start = response_content.find('{')
                json_end = response_content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response_content[json_start:json_end]
                    evaluation = json.loads(json_str)
                    # Save the raw response for debugging
                    evaluation['_raw_response'] = response_content
                    return evaluation
                else:
                    # If we can't find JSON, return the raw response wrapped in a dict
                    return {
                        "raw_text": response_content,
                        "_raw_response": response_content
                    }
            except Exception as e:
                # If all attempts fail, return the raw text
                return {
                    "error": f"Failed to parse response as JSON: {e}",
                    "raw_text": response_content, 
                    "_raw_response": response_content
                }
    except Exception as e:
        # Wrap any API errors in a dict with explanation
        error_details = {
            "error": f"Error evaluating resume with AI: {e}",
            "_raw_response": str(e)
        }
        if hasattr(e, 'response'):
            error_details["response"] = str(e.response)
        if hasattr(e, 'status_code'):
            error_details["status_code"] = e.status_code
        
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