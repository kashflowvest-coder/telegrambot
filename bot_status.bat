@echo off
cd /d "%~dp0"
echo ========================================
echo   TelegramTradingBot Service Status
echo ========================================
powershell -Command "Get-Service TelegramTradingBot | Format-List Name, Status, StartType"
echo.
echo Recent log output:
echo ----------------------------------------
powershell -Command "if (Test-Path 'bot_service.log') { Get-Content 'bot_service.log' -Tail 10 } else { Write-Output 'No log file found' }"
echo.
pause
