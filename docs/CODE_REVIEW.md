# Roteiro de Code Review

Este roteiro resume a implementacao do Painel de Gestao & CRM Comercial da Lifeline One para revisao
tecnica.

## Arquitetura

- `backend/app/main.py`: inicializacao da API, CORS, lifespan e registro de routers.
- `backend/app/api/`: rotas REST separadas por dominio.
- `backend/app/models.py`: modelos SQLAlchemy para usuarios, clientes e leads.
- `backend/app/schemas/`: schemas Pydantic de entrada e resposta.
- `backend/app/core/`: banco, seguranca JWT, dependencias de autenticacao e cache Redis.
- `frontend/`: interface web estatica consumindo a API via fetch.
- `docs/`: checklist do briefing e roteiro de revisao.

## Decisoes Principais

- JWT stateless para autenticacao.
- Bcrypt para armazenamento seguro de senha.
- PostgreSQL para dados relacionais.
- Redis para cache de metricas do dashboard com TTL de 60 segundos.
- Fallback para PostgreSQL quando Redis nao esta disponivel.
- Primeiro usuario cadastrado vira administrador para viabilizar o setup inicial.
- Rotas comerciais exigem usuario autenticado e ativo.
- Rotas de gestao de usuarios exigem permissao de administrador.

## Seguranca

- `SECRET_KEY`, expiracao de token e CORS ficam em variaveis de ambiente.
- Configuracoes sensiveis passam por `backend/app/core/config.py`.
- Em producao, `SECRET_KEY` ausente ou fraca bloqueia o startup.
- `docker-compose.yml` exige variaveis via `.env`, sem senha de banco hardcoded.
- Token do frontend fica em `sessionStorage`, reduzindo persistencia apos fechar a aba.
- Cadastro exige senha com no minimo 8 caracteres, maiuscula, minuscula e numero.
- Contas inativas nao conseguem autenticar.
- Usuarios comuns recebem `403` ao acessar endpoints administrativos.
- Senhas nunca sao retornadas pela API.
- `.env` fica fora do Git.

## Fluxos Para Demonstrar

1. Cadastrar primeiro usuario e confirmar permissao `Administrador`.
2. Fazer login e acessar dashboard.
3. Criar, detalhar, editar, filtrar e excluir cliente.
4. Criar lead no Kanban e arrastar entre colunas.
5. Abrir tela de usuarios como admin, alterar permissao e ativar/desativar conta.
6. Tentar acessar rotas privadas sem token e confirmar `401`.
7. Tentar acessar gestao de usuarios com usuario comum e confirmar `403`.

## Validacao

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest -q
```

Resultado atual:

```text
11 passed
```

## Execucao Local

API:

```powershell
cd backend
..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```powershell
cd frontend
python -m http.server 5500 --bind 127.0.0.1
```

Infra:

```powershell
docker compose up -d --build
```

## Pendencias Possiveis

- Publicar deploy final.
- Conectar o repositorio remoto definitivo e fazer push.
- Migrar frontend estatico para React/Next.js se o avaliador preferir uma stack mais robusta.
- Adicionar observabilidade/log estruturado para ambiente produtivo.
