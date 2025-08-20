from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from app import models
from app.main import app, get_db

TEST_DB_URL = "sqlite:///./test_products.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(autouse=True)
def setup_database():
    models.base.metadata.drop_all(bind=test_engine)
    models.base.metadata.create_all(bind=test_engine)
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

def test_create_product(client):
    payload = {"name": "prod1", "stock": 10, "price": 99.5}
    response = client.post("/products/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 0
    assert data["name"] == payload["name"]
    assert data["stock"] == payload["stock"]
    assert data["price"] == payload["price"]

def test_get_product_not_found(client):
    response = client.get("/products/999999")
    assert response.status_code == 404

def test_crud_flow(client):
    create_payload = {"name": "prod2", "stock": 5, "price": 10.0}
    create_resp = client.post("/products/", json=create_payload)
    assert create_resp.status_code == 201
    product_id = create_resp.json()["id"]

    read_resp = client.get(f"/products/{product_id}")
    assert read_resp.status_code == 200

    update_payload = {"stock": 7, "price": 12.5}  # parcial
    update_resp = client.put(f"/products/{product_id}", json=update_payload)
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["stock"] == 7
    assert updated["price"] == 12.5

    delete_resp = client.delete(f"/products/{product_id}")
    assert delete_resp.status_code == 200

    read_after_delete = client.get(f"/products/{product_id}")
    assert read_after_delete.status_code == 404

def test_duplicate_name_returns_400(client):
    payload = {"name": "same_name", "stock": 1, "price": 1.0}
    resp1 = client.post("/products/", json=payload)
    assert resp1.status_code == 201
    resp2 = client.post("/products/", json=payload)
    assert resp2.status_code == 400
    assert resp2.json().get("detail") == "Producto ya existe"
