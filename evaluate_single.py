#!/usr/bin/env python3
"""
Single Resume Evaluation Script
Evaluates a single resume using the same AI evaluation as the batch script
"""

import os
from pathlib import Path
import sys
sys.path.append('scripts')  # Add scripts directory to path

# Import functions from our main script
from evaluate_resumes import extract_text_from_pdf, evaluate_resume_with_ai

# Set up file paths
pdf_file = Path("PDF-RESUMES/Adam_Jinnah_JuiceboxExport_2025-04-16_10.pdf")
candidate_name = "Adam Jinnah"
output_file = Path(f"{candidate_name.replace(' ', '_')}_evaluation.md")

# Extract text from PDF
print(f"Extracting text from {pdf_file}...")
text = extract_text_from_pdf(pdf_file)

# Check if OpenAI API key is set
if not os.environ.get("OPENAI_API_KEY"):
    print("Error: OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    exit(1)

# Get AI evaluation
print(f"Evaluating {candidate_name}'s resume...")
try:
    evaluation = evaluate_resume_with_ai(text, candidate_name)
    
    # Write evaluation to file
    with open(output_file, 'w') as f:
        f.write(evaluation)
    
    # Also print to console
    print("\n" + "="*50)
    print(evaluation)
    print("="*50 + "\n")
    
    print(f"Evaluation complete! Results saved to {output_file}")
except Exception as e:
    print(f"Error processing {candidate_name}: {e}") 