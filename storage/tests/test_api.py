from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.domain.services import ItemService
from app.main import create_app
from app.storage.repository import SQLiteItemRepository


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    db_path = tmp_path / "test_items.db"

    repository = SQLiteItemRepository(str(db_path))
    service = ItemService(repository)

    return TestClient(create_app(service))


def test_create_item_201(client: TestClient) -> None:
    response = client.post(
        "/items",
        json={"name": "Mouse", "price": 1500, "quantity": 5},
    )

    assert response.status_code == 201

    data = response.json()
    assert data["id"] >= 1
    assert data["name"] == "Mouse"
    assert data["price"] == 1500
    assert data["quantity"] == 5


def test_get_existing_item_200(client: TestClient) -> None:
    created = client.post(
        "/items",
        json={"name": "Keyboard", "price": 3000, "quantity": 2},
    )

    item_id = created.json()["id"]
    response = client.get(f"/items/{item_id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Keyboard"
    assert response.json()["id"] == item_id


def test_get_missing_item_404(client: TestClient) -> None:
    response = client.get("/items/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "item not found"


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "", "price": 1500, "quantity": 5},
        {"name": "Mouse", "price": 0, "quantity": 5},
        {"name": "Mouse", "price": 1500, "quantity": -1},
    ],
)
def test_invalid_item_422(
    client: TestClient,
    payload: dict[str, str | int],
) -> None:
    response = client.post("/items", json=payload)

    assert response.status_code == 422


def test_whitespace_name_422(client: TestClient) -> None:
    response = client.post(
        "/items",
        json={"name": "   ", "price": 1500, "quantity": 5},
    )

    assert response.status_code == 422


def test_invalid_id_422(client: TestClient) -> None:
    response = client.get("/items/not-a-number")

    assert response.status_code == 422


@pytest.mark.parametrize("path", ["/docs", "/openapi.json"])
def test_documentation(client: TestClient, path: str) -> None:
    response = client.get(path)

    assert response.status_code == 200


def test_sqlite_persistence(tmp_path: Path) -> None:
    db_path = str(tmp_path / "persistent.db")

    first_repository = SQLiteItemRepository(db_path)

    created = first_repository.create(
        name="SSD",
        price=5000,
        quantity=2,
    )

    second_repository = SQLiteItemRepository(db_path)
    found = second_repository.get(created.id)

    assert found == created
