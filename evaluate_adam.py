#!/usr/bin/env python3
"""
Standalone evaluation script for Adam Jinnah's resume
"""

import os
import json
import re
import time
from pathlib import Path
import PyPDF2
from openai import OpenAI
from collections import defaultdict

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

def read_prompt_file(file_path):
    """Read prompt from a file."""
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except Exception as e:
        print(f"Error reading prompt file {file_path}: {e}")
        return None

def evaluate_resume_with_ai(resume_text, api_key):
    """Evaluate the resume using OpenAI API."""
    client = OpenAI(api_key=api_key)
    
    # Read system prompt from file
    system_prompt = read_prompt_file("system_prompt.txt")
    if not system_prompt:
        system_prompt = "You are an expert HR professional specializing in evaluating technical resumes for software development positions."
        print("Using default system prompt")
    
    # Read user prompt from file
    user_prompt_template = read_prompt_file("resume_prompt.txt")
    if not user_prompt_template:
        print("User prompt file not found, using default prompt")
        user_prompt_template = """
        Please evaluate the following resume for Adam Jinnah based on these criteria:
        1. Overall impression (score out of 10)
        2. Technical skills relevance to software development (score out of 10)
        3. Experience quality and relevance (score out of 10)
        4. Education background (score out of 10)
        5. Project complexity and impressiveness (score out of 10)
        
        Resume text:
        {resume_text}
        
        Format your response as a JSON with the following structure:
        {{
            "overall_impression": {{
                "score": X,
                "explanation": "detailed explanation"
            }},
            "technical_skills": {{
                "score": X,
                "explanation": "detailed explanation"
            }},
            "experience": {{
                "score": X,
                "explanation": "detailed explanation"
            }},
            "education": {{
                "score": X,
                "explanation": "detailed explanation"
            }},
            "projects": {{
                "score": X,
                "explanation": "detailed explanation"
            }},
            "total_score": X,
            "summary": "A brief summary of the candidate's strengths and weaknesses"
        }}
        """
    
    # Format the user prompt with the resume text
    user_prompt = user_prompt_template.format(resume_text=resume_text)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error evaluating resume with AI: {e}")
        return None

def main():
    # Set up paths
    pdf_path = "PDF-RESUMES/Adam_Jinnah_JuiceboxExport_2025-04-16_10.pdf"
    output_path = "Adam_Jinnah_evaluation.json"
    
    # Check if the PDF file exists
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return
    
    # Get OpenAI API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    # Extract text from PDF
    print(f"Extracting text from {pdf_path}...")
    resume_text = extract_text_from_pdf(pdf_path)
    if not resume_text:
        print("Failed to extract text from the PDF")
        return
    
    # Evaluate the resume
    print("Evaluating resume with AI...")
    evaluation = evaluate_resume_with_ai(resume_text, api_key)
    if not evaluation:
        print("Failed to evaluate the resume")
        return
    
    # Save the evaluation to a file
    with open(output_path, 'w') as file:
        json.dump(evaluation, file, indent=4)
    
    print(f"Evaluation complete and saved to {output_path}")
    
    # Print a summary of the evaluation
    print("\nEvaluation Summary:")
    print(f"Overall Impression: {evaluation['overall_impression']['score']}/10")
    print(f"Technical Skills: {evaluation['technical_skills']['score']}/10")
    print(f"Experience: {evaluation['experience']['score']}/10")
    print(f"Education: {evaluation['education']['score']}/10")
    print(f"Projects: {evaluation['projects']['score']}/10")
    print(f"Total Score: {evaluation['total_score']}/50")
    print(f"\nSummary: {evaluation['summary']}")

if __name__ == "__main__":
    main() 