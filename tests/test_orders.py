import uuid


def _create_product(client, business, quantity=10, price=10.0):
    payload = {
        "name": "Order Test Product",
        "sku": f"SKU-{uuid.uuid4().hex[:10]}",
        "price": price,
        "initial_quantity": quantity,
    }
    resp = client.post("/products", json=payload, headers=business["headers"])
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_customer_can_place_order_and_inventory_decrements(client, business, customer):
    product = _create_product(client, business, quantity=10, price=10.0)

    order_resp = client.post(
        "/orders",
        json={"items": [{"product_id": product["id"], "quantity": 3}]},
        headers=customer["headers"],
    )
    assert order_resp.status_code == 201, order_resp.text
    order = order_resp.json()
    assert order["total_amount"] == 30.0
    assert order["status"] == "PENDING"

    inventory_resp = client.get(f"/inventory/{product['id']}", headers=business["headers"])
    assert inventory_resp.status_code == 200
    assert inventory_resp.json()["quantity"] == 7


def test_order_rejected_when_insufficient_stock(client, business, customer):
    product = _create_product(client, business, quantity=2)

    resp = client.post(
        "/orders",
        json={"items": [{"product_id": product["id"], "quantity": 5}]},
        headers=customer["headers"],
    )
    assert resp.status_code == 400

    inventory_resp = client.get(f"/inventory/{product['id']}", headers=business["headers"])
    assert inventory_resp.json()["quantity"] == 2


def test_customer_cannot_see_another_customers_order(client, business, customer, second_customer):
    product = _create_product(client, business, quantity=10)
    order_resp = client.post(
        "/orders",
        json={"items": [{"product_id": product["id"], "quantity": 1}]},
        headers=customer["headers"],
    )
    order_id = order_resp.json()["id"]

    resp = client.get(f"/orders/{order_id}", headers=second_customer["headers"])
    assert resp.status_code == 404


def test_business_can_view_all_orders(client, business, customer):
    product = _create_product(client, business, quantity=10)
    client.post(
        "/orders",
        json={"items": [{"product_id": product["id"], "quantity": 1}]},
        headers=customer["headers"],
    )

    resp = client.get("/orders", headers=business["headers"])
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_business_cancel_restocks_inventory(client, business, customer):
    product = _create_product(client, business, quantity=10)
    order_resp = client.post(
        "/orders",
        json={"items": [{"product_id": product["id"], "quantity": 4}]},
        headers=customer["headers"],
    )
    order_id = order_resp.json()["id"]

    cancel_resp = client.patch(
        f"/orders/{order_id}/status", json={"status": "CANCELLED"}, headers=business["headers"]
    )
    assert cancel_resp.status_code == 200

    inventory_resp = client.get(f"/inventory/{product['id']}", headers=business["headers"])
    assert inventory_resp.json()["quantity"] == 10
