@echo off
title AugmentCode Unlimited - Start GUI

echo ========================================
echo   AugmentCode Unlimited - Start GUI
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python not found
    echo Please install Python 3.8 or higher
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo OK: Python environment detected
python --version
echo.

REM Check if in correct directory
if not exist "gui_main.py" (
    echo ERROR: gui_main.py not found
    echo Please ensure this batch file is in augment-cleaner-unified directory
    echo.
    pause
    exit /b 1
)

REM Check and install dependencies
echo INFO: Checking dependencies...
if exist "check_dependencies.py" (
    echo INFO: Using comprehensive dependency checker...
    python check_dependencies.py
    if %errorLevel% neq 0 (
        echo ERROR: Dependency installation failed
        echo.
        echo Possible solutions:
        echo 1. Run as administrator
        echo 2. Check network connection
        echo 3. Manual install: pip install psutil
        echo.
        pause
        exit /b 1
    )
    echo OK: All dependencies ready
) else (
    echo INFO: Using basic dependency check...
    python -c "import psutil" >nul 2>&1
    if %errorLevel% neq 0 (
        echo WARN: psutil not installed, installing...
        python -m pip install psutil --quiet
        if %errorLevel% neq 0 (
            echo WARN: Retrying with China mirror...
            python -m pip install psutil -i https://pypi.tuna.tsinghua.edu.cn/simple/ --quiet
            if %errorLevel% neq 0 (
                echo ERROR: Failed to install psutil
                echo Please install manually: pip install psutil
                pause
                exit /b 1
            )
        )
        echo OK: Dependencies installed
    ) else (
        echo OK: Dependencies check passed
    )
)
echo.

echo INFO: Starting GUI...
echo.

REM Start GUI program
python gui_main.py

REM Check exit status
if %errorLevel% neq 0 (
    echo.
    echo ERROR: Program exited with error code: %errorLevel%
    echo.
    echo Possible solutions:
    echo 1. Run as administrator
    echo 2. Check antivirus software
    echo 3. Ensure Python environment is correct
    echo 4. Try test script: python test_startup.py
    echo.
    pause
) else (
    echo.
    echo OK: Program exited normally
    pause
)
