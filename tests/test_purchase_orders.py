import uuid


def _create_product(client, business, quantity=5):
    payload = {
        "name": "PO Test Product",
        "sku": f"SKU-{uuid.uuid4().hex[:10]}",
        "price": 8.0,
        "initial_quantity": quantity,
    }
    resp = client.post("/products", json=payload, headers=business["headers"])
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_supplier(client, business):
    resp = client.post(
        "/suppliers", json={"name": f"Supplier-{uuid.uuid4().hex[:6]}"}, headers=business["headers"]
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_business_can_create_and_receive_purchase_order(client, business):
    product = _create_product(client, business, quantity=5)
    supplier = _create_supplier(client, business)

    po_resp = client.post(
        "/purchase-orders",
        json={
            "supplier_id": supplier["id"],
            "items": [{"product_id": product["id"], "quantity": 15, "unit_cost": 3.0}],
        },
        headers=business["headers"],
    )
    assert po_resp.status_code == 201, po_resp.text
    po = po_resp.json()
    assert po["status"] == "DRAFT"
    assert po["total_amount"] == 45.0

    receive_resp = client.patch(
        f"/purchase-orders/{po['id']}/status",
        json={"status": "RECEIVED"},
        headers=business["headers"],
    )
    assert receive_resp.status_code == 200
    assert receive_resp.json()["status"] == "RECEIVED"

    inventory_resp = client.get(f"/inventory/{product['id']}", headers=business["headers"])
    assert inventory_resp.json()["quantity"] == 20


def test_customer_cannot_access_purchase_orders(client, customer):
    resp = client.get("/purchase-orders", headers=customer["headers"])
    assert resp.status_code == 403


def test_customer_cannot_access_suppliers(client, customer):
    resp = client.get("/suppliers", headers=customer["headers"])
    assert resp.status_code == 403
