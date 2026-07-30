const etapas = ["Novo Lead", "Em Negociacao", "Proposta Enviada", "Fechado"];
const state = {
  view: "dashboard",
  clientes: [],
  leads: [],
  usuarios: [],
  clienteFilters: { nome: "", ativo: "" },
  clientesPage: { skip: 0, limit: 10 },
  usuariosPage: { skip: 0, limit: 10 },
  loading: false,
  setupOpen: false,
  token: sessionStorage.getItem("lifeline_token"),
  usuario: null,
};

const els = {
  status: document.querySelector("#status"),
  viewTitle: document.querySelector("#viewTitle"),
  refreshButton: document.querySelector("#refreshButton"),
  logoutButton: document.querySelector("#logoutButton"),
  navButtons: document.querySelectorAll(".nav-button[data-view]"),
  adminOnly: document.querySelectorAll(".admin-only"),
  views: document.querySelectorAll(".view"),
  authView: document.querySelector("#authView"),
  privateArea: document.querySelector("#privateArea"),
  userBox: document.querySelector("#userBox"),
  setupPanel: document.querySelector("#setupPanel"),
  loginForm: document.querySelector("#loginForm"),
  registerForm: document.querySelector("#registerForm"),
  clienteFilterForm: document.querySelector("#clienteFilterForm"),
  clearClienteFilters: document.querySelector("#clearClienteFilters"),
  clienteForm: document.querySelector("#clienteForm"),
  clienteEditForm: document.querySelector("#clienteEditForm"),
  cancelClienteEdit: document.querySelector("#cancelClienteEdit"),
  clienteDetail: document.querySelector("#clienteDetail"),
  clientesTable: document.querySelector("#clientesTable"),
  prevClientesPage: document.querySelector("#prevClientesPage"),
  nextClientesPage: document.querySelector("#nextClientesPage"),
  clientesPageInfo: document.querySelector("#clientesPageInfo"),
  leadForm: document.querySelector("#leadForm"),
  leadEditForm: document.querySelector("#leadEditForm"),
  cancelLeadEdit: document.querySelector("#cancelLeadEdit"),
  leadDetail: document.querySelector("#leadDetail"),
  kanbanBoard: document.querySelector("#kanbanBoard"),
  usuarioCreateForm: document.querySelector("#usuarioCreateForm"),
  usuarioEditForm: document.querySelector("#usuarioEditForm"),
  cancelUsuarioEdit: document.querySelector("#cancelUsuarioEdit"),
  usuariosTable: document.querySelector("#usuariosTable"),
  prevUsuariosPage: document.querySelector("#prevUsuariosPage"),
  nextUsuariosPage: document.querySelector("#nextUsuariosPage"),
  usuariosPageInfo: document.querySelector("#usuariosPageInfo"),
  metricClientes: document.querySelector("#metricClientes"),
  metricLeads: document.querySelector("#metricLeads"),
  metricValor: document.querySelector("#metricValor"),
  metricConversao: document.querySelector("#metricConversao"),
  stageSummary: document.querySelector("#stageSummary"),
};

const API_BASE = window.LIFELINE_API_BASE;

function apiUrl(path) {
  if (!API_BASE) {
    throw new Error("Configuracao da API ausente. Verifique frontend/config.js.");
  }
  return `${API_BASE.replace(/\/$/, "")}${path}`;
}

function money(value) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(Number(value || 0));
}

function setStatus(message, ok = false) {
  els.status.textContent = message;
  els.status.classList.toggle("ok", ok);
}

function setBusy(isBusy) {
  state.loading = isBusy;
  document.querySelectorAll("button").forEach((button) => {
    button.disabled = isBusy;
  });
  updatePagers();
}

function updatePagers() {
  if (!els.prevClientesPage || !els.prevUsuariosPage) {
    return;
  }
  els.prevClientesPage.disabled = state.loading || state.clientesPage.skip === 0;
  els.nextClientesPage.disabled = state.loading || state.clientes.length < state.clientesPage.limit;
  els.prevUsuariosPage.disabled = state.loading || state.usuariosPage.skip === 0;
  els.nextUsuariosPage.disabled = state.loading || state.usuarios.length < state.usuariosPage.limit;
}

function confirmAction(message) {
  return window.confirm(message);
}

