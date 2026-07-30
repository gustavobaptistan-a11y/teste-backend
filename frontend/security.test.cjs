const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

const srcDir = path.join(__dirname, "src");
const appCode = fs.readFileSync(path.join(srcDir, "App.jsx"), "utf8");
const apiCode = fs.readFileSync(path.join(srcDir, "services", "api.js"), "utf8");
const securityCode = fs.readFileSync(path.join(srcDir, "utils", "security.js"), "utf8");
const indexHtml = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");

const combined = `${appCode}\n${apiCode}\n${securityCode}\n${indexHtml}`;

assert(!combined.includes("localStorage"), "Frontend nao deve usar localStorage para token.");
assert(!combined.includes("eval("), "Frontend nao deve usar eval.");
assert(!combined.includes("new Function"), "Frontend nao deve criar funcoes dinamicas.");
assert(!combined.includes("document.cookie"), "Frontend nao deve manipular cookies manualmente.");
assert(!combined.includes("dangerouslySetInnerHTML"), "React nao deve renderizar HTML dinamico bruto.");
assert(!combined.includes(".innerHTML"), "Frontend React nao deve manipular innerHTML.");
assert(securityCode.includes("sessionStorage"), "Token deve permanecer em sessionStorage.");
assert(indexHtml.includes('type="module" src="/src/main.jsx"'), "Entrada do Vite/React deve estar configurada.");
assert(appCode.includes('autoComplete="current-password"'), "Login/troca devem usar autocomplete current-password.");
assert(appCode.includes('autoComplete="new-password"'), "Cadastro/troca devem usar autocomplete new-password.");
assert(apiCode.includes("Authorization") && apiCode.includes("Bearer"), "Requisicoes autenticadas devem enviar Authorization Bearer via camada segura.");

async function runPasswordChecks() {
  const security = await import(pathToFileURL(path.join(srcDir, "utils", "security.js")).href);
  assert(security.strongPassword("Senha123"), "Senha forte valida deve ser aceita.");
  assert(!security.strongPassword("senhafraca"), "Senha sem maiuscula/numero deve ser recusada.");
  assert(!security.strongPassword("SENHA123"), "Senha sem minuscula deve ser recusada.");
}

runPasswordChecks()
  .then(() => {
    console.log("Frontend security checks passed.");
  })
  .catch((error) => {
    console.error(error.message);
    process.exit(1);
  });
