# Lifeline One

Backend FastAPI com PostgreSQL e frontend estatico para gestao comercial.

## Backend

```bash
cd backend
..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

A API fica em `http://127.0.0.1:8000` e a documentacao Swagger em `http://127.0.0.1:8000/docs`.

Configure a conexao no arquivo `.env`:

```env
ENVIRONMENT=development
DATABASE_URL=postgresql://usuario:senha-forte@localhost:5432/lifeline_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=gere-uma-chave-com-pelo-menos-32-caracteres
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://127.0.0.1:5500,http://localhost:5500
SQL_ECHO=false
```

As tabelas `usuarios`, `clientes` e `leads` sao criadas automaticamente ao iniciar a API.

O primeiro usuario cadastrado recebe permissao `Administrador`. Os proximos usuarios entram como
`Usuario Comum` e podem ser gerenciados pela tela administrativa.

Rotas de clientes, kanban, dashboard e administracao de usuarios exigem JWT. No Swagger, faca login em
`/auth/token` e use o botao `Authorize` com o token retornado.

O cadastro exige senha com no minimo 8 caracteres, letra maiuscula, letra minuscula e numero.

## Frontend

```bash
cd ..\frontend
python -m http.server 5500 --bind 127.0.0.1
```

Acesse `http://127.0.0.1:5500`.

O frontend possui login/cadastro, painel comercial protegido e tela de usuarios visivel apenas para
administradores.

## Redis

O dashboard usa Redis para cache das metricas comerciais por 60 segundos. Alteracoes em clientes ou leads
invalidam o cache automaticamente.

Se o Redis nao estiver disponivel, a API continua funcionando e calcula as metricas direto do PostgreSQL.

## Testes

```bash
cd backend
..\.venv\Scripts\python.exe -m pytest -q
```

Os testes rodam com SQLite isolado e cobrem autenticacao, permissoes administrativas e CRUD de clientes.

## Migracoes

```bash
cd backend
..\.venv\Scripts\python.exe -m alembic upgrade head
```

O projeto tambem mantem criacao/migracao leve no startup para facilitar execucao local do teste.
