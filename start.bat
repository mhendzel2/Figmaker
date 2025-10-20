@echo off
echo Starting Figmaker...
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found at .venv\
    echo Please run the following commands first:
    echo   python -m venv .venv
    echo   .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if activation was successful
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Launch Figmaker GUI
echo Launching Figmaker GUI...
echo.
python Figmaker.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Figmaker exited with an error.
    pause
)

echo.
echo Figmaker closed.
pause