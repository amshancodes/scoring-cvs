import os
import re
from pathlib import Path
import markdown
from bs4 import BeautifulSoup
import pandas as pd
from collections import defaultdict

def extract_score_from_evaluation(file_path):
    """Extract scores and other key information from evaluation file."""
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
    
    # Extract green flag percentage
    percentage_match = re.search(r'Green Flag Percentage: (.*?)%', content)
    percentage = percentage_match.group(1) if percentage_match else "0"
    
    # Extract individual flag scores
    flag_scores = {}
    flag_pattern = re.compile(r'\| (\d+) \| \*\*(.*?)\*\* \| (.*?) \| (Critical)? \| (\d+) \|')
    for match in flag_pattern.finditer(content):
        flag_id = match.group(1)
        flag_score = match.group(5)
        flag_scores[f"Flag_{flag_id}"] = int(flag_score) if flag_score.isdigit() else 0
    
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
        "name": name,
        "role": role,
        "recommendation": recommendation,
        "total_score": float(total_score) if total_score.replace('.', '', 1).isdigit() else 0,
        "critical_score": float(critical_score) if critical_score.replace('.', '', 1).isdigit() else 0,
        "percentage": float(percentage) if percentage.replace('.', '', 1).isdigit() else 0,
        "flag_scores": flag_scores,
        "strengths": strengths,
        "improvements": improvements,
        "file_path": file_path
    }

def generate_summary():
    """Generate a comprehensive summary of all candidates."""
    evaluations_dir = Path("evaluations")
    candidates = []
    
    # Process all evaluation files
    for eval_file in evaluations_dir.glob("*_evaluation.md"):
        candidate_data = extract_score_from_evaluation(eval_file)
        candidates.append(candidate_data)
    
    # Sort candidates by total score (descending)
    candidates.sort(key=lambda x: (x["total_score"], x["critical_score"]), reverse=True)
    
    # Get top 10 candidates
    top_candidates = candidates[:10]
    
    # Calculate stats
    total_candidates = len(candidates)
    strong_candidates = sum(1 for c in candidates if c["recommendation"] == "Strong Candidate")
    consider_candidates = sum(1 for c in candidates if c["recommendation"] == "Consider")
    reject_candidates = sum(1 for c in candidates if c["recommendation"] == "Reject")
    
    # Calculate average scores
    avg_total = sum(c["total_score"] for c in candidates) / total_candidates if total_candidates > 0 else 0
    avg_critical = sum(c["critical_score"] for c in candidates) / total_candidates if total_candidates > 0 else 0
    
    # Analyze common strengths and areas for improvement
    all_strengths = defaultdict(int)
    all_improvements = defaultdict(int)
    
    for candidate in candidates:
        for strength in candidate["strengths"]:
            all_strengths[strength] += 1
        for improvement in candidate["improvements"]:
            all_improvements[improvement] += 1
    
    top_strengths = sorted(all_strengths.items(), key=lambda x: x[1], reverse=True)[:5]
    top_improvements = sorted(all_improvements.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Create summary markdown
    summary = f"""# Comprehensive Candidate Assessment for Applied AI Researcher Position

## 📊 Overall Statistics

- **Total Candidates Evaluated:** {total_candidates}
- **Strong Candidates:** {strong_candidates} ({strong_candidates/total_candidates*100:.1f}%)
- **Consider Candidates:** {consider_candidates} ({consider_candidates/total_candidates*100:.1f}%)
- **Reject Candidates:** {reject_candidates} ({reject_candidates/total_candidates*100:.1f}%)
- **Average Total Score:** {avg_total:.2f}/10
- **Average Critical Score:** {avg_critical:.2f}/6

## 🏆 Top 10 Candidates

| **Rank** | **Candidate** | **Current Role** | **Total Score** | **Critical Score** | **Recommendation** |
|----------|---------------|------------------|-----------------|-------------------|------------------|
"""
    
    # Add top candidates to table
    for i, candidate in enumerate(top_candidates, 1):
        summary += f"| {i} | {candidate['name']} | {candidate['role']} | {candidate['total_score']}/10 | {candidate['critical_score']}/6 | {candidate['recommendation']} |\n"
    
    # Add detailed analysis for top candidates
    summary += "\n## 🔍 Detailed Analysis of Top Candidates\n\n"
    
    for i, candidate in enumerate(top_candidates, 1):
        summary += f"### {i}. {candidate['name']} - {candidate['role']}\n\n"
        summary += f"**Recommendation:** {candidate['recommendation']}\n\n"
        summary += f"**Total Score:** {candidate['total_score']}/10\n\n"
        summary += f"**Critical Score:** {candidate['critical_score']}/6\n\n"
        
        # Add strengths
        summary += "**Key Strengths:**\n\n"
        for strength in candidate['strengths']:
            summary += f"- {strength}\n"
        
        # Add areas for improvement
        if candidate['improvements'] and candidate['improvements'][0] != "No significant areas for improvement identified based on the criteria":
            summary += "\n**Areas for Improvement:**\n\n"
            for improvement in candidate['improvements']:
                summary += f"- {improvement}\n"
        else:
            summary += "\n**Areas for Improvement:** None significant identified\n"
        
        summary += "\n"
    
    # Add common patterns section
    summary += "## 📈 Common Patterns Across Candidates\n\n"
    
    summary += "### Most Common Strengths\n\n"
    for strength, count in top_strengths:
        summary += f"- **{strength}** (found in {count} candidates)\n"
    
    summary += "\n### Most Common Areas for Improvement\n\n"
    for improvement, count in top_improvements:
        summary += f"- **{improvement}** (found in {count} candidates)\n"
    
    # Add recruiter insights
    summary += """
## 💡 Recruiter Insights

### Key Observations
- The strongest candidates demonstrate a combination of deep technical expertise in AI/ML and LLM/NLP technologies, along with practical experience implementing RAG systems.
- Candidates with startup experience tend to show more initiative and hands-on ownership in their past roles.
- The best candidates show clear evidence of delivering measurable business impact through their technical work.

### Hiring Recommendations
1. Focus interviews on practical implementation details of RAG systems for top candidates
2. Assess cultural fit and ability to work in fast-paced environments
3. Ask for specific examples of business outcomes from their technical work
4. Evaluate their approach to problem-solving and adaptability

### Assessment Methodology
- Each candidate was evaluated against Vlad's Flag V4 validation criteria
- Critical flags (AI/ML Experience, LLM/NLP Specialization, RAG Implementation) were weighted more heavily
- Additional consideration was given to candidates with a combination of technical depth and leadership experience
- Educational background was considered but placed less emphasis than practical experience
"""
    
    # Write summary to file
    summary_file = Path("candidate_assessment_summary.md")
    with open(summary_file, "w") as f:
        f.write(summary)
    
    print(f"Summary generated: {summary_file}")

if __name__ == "__main__":
    generate_summary() 