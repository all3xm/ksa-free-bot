@echo off
setlocal
cd /d "%~dp0"
title KSA Free BOT

if not exist ".env" (
    copy /y ".env.example" ".env" >nul
    echo A new .env file was created.
    echo Add your Discord bot token and server ID, save it, then run start.bat again.
    start "" notepad.exe "%~dp0.env"
    echo.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo First-time setup: creating the private Python environment...
    where py >nul 2>nul
    if not errorlevel 1 (
        py -3 -m venv ".venv"
    ) else (
        python -m venv ".venv"
    )
    if errorlevel 1 goto :python_error

    echo Installing the small list of required packages...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    if errorlevel 1 goto :install_error
    ".venv\Scripts\python.exe" -m pip install -r "requirements.txt"
    if errorlevel 1 goto :install_error
)

echo Starting KSA Free BOT...
echo Author: KSAGlory
echo Community: discord.gg/ksahub
echo Keep this window open while the bot is running.
echo.
"%~dp0.venv\Scripts\python.exe" "%~dp0bot.py"
set "BOT_EXIT_CODE=%ERRORLEVEL%"
echo.
echo The bot stopped with exit code %BOT_EXIT_CODE%.
pause
exit /b %BOT_EXIT_CODE%

:python_error
echo.
echo Python 3 was not found. Install it from https://www.python.org/downloads/
echo During installation, select "Add Python to PATH".
pause
exit /b 2

:install_error
echo.
echo The required packages could not be installed. Check your internet connection and try again.
pause
exit /b 3
