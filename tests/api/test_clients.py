def test_create_client(client):
    response = client.post(
        "/clients",
        json={
            "name": "Ana",
            "cpf": "529.982.247-25",
            "email": "ana@test.com"
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["cpf"] == "52998224725"
    assert data["is_active"] is True
