# Candidate Evaluation Tool - User Guide

This guide provides detailed instructions for using the Candidate Evaluation Tool, an internal application for evaluating candidate resumes with AI assistance.

## Getting Started

### Accessing the Tool

**Online (Preferred Method):**
- Visit the Streamlit Cloud deployment at `https://your-app-name.streamlit.app/`
- Enter password: `demo123` when prompted

**Locally:**
1. Install dependencies: `pip install -r requirements.txt`
2. Set your API key: `export OPENAI_API_KEY="your-api-key-here"`
3. Run the app: `streamlit run app.py`

## Step-by-Step Usage Guide

### Step 1: Resume Input

You have three options for submitting resumes:

#### Option A: Upload PDF Files (Recommended for Batch Processing)
1. Select the "Upload PDF(s)" tab
2. Click "Browse files" or drag and drop PDF files
3. You can select multiple files for batch processing
4. Wait for confirmation that files were successfully queued
5. Click "Next: Configure Evaluation"

#### Option B: Paste Resume Text
1. Select the "Paste Text" tab
2. Copy and paste the resume text into the text area
3. Click "Use this text"
4. Click "Next: Configure Evaluation"

#### Option C: Use Sample Resume
1. Select the "Sample Resume" tab
2. Click "Load Sample Resume"
3. Click "Next: Configure Evaluation"

### Step 2: Configure Evaluation

1. Review the available evaluation templates
2. Click "Select" on your preferred template (default is recommended for most cases)

#### Advanced: Customizing Prompts
1. Click "Advanced Options" to expand
2. Check "Edit evaluation prompts"
3. Modify the system prompt and/or user prompt as needed
4. **IMPORTANT**: Keep the `{resume_text}` placeholder in the user prompt
5. Click "Save Custom Prompts" to apply changes
6. Click "Start Evaluation" to proceed

### Step 3: Evaluation Process

1. Wait while the system processes the resume(s)
2. You'll see progress indicators showing:
   - Phase 1: Preparing resume content for analysis
   - Phase 2: Analyzing candidate qualifications and experience
   - Phase 3: Generating comprehensive evaluation report
3. When complete, the results will be displayed below

### Reviewing Results

For individual resumees:
- Each evaluation is displayed in an expandable section
- Click on a resume name to view its detailed evaluation
- Use the "Download Markdown" button to save individual evaluations

For batch processing:
1. Look for the "Batch Download" section at the top of results
2. Click "Download All Evaluations as ZIP" to get all results at once
3. The ZIP file will contain all successful evaluations as separate markdown files

## Understanding Evaluation Results

Each evaluation includes:

- **Overall Recommendation**: Whether to hire/interview/reject
- **Technical Skills Assessment**: Evaluation of candidate's technical abilities
- **Experience Analysis**: Review of relevant work history
- **Education Review**: Assessment of academic background
- **Projects Evaluation**: Analysis of highlighted projects
- **Strengths & Weaknesses**: Summary of candidate's advantages and limitations

## Tips for Best Results

1. **Use PDF Format**: For most consistent results, submit resumes in PDF format
2. **Batch Processing**: Upload multiple resumes at once for efficiency
3. **Custom Prompts**: Adjust evaluation criteria for specific roles when needed
4. **Multiple Sessions**: Use "Evaluate Another Resume/Batch" to start fresh

## Providing Feedback

Please report any issues or suggestions to amshan@tryhire.co, including:
- Problems with the evaluation quality
- Technical bugs or UI issues
- Feature requests for future improvements

## FAQ

**Q: Why doesn't my PDF extract correctly?**
A: Some PDF formats may not extract well. Try converting to a standard PDF format or paste the text directly.

**Q: Can I use the evaluation results outside of Hire AI?**
A: The tool is for internal use only. Evaluations should not be shared externally.

**Q: Does the tool store my resume data?**
A: Uploaded resumes are not permanently stored. They're only used for the current evaluation session.

**Q: What model is used for evaluation?**
A: By default, the tool uses GPT-4, OpenAI's most capable model for comprehensive evaluations. 