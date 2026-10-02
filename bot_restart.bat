@echo off
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)
cd /d "%~dp0"
.\nssm.exe restart TelegramTradingBot
echo.
echo Bot restarted.
pause
