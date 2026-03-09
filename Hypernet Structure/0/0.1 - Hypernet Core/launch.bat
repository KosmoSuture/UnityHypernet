@echo off
title Hypernet
echo.
echo   Starting Hypernet...
echo   Close this window to shut down.
echo.
cd /d "%~dp0"
python -m hypernet launch %*
pause
