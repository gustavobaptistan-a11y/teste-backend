# Checklist do Briefing

Mapeamento dos requisitos do teste tecnico Lifeline One para a implementacao atual.

## Modulo 1 - Autenticacao e Seguranca

- [x] Cadastro de usuarios.
- [x] Login seguro.
- [x] Autenticacao baseada em JWT.
- [x] Senhas armazenadas com hash bcrypt.
- [x] Rotas privadas protegidas por token.
- [x] Bloqueio de login para contas inativas.
- [x] Controle de permissao para rotas administrativas.
- [x] `SECRET_KEY`, CORS e expiracao do token configuraveis por ambiente.
- [x] Politica de senha forte no cadastro.
- [x] Segredos removidos do codigo e do Docker Compose.
- [x] Token no frontend armazenado apenas em `sessionStorage`.
- [x] Headers HTTP basicos de seguranca na API.
- [x] Cadastro publico permitido somente para bootstrap do primeiro administrador.
- [x] Criacao posterior de usuarios restrita a administradores.
- [x] Configuracao de API removida da tela de login.

## Modulo 2 - Gestao de Clientes

- [x] Criar cliente.
- [x] Listar clientes.
- [x] Visualizar detalhes do cliente.
- [x] Editar cliente.
- [x] Excluir cliente.
- [x] Filtrar por nome.
- [x] Filtrar por status ativo/inativo.
- [x] Campos comerciais: empresa, origem e observacoes.
- [x] Persistencia em PostgreSQL.

## Modulo 3 - Kanban Comercial

- [x] Quadro visual em colunas.
- [x] Criacao de oportunidades.
- [x] Movimentacao entre etapas comerciais.
- [x] Exclusao de oportunidades.
- [x] Persistencia em PostgreSQL.
- [x] Movimentacao por drag-and-drop no frontend.

## Modulo 4 - Dashboard Comercial

- [x] Total de clientes ativos.
- [x] Volume de oportunidades no Kanban.
- [x] Valor estimado do pipeline.
- [x] Distribuicao por etapa.
- [x] Taxa de conversao simples.
- [x] Cache de metricas com Redis.
- [x] Fallback para PostgreSQL se Redis estiver indisponivel.
- [x] Invalidacao de cache ao alterar clientes ou leads.

## Modulo 5 - Configuracoes e Gestao de Usuarios

- [x] Pagina administrativa de usuarios.
- [x] Listagem de usuarios cadastrados.
- [x] Alteracao de permissao.
- [x] Ativacao/desativacao de contas.
- [x] Acesso restrito a administradores.
- [x] Edicao de nome/e-mail do usuario pelo frontend.

## Stack Obrigatoria

- [x] Python/FastAPI.
- [x] Endpoints RESTful.
- [x] Validacao com Pydantic.
- [x] JWT.
- [x] PostgreSQL.
- [x] Redis.
- [x] Frontend limpo e responsivo.

## Entregaveis

- [x] Repositorio organizado como projeto fullstack.
- [x] README de execucao.
- [x] `docker-compose.yml`.
- [x] Testes automatizados de seguranca e CRUD.
- [ ] Deploy publicado.
- [x] Roteiro de code review final.
