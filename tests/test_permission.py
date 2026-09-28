import pytest

WRITE_ENDPOINTS = [
    ("post", "/brands"),
    ("patch", "/brands/1"),
    ("delete", "/brands/1"),
    ("post", "/notes"),
    ("patch", "/notes/1"),
    ("delete", "/notes/1"),
    ("post", "/perfumes"),
    ("patch", "/perfumes/1"),
    ("delete", "/perfumes/1"),
]

READ_ENDPOINTS = ["/brands", "/notes", "/perfumes"]


@pytest.mark.parametrize(("method", "url"), WRITE_ENDPOINTS)
def test_write_endpoints_require_authentication(client, method, url):
    response = client.request(method, url, json={})

    assert response.status_code == 401


@pytest.mark.parametrize(("method", "url"), WRITE_ENDPOINTS)
def test_write_endpoints_forbid_regular_users(client, user_headers, method, url):
    response = client.request(method, url, json={}, headers=user_headers)

    assert response.status_code == 403


@pytest.mark.parametrize("url", READ_ENDPOINTS)
def test_read_endpoints_are_public(client, url):
    response = client.get(url)

    assert response.status_code == 200


def test_admin_can_create_brand(client, admin_headers):
    response = client.post("/brands", json={"name": "Dior"}, headers=admin_headers)

    assert response.status_code == 201
