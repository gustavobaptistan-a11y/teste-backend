import { useEffect, useMemo, useState } from "react";

import { apiRequest } from "./services/api.js";
import {
  assertStrongPassword,
  clearStoredToken,
  passwordMessage,
  readStoredToken,
  storeToken,
  strongPassword,
} from "./utils/security.js";

const etapas = ["Novo Lead", "Em Negociacao", "Proposta Enviada", "Fechado"];
const pageLimit = 10;

const initialClienteForm = {
  nome: "",
  email: "",
  telefone: "",
  empresa: "",
  origem: "",
  observacoes: "",
};

const initialLeadForm = {
  titulo: "",
  cliente_nome: "",
  valor: "",
  etapa: etapas[0],
  descricao: "",
};

const initialUserForm = {
  nome: "",
  email: "",
  senha: "",
};

const initialPasswordForm = {
  senha_atual: "",
  nova_senha: "",
  confirmar_nova_senha: "",
};

function money(value) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(Number(value || 0));
}

function statusClass(active) {
  return active ? "badge badge-green" : "badge badge-coral";
}

function userInitials(nome = "") {
  return (
    nome
      .split(" ")
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0])
      .join("")
      .toUpperCase() || "LO"
  );
}

function NavGroup({ label, items, view, onView }) {
  return (
    <div className="nav-group">
      <span className="nav-group-label">{label}</span>
      {items.map(([id, itemLabel, icon]) => (
        <button key={id} className={`nav-button ${view === id ? "active" : ""}`} type="button" onClick={() => onView(id)}>
          <span className="nav-icon" aria-hidden="true">
            {icon}
          </span>
          {itemLabel}
        </button>
      ))}
    </div>
  );
}

function ConfirmModal({ confirmation, onResolve }) {
  if (!confirmation) {
    return null;
  }

  return (
    <div className="modal" role="dialog" aria-modal="true" aria-labelledby="confirmTitle">
      <div className="modal-panel">
        <p className="eyebrow">Confirmacao segura</p>
        <h2 id="confirmTitle">Confirmar acao</h2>
        <p>{confirmation.message}</p>
        <div className="modal-actions">
          <button className="ghost-button" type="button" onClick={() => onResolve(false)}>
            Cancelar
          </button>
          <button className="primary-button" type="button" onClick={() => onResolve(true)} autoFocus>
            Confirmar
          </button>
        </div>
      </div>
    </div>
  );
}

function AuthView({ setupOpen, onLogin, onRegister, onError, status }) {
  const [login, setLogin] = useState({ email: "", senha: "" });
  const [register, setRegister] = useState(initialUserForm);
  const [recoveryOpen, setRecoveryOpen] = useState(false);

  async function submitLogin(event) {
    event.preventDefault();
    try {
      await onLogin(login.email, login.senha);
    } catch (error) {
      onError(error.message);
    }
  }

  async function submitRegister(event) {
    event.preventDefault();
    try {
      assertStrongPassword(register.senha);
      await onRegister(register);
      setRegister(initialUserForm);
    } catch (error) {
      onError(error.message);
    }
  }

  return (
    <main className="app-shell">
      <section className="auth-view">
        <div className="auth-brand" aria-label="Lifeline One">
          <div className="brand-mark" aria-hidden="true">
            L1
          </div>
          <strong>Lifeline One</strong>
        </div>
        <div className="auth-panel">
          <h2>Bem-vindo de volta</h2>
          <p className="auth-copy">Acesse o painel comercial da sua equipe.</p>
          <form className="auth-form" onSubmit={submitLogin}>
            <label className="auth-field">
              <span>E-mail corporativo</span>
              <input
                value={login.email}
                onChange={(event) => setLogin({ ...login, email: event.target.value })}
                type="email"
                placeholder="voce@empresa.com"
                autoComplete="username"
                required
              />
            </label>
            <label className="auth-field">
              <span>Senha</span>
              <input
                value={login.senha}
                onChange={(event) => setLogin({ ...login, senha: event.target.value })}
                type="password"
                placeholder="********"
                autoComplete="current-password"
                required
              />
            </label>
            <div className="auth-options">
              <button
                className="auth-link"
                type="button"
                onClick={() => setRecoveryOpen(true)}
              >
                Esqueci minha senha
              </button>
            </div>
            <button className="primary-button auth-submit" type="submit">
              ENTRAR
            </button>
          </form>

          {setupOpen && (
            <section className="setup-panel">
              <div className="divider" />
              <p className="setup-copy">Novo na equipe? Crie o administrador inicial.</p>
              <form className="auth-form" onSubmit={submitRegister}>
                <label className="auth-field">
                  <span>Nome</span>
                  <input
                    value={register.nome}
                    onChange={(event) => setRegister({ ...register, nome: event.target.value })}
                    placeholder="Nome completo"
                    autoComplete="name"
                    required
                  />
                </label>
                <label className="auth-field">
                  <span>E-mail corporativo</span>
                  <input
                    value={register.email}
                    onChange={(event) => setRegister({ ...register, email: event.target.value })}
                    type="email"
                    placeholder="voce@empresa.com"
                    autoComplete="username"
                    required
                  />
                </label>
                <label className="auth-field">
                  <span>Senha forte</span>
                  <input
                    value={register.senha}
                    onChange={(event) => setRegister({ ...register, senha: event.target.value })}
                    type="password"
                    placeholder="********"
                    autoComplete="new-password"
                    minLength="8"
                    required
                  />
                </label>
                <span className={`password-hint ${register.senha ? (strongPassword(register.senha) ? "ok" : "error") : ""}`}>
                  {passwordMessage(register.senha)}
                </span>
                <button className="ghost-button setup-submit" type="submit">
                  Criar conta
                </button>
              </form>
            </section>
          )}
        </div>
        {recoveryOpen && (
          <div className="auth-recovery-modal" role="dialog" aria-modal="true" aria-labelledby="recoveryTitle">
            <div className="auth-recovery-panel">
              <p className="eyebrow">Recuperacao de acesso</p>
              <h2 id="recoveryTitle">Redefinicao de senha</h2>
              <p>Solicite a redefinicao de senha ao administrador ou a equipe de TI responsavel pelo painel.</p>
              <button className="primary-button" type="button" onClick={() => setRecoveryOpen(false)} autoFocus>
                Entendi
              </button>
            </div>
          </div>
        )}
      </section>
      <section className={`status ${status.ok ? "ok" : ""}`} aria-live="polite">
        {status.message}
      </section>
      <footer className="auth-footer">
        Desenvolvido por <strong>LIFELINEONE</strong>
      </footer>
    </main>
  );
}

