Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " ShieldGuard AI - Entorno de Demostracion en Vivo" -ForegroundColor White
Write-Host " Golang Backend (:8080) + Angular Risk Console (:4200)" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$root = $PSScriptRoot
if (-not $root) { $root = (Get-Location).Path }

Write-Host "[1/2] Iniciando Backend en Go (:8080)..." -ForegroundColor Green
Start-Process powershell -WorkingDirectory "$root\backend" -ArgumentList "-NoExit", "-Command", ".\shieldguard-backend.exe"

Start-Sleep -Seconds 2

Write-Host "[2/2] Iniciando Frontend en Angular (:4200)..." -ForegroundColor Green
Start-Process powershell -WorkingDirectory "$root\frontend" -ArgumentList "-NoExit", "-Command", "pnpm start"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " Todo listo! Abre tu navegador en:" -ForegroundColor Yellow
Write-Host " URL: http://localhost:4200" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
