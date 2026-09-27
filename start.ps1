# start.ps1 - PowerShell launcher for Krone Field Service & Telematics Dashboard
param (
    [string]$Mode = "preview",
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 4173
)

$pythonExe = "C:\Users\Naveen\AppData\Local\Programs\Python\Python312\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  Launching Krone Agriculture India Enterprise Dashboard" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Green

& $pythonExe start_system.py --mode $Mode --backend-port $BackendPort --frontend-port $FrontendPort
