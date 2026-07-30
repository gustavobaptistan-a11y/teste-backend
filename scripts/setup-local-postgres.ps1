param(
  [string]$DatabaseName = "lifeline_db",
  [string]$AppUser = "lifeline_user"
)

$ErrorActionPreference = "Stop"

if ($DatabaseName -notmatch "^[A-Za-z_][A-Za-z0-9_]*$") {
  throw "Nome de banco invalido. Use apenas letras, numeros e underscore, sem iniciar por numero."
}

if ($AppUser -notmatch "^[A-Za-z_][A-Za-z0-9_]*$") {
  throw "Nome de usuario invalido. Use apenas letras, numeros e underscore, sem iniciar por numero."
}

$psqlCandidates = @(
  "C:\Program Files\PostgreSQL\18\bin\psql.exe",
  "C:\Program Files\PostgreSQL\18\pgAdmin 4\runtime\psql.exe"
)

$psql = $psqlCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $psql) {
  throw "psql.exe nao encontrado. Instale PostgreSQL 18 ou adicione psql ao PATH."
}

function Read-PlainSecret([string]$Prompt) {
  $secure = Read-Host $Prompt -AsSecureString
  $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
  try {
    return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
  } finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
  }
}

$postgresPassword = Read-PlainSecret "Senha do usuario postgres local"
$appPassword = Read-PlainSecret "Senha nova para o usuario lifeline_user"
$appPasswordSql = $appPassword.Replace("'", "''")
$appPasswordUrl = [Uri]::EscapeDataString($appPassword)

$env:PGPASSWORD = $postgresPassword

$roleExists = & $psql -h 127.0.0.1 -U postgres -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname = '$AppUser';"
if ($LASTEXITCODE -ne 0) {
  throw "Nao foi possivel conectar ao PostgreSQL local como postgres."
}

if (-not $roleExists) {
  & $psql -h 127.0.0.1 -U postgres -d postgres -c "CREATE USER $AppUser WITH PASSWORD '$appPasswordSql';"
} else {
  & $psql -h 127.0.0.1 -U postgres -d postgres -c "ALTER USER $AppUser WITH PASSWORD '$appPasswordSql';"
}

$dbExists = & $psql -h 127.0.0.1 -U postgres -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$DatabaseName';"
if (-not $dbExists) {
  & $psql -h 127.0.0.1 -U postgres -d postgres -c "CREATE DATABASE $DatabaseName OWNER $AppUser;"
}

& $psql -h 127.0.0.1 -U postgres -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DatabaseName TO $AppUser;"

$ownershipSql = @"
ALTER SCHEMA public OWNER TO $AppUser;
GRANT ALL ON SCHEMA public TO $AppUser;
DO `$`$
DECLARE
  item record;
BEGIN
  FOR item IN
    SELECT tablename AS name FROM pg_tables WHERE schemaname = 'public'
  LOOP
    EXECUTE format('ALTER TABLE public.%I OWNER TO $AppUser', item.name);
  END LOOP;

  FOR item IN
    SELECT sequencename AS name FROM pg_sequences WHERE schemaname = 'public'
  LOOP
    EXECUTE format('ALTER SEQUENCE public.%I OWNER TO $AppUser', item.name);
  END LOOP;
END
`$`$;
"@

& $psql -h 127.0.0.1 -U postgres -d $DatabaseName -c $ownershipSql

$env:PGPASSWORD = $appPassword
& $psql -h 127.0.0.1 -U $AppUser -d $DatabaseName -c "SELECT 1;"
if ($LASTEXITCODE -ne 0) {
  throw "Banco criado, mas o usuario da aplicacao nao conseguiu conectar."
}

$secretKey = & python -c "import secrets; print(secrets.token_urlsafe(48))"
$envPath = Join-Path $PSScriptRoot "..\backend\.env"
$envContent = @"
ENVIRONMENT=development
DATABASE_URL=postgresql+psycopg://${AppUser}:${appPasswordUrl}@127.0.0.1:5432/$DatabaseName
REDIS_URL=
SECRET_KEY=$secretKey
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://127.0.0.1:5500,http://localhost:5500
SQL_ECHO=false
"@

Set-Content -Path $envPath -Value $envContent -Encoding UTF8
$env:PGPASSWORD = $null
Write-Host "PostgreSQL local configurado e backend\.env atualizado."
Write-Host "Redis ficou desativado localmente. A API usara fallback seguro para o PostgreSQL."
