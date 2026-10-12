
def test_category_crud(client):
    response = client.post(
        "/categories",
        json={"name": "Electronics", "description": "Electronic items"},
    )
    assert response.status_code == 201
    category = response.json()
    category_id = category["id"]
    assert category["name"] == "Electronics"
    assert "created_at" in category

    assert client.get("/categories").status_code == 200
    assert client.get(f"/categories/{category_id}").status_code == 200

    updated = client.put(
        f"/categories/{category_id}",
        json={"name": "Gadgets"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Gadgets"

    deleted = client.delete(f"/categories/{category_id}")
    assert deleted.status_code == 204

    assert client.get(f"/categories/{category_id}").status_code == 404


def test_duplicate_category(client):
    payload = {"name": "Books", "description": "Reading material"}
    assert client.post("/categories", json=payload).status_code == 201
    assert client.post("/categories", json=payload).status_code == 409


def test_missing_category(client):
    assert client.get("/categories/9999").status_code == 404
    assert client.put("/categories/9999", json={"name": "Unknown"}).status_code == 404
    assert client.delete("/categories/9999").status_code == 404


def test_cannot_delete_category_with_products(client):
    category = client.post(
        "/categories", json={"name": "Computers"}
    ).json()

    response = client.post(
        "/products",
        json={
            "name": "Laptop",
            "category_id": category["id"],
            "price": 500,
            "quantity": 2,
        },
    )
    assert response.status_code == 201

    assert client.get(
        f"/categories/{category['id']}/products"
    ).status_code == 200

    assert client.delete(
        f"/categories/{category['id']}"
    ).status_code == 409
