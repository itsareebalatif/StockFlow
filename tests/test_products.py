import uuid


def _create_product(client, business, **overrides):
    payload = {
        "name": "Test Widget",
        "sku": f"SKU-{uuid.uuid4().hex[:10]}",
        "price": 12.5,
        "initial_quantity": 10,
        **overrides,
    }
    return client.post("/products", json=payload, headers=business["headers"])


def test_business_can_create_product(client, business):
    resp = _create_product(client, business)
    assert resp.status_code == 201
    body = resp.json()
    assert body["available_quantity"] == 10


def test_customer_cannot_create_product(client, customer):
    payload = {"name": "X", "sku": f"SKU-{uuid.uuid4().hex[:10]}", "price": 5}
    resp = client.post("/products", json=payload, headers=customer["headers"])
    assert resp.status_code == 403


def test_duplicate_sku_rejected(client, business):
    resp = _create_product(client, business, sku="DUPLICATE-SKU")
    assert resp.status_code == 201

    resp2 = _create_product(client, business, sku="DUPLICATE-SKU")
    assert resp2.status_code == 400


def test_customer_can_list_and_read_products(client, business, customer):
    create_resp = _create_product(client, business)
    product_id = create_resp.json()["id"]

    list_resp = client.get("/products", headers=customer["headers"])
    assert list_resp.status_code == 200
    assert any(p["id"] == product_id for p in list_resp.json())

    get_resp = client.get(f"/products/{product_id}", headers=customer["headers"])
    assert get_resp.status_code == 200


def test_business_can_update_and_delete_product(client, business):
    create_resp = _create_product(client, business)
    product_id = create_resp.json()["id"]

    update_resp = client.patch(
        f"/products/{product_id}", json={"price": 99.99}, headers=business["headers"]
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["price"] == 99.99

    delete_resp = client.delete(f"/products/{product_id}", headers=business["headers"])
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/products/{product_id}", headers=business["headers"])
    assert get_resp.status_code == 404
