@echo off
title Live Traffic Monitor
color 0B
echo.
echo  ============================================================
echo   📡  AI Trading Bot — Real-time Traffic Monitor
echo  ============================================================
echo   Starting Flask monitor server on port 5001...
echo   Open your browser at: http://localhost:5001
echo  ============================================================
echo.
cd /d "%~dp0"
py traffic_monitor.py
pause
