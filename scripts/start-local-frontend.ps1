$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$frontend = Join-Path $root "frontend"

Set-Location $frontend
npm run dev