async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (!(options.body instanceof URLSearchParams)) {
    headers["Content-Type"] = "application/json";
  }
  if (state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }

  let response;
  try {
    response = await fetch(apiUrl(path), { ...options, headers });
  } catch {
    throw new Error("API indisponivel. Inicie o backend em http://127.0.0.1:8000.");
  }

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (response.status === 401) {
      clearSession(false);
    }
    throw new Error(data.detail || "Nao foi possivel concluir a operacao.");
  }
  return data;
}

function clearSession(showMessage = true) {
  state.token = null;
  state.usuario = null;
  state.usuarios = [];
  sessionStorage.removeItem("lifeline_token");
  switchView("dashboard");
  updateAuthUi();
  if (showMessage) {
    setStatus("Sessao encerrada.", true);
  }
}

function formData(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function clientePayloadFromForm(form) {
  const payload = formData(form);
  if ("ativo" in payload) {
    payload.ativo = payload.ativo === "true";
  }
  return payload;
}

function clientesQueryString() {
  const params = new URLSearchParams();
  if (state.clienteFilters.nome) {
    params.set("nome", state.clienteFilters.nome);
  }
  if (state.clienteFilters.ativo) {
    params.set("ativo", state.clienteFilters.ativo);
  }
  params.set("skip", state.clientesPage.skip);
  params.set("limit", state.clientesPage.limit);
  const query = params.toString();
  return query ? `?${query}` : "";
}

function usuariosQueryString() {
  const params = new URLSearchParams();
  params.set("skip", state.usuariosPage.skip);
  params.set("limit", state.usuariosPage.limit);
  return `?${params.toString()}`;
}

function isAdmin() {
  return state.usuario?.permissao === "Administrador";
}

function updateAuthUi() {
  const authenticated = Boolean(state.token && state.usuario);
  els.authView.classList.toggle("hidden", authenticated);
  els.privateArea.classList.toggle("hidden", !authenticated);
  document.body.classList.toggle("logged-out", !authenticated);
  els.setupPanel.classList.toggle("hidden", !state.setupOpen || authenticated);

  els.adminOnly.forEach((el) => el.classList.toggle("hidden", !isAdmin()));
  els.logoutButton.style.display = authenticated ? "block" : "none";
  els.userBox.innerHTML = authenticated
    ? `<strong>${state.usuario.nome}</strong><span>${state.usuario.permissao}</span>`
    : "";
}

function switchView(view) {
  if (view === "usuarios" && !isAdmin()) {
    setStatus("Acesso restrito a administradores.");
    return;
  }

  state.view = view;
  els.viewTitle.textContent = view === "kanban" ? "Kanban" : view[0].toUpperCase() + view.slice(1);
  els.navButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.view === view);
  });
  els.views.forEach((section) => {
    section.classList.toggle("active", section.id === `${view}View`);
  });
}

function renderClientes() {
  const page = Math.floor(state.clientesPage.skip / state.clientesPage.limit) + 1;
  els.clientesPageInfo.textContent = `Pagina ${page}`;
  els.prevClientesPage.disabled = state.clientesPage.skip === 0 || state.loading;
  els.nextClientesPage.disabled = state.clientes.length < state.clientesPage.limit || state.loading;

  if (!state.clientes.length) {
    els.clientesTable.innerHTML = '<tr><td colspan="6">Nenhum cliente encontrado.</td></tr>';
    return;
  }

  els.clientesTable.innerHTML = state.clientes
    .map(
      (cliente) => `
        <tr>
          <td>${cliente.nome}</td>
          <td>${cliente.email}</td>
          <td>${cliente.telefone}</td>
          <td>${cliente.empresa || "-"}</td>
          <td>${cliente.origem || "-"}</td>
          <td>${cliente.ativo ? "Ativo" : "Inativo"}</td>
          <td>
            <div class="row-actions">
              <button class="ghost-button" data-detail-cliente="${cliente.id}">Detalhes</button>
              <button class="ghost-button" data-edit-cliente="${cliente.id}">Editar</button>
              <button class="ghost-button" data-delete-cliente="${cliente.id}">Excluir</button>
            </div>
          </td>
        </tr>
      `,
    )
    .join("");
}

function renderClienteDetail(cliente) {
  els.clienteDetail.innerHTML = `
    <div class="detail-item"><span>Nome</span><strong>${cliente.nome}</strong></div>
    <div class="detail-item"><span>E-mail</span><strong>${cliente.email}</strong></div>
    <div class="detail-item"><span>Telefone</span><strong>${cliente.telefone}</strong></div>
    <div class="detail-item"><span>Empresa</span><strong>${cliente.empresa || "-"}</strong></div>
    <div class="detail-item"><span>Origem</span><strong>${cliente.origem || "-"}</strong></div>
    <div class="detail-item"><span>Status</span><strong>${cliente.ativo ? "Ativo" : "Inativo"}</strong></div>
    <div class="detail-item"><span>Observacoes</span><strong>${cliente.observacoes || "-"}</strong></div>
  `;
  els.clienteDetail.classList.remove("hidden");
}

