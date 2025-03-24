@echo off
setlocal EnableDelayedExpansion

echo Setting up Git hooks for this repository...

REM Get the git root directory
for /f "tokens=*" %%a in ('git rev-parse --show-toplevel') do set GIT_ROOT=%%a
set HOOKS_DIR=%GIT_ROOT%\.git\hooks
set PRE_COMMIT=%HOOKS_DIR%\pre-commit

REM Check if git hooks directory exists
if not exist "%HOOKS_DIR%" (
    echo Error: Git hooks directory not found at %HOOKS_DIR%
    echo Make sure you're in a git repository.
    exit /b 1
)

REM Create pre-commit file
echo Creating pre-commit hook...
copy pre-commit.py "%PRE_COMMIT%" >nul

REM Add shebang line for Python script
echo @echo off>"%PRE_COMMIT%.bat"
echo python "%PRE_COMMIT%" %%*>>"%PRE_COMMIT%.bat"
echo exit /b %%ERRORLEVEL%%>>"%PRE_COMMIT%.bat"

REM Check if the hook was created successfully
if exist "%PRE_COMMIT%" (
    echo Success! Pre-commit hook installed at %PRE_COMMIT%
) else (
    echo Error: Failed to create pre-commit hook
    exit /b 1
)

REM Install required packages
echo.
echo Checking required packages...

REM Function to check and install a package
call :check_and_install black
call :check_and_install isort
call :check_and_install flake8
call :check_and_install colorama

echo.
echo Setup complete!
echo Your code will now be automatically formatted with black and isort, and checked with flake8 before each commit.
echo If you want to skip the pre-commit hook, use the --no-verify flag: git commit --no-verify

exit /b 0

:check_and_install
pip show %1 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo %1 not found. Installing...
    pip install %1
    if %ERRORLEVEL% EQU 0 (
        echo Successfully installed %1
    ) else (
        echo Failed to install %1. Please install it manually with 'pip install %1'
        exit /b 1
    )
) else (
    echo %1 is already installed
)
exit /b 0