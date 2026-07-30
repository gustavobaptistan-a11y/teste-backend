from tests.conftest import create_user, login_headers


def test_crud_completo_de_clientes(client):
    create_user(client, "admin@teste.com")
    headers = login_headers(client, "admin@teste.com")

    payload = {
        "nome": "Cliente Teste",
        "email": "cliente@teste.com",
        "telefone": "(11) 90000-0000",
        "empresa": "Empresa Teste",
        "origem": "Indicacao",
        "observacoes": "Contato comercial prioritario",
    }

    created = client.post("/clientes/", headers=headers, json=payload)
    assert created.status_code == 201
    cliente_id = created.json()["id"]

    detail = client.get(f"/clientes/{cliente_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["nome"] == payload["nome"]

    updated_payload = {
        **payload,
        "nome": "Cliente Editado",
        "empresa": "Empresa Editada",
        "ativo": False,
    }
    updated = client.put(f"/clientes/{cliente_id}", headers=headers, json=updated_payload)
    assert updated.status_code == 200
    assert updated.json()["nome"] == "Cliente Editado"
    assert updated.json()["empresa"] == "Empresa Editada"
    assert updated.json()["ativo"] is False

    inactive = client.get("/clientes/?ativo=false&nome=Editado", headers=headers)
    assert inactive.status_code == 200
    assert len(inactive.json()) == 1

    deleted = client.delete(f"/clientes/{cliente_id}", headers=headers)
    assert deleted.status_code == 204

    missing = client.get(f"/clientes/{cliente_id}", headers=headers)
    assert missing.status_code == 404


def test_cliente_sem_token_recebe_401(client):
    response = client.get("/clientes/")

    assert response.status_code == 401


def test_cliente_rejeita_payload_excessivo(client):
    create_user(client, "admin@teste.com")
    headers = login_headers(client, "admin@teste.com")

    response = client.post(
        "/clientes/",
        headers=headers,
        json={
            "nome": "A",
            "email": "cliente@teste.com",
            "telefone": "123",
            "empresa": "x" * 300,
            "origem": "Site",
            "observacoes": "Observacao de teste",
        },
    )

    assert response.status_code == 422