function fillClienteEditForm(cliente) {
  els.clienteEditForm.elements.id.value = cliente.id;
  els.clienteEditForm.elements.nome.value = cliente.nome;
  els.clienteEditForm.elements.email.value = cliente.email;
  els.clienteEditForm.elements.telefone.value = cliente.telefone;
  els.clienteEditForm.elements.empresa.value = cliente.empresa || "";
  els.clienteEditForm.elements.origem.value = cliente.origem || "";
  els.clienteEditForm.elements.observacoes.value = cliente.observacoes || "";
  els.clienteEditForm.elements.ativo.value = String(cliente.ativo);
  els.clienteEditForm.classList.remove("hidden");
  els.clienteDetail.classList.add("hidden");
}

function resetClienteEdit() {
  els.clienteEditForm.reset();
  els.clienteEditForm.classList.add("hidden");
}

function fillUsuarioEditForm(usuario) {
  els.usuarioEditForm.elements.id.value = usuario.id;
  els.usuarioEditForm.elements.nome.value = usuario.nome;
  els.usuarioEditForm.elements.email.value = usuario.email;
  els.usuarioEditForm.elements.permissao.value = usuario.permissao;
  els.usuarioEditForm.elements.ativo.value = String(usuario.ativo);
  els.usuarioEditForm.classList.remove("hidden");
}

function resetUsuarioEdit() {
  els.usuarioEditForm.reset();
  els.usuarioEditForm.classList.add("hidden");
}

function renderLeadDetail(lead) {
  els.leadDetail.innerHTML = `
    <div class="detail-item"><span>Titulo</span><strong>${lead.titulo}</strong></div>
    <div class="detail-item"><span>Cliente</span><strong>${lead.cliente_nome}</strong></div>
    <div class="detail-item"><span>Valor</span><strong>${money(lead.valor)}</strong></div>
    <div class="detail-item"><span>Etapa</span><strong>${lead.etapa}</strong></div>
    <div class="detail-item"><span>Descricao</span><strong>${lead.descricao || "-"}</strong></div>
  `;
  els.leadDetail.classList.remove("hidden");
}

function fillLeadEditForm(lead) {
  els.leadEditForm.elements.id.value = lead.id;
  els.leadEditForm.elements.titulo.value = lead.titulo;
  els.leadEditForm.elements.cliente_nome.value = lead.cliente_nome;
  els.leadEditForm.elements.valor.value = lead.valor;
  els.leadEditForm.elements.etapa.value = lead.etapa;
  els.leadEditForm.elements.descricao.value = lead.descricao || "";
  els.leadEditForm.classList.remove("hidden");
  els.leadDetail.classList.add("hidden");
}

function resetLeadEdit() {
  els.leadEditForm.reset();
  els.leadEditForm.classList.add("hidden");
}

function leadCard(lead) {
  const currentIndex = etapas.indexOf(lead.etapa);
  const nextStage = etapas[Math.min(currentIndex + 1, etapas.length - 1)];
  const prevStage = etapas[Math.max(currentIndex - 1, 0)];

  return `
    <article class="lead-card" draggable="true" data-lead-card="${lead.id}">
      <strong>${lead.titulo}</strong>
      <span class="lead-meta">${lead.cliente_nome} - ${money(lead.valor)}</span>
      ${lead.descricao ? `<span class="lead-meta">${lead.descricao}</span>` : ""}
      <div class="lead-actions">
        <button class="ghost-button" data-detail-lead="${lead.id}">Detalhes</button>
        <button class="ghost-button" data-edit-lead="${lead.id}">Editar</button>
        <button class="ghost-button" data-move-lead="${lead.id}" data-stage="${prevStage}">Voltar</button>
        <button class="ghost-button" data-move-lead="${lead.id}" data-stage="${nextStage}">Avancar</button>
        <button class="ghost-button" data-delete-lead="${lead.id}">Excluir</button>
      </div>
    </article>
  `;
}

