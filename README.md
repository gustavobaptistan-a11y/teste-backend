# Lifeline One - Painel de Gestao & CRM Comercial

Projeto fullstack para o teste tecnico da Lifeline One, com API FastAPI, PostgreSQL e frontend
operacional para CRM comercial.

## Estrutura

```text
backend/   API REST com FastAPI, JWT, SQLAlchemy e PostgreSQL
frontend/  Interface web estatica com login, dashboard, clientes, kanban e usuarios
```

## Requisitos atendidos

- Autenticacao com JWT.
- Cadastro e login de usuarios com senha hasheada.
- Rotas privadas protegidas por token.
- Gestao administrativa de usuarios com permissao e status.
- CRUD completo de clientes.
- Filtros de clientes por nome e status.
- Kanban comercial com movimentacao de oportunidades.
- Dashboard comercial com metricas consolidadas.
- PostgreSQL como banco relacional.

## Backend

```powershell
cd backend
..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

A API fica em `http://127.0.0.1:8000`.

Swagger:

```text
http://127.0.0.1:8000/docs
```

Configure `backend/.env`:

```env
DATABASE_URL=postgresql://usuario:senha@localhost:5432/lifeline_db
```

O primeiro usuario cadastrado recebe permissao `Administrador`. Os proximos entram como
`Usuario Comum`.

## Frontend

```powershell
cd frontend
python -m http.server 5500 --bind 127.0.0.1
```

Acesse:

```text
http://127.0.0.1:5500
```

## Historico

Os repositorios separados de `backend` e `frontend` foram consolidados em um repositorio unico na raiz do
projeto. Backups locais dos historicos anteriores foram gerados em `.git-history/` e ficam fora do Git.

## Proxima etapa

Implementar Redis para cache de metricas do dashboard, conforme briefing.
