# Deploy Final Seguro

Este roteiro fecha a entrega do teste tecnico Lifeline One em ambiente publicado com HTTPS.
Nao coloque senhas, tokens ou chaves reais no Git. Use sempre variaveis de ambiente do provedor.

## Arquitetura Recomendada

- Backend: FastAPI em Render, Railway, Fly.io ou VPS Docker.
- Banco: PostgreSQL gerenciado.
- Cache: Redis gerenciado.
- Frontend: Vercel, Netlify, Cloudflare Pages ou host estatico com Nginx.

## Variaveis Obrigatorias da API

Configure no provedor da API:

```env
ENVIRONMENT=production
DATABASE_URL=postgresql://usuario:senha-url-encoded@host:5432/database
REDIS_URL=redis://host:6379/0
SECRET_KEY=gere-uma-chave-aleatoria-com-mais-de-32-caracteres
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://seu-frontend.com
SQL_ECHO=false
```

Regras de seguranca:

- `SECRET_KEY` precisa ser unica do ambiente e nao deve aparecer no repositorio.
- `CORS_ORIGINS` deve conter apenas o dominio HTTPS real do frontend.
- `SQL_ECHO` deve ficar `false` em producao.
- Senhas com caracteres especiais precisam estar URL-encoded dentro de `DATABASE_URL`.

## Backend

Com Docker:

```bash
docker build -t lifeline-api ./backend
docker run --env-file .env -p 8000:8000 lifeline-api
```

Antes de liberar o acesso ao avaliador, rode a migracao no ambiente publicado:

```bash
alembic upgrade head
```

Endpoints para conferencia:

```text
GET /health
GET /docs
```

Rotas privadas devem responder `401` sem token:

```text
/clientes/
/kanban/
/dashboard/metricas
/usuarios/
/auth/me
```

## Frontend

Configure `frontend/public/config.js` antes do build:

```js
window.LIFELINE_API_BASE = "https://sua-api.com";
```

Build:

```bash
cd frontend
npm install
npm run build
```

Publique a pasta:

```text
frontend/dist
```

Se usar Nginx, adapte `frontend/nginx.example.conf` e troque:

```text
seu-frontend.com
https://api.seu-dominio.com
```

## Checklist de Validacao

- [ ] API publicada em HTTPS.
- [ ] Frontend publicado em HTTPS.
- [ ] `CORS_ORIGINS` aponta para o frontend real.
- [ ] `frontend/public/config.js` aponta para a API real.
- [ ] PostgreSQL conectado.
- [ ] Redis conectado ou fallback documentado funcionando.
- [ ] `alembic upgrade head` executado.
- [ ] Primeiro usuario administrador criado.
- [ ] Login e logout testados.
- [ ] Dashboard carrega metricas.
- [ ] CRUD de clientes testado: criar, listar, detalhar, editar e excluir.
- [ ] Filtros de clientes por nome e status testados.
- [ ] Kanban testado: criar, mover, editar, detalhar e excluir oportunidade.
- [ ] Usuarios e Acessos visivel apenas para Administrador.
- [ ] Usuario comum recebe bloqueio em rotas administrativas.
- [ ] Headers de seguranca aplicados no frontend.
- [ ] Rotas privadas retornam `401` sem token.

## Entrega ao Avaliador

Envie:

- URL do frontend.
- URL da API ou Swagger.
- Link do repositorio GitHub.
- Credenciais de um usuario de teste, se o avaliador solicitar.
- Observacao de que o primeiro cadastro cria o Administrador quando a base esta vazia.