function renderKanban() {
  els.kanbanBoard.innerHTML = etapas
    .map((etapa) => {
      const leads = state.leads.filter((lead) => lead.etapa === etapa);
      return `
        <section class="kanban-column">
          <header>
            <h3>${etapa}</h3>
            <strong>${leads.length}</strong>
          </header>
          <div class="lead-list" data-drop-stage="${etapa}">
            ${leads.map(leadCard).join("") || '<span class="lead-meta">Nenhuma oportunidade nesta etapa.</span>'}
          </div>
        </section>
      `;
    })
    .join("");
}

function renderDashboard(metricas) {
  els.metricClientes.textContent = metricas.clientes.total_ativos;
  els.metricLeads.textContent = metricas.pipeline.total_oportunidades;
  els.metricValor.textContent = money(metricas.pipeline.valor_total_estimado);
  els.metricConversao.textContent = `${metricas.desempenho.taxa_conversao_percentual}%`;

  const distribuicao = metricas.pipeline.distribuicao_por_etapa;
  els.stageSummary.innerHTML = etapas
    .map(
      (etapa) => `
        <article class="stage-item">
          <span>${etapa}</span>
          <strong>${distribuicao[etapa] || 0}</strong>
        </article>
      `,
    )
    .join("");
}

function renderUsuarios() {
  const page = Math.floor(state.usuariosPage.skip / state.usuariosPage.limit) + 1;
  els.usuariosPageInfo.textContent = `Pagina ${page}`;
  els.prevUsuariosPage.disabled = state.usuariosPage.skip === 0 || state.loading;
  els.nextUsuariosPage.disabled = state.usuarios.length < state.usuariosPage.limit || state.loading;

  if (!state.usuarios.length) {
    els.usuariosTable.innerHTML = '<tr><td colspan="5">Nenhum usuario encontrado.</td></tr>';
    return;
  }

  els.usuariosTable.innerHTML = state.usuarios
    .map(
      (usuario) => `
        <tr>
          <td>${usuario.nome}</td>
          <td>${usuario.email}</td>
          <td>
            <select data-user-permission="${usuario.id}">
              <option ${usuario.permissao === "Administrador" ? "selected" : ""}>Administrador</option>
              <option ${usuario.permissao === "Usuario Comum" ? "selected" : ""}>Usuario Comum</option>
            </select>
          </td>
          <td>${usuario.ativo ? "Ativo" : "Inativo"}</td>
          <td>
            <div class="row-actions">
              <button class="ghost-button" data-edit-user="${usuario.id}">Editar</button>
              <button class="ghost-button" data-toggle-user="${usuario.id}" data-active="${!usuario.ativo}">
                ${usuario.ativo ? "Desativar" : "Ativar"}
              </button>
            </div>
          </td>
        </tr>
      `,
    )
    .join("");
}

async function loadAll() {
  if (!state.token) {
    updateAuthUi();
    return;
  }

  setStatus("Carregando dados...");
  setBusy(true);
  try {
    const requests = [
      request(`/clientes/${clientesQueryString()}`),
      request("/kanban/"),
      request("/dashboard/metricas"),
    ];
    if (isAdmin()) {
      requests.push(request(`/usuarios/${usuariosQueryString()}`));
    }

    const [clientes, leads, metricas, usuarios = []] = await Promise.all(requests);
    state.clientes = clientes;
    state.leads = leads;
    state.usuarios = usuarios;
    renderClientes();
    resetClienteEdit();
    els.clienteDetail.classList.add("hidden");
    renderKanban();
    resetLeadEdit();
    els.leadDetail.classList.add("hidden");
    renderDashboard(metricas);
    renderUsuarios();
    resetUsuarioEdit();
    setStatus("Dados atualizados.", true);
  } finally {
    setBusy(false);
  }
}

async function hydrateSession() {
  await loadSetupStatus();

  if (!state.token) {
    updateAuthUi();
    return;
  }

  try {
    state.usuario = await request("/auth/me");
    updateAuthUi();
    await loadAll();
  } catch (error) {
    logout(false);
    setStatus(error.message);
  }
}

async function loadSetupStatus() {
  try {
    const data = await request("/usuarios/setup-status");
    state.setupOpen = Boolean(data.primeiro_acesso_aberto);
  } catch {
    state.setupOpen = false;
  }
}

