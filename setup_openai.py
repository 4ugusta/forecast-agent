#!/usr/bin/env python3
"""
Helper script to set up the OpenAI API key for LLM-based forecasting.
"""

import os
import argparse
import sys
from pathlib import Path

def main():
    """Set up the OpenAI API key."""
    parser = argparse.ArgumentParser(description="Set up OpenAI API key for LLM-based forecasting")
    parser.add_argument("--key", "-k", help="Your OpenAI API Key")
    args = parser.parse_args()
    
    api_key = args.key
    
    if not api_key:
        # Prompt for the API key
        api_key = input("Enter your OpenAI API key: ")
    
    if not api_key:
        print("Error: No API key provided.")
        sys.exit(1)
    
    # Set the API key in the environment and check if it works
    os.environ["OPENAI_API_KEY"] = api_key
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Make a simple request to verify the API key
        models = client.models.list()
        print("\n✓ API key verified successfully!\n")
        
        # Save to .env file for persistence
        env_path = Path(__file__).parent / ".env"
        with open(env_path, "w") as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
        
        print(f"API key saved to {env_path}")
        print("\nTo use LLM-based forecasting, run commands with the --llm flag, for example:")
        print("  python main.py sample --months 2 --llm")
        print("  python main.py cli --data sample_data.csv --months 3 --llm")
        
    except Exception as e:
        print(f"Error verifying API key: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
