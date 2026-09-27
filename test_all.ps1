# test_all.ps1 - Automated test suite runner
Write-Host "Running complete test suite for Krone Enterprise Dashboard..." -ForegroundColor Cyan

$pythonExe = "C:\Users\Naveen\AppData\Local\Programs\Python\Python312\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

& $pythonExe -m pytest tests/ backend/tests/ -v --durations=10
