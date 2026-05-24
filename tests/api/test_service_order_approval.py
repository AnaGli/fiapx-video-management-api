from app.models.service_order import ServiceOrderStatus


def test_approve_service_order_success(client, db_session):
    """
    Cenário:
    - Existe cliente com CPF
    - Existe OS em AGUARDANDO_APROVACAO
    - Cliente aprova a OS via CPF
    """

    # 🔹 Cria cliente
    client_resp = client.post(
        "/clients",
        json={
            "name": "Cliente Teste",
            "cpf": "129.139.610-10",
            "email": "test@test.com"
        },
    )
    cpf = client_resp.json()["cpf"]
    assert client_resp.status_code == 201
    client_id = client_resp.json()["id"]

    vehicle_resp = client.post(
    f"/clients/{cpf}/vehicles",
    json={
        "plate": "ABC1234",
        "brand": "VW",
        "model": "Gol",
        "year": 2020,
    },
    )

    assert vehicle_resp.status_code == 201
    vehicle_id = vehicle_resp.json()["id"]


    # 🔹 Cria OS
    order_resp = client.post(
        "/service-orders",
        json={
            "client_id": client_id,
            "vehicle_id": vehicle_id,
        },
    )
    assert order_resp.status_code == 201
    order = order_resp.json()
    order_id = order["id"]

    # 🔹 Força status para AGUARDANDO_APROVACAO (simula orçamento enviado)
    order["status"] = ServiceOrderStatus.AGUARDANDO_APROVACAO.value

    # Atualiza direto no banco (integração real)
    from app.models.service_order import ServiceOrder

    db_order = db_session.get(ServiceOrder, order_id)
    db_order.status = ServiceOrderStatus.AGUARDANDO_APROVACAO
    db_session.commit()

    # 🔹 Aprovação do orçamento (SEM TOKEN)
    approve_resp = client.post(
        f"/service-orders/{order_id}/approve",
        json={"cpf": "129.139.610-10"},
    )

    assert approve_resp.status_code == 200, approve_resp.text

    data = approve_resp.json()

    assert data["status"] == ServiceOrderStatus.EM_EXECUCAO.value
    assert data["id"] == order_id

def test_approve_service_order_invalid_cpf(client):
    resp = client.post(
        "/service-orders/999/approve",
        json={"cpf": "111.111.111-11"},
    )

    assert resp.status_code in (400, 422)
