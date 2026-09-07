import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.config import settings
from app.db.session import get_db

engine = create_engine(settings.DATABASE_URL)


@pytest.fixture()
def db_session():
    """Run each test in one outer transaction, then roll it back.

    The app's service functions call db.commit() as they go (e.g. after creating
    a user). We don't want those commits to actually save data to Supabase, so
    join_transaction_mode="create_savepoint" makes each db.commit() only close a
    SAVEPOINT nested inside our outer transaction, instead of ending it. The outer
    transaction stays open until we roll it back below, which erases everything
    the test did.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection, join_transaction_mode="create_savepoint")()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def register_and_login(client: TestClient, role: str) -> dict:
    """Register a fresh unique user of the given role and log in.

    Returns a dict with: headers, access_token, refresh_token, user, email, password.
    """
    email = f"{role.lower()}_{uuid.uuid4().hex}@test.com"
    password = "testpass123"
    path = "/auth/register-business" if role == "BUSINESS" else "/auth/register"

    register_resp = client.post(path, json={"email": email, "password": password})
    assert register_resp.status_code == 201, register_resp.text
    user = register_resp.json()

    login_resp = client.post("/auth/login", json={"email": email, "password": password})
    assert login_resp.status_code == 200, login_resp.text
    tokens = login_resp.json()

    return {
        "headers": {"Authorization": f"Bearer {tokens['access_token']}"},
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "user": user,
        "email": email,
        "password": password,
    }


@pytest.fixture()
def business(client):
    return register_and_login(client, "BUSINESS")


@pytest.fixture()
def customer(client):
    return register_and_login(client, "CUSTOMER")


@pytest.fixture()
def second_customer(client):
    return register_and_login(client, "CUSTOMER")
