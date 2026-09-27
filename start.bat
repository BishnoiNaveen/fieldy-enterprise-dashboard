@echo off
REM start.bat - Windows launcher for Krone Field Service & Telematics Dashboard
title Krone Field Service ^& Telematics Dashboard
echo Launching Krone Enterprise Dashboard...
python start_system.py %*
if %ERRORLEVEL% NEQ 0 (
    echo Python launch failed. Trying with explicit Python path...
    C:\Users\Naveen\AppData\Local\Programs\Python\Python312\python.exe start_system.py %*
)
pause