async function login(email, senha) {
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", senha);

  const data = await request("/auth/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });

  state.token = data.access_token;
  state.usuario = data.usuario;
  sessionStorage.setItem("lifeline_token", state.token);
  updateAuthUi();
  await loadAll();
}

async function logout(showMessage = true, revokeRemote = true) {
  if (revokeRemote && state.token) {
    await request("/auth/logout", { method: "POST" }).catch(() => null);
  }

  clearSession(showMessage);
}

els.navButtons.forEach((button) => {
  button.addEventListener("click", () => switchView(button.dataset.view));
});

els.refreshButton.addEventListener("click", () => {
  loadAll().catch((error) => setStatus(error.message));
});

els.logoutButton.addEventListener("click", () => {
  if (confirmAction("Deseja encerrar sua sessao?")) {
    logout();
  }
});

els.loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formData(els.loginForm);
  try {
    await login(payload.email, payload.senha);
  } catch (error) {
    setStatus(error.message);
  }
});

els.registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formData(els.registerForm);
  try {
    await request("/usuarios/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    els.registerForm.reset();
    await login(payload.email, payload.senha);
  } catch (error) {
    setStatus(error.message);
  }
});

els.usuarioCreateForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formData(els.usuarioCreateForm);
  try {
    await request("/usuarios/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    els.usuarioCreateForm.reset();
    await loadAll();
    setStatus("Usuario criado.", true);
  } catch (error) {
    setStatus(error.message);
  }
});

els.clienteFilterForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formData(els.clienteFilterForm);
  state.clienteFilters = {
    nome: payload.nome.trim(),
    ativo: payload.ativo,
  };
  state.clientesPage.skip = 0;
  await loadAll().catch((error) => setStatus(error.message));
});

els.clearClienteFilters.addEventListener("click", async () => {
  els.clienteFilterForm.reset();
  state.clienteFilters = { nome: "", ativo: "" };
  state.clientesPage.skip = 0;
  await loadAll().catch((error) => setStatus(error.message));
});

els.prevClientesPage.addEventListener("click", async () => {
  state.clientesPage.skip = Math.max(0, state.clientesPage.skip - state.clientesPage.limit);
  await loadAll().catch((error) => setStatus(error.message));
});

els.nextClientesPage.addEventListener("click", async () => {
  state.clientesPage.skip += state.clientesPage.limit;
  await loadAll().catch((error) => setStatus(error.message));
});

els.clienteForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await request("/clientes/", {
      method: "POST",
      body: JSON.stringify(formData(els.clienteForm)),
    });
    els.clienteForm.reset();
    await loadAll();
  } catch (error) {
    setStatus(error.message);
  }
});

els.clienteEditForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = clientePayloadFromForm(els.clienteEditForm);
  const clienteId = payload.id;
  delete payload.id;

  try {
    await request(`/clientes/${clienteId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
    await loadAll();
    setStatus("Cliente atualizado.", true);
  } catch (error) {
    setStatus(error.message);
  }
});

els.cancelClienteEdit.addEventListener("click", () => {
  resetClienteEdit();
});

els.usuarioEditForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formData(els.usuarioEditForm);
  const usuarioId = payload.id;
  delete payload.id;
  payload.ativo = payload.ativo === "true";

  try {
    await request(`/usuarios/${usuarioId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
    await loadAll();
    setStatus("Usuario atualizado.", true);
  } catch (error) {
    setStatus(error.message);
  }
});

els.cancelUsuarioEdit.addEventListener("click", () => {
  resetUsuarioEdit();
});

els.prevUsuariosPage.addEventListener("click", async () => {
  state.usuariosPage.skip = Math.max(0, state.usuariosPage.skip - state.usuariosPage.limit);
  await loadAll().catch((error) => setStatus(error.message));
});

els.nextUsuariosPage.addEventListener("click", async () => {
  state.usuariosPage.skip += state.usuariosPage.limit;
  await loadAll().catch((error) => setStatus(error.message));
});

els.leadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formData(els.leadForm);
  payload.valor = Number(payload.valor);

  try {
    await request("/kanban/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    els.leadForm.reset();
    await loadAll();
  } catch (error) {
    setStatus(error.message);
  }
});

