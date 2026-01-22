@echo off
REM ================================================
REM Setup Script for MyTasks - To-Do List Application
REM This script automatically sets up the project
REM ================================================

echo.
echo ===================================================
echo  MyTasks - Setup Script
echo ===================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please download Python from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/5] Creating .env file...
if not exist .env (
    copy .env.example .env
    echo Created .env file from .env.example
)

echo [5/5] Creating necessary directories...
if not exist instance mkdir instance
if not exist app\static\css mkdir app\static\css
if not exist app\static\js mkdir app\static\js
if not exist app\templates mkdir app\templates

echo.
echo ===================================================
echo  Setup Complete!
echo ===================================================
echo.
echo Next steps:
echo 1. Run: start.bat (to start the application)
echo 2. Open your browser: http://127.0.0.1:5000
echo 3. Register a new account
echo 4. Start adding tasks!
echo.
echo For more information, see README.md
echo.
pause
