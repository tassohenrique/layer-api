import pytest


@pytest.fixture
def client(client, admin_headers):
    """Neste arquivo, todas as requisições são feitas como administrador."""
    client.headers.update(admin_headers)
    return client


@pytest.fixture
def brand(client):
    return client.post("/brands", json={"name": "Dior", "country": "França"}).json()


@pytest.fixture
def notes(client):
    return [
        client.post("/notes", json={"name": name}).json()
        for name in ["Bergamota", "Pimenta", "Ambroxan"]
    ]


def perfume_payload(brand_id, available_notes, **overrides):
    payload = {
        "name": "Sauvage",
        "brand_id": brand_id,
        "release_year": 2015,
        "gender": "masculine",
        "concentration": "edt",
        "perfumer": "François Demachy",
        "notes": [
            {"note_id": available_notes[0]["id"], "layer": "top"},
            {"note_id": available_notes[1]["id"], "layer": "heart"},
            {"note_id": available_notes[2]["id"], "layer": "base"},
        ],
    }
    payload.update(overrides)
    return payload


def create_perfume(client, brand, notes, **overrides):
    response = client.post(
        "/perfumes", json=perfume_payload(brand["id"], notes, **overrides)
    )
    assert response.status_code == 201
    return response.json()


def test_create_perfume_returns_nested_brand_and_notes(client, brand, notes):
    data = create_perfume(client, brand, notes)

    assert data["name"] == "Sauvage"
    assert data["brand"] == {"id": brand["id"], "name": "Dior"}
    assert {(item["note"]["name"], item["layer"]) for item in data["notes"]} == {
        ("Bergamota", "top"),
        ("Pimenta", "heart"),
        ("Ambroxan", "base"),
    }


def test_create_perfume_with_duplicate_name_in_same_brand_returns_409(
    client, brand, notes
):
    create_perfume(client, brand, notes)

    response = client.post(
        "/perfumes", json=perfume_payload(brand["id"], notes, name="sauvage")
    )

    assert response.status_code == 409


def test_same_perfume_name_is_allowed_in_different_brands(client, brand, notes):
    other_brand = client.post("/brands", json={"name": "Outra Marca"}).json()
    create_perfume(client, brand, notes)

    response = client.post("/perfumes", json=perfume_payload(other_brand["id"], notes))

    assert response.status_code == 201


def test_create_perfume_with_missing_brand_returns_404(client, notes):
    response = client.post("/perfumes", json=perfume_payload(999999, notes))

    assert response.status_code == 404


def test_create_perfume_with_missing_note_returns_404(client, brand, notes):
    payload = perfume_payload(
        brand["id"], notes, notes=[{"note_id": 999999, "layer": "top"}]
    )

    response = client.post("/perfumes", json=payload)

    assert response.status_code == 404
    assert "999999" in response.json()["detail"]


def test_create_perfume_with_repeated_note_returns_422(client, brand, notes):
    repeated = [
        {"note_id": notes[0]["id"], "layer": "top"},
        {"note_id": notes[0]["id"], "layer": "base"},
    ]

    response = client.post(
        "/perfumes", json=perfume_payload(brand["id"], notes, notes=repeated)
    )

    assert response.status_code == 422


def test_create_perfume_with_invalid_concentration_returns_422(client, brand, notes):
    payload = perfume_payload(brand["id"], notes, concentration="banana")

    response = client.post("/perfumes", json=payload)

    assert response.status_code == 422


def test_list_perfumes_filtered_by_brand(client, brand, notes):
    other_brand = client.post("/brands", json={"name": "Chanel"}).json()
    create_perfume(client, brand, notes, name="Sauvage")
    create_perfume(client, other_brand, notes, name="Bleu de Chanel")

    response = client.get("/perfumes", params={"brand_id": brand["id"]})

    assert [perfume["name"] for perfume in response.json()] == ["Sauvage"]


def test_update_perfume_replaces_notes(client, brand, notes):
    perfume = create_perfume(client, brand, notes)
    new_notes = [{"note_id": notes[0]["id"], "layer": "top"}]

    response = client.patch(f"/perfumes/{perfume['id']}", json={"notes": new_notes})

    assert response.status_code == 200
    assert len(response.json()["notes"]) == 1


def test_update_perfume_can_move_note_to_another_layer(client, brand, notes):
    perfume = create_perfume(client, brand, notes)
    moved = [{"note_id": notes[0]["id"], "layer": "base"}]

    response = client.patch(f"/perfumes/{perfume['id']}", json={"notes": moved})

    assert response.status_code == 200
    assert response.json()["notes"][0]["layer"] == "base"


def test_update_perfume_without_notes_keeps_existing_notes(client, brand, notes):
    perfume = create_perfume(client, brand, notes)

    response = client.patch(f"/perfumes/{perfume['id']}", json={"release_year": 2018})

    assert response.json()["release_year"] == 2018
    assert len(response.json()["notes"]) == 3


def test_update_perfume_with_null_gender_returns_422(client, brand, notes):
    perfume = create_perfume(client, brand, notes)

    response = client.patch(f"/perfumes/{perfume['id']}", json={"gender": None})

    assert response.status_code == 422


def test_delete_perfume(client, brand, notes):
    perfume = create_perfume(client, brand, notes)

    response = client.delete(f"/perfumes/{perfume['id']}")
    assert response.status_code == 204

    response = client.get(f"/perfumes/{perfume['id']}")
    assert response.status_code == 404


def test_delete_brand_with_perfumes_returns_409(client, brand, notes):
    create_perfume(client, brand, notes)

    response = client.delete(f"/brands/{brand['id']}")

    assert response.status_code == 409


def test_delete_note_in_use_returns_409(client, brand, notes):
    create_perfume(client, brand, notes)

    response = client.delete(f"/notes/{notes[0]['id']}")

    assert response.status_code == 409


def test_update_perfume_to_existing_name_in_same_brand_returns_409(
    client, brand, notes
):
    create_perfume(client, brand, notes, name="Sauvage")
    other = create_perfume(client, brand, notes, name="Fahrenheit")

    response = client.patch(f"/perfumes/{other['id']}", json={"name": "SAUVAGE"})

    assert response.status_code == 409


def test_update_perfume_can_move_to_another_brand(client, brand, notes):
    perfume = create_perfume(client, brand, notes)
    other_brand = client.post("/brands", json={"name": "Chanel"}).json()

    response = client.patch(
        f"/perfumes/{perfume['id']}", json={"brand_id": other_brand["id"]}
    )

    assert response.status_code == 200
    assert response.json()["brand"]["name"] == "Chanel"


def test_update_perfume_to_missing_brand_returns_404(client, brand, notes):
    perfume = create_perfume(client, brand, notes)

    response = client.patch(f"/perfumes/{perfume['id']}", json={"brand_id": 999999})

    assert response.status_code == 404
