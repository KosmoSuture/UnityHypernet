@echo off
title Hypernet — First-Run Setup
color 0F
echo.
echo   H Y P E R N E T
echo   =========================
echo   First-Run Setup
echo.

:: -------------------------------------------------------
:: Check for Python
:: -------------------------------------------------------
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo   Python found.
    goto :run_bootstrap
)

where py >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo   Python found (py launcher).
    set PYTHON_CMD=py
    goto :run_bootstrap_py
)

:: Python not found at all
echo.
echo   ============================================
echo    Python is NOT installed on this system.
echo   ============================================
echo.
echo   The Hypernet requires Python 3.10 or later.
echo.
echo   To install Python:
echo.
echo     Option 1 (recommended):
echo       winget install Python.Python.3.13
echo.
echo     Option 2:
echo       Download from https://python.org/downloads/
echo       IMPORTANT: Check "Add Python to PATH" during install!
echo.
echo   After installing Python, close this window and
echo   double-click install.bat again.
echo.
pause
exit /b 1

:: -------------------------------------------------------
:: Run bootstrap with python
:: -------------------------------------------------------
:run_bootstrap
cd /d "%~dp0"
echo   Running bootstrap...
echo.
python bootstrap.py %*
goto :done

:run_bootstrap_py
cd /d "%~dp0"
echo   Running bootstrap...
echo.
py bootstrap.py %*
goto :done

:done
echo.
echo   ============================================
echo   Setup complete. You can close this window.
echo   ============================================
echo.
echo   To launch the Hypernet:
echo     - Double-click launch.bat
echo     - Or run: python -m hypernet launch
echo.
pause
