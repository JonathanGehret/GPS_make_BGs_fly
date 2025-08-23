@echo off
REM GPS Analysis Suite - Windows Launcher
REM Double-click this file to start the GPS Analysis Suite

title GPS Analysis Suite
cd /d "%~dp0"

echo.
echo  =====================================================
echo   🦅 Bearded Vulture GPS Analysis Suite
echo  =====================================================
echo.
echo  Starting application...
echo.

REM Try python3 first, then python
python3 main.py 2>nul
if %errorlevel% neq 0 (
    python main.py 2>nul
    if %errorlevel% neq 0 (
        echo ❌ Error: Python not found or not working properly
        echo.
        echo 🔧 Please install Python 3.8 or later:
        echo    https://www.python.org/downloads/
        echo.
        echo 📍 Make sure to check "Add Python to PATH" during installation
        echo.
        pause
    )
)
