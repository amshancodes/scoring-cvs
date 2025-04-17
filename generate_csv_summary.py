import os
import re
import csv
from pathlib import Path

def extract_info_from_evaluation(file_path):
    """Extract key information from an evaluation file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract candidate name and role
    name_role_match = re.search(r'# (.*?) - (.*?)\n', content)
    name = name_role_match.group(1) if name_role_match else "Unknown"
    role = name_role_match.group(2) if name_role_match else "Unknown"
    
    # Extract recommendation
    recommendation_match = re.search(r'## 🏆 RECOMMENDATION: (.*?)\n', content)
    recommendation = recommendation_match.group(1) if recommendation_match else "Unknown"
    
    # Extract total score
    total_score_match = re.search(r'Sum of all positive flags: (.*?) = \*\*(.*?)\*\*', content)
    total_score = total_score_match.group(2) if total_score_match else "0"
    
    # Extract critical flag score
    critical_score_match = re.search(r'Sum of positive critical flags: (.*?) = \*\*(.*?)\*\*', content)
    critical_score = critical_score_match.group(2) if critical_score_match else "0"
    
    # Extract individual flag scores
    flag_scores = {}
    flag_pattern = re.compile(r'\| (\d+) \| \*\*(.*?)\*\* \| (.*?) \| (Critical)? \| ([-\d]+) \| (.*?) \|')
    for match in flag_pattern.finditer(content):
        flag_id = match.group(1)
        flag_score = match.group(5)
        confirmation = match.group(6).strip()
        flag_scores[f"Flag_{flag_id}"] = {
            "score": int(flag_score) if flag_score.lstrip('-').isdigit() else 0,
            "confirmation": confirmation
        }
    
    # Extract LinkedIn URL if available
    linkedin_match = re.search(r'https?://(?:www\.)?linkedin\.com/\S+', content)
    linkedin_url = linkedin_match.group(0) if linkedin_match else ""
    
    # Extract strengths
    strengths = []
    strength_pattern = re.compile(r'- 💪 (.*?)\n')
    for match in strength_pattern.finditer(content):
        strengths.append(match.group(1))
    
    # Extract areas for improvement
    improvements = []
    improvement_pattern = re.compile(r'- [⚠️🔍] (.*?)\n')
    for match in improvement_pattern.finditer(content):
        improvements.append(match.group(1))
    
    return {
        "Name": name,
        "Current Role": role,
        "Recommendation": recommendation,
        "Total Score": float(total_score) if total_score.replace('.', '', 1).isdigit() else 0,
        "Critical Score": float(critical_score) if critical_score.replace('.', '', 1).isdigit() else 0,
        "LinkedIn URL": linkedin_url,
        "AI/ML Score": flag_scores.get("Flag_1", {}).get("score", 0),
        "LLM/NLP Score": flag_scores.get("Flag_2", {}).get("score", 0),
        "RAG Score": flag_scores.get("Flag_3", {}).get("score", 0),
        "Startup Score": flag_scores.get("Flag_4", {}).get("score", 0),
        "STEM Score": flag_scores.get("Flag_5", {}).get("score", 0),
        "Red Flags": flag_scores.get("Flag_6", {}).get("score", 0),
        "Key Strengths": "; ".join(strengths[:2]) if strengths else "",
        "Areas for Improvement": "; ".join(improvements[:2]) if improvements else ""
    }

def generate_csv_summary():
    """Generate a CSV summary of all candidate evaluations."""
    evaluations_dir = Path("evaluations")
    candidates = []
    
    # Process all evaluation files
    for eval_file in evaluations_dir.glob("*_evaluation.md"):
        try:
            candidate_data = extract_info_from_evaluation(eval_file)
            candidates.append(candidate_data)
        except Exception as e:
            print(f"Error processing {eval_file}: {e}")
    
    # Sort candidates by total score (descending)
    candidates.sort(key=lambda x: x["Total Score"], reverse=True)
    
    # Define CSV file path
    csv_file = Path("candidate_summary.csv")
    
    # Define CSV headers
    headers = [
        "Name", "Current Role", "Recommendation", "Total Score", "Critical Score",
        "LinkedIn URL", "AI/ML Score", "LLM/NLP Score", "RAG Score", 
        "Startup Score", "STEM Score", "Red Flags", "Key Strengths", "Areas for Improvement"
    ]
    
    # Write to CSV
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(candidates)
    
    print(f"CSV summary generated: {csv_file}")
    return csv_file

if __name__ == "__main__":
    generate_csv_summary() 