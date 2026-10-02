@echo off
title AI Automated Trading Bot
echo ========================================================
echo   Launching AI Automated Trading Bot (@Algo_tradesbot)
echo ========================================================
cd /d "%~dp0"

:loop
echo [%date% %time%] Starting AI Automated Trading Bot...
py bot.py
echo.
echo ========================================================
echo [%date% %time%] Bot stopped or crashed!
echo Auto-restarting in 5 seconds... (Press Ctrl+C to cancel)
echo ========================================================
timeout /t 5 /nobreak >nul
goto loop
