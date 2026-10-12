
def create_category(client):
    response = client.post(
        "/categories",
        json={"name": "Electronics"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_product(client, category_id, name="Laptop", price=500, quantity=2):
    return client.post(
        "/products",
        json={
            "name": name,
            "description": "Test product",
            "category_id": category_id,
            "price": price,
            "quantity": quantity,
        },
    )


def test_product_crud(client):
    category_id = create_category(client)
    response = create_product(client, category_id)
    assert response.status_code == 201

    product = response.json()
    product_id = product["id"]
    assert product["price"] == 500
    assert product["quantity"] == 2
    assert "created_at" in product
    assert "updated_at" in product

    assert client.get("/products").status_code == 200
    assert client.get(f"/products/{product_id}").status_code == 200

    updated = client.put(
        f"/products/{product_id}",
        json={"price": 750, "quantity": 3},
    )
    assert updated.status_code == 200
    assert updated.json()["price"] == 750
    assert updated.json()["quantity"] == 3

    assert client.delete(f"/products/{product_id}").status_code == 204
    assert client.get(f"/products/{product_id}").status_code == 404


def test_product_validation_and_category_reference(client):
    category_id = create_category(client)

    assert create_product(client, 9999).status_code == 404
    assert create_product(client, category_id, price=-1).status_code == 422
    assert create_product(client, category_id, quantity=-1).status_code == 422
    assert create_product(client, category_id, name=" ").status_code == 422

    product = create_product(client, category_id).json()
    assert client.put(
        f"/products/{product['id']}",
        json={"category_id": 9999},
    ).status_code == 404


def test_product_search_filters_and_inventory_value(client):
    category_id = create_category(client)

    assert create_product(
        client, category_id, "Laptop Pro", 500, 2
    ).status_code == 201

    assert create_product(
        client, category_id, "Laptop Air", 1000, 1
    ).status_code == 201

    assert create_product(
        client, category_id, "Mouse", 50, 4
    ).status_code == 201

    assert len(client.get(
        "/products", params={"category_id": category_id}
    ).json()) == 3

    assert len(client.get(
        "/products", params={"min_price": 100, "max_price": 1000}
    ).json()) == 2

    assert len(client.get(
        "/products", params={"search": "laptop"}
    ).json()) == 2

    assert client.get(
        "/products", params={"min_price": 1000, "max_price": 100}
    ).status_code == 422

    inventory = client.get("/products/inventory-value")
    assert inventory.status_code == 200
    assert inventory.json()["total_inventory_value"] == 2050.0
    assert inventory.json()["product_count"] == 3


def test_missing_product_and_invalid_payload(client):
    assert client.get("/products/9999").status_code == 404
    assert client.put("/products/9999", json={"price": 20}).status_code == 404
    assert client.delete("/products/9999").status_code == 404

    category_id = create_category(client)

    assert client.post(
        "/products",
        json={
            "name": "Bad Product",
            "category_id": category_id,
            "price": 10,
        },
    ).status_code == 422
