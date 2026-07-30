export const TOKEN_STORAGE_KEY = "lifeline_token";

export function strongPassword(value) {
  return value.length >= 8 && /[a-z]/.test(value) && /[A-Z]/.test(value) && /\d/.test(value);
}

export function passwordMessage(value) {
  if (!value) {
    return "Minimo 8 caracteres, com maiuscula, minuscula e numero.";
  }
  return strongPassword(value)
    ? "Senha atende aos criterios."
    : "Use maiuscula, minuscula, numero e pelo menos 8 caracteres.";
}

export function assertStrongPassword(value) {
  if (!strongPassword(value)) {
    throw new Error("A senha deve ter no minimo 8 caracteres, com maiuscula, minuscula e numero.");
  }
}

export function readStoredToken() {
  return sessionStorage.getItem(TOKEN_STORAGE_KEY);
}

export function storeToken(token) {
  sessionStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearStoredToken() {
  sessionStorage.removeItem(TOKEN_STORAGE_KEY);
}
