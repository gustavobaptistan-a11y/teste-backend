# Lifeline One - Painel de Gestao & CRM Comercial

Projeto fullstack para o teste tecnico da Lifeline One, com API FastAPI, PostgreSQL e frontend
operacional para CRM comercial.

## Estrutura

```text
backend/   API REST com FastAPI, JWT, SQLAlchemy e PostgreSQL
docs/      Checklist do briefing e roteiro de code review
frontend/  Interface React + Vite com login, dashboard, clientes, kanban e usuarios
```

Checklist minucioso do briefing: `docs/BRIEFING_CHECKLIST.md`.
Roteiro de code review: `docs/CODE_REVIEW.md`.
Guia de deploy: `docs/DEPLOY.md`.
Roteiro final de publicacao segura: `docs/DEPLOY_FINAL.md`.

## Requisitos atendidos

- Autenticacao com JWT.
- Cadastro e login de usuarios com senha hasheada.
- Rotas privadas protegidas por token.
- Gestao administrativa de usuarios com permissao e status.
- Politica de senha forte no cadastro e na troca de senha.
- Area "Meu perfil" com troca de senha autenticada.
- Configuracoes sensiveis fora do codigo.
- CRUD completo de clientes.
- Filtros de clientes por nome e status.
- Kanban comercial com movimentacao de oportunidades.
- Dashboard comercial com metricas consolidadas.
- PostgreSQL como banco relacional.
- Redis para cache de metricas do dashboard.
- Testes automatizados cobrindo autenticacao, permissoes e CRUD de clientes.
- Renderizacao protegida contra XSS em dados dinamicos do frontend.
- Configuracao de frontend por ambiente com exemplo para producao HTTPS.
- Frontend React + Vite com build de producao.

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
ENVIRONMENT=development
DATABASE_URL=postgresql://usuario:senha-forte@localhost:5432/lifeline_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=gere-uma-chave-com-pelo-menos-32-caracteres
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://127.0.0.1:5500,http://localhost:5500
SQL_ECHO=false
```

O primeiro usuario cadastrado recebe permissao `Administrador`. Os proximos entram como
`Usuario Comum`.

Testes:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest -q
```

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Acesse:

```text
http://127.0.0.1:5500
```

Configure a URL da API em `frontend/public/config.js` quando mudar de ambiente.
Use `frontend/public/config.example.js` como referencia para producao e aponte sempre para uma API em HTTPS.

Validacoes do frontend:

```powershell
cd frontend
npm run check
npm run test:security
npm run build
```

Para publicar o frontend estatico com headers de seguranca, use `frontend/nginx.example.conf` como base
ou replique os mesmos headers no provedor escolhido.

## Historico

Os repositorios separados de `backend` e `frontend` foram consolidados em um repositorio unico na raiz do
projeto. Backups locais dos historicos anteriores foram gerados em `.git-history/` e ficam fora do Git.

## Infra com Docker

Para subir API, PostgreSQL e Redis:

```powershell
copy .env.example .env
docker compose up -d --build
```

## Proxima etapa

Publicar o deploy final, se desejado, usando HTTPS e headers de seguranca no frontend.
