import pytest
from fastapi.testclient import TestClient

from app.domain.errors import StorageUnavailableError
from app.domain.models import Item
from app.domain.services import ItemService
from app.main import create_app


class FakeItemRepository:
    def __init__(self) -> None:
        self.items: dict[int, Item] = {}
        self.next_id = 1

    def create(self, name: str, price: float, quantity: int) -> Item:
        item = Item(
            id=self.next_id,
            name=name,
            price=price,
            quantity=quantity,
        )
        self.items[item.id] = item
        self.next_id += 1
        return item

    def get(self, item_id: int) -> Item | None:
        return self.items.get(item_id)


@pytest.fixture
def client() -> TestClient:
    repository = FakeItemRepository()
    service = ItemService(repository)

    return TestClient(create_app(service))


def test_create_item_201(client: TestClient) -> None:
    response = client.post(
        "/items",
        json={"name": "Mouse", "price": 1500, "quantity": 5},
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "name": "Mouse",
        "price": 1500,
        "quantity": 5,
    }


def test_get_item_200(client: TestClient) -> None:
    created = client.post(
        "/items",
        json={"name": "Keyboard", "price": 3000, "quantity": 2},
    )

    item_id = created.json()["id"]
    response = client.get(f"/items/{item_id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Keyboard"


def test_get_missing_item_404(client: TestClient) -> None:
    response = client.get("/items/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "item not found"


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "", "price": 1500, "quantity": 5},
        {"name": "Mouse", "price": -100, "quantity": 5},
        {"name": "Mouse", "price": 1500, "quantity": -1},
    ],
)
def test_invalid_item_422(
    client: TestClient,
    payload: dict[str, str | int],
) -> None:
    response = client.post("/items", json=payload)

    assert response.status_code == 422


def test_invalid_id_422(client: TestClient) -> None:
    response = client.get("/items/0")

    assert response.status_code == 422


def test_swagger_docs(client: TestClient) -> None:
    response = client.get("/docs")

    assert response.status_code == 200


class UnavailableRepository:
    def create(self, name: str, price: float, quantity: int) -> Item:
        raise StorageUnavailableError("storage service unavailable")

    def get(self, item_id: int) -> Item | None:
        raise StorageUnavailableError("storage service unavailable")


@pytest.mark.parametrize("method", ["GET", "POST"])
def test_storage_unavailable_503(method: str) -> None:
    service = ItemService(UnavailableRepository())
    client = TestClient(create_app(service))

    if method == "GET":
        response = client.get("/items/1")
    else:
        response = client.post(
            "/items",
            json={"name": "Mouse", "price": 1500, "quantity": 5},
        )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "storage service unavailable",
    }
