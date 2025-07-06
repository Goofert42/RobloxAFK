@echo off
echo Roblox Anti-Leave Script
echo ========================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

python -m venv .venv

venv\Scripts\activate

REM Check if requirements are installed
echo Checking dependencies...
pip show pygetwindow >nul 2>&1
if errorlevel 1 (
    echo Installing required dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Starting Roblox Anti-Leave monitoring...
echo.
python main.py

pause
