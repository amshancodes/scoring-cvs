#!/usr/bin/env python3
"""
Test script to verify that the configuration files are working correctly
"""

import os
import json
from pathlib import Path

def test_config_files():
    """Test if all configuration files can be correctly loaded."""
    results = {"success": [], "failed": []}
    
    # Test required configuration files
    must_configure_dir = Path("configure/must_configure")
    required_files = [
        must_configure_dir / "config.json",
        must_configure_dir / "system_prompt.txt",
        must_configure_dir / "resume_prompt.txt"
    ]
    
    for file_path in required_files:
        try:
            if file_path.suffix == ".json":
                with open(file_path, 'r') as f:
                    config = json.load(f)
                print(f"✅ Successfully loaded {file_path}")
                print(f"   Contents: {config}")
            else:
                with open(file_path, 'r') as f:
                    content = f.read()
                print(f"✅ Successfully loaded {file_path}")
                print(f"   First 50 chars: {content[:50]}...")
            results["success"].append(str(file_path))
        except Exception as e:
            print(f"❌ Failed to load {file_path}: {e}")
            results["failed"].append(str(file_path))
    
    # Test optional configuration files
    nice_to_configure_dir = Path("configure/nice_to_configure")
    optional_files = [
        nice_to_configure_dir / "model_options.json",
        nice_to_configure_dir / "output_templates.json"
    ]
    
    for file_path in optional_files:
        try:
            if file_path.suffix == ".json":
                with open(file_path, 'r') as f:
                    config = json.load(f)
                print(f"✅ Successfully loaded {file_path}")
                print(f"   Contents: {json.dumps(config, indent=2)[:100]}...")
            else:
                with open(file_path, 'r') as f:
                    content = f.read()
                print(f"✅ Successfully loaded {file_path}")
                print(f"   First 50 chars: {content[:50]}...")
            results["success"].append(str(file_path))
        except Exception as e:
            print(f"❌ Failed to load {file_path}: {e}")
            results["failed"].append(str(file_path))
    
    # Print summary
    print("\n--- Configuration Test Summary ---")
    print(f"Successfully loaded: {len(results['success'])}/{len(required_files) + len(optional_files)} files")
    
    if results["failed"]:
        print(f"Failed to load: {len(results['failed'])} files")
        for failed in results["failed"]:
            print(f"  - {failed}")
    else:
        print("All configuration files loaded successfully! 🎉")
    
    return results

if __name__ == "__main__":
    test_config_files() 