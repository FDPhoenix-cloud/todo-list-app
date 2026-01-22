@echo off
REM ================================================
REM Start Script for MyTasks - To-Do List Application
REM This script starts the Flask development server
REM ================================================

echo.
echo ===================================================
echo  MyTasks - Starting Application
echo ===================================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Error: Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist .env (
    echo Error: .env file not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

echo Starting Flask development server...
echo.
echo ===================================================
echo  MyTasks is running!
echo ===================================================
echo.
echo 🚀 Open your browser and go to:
echo    http://127.0.0.1:5000
echo.
echo 📝 To register a new account:
echo    http://127.0.0.1:5000/auth/register
echo.
echo 📊 To view statistics:
echo    http://127.0.0.1:5000/statistics/dashboard
echo.
echo Press CTRL+C to stop the server
echo.
echo ===================================================
echo.

REM Start the Flask app
python run.py

pause
