import os
import json
import re
import time
from pathlib import Path
import PyPDF2
import openai
from collections import defaultdict

# OpenAI API setup
# Replace with your API key or set environment variable
# openai.api_key = "your-api-key-here"
openai.api_key = os.environ.get("OPENAI_API_KEY")

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

def evaluate_resume_with_ai(resume_text, candidate_name):
    """Use OpenAI to evaluate the resume against Vlad's criteria."""
    
    prompt = f"""You are an expert AI/ML technical recruiter evaluating candidates for an Applied AI Researcher position.
    
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

Please evaluate the following candidate:
Name: {candidate_name}

Resume:
{resume_text}

Output your evaluation in this exact format:

# [Candidate Name] - [Current Role]

## 🏆 RECOMMENDATION: [Reject/Consider/Strong Candidate]

### Stats

CV Filter Check: [PASS/FAIL]
CV Scoring: [X]/10

Below is the detailed evaluation of the candidate against each flag criterion:

| **Flag ID** | **Category** | **Flag** | **Critical?** | **Score** | **Confirmation** |
| --- | --- | --- | --- | --- | --- |
| 1 | **AI/ML Experience & Engineering** | 2+ years in applied AI/ML with measurable results and strong coding/engineering skills | Critical | [0-2] | [Specific evidence from CV] |
| 2 | **LLM/NLP Specialization & Engineering** | 1+ years of LLM/NLP experience with demonstrable product impact and strong technical execution | Critical | [0-2] | [Specific evidence from CV] |
| 3 | **Production-Grade RAG Implementation** | Direct experience working on a production-grade RAG system as part of a successful product team | Critical | [0-2] | [Specific evidence from CV] |
| 4 | **Startup Mentality & Hands-on Ownership** | Demonstrated ability to work in early-stage, fast-paced environments with a hands-on, product-focused mindset |  | [0-2] | [Specific evidence from CV] |
| 5 | **STEM** | STEM degree in a good university |  | [0-2] | [Specific evidence from CV] |
| 6 | Red Flags - negative points | Red flag - Can't contribute to current project | Critical | [-2-0] | [Specific concerns if any] |

### Summary Scores

- **Total Score:**
    - Sum of all positive flags: [X+Y+Z...] = **[total]**
    - Sum of all negative flags: **[total]**
- **Critical Flag Score:**
    - Sum of positive critical flags: [X+Y+Z] = **[total]**
    - Sum of negative critical flags: **[total]**
- **Green Flag Percentage:** [total positive/10 x 100]% ([total positive]/10 possible points)

### Strengths (Positive Flags) ✅

- 💪 [Strength 1 based on highest scores]
- 💪 [Strength 2]
- 💪 [Strength 3]

### Areas for Improvement (Negative Flags) 📝

- ⚠️ [Concern 1 based on lowest scores or gaps]
- 🔍 [Concern 2]
- ⚠️ [Concern 3 if applicable]

### Employment History Analysis
[Detailed analysis of employment gaps and career progression]

### Additional Insights
[World-class recruiter insights, both explicit and implicit observations]

Be extremely strict and thorough in your evaluation. For the recommendation, use these guidelines:
- Reject: Score < 6 OR any Critical Flag = 0
- Consider: Score 6-7 OR Critical Score 4-5
- Strong Candidate: Score 8+ AND Critical Score 6
"""
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = openai.chat.completions.create(
                model="gpt-4",  # Use GPT-4 for best results
                messages=[
                    {"role": "system", "content": "You are a world-class technical recruiter with expertise in AI/ML hiring."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Lower temperature for more consistent responses
                max_tokens=2500,  # Ensure we get a complete response
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Error: {e}. Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print(f"Failed after {max_retries} attempts: {e}")
                raise

def process_resumes():
    """Process all resumes in the PDF-RESUMES directory."""
    pdf_dir = Path("PDF-RESUMES")
    evaluations_dir = Path("evaluations")
    evaluations_dir.mkdir(exist_ok=True)
    
    # Process a limited number of resumes for testing
    # Remove this limit for processing all resumes
    processed_count = 0
    total_resumes = len(list(pdf_dir.glob("*.pdf")))
    
    print(f"Found {total_resumes} resumes to process")
    
    for pdf_file in pdf_dir.glob("*.pdf"):
        # Extract candidate name from filename
        filename = pdf_file.stem
        print(f"Processing {filename}...")
        
        # Skip if we already have an evaluation for this candidate
        candidate_name = " ".join(filename.split("_")[:2])  # First two parts of filename
        eval_file = evaluations_dir / f"{candidate_name.replace(' ', '_')}_evaluation.md"
        
        if eval_file.exists():
            print(f"Evaluation already exists for {candidate_name}, skipping...")
            processed_count += 1
            continue
        
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_file)
        
        # Get AI evaluation
        try:
            evaluation = evaluate_resume_with_ai(text, candidate_name)
            
            # Write evaluation file
            with open(eval_file, 'w') as f:
                f.write(evaluation)
            
            print(f"Completed evaluation for {candidate_name}")
            processed_count += 1
            print(f"Progress: {processed_count}/{total_resumes}")
            
            # Sleep to prevent API rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"Error processing {candidate_name}: {e}")
    
    print(f"Completed {processed_count} evaluations.")
    return processed_count

def generate_summary():
    """Generate a comprehensive summary of all candidates."""
    from collections import defaultdict
    
    evaluations_dir = Path("evaluations")
    candidates = []
    
    # Process all evaluation files
    for eval_file in evaluations_dir.glob("*_evaluation.md"):
        try:
            with open(eval_file, 'r') as f:
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
            flag_pattern = re.compile(r'\| (\d+) \| \*\*(.*?)\*\* \| (.*?) \| (Critical)? \| ([-\d]+) \|')
            for match in flag_pattern.finditer(content):
                flag_id = match.group(1)
                flag_score = match.group(5)
                flag_scores[f"Flag_{flag_id}"] = int(flag_score) if flag_score.lstrip('-').isdigit() else 0
            
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
            
            candidates.append({
                "name": name,
                "role": role,
                "recommendation": recommendation,
                "total_score": float(total_score) if total_score.replace('.', '', 1).isdigit() else 0,
                "critical_score": float(critical_score) if critical_score.replace('.', '', 1).isdigit() else 0,
                "percentage": float(percentage) if percentage.replace('.', '', 1).isdigit() else 0,
                "flag_scores": flag_scores,
                "strengths": strengths,
                "improvements": improvements,
                "file_path": str(eval_file)
            })
        except Exception as e:
            print(f"Error parsing {eval_file}: {e}")
    
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
- **Strong Candidates:** {strong_candidates} ({strong_candidates/total_candidates*100:.1f}% of pool)
- **Consider Candidates:** {consider_candidates} ({consider_candidates/total_candidates*100:.1f}% of pool)
- **Reject Candidates:** {reject_candidates} ({reject_candidates/total_candidates*100:.1f}% of pool)
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
    return summary_file

if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not openai.api_key:
        print("Error: OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        exit(1)
    
    print("Starting resume evaluation process...")
    processed = process_resumes()
    
    if processed > 0:
        print("Generating summary report...")
        summary_file = generate_summary()
        print(f"Process complete! Summary available at: {summary_file}")
    else:
        print("No resumes were processed. Exiting.") 