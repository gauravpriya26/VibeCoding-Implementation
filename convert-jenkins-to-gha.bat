@echo off
REM Jenkins to GitHub Actions Converter
REM This batch file provides an easy way to run the conversion tools

setlocal enabledelayedexpansion

echo.
echo ================================================================
echo           Jenkins to GitHub Actions Converter
echo ================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_AVAILABLE=1
    echo [INFO] Python is available
) else (
    set PYTHON_AVAILABLE=0
    echo [INFO] Python is not available, will use PowerShell version
)

REM Check if PowerShell is available
powershell -Command "Write-Host 'PowerShell Test'" >nul 2>&1
if %errorlevel% == 0 (
    set POWERSHELL_AVAILABLE=1
    echo [INFO] PowerShell is available
) else (
    set POWERSHELL_AVAILABLE=0
    echo [ERROR] PowerShell is not available
)

echo.

REM Get input and output paths
if "%~1"=="" (
    set /p INPUT_PATH="Enter input path (Jenkins repository): "
) else (
    set INPUT_PATH=%~1
)

if "%~2"=="" (
    set /p OUTPUT_PATH="Enter output path (GitHub Actions repository): "
) else (
    set OUTPUT_PATH=%~2
)

REM Validate paths
if not exist "%INPUT_PATH%" (
    echo [ERROR] Input path does not exist: %INPUT_PATH%
    pause
    exit /b 1
)

echo.
echo [INFO] Input Path:  %INPUT_PATH%
echo [INFO] Output Path: %OUTPUT_PATH%
echo.

REM Choose conversion tool
if %PYTHON_AVAILABLE% == 1 (
    echo [INFO] Using Python converter...
    echo.
    python jenkins-to-gha-converter.py --input "%INPUT_PATH%" --output "%OUTPUT_PATH%" --verbose
    set CONVERSION_RESULT=%errorlevel%
) else if %POWERSHELL_AVAILABLE% == 1 (
    echo [INFO] Using PowerShell converter...
    echo.
    powershell -ExecutionPolicy Bypass -File "Convert-JenkinsToGHA.ps1" -InputPath "%INPUT_PATH%" -OutputPath "%OUTPUT_PATH%" -Verbose
    set CONVERSION_RESULT=%errorlevel%
) else (
    echo [ERROR] Neither Python nor PowerShell is available
    pause
    exit /b 1
)

echo.
if %CONVERSION_RESULT% == 0 (
    echo ================================================================
    echo                    CONVERSION SUCCESSFUL!
    echo ================================================================
    echo.
    echo Your Jenkins repository has been converted to GitHub Actions.
    echo.
    echo Output location: %OUTPUT_PATH%
    echo Workflows location: %OUTPUT_PATH%\.github\workflows\
    echo.
    echo Next steps:
    echo 1. Review the generated workflows in .github/workflows/
    echo 2. Commit and push to your GitHub repository
    echo 3. Test the workflows by creating a pull request
    echo.
    echo Note: You may need to adjust some workflow settings based on
    echo your specific requirements.
    echo.
) else (
    echo ================================================================
    echo                    CONVERSION FAILED!
    echo ================================================================
    echo.
    echo Please check the error messages above and try again.
    echo.
)

pause
