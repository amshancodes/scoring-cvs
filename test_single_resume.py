#!/usr/bin/env python3
"""
Test script to evaluate a single resume with detailed debugging
"""

import os
import json
import re
import time
from pathlib import Path
import PyPDF2
from openai import OpenAI

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def load_text_file(file_path):
    """Load text from a file."""
    with open(file_path, 'r') as f:
        return f.read().strip()

def test_single_resume():
    # Configuration
    pdf_path = "PDF-PROJECTS/new-batch/Profile (42).pdf"
    system_prompt_path = "configure/must_configure/system_prompt.txt"
    model_name = "gpt-4.1-2025-04-14"
    
    # Get OpenAI API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    # Load system prompt
    system_prompt = load_text_file(system_prompt_path)
    
    # Extract text from PDF
    print(f"Extracting text from {pdf_path}...")
    resume_text = extract_text_from_pdf(pdf_path)
    
    # Create user prompt directly
    user_prompt = """You are an expert AI/ML technical recruiter evaluating candidates for an Applied AI Researcher position.
    
Review this candidate resume and provide a detailed evaluation following these exact criteria:

# Flag Criteria Evaluation

## Flag 1: AI/ML Experience & Engineering (Critical)
- 0 points: Less than 2 years OR no measurable results OR weak coding/engineering
- 1 point: 2+ years, some results, adequate coding/engineering
- 2 points: 4+ years OR "Senior AI/ML Engineer" title OR promotion OR awards OR demonstrated leadership

## Flag 2: LLM/NLP Specialization & Engineering (Critical)
- 0 points: No LLM/NLP experience OR no product impact OR weak technical execution
- 1 point: 1+ year LLM/NLP, some product impact, adequate technical execution
- 2 points: 2+ years LLM/NLP OR significant product impact OR exceptional technical execution

## Flag 3: Production-Grade RAG Implementation (Critical)
- 0 points: No RAG experience OR no evidence of product team contribution
- 1 point: Some RAG experience, unclear product impact
- 2 points: Clear evidence of building production RAG system as part of successful product team

## Flag 4: Startup Mentality & Hands-on Ownership
- 0 points: No startup experience OR no evidence of hands-on, product-focused mindset
- 1 point: Some startup or agile team experience, some ownership demonstrated
- 2 points: 2+ years startup experience OR founding role OR strong evidence of ownership

## Flag 5: STEM Degree
- 0 points: No STEM degree OR unknown university quality
- 1 point: STEM degree from average university
- 2 points: STEM degree from top-tier university

## Flag 6: Red Flags (Negative points)
- Identify any major concerns that would prevent contribution to current project
- Examples: job-hopping, employment gaps, lack of relevant skills, etc.

Resume text:
""" + resume_text + """

Your output must be in valid JSON format. Return your evaluation as a JSON object with the following structure:

{
    "overall_impression": {
        "score": 0,
        "explanation": "Detailed explanation of overall impression"
    },
    "flag_scores": {
        "ai_ml_experience": {
            "score": 0,
            "explanation": "Detailed explanation with evidence from resume"
        },
        "llm_nlp_specialization": {
            "score": 0,
            "explanation": "Detailed explanation with evidence from resume"
        },
        "rag_implementation": {
            "score": 0,
            "explanation": "Detailed explanation with evidence from resume"
        },
        "startup_mentality": {
            "score": 0,
            "explanation": "Detailed explanation with evidence from resume"
        },
        "stem_degree": {
            "score": 0,
            "explanation": "Detailed explanation with evidence from resume"
        },
        "red_flags": {
            "score": 0,
            "explanation": "Detailed explanation of any red flags or concerns"
        }
    },
    "total_score": 0,
    "critical_score": 0,
    "strengths": [
        "Strength 1",
        "Strength 2",
        "Strength 3"
    ],
    "areas_for_improvement": [
        "Area 1",
        "Area 2",
        "Area 3"
    ],
    "summary": "A concise summary of the candidate's qualifications",
    "recommendation": "Reject/Consider/Strong Candidate"
}
"""
    
    # Print prompt information
    print(f"System prompt: {system_prompt[:100]}...")
    print(f"User prompt (first 100 chars): {user_prompt[:100]}...")
    print(f"User prompt contains 'json': {'json' in user_prompt.lower()}")
    print(f"System prompt contains 'json': {'json' in system_prompt.lower()}")
    
    # Initialize the OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Send request to OpenAI
    print(f"Sending request to OpenAI API with model {model_name}...")
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        max_tokens=4000,
        response_format={"type": "json_object"}
    )
    
    # Parse the response
    response_text = response.choices[0].message.content
    
    # Save the raw response
    with open("debug_response.txt", "w") as f:
        f.write(response_text)
    print(f"Response saved to debug_response.txt")
    
    # Try to parse JSON
    try:
        evaluation = json.loads(response_text)
        print("Successfully parsed JSON response")
        print(f"Recommendation: {evaluation.get('recommendation', 'Not found')}")
        return evaluation
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f"First 500 chars of response: {response_text[:500]}")
        return None

if __name__ == "__main__":
    test_single_resume() 