def test_register_customer(client):
    resp = client.post(
        "/auth/register", json={"email": "newcustomer1@test.com", "password": "pass1234"}
    )
    assert resp.status_code == 201
    assert resp.json()["role"] == "CUSTOMER"


def test_register_business(client):
    resp = client.post(
        "/auth/register-business", json={"email": "newbiz1@test.com", "password": "pass1234"}
    )
    assert resp.status_code == 201
    assert resp.json()["role"] == "BUSINESS"


def test_register_duplicate_email_fails(client, customer):
    resp = client.post(
        "/auth/register", json={"email": customer["email"], "password": "pass1234"}
    )
    assert resp.status_code == 400


def test_login_wrong_password_fails(client, customer):
    resp = client.post(
        "/auth/login", json={"email": customer["email"], "password": "wrong-password"}
    )
    assert resp.status_code == 401


def test_protected_endpoint_without_token_returns_401(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_me_returns_current_user(client, customer):
    resp = client.get("/auth/me", headers=customer["headers"])
    assert resp.status_code == 200
    assert resp.json()["email"] == customer["email"]


def test_refresh_rotates_token_and_rejects_reuse(client, customer):
    resp = client.post("/auth/refresh", json={"refresh_token": customer["refresh_token"]})
    assert resp.status_code == 200
    new_refresh = resp.json()["refresh_token"]
    assert new_refresh != customer["refresh_token"]

    reuse_resp = client.post("/auth/refresh", json={"refresh_token": customer["refresh_token"]})
    assert reuse_resp.status_code == 401

    second_use_resp = client.post("/auth/refresh", json={"refresh_token": new_refresh})
    assert second_use_resp.status_code == 200


def test_logout_revokes_refresh_token(client, customer):
    logout_resp = client.post("/auth/logout", headers=customer["headers"])
    assert logout_resp.status_code == 204

    refresh_resp = client.post("/auth/refresh", json={"refresh_token": customer["refresh_token"]})
    assert refresh_resp.status_code == 401


def test_customer_forbidden_from_business_only_route(client, customer):
    resp = client.get("/auth/business-only", headers=customer["headers"])
    assert resp.status_code == 403


def test_business_forbidden_from_customer_only_route(client, business):
    resp = client.get("/auth/customer-only", headers=business["headers"])
    assert resp.status_code == 403
