@echo off
REM AdoptSense Frontend Startup Script for Windows
REM This script activates the virtual environment and runs the Streamlit app

echo.
echo ========================================
echo   AdoptSense Pet Adoption Predictor
echo   Streamlit Frontend
echo ========================================
echo.

REM Check if we're in the frontend directory
if not exist "app.py" (
    echo Error: app.py not found. Please run this script from the frontend directory.
    echo.
    echo Usage: Open PowerShell/CMD in the 'frontend' folder and run:
    echo   python -m streamlit run app.py
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "..\\.venv\\Scripts\\activate.bat" (
    echo Warning: Virtual environment not found at ..\\.venv
    echo Attempting to run without venv activation...
    echo.
)

REM Try to activate venv if it exists
if exist "..\\.venv\\Scripts\\activate.bat" (
    echo Activating virtual environment...
    call ..\\.venv\\Scripts\\activate.bat
    echo ✓ Virtual environment activated
    echo.
)

REM Check if streamlit is installed
python -m pip show streamlit > nul 2>&1
if errorlevel 1 (
    echo Error: Streamlit not installed
    echo.
    echo Installing dependencies...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✓ Dependencies installed
    echo.
)

REM Display startup info
echo ========================================
echo   Starting Streamlit Application...
echo ========================================
echo.
echo The app will open in your default browser at:
echo   http://localhost:8501
echo.
echo To stop the app, press Ctrl+C
echo.
echo ========================================
echo.

REM Run streamlit
python -m streamlit run app.py --logger.level=error

pause
