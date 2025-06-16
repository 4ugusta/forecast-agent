#!/bin/bash

# Setup script for the Forecast Agent with Python 3.12
echo "Setting up the Forecast Agent environment with Python 3.12..."

# Check if Python 3.12 is available
if ! command -v /opt/homebrew/bin/python3.12 &> /dev/null; then
    echo "Error: Python 3.12 is required but not found in /opt/homebrew/bin."
    echo "Please install Python 3.12 first using:"
    echo "  brew install python@3.12"
    exit 1
fi

echo "Found Python 3.12!"

# Remove old virtual environment if it exists
if [ -d "venv" ]; then
    echo "Removing old virtual environment..."
    rm -rf venv
fi

# Create a new virtual environment with Python 3.12
echo "Creating new virtual environment with Python 3.12..."
/opt/homebrew/bin/python3.12 -m venv venv

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Verify Python version
PYTHON_VERSION=$(python --version)
echo "Using $PYTHON_VERSION"

# Update pip
echo "Updating pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing requirements..."
pip install -r requirements.txt

# Check for OpenAI API key
if [ -f ".env" ]; then
    source .env
    echo "Found existing OpenAI API key configuration."
else
    echo ""
    echo "No OpenAI API key configuration found."
    echo "If you want to use LLM-based forecasting, run:"
    echo "  python setup_openai.py"
    echo ""
fi

echo "Setup complete! You can now run the Forecast Agent with Python 3.12."
echo ""
echo "Examples:"
echo "  • Run with sample data (statistical forecasting):"
echo "    python main.py sample --months 2"
echo ""
echo "  • Run with sample data (LLM-based forecasting):"
echo "    python main.py sample --months 2 --llm"
echo "" 
echo "  • Start the API server:"
echo "    python main.py api"
echo ""
echo "  • Process your own data:"
echo "    python main.py cli --data your_data.csv --months 3"
echo ""
echo "For more information, see the README.md file."
