def test_create_service_order(client):
    response = client.post(
        "/service-orders",
        json={
            "client_id": 1,
            "vehicle_id": 1
        },
    )

    assert response.status_code == 201
    data = response.json()

    assert data["status"] == "RECEBIDA"
    assert data["total_amount"] == 0
    assert data["items"] == []
