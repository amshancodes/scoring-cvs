import os
import PyPDF2
import re
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def create_evaluation_template(candidate_name, current_role):
    """Create the evaluation template for a candidate."""
    template = f"""# {candidate_name} - {current_role}

## 🏆 RECOMMENDATION: [Reject/Consider/Strong Candidate]

### Stats

CV Filter Check
CV Scoring
Below is the detailed evaluation of the candidate against each flag criterion:

| **Flag ID** | **Category** | **Flag** | **Critical?** | **Score** | **Confirmation** |
| --- | --- | --- | --- | --- | --- |
| 1 | **AI/ML Experience & Engineering** | 2+ years in applied AI/ML with measurable results and strong coding/engineering skills | Critical | [0-2] | [Evidence from CV matching EXACTLY the validation criteria in Flag V3] |
| 2 | **LLM/NLP Specialization & Engineering** | 1+ years of LLM/NLP experience with demonstrable product impact and strong technical execution | Critical | [0-2] | [Evidence matching validation criteria] |
| 3 | **Production-Grade RAG Implementation** | Direct experience working on a production-grade RAG system as part of a successful product team | Critical | [0-2] | [Evidence specifically looking for "part of a team that delivered [Product Name] using RAG"] |
| 4 | **Startup Mentality & Hands-on Ownership** | Demonstrated ability to work in early-stage, fast-paced environments with a hands-on, product-focused mindset |  | [0-2] | [Evidence specifically looking for 2+ years startup experience or founding roles] |
| 5 | **STEM** | STEM degree in a good university |  | [0-2] | [Evidence checking if university is on Vlad's specific list] |
| 6 | Red Flags - negative points | Red flag - Can't contribute to current project | Critical |  |  |

### Summary Scores

- **Total Score:**
    - Sum of all positive flags: [calculation] = **[total]**
    - Sum of all negative flags: **[total]**
- **Critical Flag Score:**
    - Sum of positive critical flags: [calculation] = **[total]**
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
[Analysis of employment gaps and career progression]

### Additional Insights
[World class recruiter insights and implicit/explicit mentions]
"""
    return template

def process_resumes():
    """Process all resumes in the PDF-RESUMES directory."""
    pdf_dir = Path("PDF-RESUMES")
    evaluations_dir = Path("evaluations")
    evaluations_dir.mkdir(exist_ok=True)
    
    for pdf_file in pdf_dir.glob("*.pdf"):
        # Extract candidate name from filename
        filename = pdf_file.stem
        candidate_name = " ".join(filename.split("_")[:2])  # First two parts of filename
        
        # Create evaluation file
        eval_file = evaluations_dir / f"{candidate_name.replace(' ', '_')}_evaluation.md"
        
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_file)
        
        # Create evaluation template
        template = create_evaluation_template(candidate_name, "[Current Role]")
        
        # Write evaluation file
        with open(eval_file, 'w') as f:
            f.write(template)
            f.write("\n\n### Raw CV Text\n```\n")
            f.write(text)
            f.write("\n```")

if __name__ == "__main__":
    process_resumes() 