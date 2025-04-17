#!/usr/bin/env python3
"""
Utility functions to integrate the configuration files into the main script (ai_evaluate_resumes.py)
This is a proof-of-concept to show how the files would be integrated.
"""

import os
import json
import string
from pathlib import Path

class ConfigLoader:
    """Load and manage configuration from the 'configure' directory."""
    
    def __init__(self, base_dir="configure"):
        self.base_dir = Path(base_dir)
        self.must_configure_dir = self.base_dir / "must_configure"
        self.nice_to_configure_dir = self.base_dir / "nice_to_configure"
        
        # Load main config
        self.config = self._load_json(self.must_configure_dir / "config.json")
        
        # Load model options if available
        try:
            model_options = self._load_json(self.nice_to_configure_dir / "model_options.json")
            self.model_options = model_options.get("model_options", {})
            self.default_model = model_options.get("default_model", "gpt-4-turbo")
        except Exception:
            self.model_options = {}
            self.default_model = "gpt-4-turbo"
        
        # Load output templates if available
        try:
            self.output_templates = self._load_json(self.nice_to_configure_dir / "output_templates.json")
        except Exception:
            self.output_templates = {}
    
    def _load_json(self, file_path):
        """Load a JSON file."""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def _load_text(self, file_path):
        """Load a text file."""
        with open(file_path, 'r') as f:
            return f.read().strip()
    
    def get_system_prompt(self):
        """Get the system prompt from the configuration."""
        try:
            return self._load_text(self.must_configure_dir / "system_prompt.txt")
        except Exception:
            return "You are an expert HR professional specializing in evaluating technical resumes."
    
    def get_user_prompt_template(self):
        """Get the user prompt template from the configuration."""
        try:
            return self._load_text(self.must_configure_dir / "resume_prompt.txt")
        except Exception:
            return "Please evaluate the following resume: {resume_text}"
    
    def get_model_config(self, model_name=None):
        """Get the configuration for a specific model."""
        if not model_name:
            model_name = self.config.get("model", self.default_model)
        
        return self.model_options.get(model_name, {})
    
    def format_output(self, output_format, evaluation, candidate_name):
        """Format the evaluation output according to the template."""
        if output_format not in self.output_templates or not self.output_templates[output_format]:
            # Default format is just the raw evaluation
            return evaluation
        
        template = self.output_templates[output_format]
        
        # Create a formatter that can handle nested dictionary access
        class NestedDictFormatter(string.Formatter):
            def get_value(self, key, args, kwargs):
                if '.' in key:
                    # Handle nested dictionary access like "overall_impression.score"
                    parts = key.split('.')
                    value = kwargs
                    for part in parts:
                        if isinstance(value, dict):
                            value = value.get(part, {})
                        else:
                            return ""  # Return empty string if the path is invalid
                    return value
                return super().get_value(key, args, kwargs)
        
        formatter = NestedDictFormatter()
        
        # Add candidate name to evaluation dict
        evaluation_with_name = evaluation.copy()
        evaluation_with_name["candidate_name"] = candidate_name
        
        # Format the output
        try:
            return formatter.format(template, **evaluation_with_name)
        except Exception as e:
            print(f"Error formatting output: {e}")
            return str(evaluation)
    
    def get_output_path(self, candidate_name):
        """Get the output path for a candidate's evaluation."""
        output_format = self.config.get("output_path", "{name}_evaluation.md")
        return output_format.replace("{name}", candidate_name.replace(" ", "_"))

# Example usage
def main():
    """Demonstrate how to use the ConfigLoader class."""
    config_loader = ConfigLoader()
    
    # Print loaded configurations
    print("Loaded configurations:")
    print(f"  Main config: {config_loader.config}")
    print(f"  Default model: {config_loader.default_model}")
    print(f"  Available models: {list(config_loader.model_options.keys())}")
    
    # Print system prompt
    system_prompt = config_loader.get_system_prompt()
    print(f"\nSystem prompt: {system_prompt[:50]}...")
    
    # Print user prompt template
    user_prompt = config_loader.get_user_prompt_template()
    print(f"\nUser prompt template: {user_prompt[:50]}...")
    
    # Example model configuration
    model_config = config_loader.get_model_config()
    print(f"\nModel configuration: {model_config}")
    
    # Example output formatting
    example_evaluation = {
        "overall_impression": {
            "score": 8,
            "explanation": "Strong candidate with relevant experience."
        },
        "technical_skills": {
            "score": 9,
            "explanation": "Excellent technical skills in required areas."
        },
        "experience": {
            "score": 7,
            "explanation": "Good experience but could use more leadership roles."
        },
        "education": {
            "score": 8,
            "explanation": "Strong educational background in relevant fields."
        },
        "projects": {
            "score": 8,
            "explanation": "Impressive project work with solid outcomes."
        },
        "total_score": 40,
        "summary": "A strong candidate with excellent technical skills."
    }
    
    candidate_name = "John Doe"
    
    # Format as markdown
    if "markdown_template" in config_loader.output_templates:
        markdown_output = config_loader.format_output("markdown_template", example_evaluation, candidate_name)
        print(f"\nMarkdown output (first 200 chars):\n{markdown_output[:200]}...")
    
    # Get output path
    output_path = config_loader.get_output_path(candidate_name)
    print(f"\nOutput path for '{candidate_name}': {output_path}")
    
    print("\nTo integrate with ai_evaluate_resumes.py:")
    print("1. Create a ConfigLoader instance at the start of the script")
    print("2. Use loader.get_system_prompt() and loader.get_user_prompt_template() in evaluate_resume_with_ai()")
    print("3. Use loader.get_model_config() to get model settings")
    print("4. Use loader.format_output() to format the evaluation output")
    print("5. Use loader.get_output_path() to get the path for saving the evaluation")

if __name__ == "__main__":
    main() 