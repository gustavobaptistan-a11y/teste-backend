from tests.conftest import create_user, login_headers


def test_healthcheck_publico(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_primeiro_usuario_vira_administrador(client):
    response = create_user(client, "admin@teste.com")

    assert response.status_code == 201
    assert response.json()["permissao"] == "Administrador"


def test_segundo_usuario_vira_usuario_comum(client):
    create_user(client, "admin@teste.com")
    admin_headers = login_headers(client, "admin@teste.com")

    public_response = create_user(client, "publico@teste.com")
    response = create_user(client, "user@teste.com", headers=admin_headers)

    assert public_response.status_code == 403
    assert response.status_code == 201
    assert response.json()["permissao"] == "Usuario Comum"


def test_cadastro_rejeita_senha_fraca(client):
    response = create_user(client, "fraco@teste.com", senha="senha123")

    assert response.status_code == 422


def test_dashboard_exige_token(client):
    response = client.get("/dashboard/metricas")

    assert response.status_code == 401


def test_admin_lista_usuarios_e_usuario_comum_recebe_403(client):
    create_user(client, "admin@teste.com")
    admin_headers = login_headers(client, "admin@teste.com")
    create_user(client, "user@teste.com", headers=admin_headers)
    user_headers = login_headers(client, "user@teste.com")

    assert client.get("/usuarios/", headers=admin_headers).status_code == 200
    assert client.get("/usuarios/", headers=user_headers).status_code == 403


def test_usuario_inativo_nao_consegue_logar(client):
    admin = create_user(client, "admin@teste.com").json()
    admin_headers = login_headers(client, admin["email"])
    user = create_user(client, "user@teste.com", headers=admin_headers).json()

    response = client.patch(
        f"/usuarios/{user['id']}/status",
        headers=admin_headers,
        json={"ativo": False},
    )

    assert response.status_code == 200
    assert client.post(
        "/auth/token",
        data={"username": user["email"], "password": "Senha123"},
    ).status_code == 403


def test_admin_altera_permissao_e_edita_usuario(client):
    create_user(client, "admin@teste.com")
    admin_headers = login_headers(client, "admin@teste.com")
    user = create_user(client, "user@teste.com", headers=admin_headers).json()

    permission = client.patch(
        f"/usuarios/{user['id']}/permissao",
        headers=admin_headers,
        json={"permissao": "Administrador"},
    )
    assert permission.status_code == 200
    assert permission.json()["permissao"] == "Administrador"

    updated = client.put(
        f"/usuarios/{user['id']}",
        headers=admin_headers,
        json={
            "nome": "Usuario Editado",
            "email": "editado@teste.com",
            "permissao": "Usuario Comum",
            "ativo": True,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["nome"] == "Usuario Editado"
    assert updated.json()["email"] == "editado@teste.com"


def test_logout_revoga_token(client, monkeypatch):
    revoked_keys = set()

    def fake_set_cache_key(key, value, ttl_seconds):
        revoked_keys.add(key)
        return True

    def fake_cache_key_exists(key):
        return key in revoked_keys

    monkeypatch.setattr("app.api.auth.set_cache_key", fake_set_cache_key)
    monkeypatch.setattr("app.core.auth.cache_key_exists", fake_cache_key_exists)

    create_user(client, "admin@teste.com")
    headers = login_headers(client, "admin@teste.com")

    assert client.get("/auth/me", headers=headers).status_code == 200
    assert client.post("/auth/logout", headers=headers).status_code == 200
    assert client.get("/auth/me", headers=headers).status_code == 401


def test_troca_senha_segura(client):
    create_user(client, "admin@teste.com")
    headers = login_headers(client, "admin@teste.com")

    wrong_current = client.put(
        "/auth/trocar-senha",
        headers=headers,
        json={
            "senha_atual": "SenhaErrada123",
            "nova_senha": "NovaSenha123",
            "confirmar_nova_senha": "NovaSenha123",
        },
    )
    assert wrong_current.status_code == 400

    weak_password = client.put(
        "/auth/trocar-senha",
        headers=headers,
        json={
            "senha_atual": "Senha123",
            "nova_senha": "senhafraca",
            "confirmar_nova_senha": "senhafraca",
        },
    )
    assert weak_password.status_code == 422

    changed = client.put(
        "/auth/trocar-senha",
        headers=headers,
        json={
            "senha_atual": "Senha123",
            "nova_senha": "NovaSenha123",
            "confirmar_nova_senha": "NovaSenha123",
        },
    )
    assert changed.status_code == 200

    old_login = client.post("/auth/token", data={"username": "admin@teste.com", "password": "Senha123"})
    new_login = client.post("/auth/token", data={"username": "admin@teste.com", "password": "NovaSenha123"})
    assert old_login.status_code == 401
    assert new_login.status_code == 200