els.leadEditForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formData(els.leadEditForm);
  const leadId = payload.id;
  delete payload.id;
  payload.valor = Number(payload.valor);

  try {
    await request(`/kanban/${leadId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
    await loadAll();
    setStatus("Lead atualizado.", true);
  } catch (error) {
    setStatus(error.message);
  }
});

els.cancelLeadEdit.addEventListener("click", () => {
  resetLeadEdit();
});

document.addEventListener("click", async (event) => {
  const detailClienteId = event.target.dataset.detailCliente;
  const editClienteId = event.target.dataset.editCliente;
  const clienteId = event.target.dataset.deleteCliente;
  const detailLeadId = event.target.dataset.detailLead;
  const editLeadId = event.target.dataset.editLead;
  const leadId = event.target.dataset.deleteLead;
  const moveLeadId = event.target.dataset.moveLead;
  const editUserId = event.target.dataset.editUser;
  const toggleUserId = event.target.dataset.toggleUser;

  try {
    if (detailClienteId) {
      const cliente = await request(`/clientes/${detailClienteId}`);
      resetClienteEdit();
      renderClienteDetail(cliente);
    }

    if (editClienteId) {
      const cliente = await request(`/clientes/${editClienteId}`);
      fillClienteEditForm(cliente);
    }

    if (clienteId) {
      if (!confirmAction("Excluir este cliente? Esta acao nao pode ser desfeita.")) {
        return;
      }
      await request(`/clientes/${clienteId}`, { method: "DELETE" });
      await loadAll();
    }

    if (detailLeadId) {
      const lead = await request(`/kanban/${detailLeadId}`);
      resetLeadEdit();
      renderLeadDetail(lead);
    }

    if (editLeadId) {
      const lead = await request(`/kanban/${editLeadId}`);
      fillLeadEditForm(lead);
    }

    if (leadId) {
      if (!confirmAction("Excluir esta oportunidade? Esta acao nao pode ser desfeita.")) {
        return;
      }
      await request(`/kanban/${leadId}`, { method: "DELETE" });
      await loadAll();
    }

    if (moveLeadId) {
      await request(`/kanban/${moveLeadId}/etapa`, {
        method: "PATCH",
        body: JSON.stringify({ etapa: event.target.dataset.stage }),
      });
      await loadAll();
    }

    if (editUserId) {
      const usuario = state.usuarios.find((item) => String(item.id) === editUserId);
      if (usuario) {
        fillUsuarioEditForm(usuario);
      }
    }

    if (toggleUserId) {
      const action = event.target.dataset.active === "true" ? "ativar" : "desativar";
      if (!confirmAction(`Deseja ${action} este usuario?`)) {
        return;
      }
      await request(`/usuarios/${toggleUserId}/status`, {
        method: "PATCH",
        body: JSON.stringify({ ativo: event.target.dataset.active === "true" }),
      });
      await loadAll();
    }
  } catch (error) {
    setStatus(error.message);
  }
});

document.addEventListener("change", async (event) => {
  const userId = event.target.dataset.userPermission;
  if (!userId) {
    return;
  }

  try {
    if (!confirmAction("Alterar a permissao deste usuario?")) {
      await loadAll();
      return;
    }
    await request(`/usuarios/${userId}/permissao`, {
      method: "PATCH",
      body: JSON.stringify({ permissao: event.target.value }),
    });
    await loadAll();
  } catch (error) {
    setStatus(error.message);
  }
});

document.addEventListener("dragstart", (event) => {
  const card = event.target.closest("[data-lead-card]");
  if (!card) {
    return;
  }

  event.dataTransfer.setData("text/plain", card.dataset.leadCard);
  event.dataTransfer.effectAllowed = "move";
  card.classList.add("dragging");
});

document.addEventListener("dragend", (event) => {
  const card = event.target.closest("[data-lead-card]");
  if (card) {
    card.classList.remove("dragging");
  }
  document.querySelectorAll("[data-drop-stage]").forEach((list) => list.classList.remove("drag-over"));
});

document.addEventListener("dragover", (event) => {
  const list = event.target.closest("[data-drop-stage]");
  if (!list) {
    return;
  }

  event.preventDefault();
  event.dataTransfer.dropEffect = "move";
  list.classList.add("drag-over");
});

document.addEventListener("dragleave", (event) => {
  const list = event.target.closest("[data-drop-stage]");
  if (list && !list.contains(event.relatedTarget)) {
    list.classList.remove("drag-over");
  }
});

document.addEventListener("drop", async (event) => {
  const list = event.target.closest("[data-drop-stage]");
  if (!list) {
    return;
  }

  event.preventDefault();
  list.classList.remove("drag-over");
  const leadId = event.dataTransfer.getData("text/plain");
  const etapa = list.dataset.dropStage;
  const lead = state.leads.find((item) => String(item.id) === leadId);

  if (!lead || lead.etapa === etapa) {
    return;
  }

  try {
    await request(`/kanban/${leadId}/etapa`, {
      method: "PATCH",
      body: JSON.stringify({ etapa }),
    });
    await loadAll();
  } catch (error) {
    setStatus(error.message);
  }
});

hydrateSession();
