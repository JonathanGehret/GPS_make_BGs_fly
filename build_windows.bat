@echo off
REM GPS Analysis Suite - Windows Build Script
REM Run this script on a Windows machine to build the executable

title GPS Analysis Suite Builder
cd /d "%~dp0"

echo.
echo  =====================================================
echo   🦅 GPS Analysis Suite - Windows Builder
echo  =====================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python not found
    echo.
    echo 🔧 Please install Python 3.8 or later:
    echo    https://www.python.org/downloads/
    echo.
    echo 📍 Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Check if virtual environment exists
if not exist ".venv" (
    echo.
    echo 📦 Creating virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ❌ Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo.
echo 🔄 Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Error: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies
echo.
echo 📥 Installing dependencies...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ❌ Error: Failed to upgrade pip
    pause
    exit /b 1
)

pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Error: Failed to install requirements
    pause
    exit /b 1
)

pip install pyinstaller
if %errorlevel% neq 0 (
    echo ❌ Error: Failed to install PyInstaller
    pause
    exit /b 1
)

REM Clean previous build
echo.
echo 🧹 Cleaning previous build...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM Build executable
echo.
echo 🔨 Building Windows executable...
pyinstaller --clean GPS_Analysis_Suite.spec
if %errorlevel% neq 0 (
    echo ❌ Error: Build failed
    echo.
    echo 💡 Troubleshooting tips:
    echo    - Make sure all dependencies are installed
    echo    - Check that the .spec file exists
    echo    - Try running: python -c "import tkinter; print('GUI OK')"
    echo.
    pause
    exit /b 1
)

REM Check if executable was created
if exist "dist\GPS_Analysis_Suite.exe" (
    echo.
    echo ✅ Build successful!
    echo 📁 Executable created: dist\GPS_Analysis_Suite.exe
    echo.
    echo 🚀 You can now run the executable:
    echo    dist\GPS_Analysis_Suite.exe
    echo.
) else (
    echo ❌ Error: Executable not found after build
    pause
    exit /b 1
)

echo Press any key to exit...
pause >nul
