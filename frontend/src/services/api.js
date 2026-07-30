export function resolveApiBase() {
  const apiBase = window.LIFELINE_API_BASE;
  if (!apiBase) {
    throw new Error("Configuracao da API ausente. Verifique frontend/public/config.js.");
  }
  return apiBase.replace(/\/$/, "");
}

export async function apiRequest(path, { token, onUnauthorized, ...options } = {}) {
  const headers = { ...(options.headers || {}) };
  if (!(options.body instanceof URLSearchParams)) {
    headers["Content-Type"] = "application/json";
  }
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  let response;
  try {
    response = await fetch(`${resolveApiBase()}${path}`, { ...options, headers });
  } catch {
    throw new Error("API indisponivel. Inicie o backend em http://127.0.0.1:8010.");
  }

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (response.status === 401 && onUnauthorized) {
      onUnauthorized();
    }
    throw new Error(data.detail || "Nao foi possivel concluir a operacao.");
  }
  return data;
}
