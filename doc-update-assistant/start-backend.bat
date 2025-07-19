@echo off
echo Starting Documentation Update Assistant Backend...
echo.

cd /d "%~dp0\backend"

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo Python is not installed or not in PATH!
    pause
    exit /b 1
)

echo.
echo Installing/updating dependencies...
python -m pip install -r requirements.txt

echo.
echo Starting backend server...
echo Backend will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

pause