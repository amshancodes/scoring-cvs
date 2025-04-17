# Resume Evaluation System

A configurable AI-powered system for evaluating candidate resumes using OpenAI's GPT-4.1 API.

## Features

- **Project-Based Organization**: Organize evaluations by projects/batches
- **Configurable Templates**: Customize evaluation criteria and prompts
- **Direct Markdown Output**: Beautiful, detailed evaluation reports
- **OpenAI Integration**: Works with GPT-4.1 and other advanced models

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
├── ai_evaluate_resumes_config.py # Main evaluation script
└── evaluate_adam.py              # Single resume evaluation
```

## Setup and Usage

1. **Configure your environment**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. **Update configuration files**:
   - Edit `configure/must_configure/config.json` to set parameters
   - Customize prompts in `system_prompt.txt` and `resume_prompt.txt`

3. **Create a project folder**:
   ```bash
   mkdir -p PDF-PROJECTS/my-new-batch
   ```

4. **Place PDFs in the project folder**:
   ```bash
   cp my-resumes/*.pdf PDF-PROJECTS/my-new-batch/
   ```

5. **Update the current project in config**:
   ```json
   {
     "current_project": "my-new-batch",
     "output_in_project_folder": true
   }
   ```

6. **Run the evaluation script**:
   ```bash
   python3 ai_evaluate_resumes_config.py
   ```

7. **Review the evaluations** in the project folder

## Configuration Options

### Main Configuration (config.json)

```json
{
  "pdf_path": "PDF-RESUMES/example.pdf",  
  "output_path": "{name}_evaluation.md",  
  "model": "gpt-4.1-2025-04-14",
  "projects_folder": "PDF-PROJECTS",
  "current_project": "new-batch",
  "output_in_project_folder": true
}
```

### System Prompt

The system prompt sets the overall context for the AI. Edit `system_prompt.txt` to modify the AI's perspective and approach.

### Resume Prompt Template

The resume prompt template (`resume_prompt.txt`) defines the evaluation criteria and formatting. It uses a template with `{resume_text}` placeholder that will be replaced with actual resume content.

## Output

Evaluations are generated as Markdown files with detailed scoring, strengths, weaknesses, and recommendations.

## License

[MIT License](LICENSE)

## User Guide

Hey there! Welcome to the Resume Evaluation System. Here's how to get started:

### Quick Setup

1. **Environment Setup**:
   - Make sure you have your OpenAI API key ready
   - Set up your environment variable: `export OPENAI_API_KEY="your-actual-api-key-here"`
   - Don't forget to update this in your terminal session or add it to your shell profile

2. **Project Organization**:
   - We organize everything by projects/folders
   - Each project (folder) in `PDF-PROJECTS/` contains related resumes and their evaluations
   - This helps keep your evaluations organized by batches, teams, or positions

3. **Configuration**:
   - Check the `configure/must_configure/` folder first
   - Update the prompts to match your company's evaluation criteria
   - Change the current project name in `config.json` when switching between projects

4. **Running Evaluations**:
   - For a single resume: `python3 evaluate_adam.py`
   - For batch processing: `python3 ai_evaluate_resumes_config.py` 

5. **Checking Results**:
   - Evaluations are saved as Markdown files
   - Find them in your project folder or in the evaluations directory
   - They're formatted for easy reading and sharing

Remember, the folder structure is designed to help you manage multiple evaluation projects at once. Just create a new folder under `PDF-PROJECTS/` whenever you start evaluating for a new position or team! 

### Prompt for Cursor

If you're using Cursor AI assistant, here's a comprehensive prompt to help set up the project:

```
Help me set up this Resume Evaluation System. I need to:
1. Check that my OpenAI API key is correctly set in my environment
2. Create a new project folder under PDF-PROJECTS for my new batch of resumes
3. Update the config.json to point to my new project
4. Customize the evaluation prompts in the configure/must_configure folder
5. Run the evaluation script on my resume PDFs
6. Review the output markdown files

Please show me the exact commands and file edits needed for each step.
```

## Heads Up

**⚠️ Known Issue:** Currently, you need to manually input your OpenAI API key each time you run the evaluation scripts. This is a temporary limitation we're working on. 

For now, make sure to set your API key before each session:
```bash
export OPENAI_API_KEY="your-actual-api-key-here"
```

We're planning to implement a more persistent solution in a future update that will securely store your API key. Thanks for your patience! 