function Sidebar({ view, usuario, onView, onLogout }) {
  const isAdmin = usuario?.permissao === "Administrador";
  const operationItems = [
    ["dashboard", "Dashboard Comercial", "D"],
    ["clientes", "Clientes", "C"],
  ];
  const commercialItems = [
    ["kanban", "Funil Comercial", "F"],
  ];
  const systemItems = [
    ["perfil", "Meu perfil", "P"],
  ];

  if (isAdmin) {
    systemItems.push(["usuarios", "Usuarios e Acessos", "U"]);
  }

  return (
    <aside className="sidebar">
      <div className="brand-block">
        <div className="brand-mark" aria-hidden="true">
          L1
        </div>
        <div>
          <strong>Lifeline One</strong>
          <span>Painel Comercial</span>
        </div>
      </div>
      <nav aria-label="Navegacao principal">
        <NavGroup label="Operacao" items={operationItems} view={view} onView={onView} />
        <NavGroup label="Comercial" items={commercialItems} view={view} onView={onView} />
        <NavGroup label="Sistema" items={systemItems} view={view} onView={onView} />
      </nav>
      <div className="user-box">
        <div className="user-avatar" aria-hidden="true">
          {userInitials(usuario.nome)}
        </div>
        <div className="user-summary">
          <strong>{usuario.nome}</strong>
          <span>{usuario.permissao}</span>
        </div>
        <button className="icon-button sidebar-logout" type="button" onClick={onLogout} title="Sair">
          &gt;
        </button>
      </div>
    </aside>
  );
}

function DashboardView({ metricas }) {
  const emptyMetricas = {
    clientes: { total_ativos: 0 },
    pipeline: { total_oportunidades: 0, valor_total_estimado: 0, distribuicao_por_etapa: {} },
    desempenho: { taxa_conversao_percentual: 0 },
  };
  const data = metricas || emptyMetricas;

  return (
    <section className="view active">
      <div className="metrics-grid">
        <article className="metric">
          <span>Clientes ativos</span>
          <strong>{data.clientes.total_ativos}</strong>
        </article>
        <article className="metric">
          <span>Oportunidades</span>
          <strong>{data.pipeline.total_oportunidades}</strong>
        </article>
        <article className="metric">
          <span>Pipeline</span>
          <strong>{money(data.pipeline.valor_total_estimado)}</strong>
        </article>
        <article className="metric">
          <span>Conversao</span>
          <strong>{data.desempenho.taxa_conversao_percentual}%</strong>
        </article>
      </div>
      <div className="stage-summary">
        {etapas.map((etapa) => (
          <article className="stage-item" key={etapa}>
            <span>{etapa}</span>
            <strong>{data.pipeline.distribuicao_por_etapa[etapa] || 0}</strong>
          </article>
        ))}
      </div>
    </section>
  );
}

