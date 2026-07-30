$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"
$python = Join-Path $root ".venv\Scripts\python.exe"

Write-Host "Testando backend..."
Set-Location $backend
& $python -m pytest -q

Write-Host "Auditando dependencias Python..."
$auditAvailable = & $python -c "import importlib.util; raise SystemExit(0 if importlib.util.find_spec('pip_audit') else 1)"
if ($LASTEXITCODE -eq 0) {
  & $python -m pip_audit
  if ($LASTEXITCODE -ne 0) {
    Write-Warning "pip-audit encontrou vulnerabilidades. Revise a saida acima."
  }
} else {
  Write-Warning "pip-audit nao esta instalado. Instale com: $python -m pip install pip-audit"
}

Write-Host "Testando frontend..."
Set-Location $frontend
npm run check
npm run test:security

Write-Host "Verificando servicos locais..."
try {
  Invoke-RestMethod -Uri "http://127.0.0.1:8010/health" -Method Get | ConvertTo-Json
} catch {
  Write-Warning "API nao respondeu em http://127.0.0.1:8010/health. Inicie scripts\start-local-backend.ps1."
}

try {
  $status = (Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:5500/").StatusCode
  Write-Host "Frontend HTTP status: $status"
} catch {
  Write-Warning "Frontend nao respondeu em http://127.0.0.1:5500. Inicie scripts\start-local-frontend.ps1."
}
