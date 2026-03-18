@echo off
title Hypernet
echo.
echo   H Y P E R N E T
echo   =========================
echo.
echo   1. Launch (server + swarm + browser)
echo   2. Launch + System Tray
echo   3. Install as Windows Service
echo   4. Service Status
echo   5. Launch (default)
echo.
choice /c 12345 /n /t 5 /d 5 /m "  Select option (auto-launches in 5s): "
cd /d "%~dp0"
if errorlevel 5 goto launch
if errorlevel 4 goto status
if errorlevel 3 goto install
if errorlevel 2 goto tray
if errorlevel 1 goto launch

:launch
echo.
echo   Starting Hypernet...
echo   Close this window to shut down.
echo.
python -m hypernet launch %*
pause
goto end

:tray
echo.
echo   Starting Hypernet with system tray...
echo.
start "Hypernet Tray" /min python -m hypernet tray
python -m hypernet launch --no-browser %*
pause
goto end

:install
echo.
echo   Installing Hypernet as a Windows service...
echo   (Requires NSSM - https://nssm.cc/download)
echo.
python -m hypernet install-service
pause
goto end

:status
echo.
python -m hypernet service-status
pause
goto end

:end
