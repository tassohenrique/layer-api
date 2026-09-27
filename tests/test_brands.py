def create_brand(client, name="Dior", country="França"):
    response = client.post("/brands", json={"name": name, "country": country})
    assert response.status_code == 201
    return response.json()


def test_create_brand(client):
    data = create_brand(client)

    assert data["name"] == "Dior"
    assert data["country"] == "França"
    assert "id" in data
    assert "created_at" in data


def test_create_brand_with_duplicate_name_returns_409(client):
    create_brand(client, name="Dior")

    response = client.post("/brands", json={"name": "dior"})

    assert response.status_code == 409


def test_create_brand_with_empty_name_returns_422(client):
    response = client.post("/brands", json={"name": ""})

    assert response.status_code == 422


def test_list_brands_returns_alphabetical_order(client):
    for name in ["Guerlain", "Chanel", "Dior"]:
        create_brand(client, name=name)

    response = client.get("/brands")

    assert response.status_code == 200
    assert [brand["name"] for brand in response.json()] == [
        "Chanel",
        "Dior",
        "Guerlain",
    ]


def test_list_brands_with_pagination(client):
    for name in ["Chanel", "Dior", "Guerlain"]:
        create_brand(client, name=name)

    response = client.get("/brands", params={"skip": 1, "limit": 1})

    assert [brand["name"] for brand in response.json()] == ["Dior"]


def test_get_brand_not_found_returns_404(client):
    response = client.get("/brands/999999")

    assert response.status_code == 404


def test_update_brand_changes_only_sent_fields(client):
    brand = create_brand(client, name="Dior", country="França")

    response = client.patch(f"/brands/{brand['id']}", json={"country": "France"})

    assert response.status_code == 200
    assert response.json()["name"] == "Dior"
    assert response.json()["country"] == "France"


def test_update_brand_to_existing_name_returns_409(client):
    create_brand(client, name="Chanel")
    dior = create_brand(client, name="Dior")

    response = client.patch(f"/brands/{dior['id']}", json={"name": "Chanel"})

    assert response.status_code == 409


def test_delete_brand(client):
    brand = create_brand(client)

    response = client.delete(f"/brands/{brand['id']}")
    assert response.status_code == 204

    response = client.get(f"/brands/{brand['id']}")
    assert response.status_code == 404
