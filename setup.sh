#!/bin/bash

# Setup script for the Forecast Agent
echo "Setting up the Forecast Agent environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found."
    exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

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

echo "Setup complete! You can now run the Forecast Agent."
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
