# Deploy Local no PC

Este roteiro e o formato combinado para apresentar o teste no seu proprio computador, sem provedor pago.
Docker nao e obrigatorio para este roteiro. Use os scripts locais abaixo para subir backend e frontend.

## URLs da Demonstracao

```text
Frontend: http://127.0.0.1:5500
API:      http://127.0.0.1:8010
Swagger:  http://127.0.0.1:8010/docs
Health:   http://127.0.0.1:8010/health
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

Se o banco local ja tiver tabelas antigas e o Alembic informar que uma relacao ja existe, marque a versao atual:

```powershell
..\.venv\Scripts\python.exe -m alembic stamp head
```

## 3. Iniciar Backend

Abra um terminal:

```powershell
.\scripts\start-local-backend.ps1
```

Confirme:

```text
http://127.0.0.1:8010/health
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

Se o script avisar que API ou frontend nao responderam, inicie os dois terminais dos passos 3 e 4 e rode a validacao novamente.

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

O projeto usa o driver `psycopg` 3. A URL local do PostgreSQL pode usar:

```env
DATABASE_URL=postgresql+psycopg://lifeline_user:senha@127.0.0.1:5432/lifeline_db
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

## Entrega na Maquina

Antes da avaliacao, deixe prontos:

- Um terminal rodando `.\scripts\start-local-backend.ps1`.
- Um terminal rodando `.\scripts\start-local-frontend.ps1`.
- Navegador aberto em `http://127.0.0.1:5500`.
- Swagger disponivel em `http://127.0.0.1:8010/docs`.
- Credenciais de um usuario administrador de teste, se a base ja nao estiver vazia.
