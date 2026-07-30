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
- Redis tambem e usado para revogacao de token no logout.
- Fallback para PostgreSQL quando Redis nao esta disponivel.
- Alembic foi configurado para migracoes versionadas de banco.
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
- Usuarios autenticados podem trocar a propria senha somente informando a senha atual.
- Apos troca de senha, o frontend limpa a sessao e exige novo login.
- O formulario de primeiro acesso aparece apenas quando ainda nao existe usuario.
- Depois do bootstrap inicial, somente administradores podem criar usuarios.
- Configuracao da URL da API nao e exibida na tela de login.
- Campos dinamicos renderizados no frontend passam por escape para reduzir risco de XSS.
- Acoes destrutivas e mudancas sensiveis usam confirmacao em modal controlado.
- Campos de senha usam `autocomplete` adequado para reduzir preenchimento incorreto.
- `frontend/nginx.example.conf` documenta headers de seguranca para publicacao do frontend.
- `frontend/config.example.js` documenta a URL HTTPS esperada para a API em producao.
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
6. Abrir "Meu perfil", trocar a senha e confirmar novo login obrigatorio.
7. Tentar acessar rotas privadas sem token e confirmar `401`.
8. Tentar acessar gestao de usuarios com usuario comum e confirmar `403`.

## Validacao

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest -q
```

Frontend:

```powershell
cd frontend
npm run check
npm run test:security
```

Resultado atual:

```text
13 passed
Frontend security checks passed.
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
- Reaplicar os headers de `frontend/nginx.example.conf` no provedor escolhido.
- Adicionar observabilidade/log estruturado para ambiente produtivo.
