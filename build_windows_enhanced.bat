@echo off
setlocal enabledelayedexpansion

REM GPS Analysis Suite - Windows Build Script (Enhanced)
REM This script handles common Windows build issues automatically

title GPS Analysis Suite - Windows Builder
color 0A
cd /d "%~dp0"

echo.
echo  =====================================================
echo   🦅 GPS Analysis Suite - Windows Builder v2.0
echo  =====================================================
echo   Enhanced with automatic problem detection
echo  =====================================================
echo.

REM Test Python installation
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python not found in PATH
    echo.
    echo 🔧 SOLUTION:
    echo    1. Download Python from: https://www.python.org/downloads/
    echo    2. During installation, CHECK "Add Python to PATH"
    echo    3. Choose "Install for all users"
    echo    4. Restart this script after installation
    echo.
    goto :error_exit
)

for /f "tokens=2" %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a
echo ✅ Python %PYTHON_VERSION% found

REM Test pip
echo 🔍 Checking pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: pip not found
    echo 🔧 Attempting to install pip...
    python -m ensurepip --upgrade
    if !errorlevel! neq 0 (
        echo ❌ Failed to install pip
        goto :error_exit
    )
)
echo ✅ pip available

REM Test tkinter (common Windows issue)
echo 🔍 Testing GUI support (tkinter)...
python -c "import tkinter; print('✅ GUI support OK')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Error: tkinter not available
    echo 🔧 SOLUTION: Reinstall Python with "tcl/tk and IDLE" option checked
    goto :error_exit
)

REM Check if spec file exists
if not exist "GPS_Analysis_Suite.spec" (
    echo ❌ Error: GPS_Analysis_Suite.spec not found
    echo 🔧 Make sure you're in the correct directory with all source files
    goto :error_exit
)
echo ✅ Build configuration found

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo ❌ Error: requirements.txt not found
    echo 🔧 Make sure you have the complete source code
    goto :error_exit
)
echo ✅ Requirements file found

REM Virtual environment setup (optional but recommended)
echo.
echo 🤔 Do you want to use a virtual environment? (Recommended)
echo    Y = Yes (isolated, safer)
echo    N = No (use system Python, faster)
choice /c YN /m "Use virtual environment"
if %errorlevel%==1 (
    set USE_VENV=true
    echo 📦 Will use virtual environment
) else (
    set USE_VENV=false
    echo 🌐 Will use system Python
)

if "%USE_VENV%"=="true" (
    if not exist ".venv" (
        echo.
        echo 📦 Creating virtual environment...
        python -m venv .venv
        if !errorlevel! neq 0 (
            echo ❌ Error: Failed to create virtual environment
            echo 💡 Trying without virtual environment...
            set USE_VENV=false
        ) else (
            echo ✅ Virtual environment created
        )
    ) else (
        echo ✅ Virtual environment already exists
    )
    
    if "%USE_VENV%"=="true" (
        echo 🔄 Activating virtual environment...
        call .venv\Scripts\activate.bat
        if !errorlevel! neq 0 (
            echo ❌ Error: Failed to activate virtual environment
            echo 💡 Trying without virtual environment...
            set USE_VENV=false
        ) else (
            echo ✅ Virtual environment activated
        )
    )
)

REM Install dependencies
echo.
echo 📥 Installing/updating dependencies...
python -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo ⚠️  Warning: Failed to upgrade pip, continuing anyway...
)

echo    Installing requirements...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ❌ Error: Failed to install requirements
    echo 💡 Trying individual package installation...
    echo    Installing pandas...
    pip install pandas --quiet
    echo    Installing numpy...
    pip install numpy --quiet
    echo    Installing matplotlib...
    pip install matplotlib --quiet
    echo    Installing plotly...
    pip install plotly --quiet
    echo    Installing requests...
    pip install requests --quiet
)

echo    Installing PyInstaller...
pip install pyinstaller --quiet
if %errorlevel% neq 0 (
    echo ❌ Error: Failed to install PyInstaller
    goto :error_exit
)

echo ✅ Dependencies installed

REM Test imports before building
echo.
echo 🧪 Testing critical imports...
python -c "import pandas, numpy, matplotlib, plotly, tkinter, requests; print('✅ All imports successful')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Error: Some packages failed to import
    echo 💡 Running detailed import test...
    python test_compatibility.py
    pause
    goto :error_exit
)

REM Clean previous builds
echo.
echo 🧹 Cleaning previous builds...
if exist "build" (
    rmdir /s /q "build" 2>nul
    echo    Removed build directory
)
if exist "dist" (
    rmdir /s /q "dist" 2>nul
    echo    Removed dist directory
)

REM Build executable
echo.
echo 🔨 Building Windows executable...
echo    This may take 2-5 minutes...
pyinstaller --clean GPS_Analysis_Suite.spec
if %errorlevel% neq 0 (
    echo.
    echo ❌ BUILD FAILED!
    echo.
    echo 🔍 Common solutions:
    echo    1. Run as Administrator
    echo    2. Disable antivirus temporarily
    echo    3. Close all other applications
    echo    4. Check Windows Event Viewer for details
    echo    5. Try: pip install --upgrade setuptools wheel
    echo.
    goto :error_exit
)

REM Verify executable was created
if exist "dist\GPS_Analysis_Suite.exe" (
    echo.
    echo 🎉 BUILD SUCCESSFUL!
    echo ✅ Executable created: dist\GPS_Analysis_Suite.exe
    
    REM Get file size
    for %%i in ("dist\GPS_Analysis_Suite.exe") do set FILE_SIZE=%%~zi
    set /a FILE_SIZE_MB=%FILE_SIZE%/1024/1024
    echo 📊 File size: ~%FILE_SIZE_MB% MB
    
    echo.
    echo 🚀 Ready to run! You can now:
    echo    • Double-click: dist\GPS_Analysis_Suite.exe
    echo    • Or run from command line: dist\GPS_Analysis_Suite.exe
    echo.
    echo 📦 To distribute: Copy the entire 'dist' folder to other computers
    echo.
    
    REM Ask if user wants to test now
    choice /c YN /m "Test the executable now"
    if !errorlevel!==1 (
        echo 🧪 Starting GPS Analysis Suite...
        cd dist
        start GPS_Analysis_Suite.exe
        cd ..
    )
    
    echo.
    echo ✅ Build completed successfully!
    
) else (
    echo ❌ Error: Executable not found after build
    echo 🔍 Check build output above for errors
    goto :error_exit
)

echo.
echo Press any key to exit...
pause >nul
exit /b 0

:error_exit
echo.
echo ❌ Build failed. Please check the error messages above.
echo 💡 For detailed help, see: WINDOWS_BUILD_GUIDE.md
echo.
echo Press any key to exit...
pause >nul
exit /b 1
