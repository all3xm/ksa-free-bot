@echo off
setlocal
cd /d "%~dp0"
title Stop KSA Free BOT

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0stop-bot.ps1"
set "STOP_EXIT_CODE=%ERRORLEVEL%"
echo.
pause
exit /b %STOP_EXIT_CODE%
