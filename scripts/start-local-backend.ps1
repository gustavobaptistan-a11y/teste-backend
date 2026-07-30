param(
  [int]$Port = 8010
)

$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$backend = Join-Path $root "backend"
$python = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
  throw "Ambiente virtual nao encontrado em .venv. Crie/ative a venv antes de iniciar."
}

if (-not (Test-Path -LiteralPath (Join-Path $backend ".env"))) {
  throw "backend\.env nao encontrado. Rode scripts\setup-local-postgres.ps1 primeiro."
}

Set-Location $backend
& $python -m uvicorn app.main:app --host 127.0.0.1 --port $Port --reload
