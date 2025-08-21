import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch
from redis import RedisError
from app.main import app, get_db
from app import models

TEST_DB_URL = "sqlite:///./test_products.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_database():
    models.base.metadata.drop_all(bind=engine)
    models.base.metadata.create_all(bind=engine)
    yield

@pytest.fixture()
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_create_product_422(client):
    bad = {"name": 12, "stock": "x", "price": "y"}
    resp = client.post("/products/", json=bad)
    assert resp.status_code == 422

def test_get_product_not_found_404(client):
    resp = client.get("/products/999999")
    assert resp.status_code == 404

def test_crud_flow(client):
    create_resp = client.post("/products/", json={"name": "prod2", "stock": 5, "price": 10.0})
    assert create_resp.status_code == 201
    pid = create_resp.json()["id"]
    read_resp = client.get(f"/products/{pid}")
    assert read_resp.status_code == 200
    version = read_resp.json().get("version")
    update_payload = {"stock": 7, "price": 12.5}
    if version is not None:
        update_payload["version"] = version
    upd = client.put(f"/products/{pid}", json=update_payload)
    assert upd.status_code == 200
    data = upd.json()
    assert data["stock"] == 7
    assert data["price"] == 12.5
    del_resp = client.delete(f"/products/{pid}")
    assert del_resp.status_code == 200
    read_after = client.get(f"/products/{pid}")
    assert read_after.status_code == 404

def test_db_failure_returns_500():
    def broken_get_db():
        db = TestingSessionLocal()
        original_commit = db.commit
        def boom():
            raise RuntimeError("DB Failure")
        db.commit = boom
        try:
            yield db
        finally:
            db.commit = original_commit
            db.close()

    app.dependency_overrides[get_db] = broken_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        resp = c.post("/products/", json={"name": "boom", "stock": 1, "price": 1.0})
    app.dependency_overrides.clear()
    assert resp.status_code == 500

@patch("app.redis_cache.redis_client.get", side_effect=RedisError("Redis GET down"))
def test_cache_get_failure_falls_back_to_db(mock_get, client):
    create = client.post("/products/", json={"name": "A", "stock": 1, "price": 1.0})
    assert create.status_code == 201
    pid = create.json()["id"]
    read = client.get(f"/products/{pid}")
    assert read.status_code == 200

@patch("app.redis_cache.redis_client.setex", side_effect=RedisError("Redis SETEX down"))
def test_cache_setex_failure_does_not_break_response(mock_setex, client):
    create = client.post("/products/", json={"name": "B", "stock": 2, "price": 2.0})
    assert create.status_code == 201
    pid = create.json()["id"]
    read = client.get(f"/products/{pid}")
    assert read.status_code == 200

@patch("app.crud.redis_client.delete", side_effect=RedisError("Redis DEL down"))
def test_update_still_works_when_cache_invalidation_fails(mock_del, client):
    create = client.post("/products/", json={"name": "C", "stock": 2, "price": 2.0})
    assert create.status_code == 201
    pid = create.json()["id"]

    ver = client.get(f"/products/{pid}").json().get("version")
    payload = {"stock": 3, "price": 2.5}
    if ver is not None:
        payload["version"] = ver

    upd = client.put(f"/products/{pid}", json=payload)
    assert upd.status_code == 200
    assert upd.json()["stock"] == 3

@patch("app.event_handler.redis_client.publish", side_effect=Exception("Redis PUB down"))
def test_publish_event_failure_does_not_break_create(mock_pub, client):
    resp = client.post("/products/", json={"name": "D", "stock": 1, "price": 1.0})
    assert resp.status_code == 201
