# Deploy Local no PC

Este roteiro e o formato combinado para apresentar o teste no seu proprio computador, sem provedor pago.

## URLs da Demonstracao

```text
Frontend: http://127.0.0.1:5500
API:      http://127.0.0.1:8000
Swagger:  http://127.0.0.1:8000/docs
Health:   http://127.0.0.1:8000/health
```

## 1. Configurar PostgreSQL Local

O PostgreSQL 18 precisa estar instalado e rodando.

Execute na raiz do projeto:

```powershell
.\scripts\setup-local-postgres.ps1
```

Se o PowerShell bloquear scripts locais, execute uma vez nesta janela:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

O script vai pedir:

- senha do usuario local `postgres`;
- senha nova para o usuario `lifeline_user`.

Ele cria:

```text
Database: lifeline_db
User:     lifeline_user
```

Tambem atualiza `backend\.env` com valores locais. Esse arquivo nao vai para o Git.

## 2. Rodar Migracoes

```powershell
cd backend
..\.venv\Scripts\python.exe -m alembic upgrade head
```

## 3. Iniciar Backend

Abra um terminal:

```powershell
.\scripts\start-local-backend.ps1
```

Confirme:

```text
http://127.0.0.1:8000/health
```

## 4. Iniciar Frontend

Abra outro terminal:

```powershell
.\scripts\start-local-frontend.ps1
```

Acesse:

```text
http://127.0.0.1:5500
```

## 5. Validar Antes da Apresentacao

```powershell
.\scripts\check-local.ps1
```

## Redis no Deploy Local

Redis e usado para cache de metricas e revogacao de token quando disponivel.
Se Redis nao estiver instalado no PC, a API continua funcionando com fallback seguro para PostgreSQL.

Para uma demonstracao local sem instalar mais nada, deixe:

```env
REDIS_URL=
```

Se instalar Redis local, use:

```env
REDIS_URL=redis://127.0.0.1:6379/0
```

## Roteiro Para o Avaliador

1. Abrir `http://127.0.0.1:5500`.
2. Criar primeiro usuario administrador se a base estiver vazia.
3. Fazer login.
4. Mostrar Dashboard.
5. Criar, listar, filtrar, detalhar, editar e excluir cliente.
6. Criar oportunidade no Kanban e mover entre etapas.
7. Mostrar Usuarios e Acessos como Administrador.
8. Mostrar Swagger e testar rota privada sem token retornando `401`.
