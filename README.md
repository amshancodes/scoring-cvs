# Candidate Evaluation Tool - v1.0

An internal AI-powered system for evaluating candidate resumes using OpenAI's GPT models, available both as a command-line tool and a Streamlit web application.

## Features

- **Dual Interface**: Run as CLI tool or interactive Streamlit web app
- **Project-Based Organization**: Organize evaluations by projects/batches
- **Configurable Templates**: Customize evaluation criteria and prompts
- **Direct Markdown Output**: Beautiful, detailed evaluation reports
- **Custom Prompts**: Edit evaluation criteria on-the-fly in the web interface
- **Bulk Upload Processing**: Evaluate multiple resumes in a single batch
- **Batch Download**: Download all evaluations as a ZIP file with one click
- **OpenAI Integration**: Works with GPT-4 and other advanced models
- **Cloud Deployment**: Hosted on Streamlit Cloud for team access
- **Visual Evaluation Process**: Clear indicators showing analysis phases
- **Responsive UI**: Immediate feedback on button clicks with no double-clicking required

## Directory Structure

```
scoring-cvs/
├── configure/                    # Configuration directory
│   ├── must_configure/           # Essential configurations
│   │   ├── config.json           # Main configuration
│   │   ├── resume_prompt.txt     # Resume evaluation prompt
│   │   └── system_prompt.txt     # System instruction prompt
│   └── nice_to_configure/        # Optional configurations
│       ├── model_options.json    # AI model parameters
│       └── output_templates.json # Output formatting templates
├── PDF-PROJECTS/                 # Project-based organization
│   └── new-batch/                # Example project
│       ├── Profile (42).pdf      # Resume PDF
│       └── Profile_(42)_evaluation.md  # Generated evaluation
├── PDF-RESUMES/                  # Legacy directory for PDFs
├── utils/                        # Utility functions
│   ├── resume_processor.py       # PDF processing and evaluation
│   └── ui_components.py          # Streamlit UI components
├── app.py                        # Streamlit web application
├── ai_evaluate_resumes_config.py # CLI batch evaluation script
└── evaluate_adam.py              # CLI single resume evaluation
```

## Command-Line Usage

### Setup

1. **Configure your environment**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. **Update configuration files**:
   - Edit `configure/must_configure/config.json` to set parameters
   - Customize prompts in `system_prompt.txt` and `resume_prompt.txt`

3. **Create a project folder and add PDFs**:
   ```bash
   mkdir -p PDF-PROJECTS/my-new-batch
   cp my-resumes/*.pdf PDF-PROJECTS/my-new-batch/
   ```

4. **Run the evaluation script**:
   ```bash
   # For batch processing
   python3 ai_evaluate_resumes_config.py
   
   # For single resume
   python3 evaluate_adam.py
   ```

## Streamlit Web Application

### Running Locally

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set API Key:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Run Streamlit:**
   ```bash
   # If streamlit isn't in your PATH, add it
   export PATH=$PATH:$HOME/Library/Python/3.9/bin
   
   # Start the app
   streamlit run app.py
   ```

### Cloud Deployment

The application is also deployed on Streamlit Cloud for team access. Visit:
https://your-app-name.streamlit.app/

Authentication is required to access the app (password: demo123).

### Streamlit App Features

- **Multiple Input Methods**: Upload PDFs, paste text, or use sample resumes
- **Bulk Processing**: Upload and evaluate multiple PDFs in one session
- **Template Selection**: Choose from different evaluation templates
- **Custom Prompts**: Edit system and user prompts directly in the UI
- **Real-time Feedback**: View evaluation progress and results immediately
- **Downloadable Results**: Save evaluations as Markdown files or ZIP
- **User-Friendly Interface**: Intuitive design with expandable sections
- **Status Indicators**: Clear feedback on evaluation success/errors
- **Recommendations**: Automatically highlighted hiring recommendations
- **Phase Visualization**: Shows each phase of the evaluation process
- **One-Click Navigation**: Responsive buttons without double-clicking required

## Configuration

### Custom Prompts in Web Interface

The Streamlit app allows editing evaluation prompts on-the-fly:

1. Go to the "Configure Evaluation" step
2. Click on "Advanced Options"
3. Check "Edit evaluation prompts"
4. Modify the system and user prompts as needed
5. **IMPORTANT**: Keep the `{resume_text}` placeholder in the user prompt
6. Click "Save Custom Prompts"

The custom prompts will be used for the current evaluation session.

### System Prompt

The system prompt sets the overall context for the AI. Edit `system_prompt.txt` to modify the AI's perspective and approach.

### Resume Prompt Template

The resume prompt template (`resume_prompt.txt`) defines the evaluation criteria and formatting. It uses a template with `{resume_text}` placeholder that will be replaced with actual resume content.

## Output

Evaluations are generated as Markdown files with detailed scoring, strengths, weaknesses, and recommendations. When evaluating multiple resumes, all evaluations can be downloaded as a single ZIP file.

## Using the Batch Download Feature

When evaluating multiple resumes at once:

1. Upload your PDF files in the first step
2. Complete the evaluation process
3. Look for the "Batch Download" section above individual results
4. Click the "📥 Download All Evaluations as ZIP" button
5. A ZIP file containing all successful evaluations will be downloaded

## Recent Improvements

- **Rebranded as "Candidate Evaluation Tool"** for clearer purpose
- **Enhanced Navigation** with immediate button response
- **Added Batch Download** feature for multiple evaluations
- **Improved Evaluation Process Visualization** with phase indicators
- **Fixed UI Issues** that required double-clicking navigation buttons
- **Updated Tool Information** with clearer project context

## Roadmap and Future Improvements

- [ ] Secure API key storage to avoid manual entry
- [ ] Export evaluations in multiple formats (PDF, DOCX)
- [ ] Integration with applicant tracking systems (ATS)
- [ ] More granular evaluation templates for different roles
- [ ] Batch comparison view to rank multiple candidates
- [ ] Enhanced data visualization of evaluation metrics
- [ ] Mobile-friendly responsive design
- [ ] Authentication improvements and user management

## License

[MIT License](LICENSE)

## Troubleshooting

**⚠️ Common Issues:**

1. **API Key Issues**: Ensure your OpenAI API key is set as an environment variable
2. **PDF Extraction Issues**: Some PDF formats may not extract correctly
3. **Placeholder Errors**: Custom prompts must include the `{resume_text}` placeholder
4. **Browser Compatibility**: For best results, use Chrome or Firefox

If you encounter persistent issues, please report them to amshan@tryhire.co.
