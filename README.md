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