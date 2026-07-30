from tests.conftest import create_user, login_headers


def test_cria_move_exclui_lead_e_atualiza_dashboard(client):
    create_user(client, "admin@teste.com")
    headers = login_headers(client, "admin@teste.com")

    cliente = client.post(
        "/clientes/",
        headers=headers,
        json={
            "nome": "Cliente Dashboard",
            "email": "dashboard@teste.com",
            "telefone": "(11) 91111-1111",
            "empresa": "Empresa Dashboard",
            "origem": "Site",
            "observacoes": "Cliente de teste para metricas",
        },
    )
    assert cliente.status_code == 201

    lead_payload = {
        "titulo": "Plano Empresarial",
        "cliente_nome": "Cliente Dashboard",
        "valor": 3000,
        "etapa": "Novo Lead",
        "descricao": "Teste de pipeline",
    }
    lead = client.post("/kanban/", headers=headers, json=lead_payload)
    assert lead.status_code == 201
    lead_id = lead.json()["id"]

    dashboard = client.get("/dashboard/metricas", headers=headers)
    assert dashboard.status_code == 200
    assert dashboard.json()["clientes"]["total_ativos"] == 1
    assert dashboard.json()["pipeline"]["total_oportunidades"] == 1
    assert dashboard.json()["pipeline"]["valor_total_estimado"] == 3000

    moved = client.patch(
        f"/kanban/{lead_id}/etapa",
        headers=headers,
        json={"etapa": "Fechado"},
    )
    assert moved.status_code == 200
    assert moved.json()["etapa"] == "Fechado"

    dashboard = client.get("/dashboard/metricas", headers=headers)
    assert dashboard.json()["pipeline"]["distribuicao_por_etapa"]["Fechado"] == 1
    assert dashboard.json()["desempenho"]["taxa_conversao_percentual"] == 100

    deleted = client.delete(f"/kanban/{lead_id}", headers=headers)
    assert deleted.status_code == 204

    dashboard = client.get("/dashboard/metricas", headers=headers)
    assert dashboard.json()["pipeline"]["total_oportunidades"] == 0


def test_kanban_exige_token(client):
    response = client.get("/kanban/")

    assert response.status_code == 401
