@echo off
REM Uptime Monitor Launcher
REM Double-click this file to start the application

echo Starting Uptime Monitor...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the application
python main.py

REM If there's an error, pause so you can see it
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit...
    pause > nul
)
