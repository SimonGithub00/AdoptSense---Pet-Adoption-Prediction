#!/bin/bash

# AdoptSense Frontend Startup Script for macOS/Linux
# This script activates the virtual environment and runs the Streamlit app

echo ""
echo "========================================"
echo "  AdoptSense Pet Adoption Predictor"
echo "  Streamlit Frontend"
echo "========================================"
echo ""

# Check if we're in the frontend directory
if [ ! -f "app.py" ]; then
    echo "Error: app.py not found. Please run this script from the frontend directory."
    echo ""
    echo "Usage: cd frontend && bash run_app.sh"
    echo ""
    exit 1
fi

# Check and activate virtual environment
if [ -f "../.venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source ../.venv/bin/activate
    echo "✓ Virtual environment activated"
    echo ""
fi

# Check if streamlit is installed
python -m pip show streamlit > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Streamlit not installed"
    echo ""
    echo "Installing dependencies..."
    python -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
    echo "✓ Dependencies installed"
    echo ""
fi

# Display startup info
echo "========================================"
echo "  Starting Streamlit Application..."
echo "========================================"
echo ""
echo "The app will open in your default browser at:"
echo "  http://localhost:8501"
echo ""
echo "To stop the app, press Ctrl+C"
echo ""
echo "========================================"
echo ""

# Run streamlit
python -m streamlit run app.py --logger.level=error