function ClientesView({
  clientes,
  filters,
  setFilters,
  page,
  setPage,
  onCreate,
  onUpdate,
  onDelete,
  onDetail,
  detail,
}) {
  const [filterDraft, setFilterDraft] = useState(filters);
  const [formOpen, setFormOpen] = useState(false);
  const [createForm, setCreateForm] = useState(initialClienteForm);
  const [editForm, setEditForm] = useState(null);

  function submitFilters(event) {
    event.preventDefault();
    setFilters({ nome: filterDraft.nome.trim(), ativo: filterDraft.ativo });
    setPage(0);
  }

  async function submitCreate(event) {
    event.preventDefault();
    const ok = await onCreate(createForm);
    if (ok === false) {
      return;
    }
    setCreateForm(initialClienteForm);
    setFormOpen(false);
  }

  async function submitEdit(event) {
    event.preventDefault();
    const ok = await onUpdate(editForm.id, {
      nome: editForm.nome,
      email: editForm.email,
      telefone: editForm.telefone,
      empresa: editForm.empresa,
      origem: editForm.origem,
      observacoes: editForm.observacoes,
      ativo: editForm.ativo === "true",
    });
    if (ok === false) {
      return;
    }
    setEditForm(null);
  }

  return (
    <section className="view active">
      <form className="filter-bar" onSubmit={submitFilters}>
        <input
          value={filterDraft.nome}
          onChange={(event) => setFilterDraft({ ...filterDraft, nome: event.target.value })}
          placeholder="Buscar por nome"
          autoComplete="off"
        />
        <select value={filterDraft.ativo} onChange={(event) => setFilterDraft({ ...filterDraft, ativo: event.target.value })}>
          <option value="">Todos os status</option>
          <option value="true">Ativos</option>
          <option value="false">Inativos</option>
        </select>
        <button className="primary-button" type="submit">
          Filtrar
        </button>
        <button
          className="ghost-button"
          type="button"
          onClick={() => {
            setFilterDraft({ nome: "", ativo: "" });
            setFilters({ nome: "", ativo: "" });
            setPage(0);
          }}
        >
          Limpar
        </button>
      </form>

      <div className="section-actions">
        <button
          className="primary-button"
          type="button"
          onClick={() => {
            setEditForm(null);
            setFormOpen(!formOpen);
          }}
        >
          {formOpen ? "Fechar cadastro" : "Novo cliente"}
        </button>
      </div>

      {formOpen && (
        <ClienteForm form={createForm} setForm={setCreateForm} submitLabel="Salvar cliente" onSubmit={submitCreate} />
      )}

      {detail && <ClienteDetail cliente={detail} />}

      {editForm && (
        <form className="form-grid" onSubmit={submitEdit}>
          <ClienteInputs form={editForm} setForm={setEditForm} />
          <select value={editForm.ativo} onChange={(event) => setEditForm({ ...editForm, ativo: event.target.value })}>
            <option value="true">Ativo</option>
            <option value="false">Inativo</option>
          </select>
          <button className="primary-button" type="submit">
            Atualizar cliente
          </button>
          <button className="ghost-button" type="button" onClick={() => setEditForm(null)}>
            Cancelar
          </button>
        </form>
      )}

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Nome</th>
              <th>E-mail</th>
              <th>Telefone</th>
              <th>Empresa</th>
              <th>Origem</th>
              <th>Status</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {clientes.length ? (
              clientes.map((cliente) => (
                <tr key={cliente.id}>
                  <td>{cliente.nome}</td>
                  <td>{cliente.email}</td>
                  <td>{cliente.telefone}</td>
                  <td>{cliente.empresa || "-"}</td>
                  <td>{cliente.origem || "-"}</td>
                  <td>
                    <span className={statusClass(cliente.ativo)}>{cliente.ativo ? "Ativo" : "Inativo"}</span>
                  </td>
                  <td>
                    <div className="row-actions">
                      <button className="ghost-button" type="button" onClick={() => onDetail(cliente.id)}>
                        Detalhes
                      </button>
                      <button
                        className="ghost-button"
                        type="button"
                        onClick={() => {
                          setFormOpen(false);
                          setEditForm({ ...cliente, ativo: String(cliente.ativo) });
                        }}
                      >
                        Editar
                      </button>
                      <button className="ghost-button danger-button" type="button" onClick={() => onDelete(cliente.id)}>
                        Excluir
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7">Nenhum cliente encontrado.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <Pager page={page} itemCount={clientes.length} onPrev={() => setPage(Math.max(0, page - pageLimit))} onNext={() => setPage(page + pageLimit)} />
    </section>
  );
}

function ClienteInputs({ form, setForm }) {
  return (
    <>
      <input value={form.nome} onChange={(event) => setForm({ ...form, nome: event.target.value })} placeholder="Nome" autoComplete="name" required />
      <input
        value={form.email}
        onChange={(event) => setForm({ ...form, email: event.target.value })}
        type="email"
        placeholder="E-mail"
        autoComplete="email"
        required
      />
      <input value={form.telefone} onChange={(event) => setForm({ ...form, telefone: event.target.value })} placeholder="Telefone" autoComplete="tel" required />
      <input value={form.empresa || ""} onChange={(event) => setForm({ ...form, empresa: event.target.value })} placeholder="Empresa" autoComplete="organization" />
      <input value={form.origem || ""} onChange={(event) => setForm({ ...form, origem: event.target.value })} placeholder="Origem" autoComplete="off" />
      <input value={form.observacoes || ""} onChange={(event) => setForm({ ...form, observacoes: event.target.value })} placeholder="Observacoes" autoComplete="off" />
    </>
  );
}

function ClienteForm({ form, setForm, submitLabel, onSubmit }) {
  return (
    <form className="form-grid" onSubmit={onSubmit}>
      <ClienteInputs form={form} setForm={setForm} />
      <button className="primary-button" type="submit">
        {submitLabel}
      </button>
    </form>
  );
}

function ClienteDetail({ cliente }) {
  return (
    <section className="detail-panel">
      <DetailItem label="Nome" value={cliente.nome} />
      <DetailItem label="E-mail" value={cliente.email} />
      <DetailItem label="Telefone" value={cliente.telefone} />
      <DetailItem label="Empresa" value={cliente.empresa || "-"} />
      <DetailItem label="Origem" value={cliente.origem || "-"} />
      <DetailItem label="Status" value={cliente.ativo ? "Ativo" : "Inativo"} />
      <DetailItem label="Observacoes" value={cliente.observacoes || "-"} />
    </section>
  );
}

function KanbanView({ leads, onCreate, onUpdate, onMove, onDelete, onDetail, detail }) {
  const [formOpen, setFormOpen] = useState(false);
  const [createForm, setCreateForm] = useState(initialLeadForm);
  const [editForm, setEditForm] = useState(null);
  const [draggingId, setDraggingId] = useState(null);

  async function submitCreate(event) {
    event.preventDefault();
    const ok = await onCreate({ ...createForm, valor: Number(createForm.valor) });
    if (ok === false) {
      return;
    }
    setCreateForm(initialLeadForm);
    setFormOpen(false);
  }

  async function submitEdit(event) {
    event.preventDefault();
    const ok = await onUpdate(editForm.id, { ...editForm, valor: Number(editForm.valor) });
    if (ok === false) {
      return;
    }
    setEditForm(null);
  }

  function moveByStep(lead, direction) {
    const index = etapas.indexOf(lead.etapa);
    const nextIndex = Math.min(Math.max(index + direction, 0), etapas.length - 1);
    if (etapas[nextIndex] !== lead.etapa) {
      onMove(lead.id, etapas[nextIndex]);
    }
  }

  return (
    <section className="view active">
      <div className="section-actions">
        <button
          className="primary-button"
          type="button"
          onClick={() => {
            setEditForm(null);
            setFormOpen(!formOpen);
          }}
        >
          {formOpen ? "Fechar cadastro" : "Nova oportunidade"}
        </button>
      </div>

      {formOpen && <LeadForm form={createForm} setForm={setCreateForm} submitLabel="Criar lead" onSubmit={submitCreate} />}
      {detail && <LeadDetail lead={detail} />}
      {editForm && <LeadForm form={editForm} setForm={setEditForm} submitLabel="Atualizar lead" onSubmit={submitEdit} onCancel={() => setEditForm(null)} />}

      <div className="kanban-board">
        {etapas.map((etapa) => {
          const stageLeads = leads.filter((lead) => lead.etapa === etapa);
          return (
            <section className="kanban-column" key={etapa}>
              <header>
                <h3>{etapa}</h3>
                <strong>{stageLeads.length}</strong>
              </header>
              <div
                className="lead-list"
                onDragOver={(event) => event.preventDefault()}
                onDrop={(event) => {
                  event.preventDefault();
                  if (draggingId) {
                    onMove(draggingId, etapa);
                  }
                  setDraggingId(null);
                }}
              >
                {stageLeads.length ? (
                  stageLeads.map((lead) => (
                    <article className="lead-card" draggable key={lead.id} onDragStart={() => setDraggingId(lead.id)} onDragEnd={() => setDraggingId(null)}>
                      <strong>{lead.titulo}</strong>
                      <span className="lead-meta">
                        {lead.cliente_nome} - {money(lead.valor)}
                      </span>
                      {lead.descricao && <span className="lead-meta">{lead.descricao}</span>}
                      <div className="lead-actions">
                        <button className="ghost-button" type="button" onClick={() => onDetail(lead.id)}>
                          Detalhes
                        </button>
                        <button
                          className="ghost-button"
                          type="button"
                          onClick={() => {
                            setFormOpen(false);
                            setEditForm({ ...lead, valor: String(lead.valor) });
                          }}
                        >
                          Editar
                        </button>
                        <button className="ghost-button" type="button" onClick={() => moveByStep(lead, -1)}>
                          Voltar
                        </button>
                        <button className="ghost-button" type="button" onClick={() => moveByStep(lead, 1)}>
                          Avancar
                        </button>
                        <button className="ghost-button danger-button" type="button" onClick={() => onDelete(lead.id)}>
                          Excluir
                        </button>
                      </div>
                    </article>
                  ))
                ) : (
                  <span className="lead-meta">Nenhuma oportunidade nesta etapa.</span>
                )}
              </div>
            </section>
          );
        })}
      </div>
    </section>
  );
}

function LeadForm({ form, setForm, submitLabel, onSubmit, onCancel }) {
  return (
    <form className="form-grid lead-form" onSubmit={onSubmit}>
      <input value={form.titulo} onChange={(event) => setForm({ ...form, titulo: event.target.value })} placeholder="Titulo da oportunidade" autoComplete="off" required />
      <input value={form.cliente_nome} onChange={(event) => setForm({ ...form, cliente_nome: event.target.value })} placeholder="Cliente" autoComplete="off" required />
      <input value={form.valor} onChange={(event) => setForm({ ...form, valor: event.target.value })} type="number" min="0" step="0.01" placeholder="Valor" required />
      <select value={form.etapa} onChange={(event) => setForm({ ...form, etapa: event.target.value })}>
        {etapas.map((etapa) => (
          <option key={etapa}>{etapa}</option>
        ))}
      </select>
      <input value={form.descricao || ""} onChange={(event) => setForm({ ...form, descricao: event.target.value })} placeholder="Descricao" autoComplete="off" />
      <button className="primary-button" type="submit">
        {submitLabel}
      </button>
      {onCancel && (
        <button className="ghost-button" type="button" onClick={onCancel}>
          Cancelar
        </button>
      )}
    </form>
  );
}

function LeadDetail({ lead }) {
  return (
    <section className="detail-panel">
      <DetailItem label="Titulo" value={lead.titulo} />
      <DetailItem label="Cliente" value={lead.cliente_nome} />
      <DetailItem label="Valor" value={money(lead.valor)} />
      <DetailItem label="Etapa" value={lead.etapa} />
      <DetailItem label="Descricao" value={lead.descricao || "-"} />
    </section>
  );
}

function PerfilView({ usuario, onPasswordChange, onError }) {
  const [form, setForm] = useState(initialPasswordForm);

  async function submitPassword(event) {
    event.preventDefault();
    try {
      assertStrongPassword(form.nova_senha);
      if (form.nova_senha !== form.confirmar_nova_senha) {
        throw new Error("A confirmacao deve ser igual a nova senha.");
      }
      const ok = await onPasswordChange(form);
      if (ok === false) {
        return;
      }
      setForm(initialPasswordForm);
    } catch (error) {
      onError(error.message);
    }
  }

  return (
    <section className="view active">
      <section className="detail-panel">
        <DetailItem label="Nome" value={usuario.nome} />
        <DetailItem label="E-mail" value={usuario.email} />
        <DetailItem label="Permissao" value={usuario.permissao} />
        <DetailItem label="Status" value={usuario.ativo ? "Ativo" : "Inativo"} />
      </section>
      <form className="form-grid password-form" onSubmit={submitPassword}>
        <input
          value={form.senha_atual}
          onChange={(event) => setForm({ ...form, senha_atual: event.target.value })}
          type="password"
          placeholder="Senha atual"
          autoComplete="current-password"
          required
        />
        <input
          value={form.nova_senha}
          onChange={(event) => setForm({ ...form, nova_senha: event.target.value })}
          type="password"
          placeholder="Nova senha forte"
          autoComplete="new-password"
          minLength="8"
          required
        />
        <input
          value={form.confirmar_nova_senha}
          onChange={(event) => setForm({ ...form, confirmar_nova_senha: event.target.value })}
          type="password"
          placeholder="Confirmar nova senha"
          autoComplete="new-password"
          minLength="8"
          required
        />
        <span className={`password-hint ${form.nova_senha ? (strongPassword(form.nova_senha) ? "ok" : "error") : ""}`}>{passwordMessage(form.nova_senha)}</span>
        <button className="primary-button" type="submit">
          Alterar senha
        </button>
      </form>
    </section>
  );
}

function UsuariosView({ usuarios, page, setPage, onCreate, onUpdate, onStatus, onPermission, onError }) {
  const [formOpen, setFormOpen] = useState(false);
  const [createForm, setCreateForm] = useState(initialUserForm);
  const [editForm, setEditForm] = useState(null);

  async function submitCreate(event) {
    event.preventDefault();
    try {
      assertStrongPassword(createForm.senha);
      const ok = await onCreate(createForm);
      if (ok === false) {
        return;
      }
      setCreateForm(initialUserForm);
      setFormOpen(false);
    } catch (error) {
      onError(error.message);
    }
  }

  async function submitEdit(event) {
    event.preventDefault();
    const ok = await onUpdate(editForm.id, { nome: editForm.nome, email: editForm.email, permissao: editForm.permissao, ativo: editForm.ativo === "true" });
    if (ok === false) {
      return;
    }
    setEditForm(null);
  }

  return (
    <section className="view active">
      <div className="section-actions">
        <button
          className="primary-button"
          type="button"
          onClick={() => {
            setEditForm(null);
            setFormOpen(!formOpen);
          }}
        >
          {formOpen ? "Fechar cadastro" : "Novo usuario"}
        </button>
      </div>

      {formOpen && (
        <form className="form-grid" onSubmit={submitCreate}>
          <input value={createForm.nome} onChange={(event) => setCreateForm({ ...createForm, nome: event.target.value })} placeholder="Nome" autoComplete="name" required />
          <input
            value={createForm.email}
            onChange={(event) => setCreateForm({ ...createForm, email: event.target.value })}
            type="email"
            placeholder="E-mail"
            autoComplete="username"
            required
          />
          <input
            value={createForm.senha}
            onChange={(event) => setCreateForm({ ...createForm, senha: event.target.value })}
            type="password"
            placeholder="Senha forte"
            autoComplete="new-password"
            minLength="8"
            required
          />
          <span className={`password-hint ${createForm.senha ? (strongPassword(createForm.senha) ? "ok" : "error") : ""}`}>{passwordMessage(createForm.senha)}</span>
          <button className="primary-button" type="submit">
            Criar usuario
          </button>
        </form>
      )}

      {editForm && (
        <form className="form-grid" onSubmit={submitEdit}>
          <input value={editForm.nome} onChange={(event) => setEditForm({ ...editForm, nome: event.target.value })} placeholder="Nome" autoComplete="name" required />
          <input value={editForm.email} onChange={(event) => setEditForm({ ...editForm, email: event.target.value })} type="email" placeholder="E-mail" autoComplete="username" required />
          <select value={editForm.permissao} onChange={(event) => setEditForm({ ...editForm, permissao: event.target.value })}>
            <option>Administrador</option>
            <option>Usuario Comum</option>
          </select>
          <select value={editForm.ativo} onChange={(event) => setEditForm({ ...editForm, ativo: event.target.value })}>
            <option value="true">Ativo</option>
            <option value="false">Inativo</option>
          </select>
          <button className="primary-button" type="submit">
            Atualizar usuario
          </button>
          <button className="ghost-button" type="button" onClick={() => setEditForm(null)}>
            Cancelar
          </button>
        </form>
      )}

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Nome</th>
              <th>E-mail</th>
              <th>Permissao</th>
              <th>Status</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {usuarios.length ? (
              usuarios.map((usuario) => (
                <tr key={usuario.id}>
                  <td>{usuario.nome}</td>
                  <td>{usuario.email}</td>
                  <td>
                    <select value={usuario.permissao} onChange={(event) => onPermission(usuario.id, event.target.value)}>
                      <option>Administrador</option>
                      <option>Usuario Comum</option>
                    </select>
                  </td>
                  <td>
                    <span className={statusClass(usuario.ativo)}>{usuario.ativo ? "Ativo" : "Inativo"}</span>
                  </td>
                  <td>
                    <div className="row-actions">
                      <button
                        className="ghost-button"
                        type="button"
                        onClick={() => {
                          setFormOpen(false);
                          setEditForm({ ...usuario, ativo: String(usuario.ativo) });
                        }}
                      >
                        Editar
                      </button>
                      <button className="ghost-button" type="button" onClick={() => onStatus(usuario.id, !usuario.ativo)}>
                        {usuario.ativo ? "Desativar" : "Ativar"}
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="5">Nenhum usuario encontrado.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <Pager page={page} itemCount={usuarios.length} onPrev={() => setPage(Math.max(0, page - pageLimit))} onNext={() => setPage(page + pageLimit)} />
    </section>
  );
}

function DetailItem({ label, value }) {
  return (
    <div className="detail-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function Pager({ page, itemCount, onPrev, onNext }) {
  return (
    <div className="pager">
      <button className="ghost-button" type="button" disabled={page === 0} onClick={onPrev}>
        Anterior
      </button>
      <span>Pagina {Math.floor(page / pageLimit) + 1}</span>
      <button className="ghost-button" type="button" disabled={itemCount < pageLimit} onClick={onNext}>
        Proxima
      </button>
    </div>
  );
}

function App() {
  const [token, setToken] = useState(readStoredToken());
  const [usuario, setUsuario] = useState(null);
  const [view, setView] = useState("dashboard");
  const [status, setStatusState] = useState({ message: "", ok: false });
  const [setupOpen, setSetupOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [clientes, setClientes] = useState([]);
  const [leads, setLeads] = useState([]);
  const [usuarios, setUsuarios] = useState([]);
  const [metricas, setMetricas] = useState(null);
  const [clienteFilters, setClienteFilters] = useState({ nome: "", ativo: "" });
  const [clientesPage, setClientesPage] = useState(0);
  const [usuariosPage, setUsuariosPage] = useState(0);
  const [clienteDetail, setClienteDetail] = useState(null);
  const [leadDetail, setLeadDetail] = useState(null);
  const [confirmation, setConfirmation] = useState(null);

  const isAdmin = usuario?.permissao === "Administrador";
  const viewTitle = view === "kanban" ? "Kanban" : view === "perfil" ? "Meu perfil" : view[0].toUpperCase() + view.slice(1);

  const requestWithSession = useMemo(
    () => (path, options = {}) =>
      apiRequest(path, {
        ...options,
        token,
        onUnauthorized: () => clearSession(false),
      }),
    [token],
  );

  function setStatus(message, ok = false) {
    setStatusState({ message, ok });
  }

  useEffect(() => {
    if (!status.message || !status.ok) {
      return undefined;
    }

    const timer = window.setTimeout(() => {
      setStatusState((current) => (current.message === status.message && current.ok === status.ok ? { message: "", ok: false } : current));
    }, 5000);

    return () => window.clearTimeout(timer);
  }, [status]);

  function clearSession(showMessage = true) {
    clearStoredToken();
    setToken(null);
    setUsuario(null);
    setUsuarios([]);
    setView("dashboard");
    if (showMessage) {
      setStatus("Sessao encerrada.", true);
    }
  }

  function confirmAction(message) {
    return new Promise((resolve) => {
      setConfirmation({ message, resolve });
    });
  }

  function resolveConfirm(accepted) {
    if (confirmation?.resolve) {
      confirmation.resolve(accepted);
    }
    setConfirmation(null);
  }

  function clientesQuery() {
    const params = new URLSearchParams();
    if (clienteFilters.nome) {
      params.set("nome", clienteFilters.nome);
    }
    if (clienteFilters.ativo) {
      params.set("ativo", clienteFilters.ativo);
    }
    params.set("skip", clientesPage);
    params.set("limit", pageLimit);
    return `?${params.toString()}`;
  }

  function usuariosQuery() {
    const params = new URLSearchParams();
    params.set("skip", usuariosPage);
    params.set("limit", pageLimit);
    return `?${params.toString()}`;
  }

  async function loadSetupStatus() {
    try {
      const data = await apiRequest("/usuarios/setup-status");
      setSetupOpen(Boolean(data.primeiro_acesso_aberto));
    } catch {
      setSetupOpen(false);
    }
  }

  async function loadAll() {
    if (!token || !usuario) {
      return;
    }

    setLoading(true);
    setStatus("Carregando dados...");
    try {
      const requests = [requestWithSession(`/clientes/${clientesQuery()}`), requestWithSession("/kanban/"), requestWithSession("/dashboard/metricas")];
      if (isAdmin) {
        requests.push(requestWithSession(`/usuarios/${usuariosQuery()}`));
      }
      const [clientesData, leadsData, metricasData, usuariosData = []] = await Promise.all(requests);
      setClientes(clientesData);
      setLeads(leadsData);
      setMetricas(metricasData);
      setUsuarios(usuariosData);
      setClienteDetail(null);
      setLeadDetail(null);
      setStatus("Dados atualizados.", true);
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSetupStatus();
  }, []);

  useEffect(() => {
    async function hydrateSession() {
      if (!token) {
        return;
      }
      try {
        const me = await apiRequest("/auth/me", {
          token,
          onUnauthorized: () => clearSession(false),
        });
        setUsuario(me);
      } catch (error) {
        clearSession(false);
        setStatus(error.message);
      }
    }
    hydrateSession();
  }, [token]);

  useEffect(() => {
    loadAll();
  }, [usuario, token, clienteFilters, clientesPage, usuariosPage]);

  async function login(email, senha) {
    const body = new URLSearchParams();
    body.set("username", email);
    body.set("password", senha);
    const data = await apiRequest("/auth/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    storeToken(data.access_token);
    setToken(data.access_token);
    setUsuario(data.usuario);
  }

  async function register(payload) {
    await apiRequest("/usuarios/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    await login(payload.email, payload.senha);
  }

  async function logout() {
    if (await confirmAction("Deseja encerrar sua sessao?")) {
      if (token) {
        await requestWithSession("/auth/logout", { method: "POST" }).catch(() => null);
      }
      clearSession();
    }
  }

  async function action(handler, successMessage) {
    try {
      await handler();
      await loadAll();
      if (successMessage) {
        setStatus(successMessage, true);
      }
      return true;
    } catch (error) {
      setStatus(error.message);
      return false;
    }
  }

  async function createCliente(payload) {
    await action(
      () =>
        requestWithSession("/clientes/", {
          method: "POST",
          body: JSON.stringify(payload),
        }),
      "Cliente criado.",
    );
  }

  async function updateCliente(id, payload) {
    await action(
      () =>
        requestWithSession(`/clientes/${id}`, {
          method: "PUT",
          body: JSON.stringify(payload),
        }),
      "Cliente atualizado.",
    );
  }

  async function deleteCliente(id) {
    if (!(await confirmAction("Excluir este cliente? Esta acao nao pode ser desfeita."))) {
      return;
    }
    await action(() => requestWithSession(`/clientes/${id}`, { method: "DELETE" }), "Cliente excluido.");
  }

  async function detailCliente(id) {
    try {
      setClienteDetail(await requestWithSession(`/clientes/${id}`));
    } catch (error) {
      setStatus(error.message);
    }
  }

  async function createLead(payload) {
    await action(
      () =>
        requestWithSession("/kanban/", {
          method: "POST",
          body: JSON.stringify(payload),
        }),
      "Oportunidade criada.",
    );
  }

  async function updateLead(id, payload) {
    const safePayload = { ...payload };
    delete safePayload.id;
    await action(
      () =>
        requestWithSession(`/kanban/${id}`, {
          method: "PUT",
          body: JSON.stringify(safePayload),
        }),
      "Oportunidade atualizada.",
    );
  }

  async function moveLead(id, etapa) {
    await action(() =>
      requestWithSession(`/kanban/${id}/etapa`, {
        method: "PATCH",
        body: JSON.stringify({ etapa }),
      }),
    );
  }

  async function deleteLead(id) {
    if (!(await confirmAction("Excluir esta oportunidade? Esta acao nao pode ser desfeita."))) {
      return;
    }
    await action(() => requestWithSession(`/kanban/${id}`, { method: "DELETE" }), "Oportunidade excluida.");
  }

  async function detailLead(id) {
    try {
      setLeadDetail(await requestWithSession(`/kanban/${id}`));
    } catch (error) {
      setStatus(error.message);
    }
  }

  async function changePassword(payload) {
    await requestWithSession("/auth/trocar-senha", {
      method: "PUT",
      body: JSON.stringify(payload),
    });
    clearSession(false);
    setStatus("Senha alterada com sucesso. Faca login novamente.", true);
  }

  async function createUsuario(payload) {
    await action(
      () =>
        requestWithSession("/usuarios/", {
          method: "POST",
          body: JSON.stringify(payload),
        }),
      "Usuario criado.",
    );
  }

  async function updateUsuario(id, payload) {
    await action(
      () =>
        requestWithSession(`/usuarios/${id}`, {
          method: "PUT",
          body: JSON.stringify(payload),
        }),
      "Usuario atualizado.",
    );
  }

  async function changeUserStatus(id, ativo) {
    const actionName = ativo ? "ativar" : "desativar";
    if (!(await confirmAction(`Deseja ${actionName} este usuario?`))) {
      return;
    }
    await action(() =>
      requestWithSession(`/usuarios/${id}/status`, {
        method: "PATCH",
        body: JSON.stringify({ ativo }),
      }),
    );
  }

  async function changeUserPermission(id, permissao) {
    if (!(await confirmAction("Alterar a permissao deste usuario?"))) {
      await loadAll();
      return;
    }
    await action(() =>
      requestWithSession(`/usuarios/${id}/permissao`, {
        method: "PATCH",
        body: JSON.stringify({ permissao }),
      }),
    );
  }

  if (!token || !usuario) {
    return (
      <div className="app-root logged-out">
        <AuthView setupOpen={setupOpen} status={status} onError={(message) => setStatus(message)} onLogin={login} onRegister={register} />
        <ConfirmModal confirmation={confirmation} onResolve={resolveConfirm} />
      </div>
    );
  }

  return (
    <div className="app-root">
      <Sidebar
        view={view}
        usuario={usuario}
        onView={(nextView) => {
          if (nextView === "usuarios" && !isAdmin) {
            setStatus("Acesso restrito a administradores.");
            return;
          }
          setView(nextView);
        }}
        onLogout={logout}
      />
      <main className="app-shell">
        <section className={`status ${status.ok ? "ok" : ""}`} aria-live="polite">
          {status.message}
        </section>
        <section className="private-area">
          <header className="topbar">
            <div className="topbar-title">
              <p className="breadcrumb">
                <span>Painel Lifelineone</span>
                <span>/</span>
                <strong>{viewTitle}</strong>
              </p>
              <h2>{viewTitle}</h2>
            </div>
            <label className="topbar-search">
              <span aria-hidden="true">Buscar</span>
              <input value="" readOnly placeholder="Buscar no CRM..." aria-label="Buscar no CRM" />
              <kbd>Ctrl K</kbd>
            </label>
            <div className="topbar-actions">
              <button className="icon-button refresh-button" type="button" onClick={loadAll} disabled={loading} title="Atualizar dados">
                Atualizar
              </button>
            </div>
          </header>

          {view === "dashboard" && <DashboardView metricas={metricas} />}
          {view === "clientes" && (
            <ClientesView
              clientes={clientes}
              filters={clienteFilters}
              setFilters={setClienteFilters}
              page={clientesPage}
              setPage={setClientesPage}
              onCreate={createCliente}
              onUpdate={updateCliente}
              onDelete={deleteCliente}
              onDetail={detailCliente}
              detail={clienteDetail}
            />
          )}
          {view === "kanban" && <KanbanView leads={leads} onCreate={createLead} onUpdate={updateLead} onMove={moveLead} onDelete={deleteLead} onDetail={detailLead} detail={leadDetail} />}
          {view === "perfil" && <PerfilView usuario={usuario} onError={(message) => setStatus(message)} onPasswordChange={changePassword} />}
          {view === "usuarios" && isAdmin && (
            <UsuariosView
              usuarios={usuarios}
              page={usuariosPage}
              setPage={setUsuariosPage}
              onCreate={createUsuario}
              onUpdate={updateUsuario}
              onStatus={changeUserStatus}
              onPermission={changeUserPermission}
              onError={(message) => setStatus(message)}
            />
          )}
        </section>
        <footer className="app-footer">
          Desenvolvido por <strong>LIFELINEONE</strong>
        </footer>
      </main>
      <ConfirmModal confirmation={confirmation} onResolve={resolveConfirm} />
    </div>
  );
}

export default App;
