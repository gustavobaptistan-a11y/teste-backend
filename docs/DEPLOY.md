# Guia de Deploy

Este projeto esta pronto para deploy em ambiente com Docker ou em servicos separados para API, banco,
Redis e frontend React/Vite.

## Opcao 1 - Docker em VPS

1. Configure variaveis seguras:

```env
ENVIRONMENT=production
POSTGRES_DB=lifeline_db
POSTGRES_USER=lifeline_user
POSTGRES_PASSWORD=gere-uma-senha-forte
DATABASE_URL=postgresql://lifeline_user:senha-url-encoded@postgres:5432/lifeline_db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=gere-uma-chave-com-pelo-menos-32-caracteres
CORS_ORIGINS=https://seu-frontend.com
SQL_ECHO=false
```

2. Suba os servicos:

```powershell
copy .env.example .env
docker compose up -d --build
```

3. Acesse a API:

```text
http://servidor:8000/docs
```

4. Configure `frontend/public/config.js` com a URL publica da API em HTTPS:

```js
window.LIFELINE_API_BASE = "https://api.seu-dominio.com";
```

5. Gere o build do frontend e sirva a pasta `frontend/dist` em Nginx, Apache, Vercel, Netlify ou outro host estatico:

```powershell
cd frontend
npm install
npm run build
```

Use `frontend/nginx.example.conf` como referencia quando usar Nginx.

## Opcao 2 - Servicos Gerenciados

- API: Render, Railway, Fly.io, Heroku-like ou VPS.
- PostgreSQL: banco gerenciado do provedor.
- Redis: Redis gerenciado do provedor.
- Frontend: Vercel, Netlify, GitHub Pages ou outro host estatico.

Variaveis obrigatorias da API:

```env
DATABASE_URL=
REDIS_URL=
SECRET_KEY=
CORS_ORIGINS=
```

## Checklist Antes de Publicar

- [ ] Trocar `SECRET_KEY`.
- [ ] Trocar `POSTGRES_PASSWORD`.
- [ ] Usar senha URL-encoded dentro de `DATABASE_URL` se ela tiver caracteres especiais.
- [ ] Definir `CORS_ORIGINS` com a URL real do frontend.
- [ ] Configurar `frontend/public/config.js` com a URL HTTPS real da API antes do build.
- [ ] Servir o frontend com `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy` e `Permissions-Policy`.
- [ ] Confirmar que `.env` nao esta versionado.
- [ ] Rodar `pytest -q`.
- [ ] Rodar `npm run check`, `npm run test:security` e `npm run build` dentro de `frontend`.
- [ ] Confirmar que o primeiro usuario admin foi criado.
- [ ] Testar login, dashboard, clientes, kanban e usuarios no ambiente publicado.

## GitHub

A versao fullstack foi publicada na branch `fullstack-main`.

O `main` remoto ainda preserva o historico antigo do backend. Para tornar a versao fullstack a principal,
abra um pull request da branch `fullstack-main` ou atualize a branch padrao do repositorio no GitHub.
