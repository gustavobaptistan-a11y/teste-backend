from tests.conftest import create_user, login_headers


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
