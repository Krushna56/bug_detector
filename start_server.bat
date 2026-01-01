@echo off
REM Startup script for Bug Detector API
REM Sets PYTHONPATH to include backend directory

echo Starting Bug Detector AI Security Agent...

REM Set PYTHONPATH to include backend directory
set PYTHONPATH=%CD%\backend;%PYTHONPATH%

REM Change to orchestrator directory
cd backend\orchestrator

REM Start the server
echo.
echo Server starting at http://localhost:8000
echo API docs available at http://localhost:8000/docs
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
