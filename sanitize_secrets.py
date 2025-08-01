#!/usr/bin/env python3
"""
Emergency credential sanitization script
Removes all hardcoded secrets from files
"""

import os
import re

# Define the secrets to replace
SECRETS_TO_SANITIZE = {
    "YOUR_OPENROUTER_API_KEY_HERE": "YOUR_OPENROUTER_API_KEY_HERE",
    "YOUR_ELEVENLABS_API_KEY_HERE": "YOUR_ELEVENLABS_API_KEY_HERE", 
    "YOUR_PHONE_NUMBER_SID_HERE": "YOUR_PHONE_NUMBER_SID_HERE",
    "YOUR_RENDER_API_KEY_HERE": "YOUR_RENDER_API_KEY_HERE",
    "YOUR_SECURE_PASSWORD_HERE": "YOUR_SECURE_PASSWORD_HERE",
    "YOUR_DB_HOST_HERE": "YOUR_DB_HOST_HERE"
}

def sanitize_file(filepath):
    """Sanitize a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace each secret
        for secret, replacement in SECRETS_TO_SANITIZE.items():
            content = content.replace(secret, replacement)
        
        # Only write if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Sanitized: {filepath}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error sanitizing {filepath}: {e}")
        return False

def main():
    """Main sanitization function"""
    print("EMERGENCY CREDENTIAL SANITIZATION")
    print("=" * 50)
    
    # File patterns to check
    patterns = ['*.py', '*.md', '*.yaml', '*.yml', '*.json']
    
    sanitized_count = 0
    
    # Walk through all files
    for root, dirs, files in os.walk('.'):
        # Skip .git directory
        if '.git' in dirs:
            dirs.remove('.git')
            
        for file in files:
            if any(file.endswith(pattern.replace('*', '')) for pattern in patterns):
                filepath = os.path.join(root, file)
                if sanitize_file(filepath):
                    sanitized_count += 1
    
    print("=" * 50)
    print(f"Sanitized {sanitized_count} files")
    print("All credentials removed!")

if __name__ == "__main__":
    main()