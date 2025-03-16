@echo off
:: Check if Python is installed
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python is not installed or not added to PATH.
    echo Please install Python or adjust your PATH variable.
    pause
    exit /B
)

echo Starting Video Converter...
python main.py
pause
