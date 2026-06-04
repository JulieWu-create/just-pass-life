@echo off
echo ============================================================
echo      Just Pass Life (剛好及格的人生) - Local Launcher
echo ============================================================
echo.

:: 1. Check Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in your system PATH.
    echo Please install Python 3.10+ and check 'Add Python to environment variables'.
    pause
    exit /b 1
)

:: 2. Check virtual environment
if not exist .venv (
    echo [INFO] Creating Python virtual environment in .venv...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: 3. Activate venv & install requirements
echo [INFO] Activating virtual environment & installing dependencies...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

:: 4. Re-extract game data if needed
if not exist static\game_data.json (
    echo [INFO] Extracting game data from script file...
    python build_game_data.py
)

:: 5. Launch FastAPI server
echo.
echo [SUCCESS] Server is starting up!
echo [INFO] Open your browser and go to: http://127.0.0.1:8000
echo.
echo Press Ctrl+C in this console window to stop the server.
echo ============================================================
echo.
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause
