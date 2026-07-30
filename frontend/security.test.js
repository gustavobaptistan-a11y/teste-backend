const fs = require("fs");
const path = require("path");
const vm = require("vm");

function inputStub() {
  return {
    value: "",
    addEventListener() {},
    focus() {},
    classList: {
      toggle() {},
      add() {},
      remove() {},
      contains() {
        return true;
      },
    },
  };
}

function elementStub() {
  return {
    textContent: "",
    innerHTML: "",
    className: "",
    style: {},
    elements: {
      senha: inputStub(),
      nova_senha: inputStub(),
    },
    classList: {
      toggle() {},
      add() {},
      remove() {},
      contains() {
        return true;
      },
    },
    addEventListener() {},
    querySelectorAll() {
      return [];
    },
    querySelector() {
      return elementStub();
    },
    reset() {},
    focus() {},
  };
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

const appCode = fs.readFileSync(path.join(__dirname, "app.js"), "utf8");
const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");

assert(!appCode.includes("localStorage"), "Frontend nao deve usar localStorage para token.");
assert(!appCode.includes("eval("), "Frontend nao deve usar eval.");
assert(!appCode.includes("new Function"), "Frontend nao deve criar funcoes dinamicas.");
assert(!appCode.includes("document.cookie"), "Frontend nao deve manipular cookies manualmente.");
assert(html.includes('autocomplete="current-password"'), "Login/troca devem usar autocomplete current-password.");
assert(html.includes('autocomplete="new-password"'), "Cadastro/troca devem usar autocomplete new-password.");

const elements = {};
const documentStub = {
  querySelector(selector) {
    elements[selector] ||= elementStub();
    return elements[selector];
  },
  querySelectorAll() {
    return [];
  },
  addEventListener() {},
};

const context = {
  document: documentStub,
  sessionStorage: {
    getItem() {
      return null;
    },
    setItem() {},
    removeItem() {},
  },
  window: {
    LIFELINE_API_BASE: "http://127.0.0.1:8000",
  },
  Intl,
  URLSearchParams,
  FormData: class {},
  fetch() {},
  assert,
  console,
};

const appWithoutHydration = appCode.replace(/hydrateSession\(\);\s*$/, "");
const renderTest = `
state.clientes = [{
  id: 1,
  nome: "<img src=x onerror=alert(1)>",
  email: "cliente@example.com<script>alert(1)</script>",
  telefone: "<b>999</b>",
  empresa: "ACME",
  origem: "Site",
  ativo: true
}];
renderClientes();
const renderedHtml = els.clientesTable.innerHTML;
assert(!renderedHtml.includes("<script>"), "Script nao pode renderizar como HTML ativo.");
assert(!renderedHtml.includes("<img"), "Imagem maliciosa nao pode renderizar como HTML ativo.");
assert(renderedHtml.includes("&lt;img") && renderedHtml.includes("&lt;script&gt;"), "Payload deve aparecer escapado.");
assert(strongPassword("Senha123"), "Senha forte valida deve ser aceita.");
assert(!strongPassword("senhafraca"), "Senha sem maiuscula/numero deve ser recusada.");
`;

vm.createContext(context);
vm.runInContext(`${appWithoutHydration}\n${renderTest}`, context);

console.log("Frontend security checks passed.");
