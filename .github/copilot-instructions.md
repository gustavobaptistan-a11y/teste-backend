# Instrucoes Para Assistentes De Codigo

Este projeto e um painel fullstack da Lifeline One com backend FastAPI e frontend React + Vite.
Ao criar, modificar ou refatorar codigo, siga estas diretrizes.

## Analise De Impacto

- Antes de alterar componentes, funcoes, servicos ou rotas, revise o contexto e os contratos existentes.
- Preserve os endpoints, payloads e formatos de resposta da API sempre que possivel.
- Evite refatoracoes amplas sem necessidade direta para a tarefa.
- Nao remova validacoes, confirmacoes ou protecoes existentes sem substituir por alternativa equivalente ou mais segura.
- Mantenha compatibilidade com o fluxo atual de autenticacao, clientes, kanban, dashboard, perfil e usuarios.

## Seguranca Em Primeiro Lugar

- Nunca exponha chaves de API, tokens, credenciais, segredos ou valores reais de `.env` no codigo cliente.
- O token de autenticacao do frontend deve permanecer em `sessionStorage`, salvo decisao arquitetural documentada e revisada.
- Nao use `localStorage` para token.
- Nao use `dangerouslySetInnerHTML`, `innerHTML`, `eval`, `new Function` ou manipulacao manual de `document.cookie`.
- Valide entradas de formulario antes de enviar dados sensiveis.
- Mantenha senha sempre em campos `type="password"` com `autocomplete` adequado.
- Preserve mensagens de erro de autenticacao genericas quando necessario para evitar enumeracao.
- Respeite controle de acesso: funcionalidades administrativas devem continuar restritas a administradores no frontend e no backend.
- Dados pessoais de clientes e usuarios devem aparecer somente nas telas autenticadas necessarias para o fluxo comercial.
- Para deploy, a API deve ser configurada por `frontend/public/config.js` e apontar para HTTPS em producao.

## Padrao Tecnologico

- O frontend e uma SPA em React + Vite.
- Nao use recursos exclusivos de Next.js, como `getStaticProps`, app router, server components ou APIs server-side do Next.
- Siga a arquitetura atual:
  - `frontend/src/App.jsx`
  - `frontend/src/services/api.js`
  - `frontend/src/utils/security.js`
  - `frontend/src/styles.css`
- Prefira componentes pequenos e funcoes auxiliares claras quando a mudanca crescer.
- Mantenha estilos alinhados ao painel CRM interno: visual profissional, denso, responsivo e sem aparencia de landing page.

## Qualidade E Validacao

- Escreva codigo limpo, legivel e modular.
- Se TypeScript for introduzido no futuro, tipar props, retornos de API e estados principais.
- Apos mudancas de frontend, rode:

```powershell
cd frontend
npm run check
npm run test:security
```

- Apos mudancas que possam afetar integracao, rode tambem:

```powershell
cd ..
.\.venv\Scripts\python.exe -m pytest backend\tests
```

- Para dependencias novas, rode:

```powershell
cd frontend
npm audit --audit-level=high
```

## Documentacao

- Atualize `README.md`, `docs/DEPLOY.md`, `docs/BRIEFING_CHECKLIST.md` ou `docs/CODE_REVIEW.md` quando a mudanca afetar execucao, seguranca, arquitetura ou requisitos do briefing.
- Explique brevemente mudancas criticas e informe testes manuais recomendados quando houver impacto de fluxo.
