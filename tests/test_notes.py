import pytest


@pytest.fixture
def client(client, admin_headers):
    """Neste arquivo, todas as requisições são feitas como administrador."""
    client.headers.update(admin_headers)
    return client


def create_note(client, name="Bergamota"):
    response = client.post("/notes", json={"name": name})
    assert response.status_code == 201
    return response.json()


def test_create_note(client):
    data = create_note(client)

    assert data["name"] == "Bergamota"
    assert "id" in data
    assert "created_at" in data


def test_create_note_with_duplicate_name_returns_409(client):
    create_note(client, name="Oud")

    response = client.post("/notes", json={"name": "oud"})

    assert response.status_code == 409


def test_create_note_with_name_too_long_returns_422(client):
    response = client.post("/notes", json={"name": "a" * 61})

    assert response.status_code == 422


def test_list_notes_returns_alphabetical_order(client):
    for name in ["Vetiver", "Baunilha", "Oud"]:
        create_note(client, name=name)

    response = client.get("/notes")

    assert response.status_code == 200
    assert [note["name"] for note in response.json()] == ["Baunilha", "Oud", "Vetiver"]


def test_get_note_not_found_returns_404(client):
    response = client.get("/notes/999999")

    assert response.status_code == 404


def test_update_note(client):
    note = create_note(client, name="Bergamota")

    response = client.patch(
        f"/notes/{note['id']}", json={"name": "Bergamota da Calábria"}
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Bergamota da Calábria"


def test_update_note_to_existing_name_returns_409(client):
    create_note(client, name="Oud")
    vanilla = create_note(client, name="Baunilha")

    response = client.patch(f"/notes/{vanilla['id']}", json={"name": "Oud"})

    assert response.status_code == 409


def test_delete_note(client):
    note = create_note(client)

    response = client.delete(f"/notes/{note['id']}")
    assert response.status_code == 204

    response = client.get(f"/notes/{note['id']}")
    assert response.status_code == 404


def test_update_note_with_null_name_returns_422(client):
    note = create_note(client)

    response = client.patch(f"/notes/{note['id']}", json={"name": None})

    assert response.status_code == 422
