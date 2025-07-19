@echo off
echo Starting Documentation Update Assistant Frontend...
echo.

cd /d "%~dp0\frontend"

echo Checking Node.js installation...
node --version
if errorlevel 1 (
    echo Node.js is not installed or not in PATH!
    pause
    exit /b 1
)

npm --version
if errorlevel 1 (
    echo npm is not available!
    pause
    exit /b 1
)

echo.
echo Installing/updating dependencies...
npm install

echo.
echo Starting frontend development server...
echo Frontend will be available at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

npm run dev

pause