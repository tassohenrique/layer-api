import pytest
from sqlalchemy import func, select

from app.models import Review


@pytest.fixture
def perfume(client, admin_headers):
    brand = client.post("/brands", json={"name": "Dior"}, headers=admin_headers).json()
    return client.post(
        "/perfumes",
        json={"name": "Sauvage", "brand_id": brand["id"], "gender": "masculine"},
        headers=admin_headers,
    ).json()


def create_review(client, perfume_id, headers, **overrides):
    payload = {"rating": 8, "longevity": 4, "sillage": 3, "text": "Muito bom."}
    payload.update(overrides)
    response = client.post(
        f"/perfumes/{perfume_id}/reviews", json=payload, headers=headers
    )
    assert response.status_code == 201
    return response.json()


# --- Leitura ---


def test_anyone_can_list_reviews(client, perfume):
    response = client.get(f"/perfumes/{perfume['id']}/reviews")

    assert response.status_code == 200
    assert response.json() == []


def test_list_reviews_of_missing_perfume_returns_404(client):
    response = client.get("/perfumes/999999/reviews")

    assert response.status_code == 404


def test_reviews_are_listed_newest_first(
    client, perfume, user_headers, other_user_headers
):
    first = create_review(client, perfume["id"], user_headers)
    second = create_review(client, perfume["id"], other_user_headers)

    response = client.get(f"/perfumes/{perfume['id']}/reviews")

    assert [review["id"] for review in response.json()] == [second["id"], first["id"]]


# --- Criação ---


def test_create_review_requires_login(client, perfume):
    response = client.post(f"/perfumes/{perfume['id']}/reviews", json={"rating": 8})

    assert response.status_code == 401


def test_user_can_create_review(client, perfume, user_headers):
    data = create_review(client, perfume["id"], user_headers)

    assert data["rating"] == 8
    assert data["perfume_id"] == perfume["id"]
    assert data["author"]["name"] == "Usuário de Teste"
    assert "email" not in data["author"]


def test_user_cannot_review_same_perfume_twice(client, perfume, user_headers):
    create_review(client, perfume["id"], user_headers)

    response = client.post(
        f"/perfumes/{perfume['id']}/reviews", json={"rating": 5}, headers=user_headers
    )

    assert response.status_code == 409


@pytest.mark.parametrize("rating", [0, 11])
def test_create_review_with_rating_out_of_range_returns_422(
    client, perfume, user_headers, rating
):
    response = client.post(
        f"/perfumes/{perfume['id']}/reviews",
        json={"rating": rating},
        headers=user_headers,
    )

    assert response.status_code == 422


def test_create_review_for_missing_perfume_returns_404(client, user_headers):
    response = client.post(
        "/perfumes/999999/reviews", json={"rating": 8}, headers=user_headers
    )

    assert response.status_code == 404


# --- Edição ---


def test_author_can_update_review(client, perfume, user_headers):
    review = create_review(client, perfume["id"], user_headers)

    response = client.patch(
        f"/reviews/{review['id']}", json={"rating": 10}, headers=user_headers
    )

    assert response.status_code == 200
    assert response.json()["rating"] == 10
    assert response.json()["text"] == "Muito bom."
    assert response.json()["updated_at"] != review["updated_at"]


def test_other_user_cannot_update_review(
    client, perfume, user_headers, other_user_headers
):
    review = create_review(client, perfume["id"], user_headers)

    response = client.patch(
        f"/reviews/{review['id']}", json={"rating": 1}, headers=other_user_headers
    )

    assert response.status_code == 403


def test_update_review_with_null_rating_returns_422(client, perfume, user_headers):
    review = create_review(client, perfume["id"], user_headers)

    response = client.patch(
        f"/reviews/{review['id']}", json={"rating": None}, headers=user_headers
    )

    assert response.status_code == 422


# --- Exclusão ---


def test_author_can_delete_review(client, perfume, user_headers):
    review = create_review(client, perfume["id"], user_headers)

    response = client.delete(f"/reviews/{review['id']}", headers=user_headers)

    assert response.status_code == 204


def test_other_user_cannot_delete_review(
    client, perfume, user_headers, other_user_headers
):
    review = create_review(client, perfume["id"], user_headers)

    response = client.delete(f"/reviews/{review['id']}", headers=other_user_headers)

    assert response.status_code == 403


def test_admin_can_delete_any_review(client, perfume, user_headers, admin_headers):
    review = create_review(client, perfume["id"], user_headers)

    response = client.delete(f"/reviews/{review['id']}", headers=admin_headers)

    assert response.status_code == 204


def test_reviews_are_deleted_with_their_perfume(
    client, db_session, perfume, user_headers, admin_headers
):
    create_review(client, perfume["id"], user_headers)

    client.delete(f"/perfumes/{perfume['id']}", headers=admin_headers)

    remaining = db_session.scalar(select(func.count()).select_from(Review))
    assert remaining == 0


# --- Média e ranking ---


def test_perfume_shows_average_rating_and_review_count(
    client, perfume, user_headers, other_user_headers
):
    create_review(client, perfume["id"], user_headers, rating=8)
    create_review(client, perfume["id"], other_user_headers, rating=9)

    response = client.get(f"/perfumes/{perfume['id']}")

    assert response.json()["average_rating"] == 8.5
    assert response.json()["review_count"] == 2


def test_perfume_without_reviews_has_no_average(client, perfume):
    response = client.get(f"/perfumes/{perfume['id']}")

    assert response.json()["average_rating"] is None
    assert response.json()["review_count"] == 0


def test_list_perfumes_sorted_by_rating_puts_unrated_last(
    client, admin_headers, user_headers
):
    brand = client.post(
        "/brands", json={"name": "Chanel"}, headers=admin_headers
    ).json()
    ids = {}
    for name in ["Bleu", "Allure", "Egoiste"]:
        response = client.post(
            "/perfumes",
            json={"name": name, "brand_id": brand["id"], "gender": "masculine"},
            headers=admin_headers,
        )
        ids[name] = response.json()["id"]

    create_review(client, ids["Bleu"], user_headers, rating=5)
    create_review(client, ids["Allure"], user_headers, rating=9)

    response = client.get("/perfumes", params={"sort": "rating"})

    assert [perfume["name"] for perfume in response.json()] == [
        "Allure",
        "Bleu",
        "Egoiste",
    ]
