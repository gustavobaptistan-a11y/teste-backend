$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"
$python = Join-Path $root ".venv\Scripts\python.exe"

Write-Host "Testando backend..."
Set-Location $backend
& $python -m pytest -q

Write-Host "Testando frontend..."
Set-Location $frontend
npm run check
npm run test:security

Write-Host "Verificando servicos locais..."
try {
  Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get | ConvertTo-Json
} catch {
  Write-Warning "API nao respondeu em http://127.0.0.1:8000/health. Inicie scripts\start-local-backend.ps1."
}

try {
  $status = (Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:5500/").StatusCode
  Write-Host "Frontend HTTP status: $status"
} catch {
  Write-Warning "Frontend nao respondeu em http://127.0.0.1:5500. Inicie scripts\start-local-frontend.ps1."
}
