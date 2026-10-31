import json
from collections.abc import Callable

import httpx
import pytest

from app.domain.errors import (
    StorageResponseError,
    StorageUnavailableError,
)
from app.domain.models import Item
from app.storage.client import HttpItemRepository

Handler = Callable[[httpx.Request], httpx.Response]


def make_repository(
    monkeypatch: pytest.MonkeyPatch,
    handler: Handler,
) -> HttpItemRepository:
    original_client = httpx.Client

    def fake_client(*args: object, **kwargs: object) -> httpx.Client:
        return original_client(
            *args,
            transport=httpx.MockTransport(handler),
            **kwargs,
        )

    monkeypatch.setattr(httpx, "Client", fake_client)

    return HttpItemRepository(
        base_url="http://storage.test",
        timeout=0.5,
    )


def test_create_item(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/items"
        assert json.loads(request.content) == {
            "name": "Mouse",
            "price": 1500,
            "quantity": 5,
        }

        return httpx.Response(
            201,
            json={
                "id": 12,
                "name": "Mouse",
                "price": 1500,
                "quantity": 5,
            },
        )

    repository = make_repository(monkeypatch, handler)
    item = repository.create("Mouse", 1500, 5)

    assert isinstance(item, Item)
    assert item.id == 12
    assert item.name == "Mouse"


def test_get_item(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/items/12"

        return httpx.Response(
            200,
            json={
                "id": 12,
                "name": "Keyboard",
                "price": 3000,
                "quantity": 2,
            },
        )

    repository = make_repository(monkeypatch, handler)

    item = repository.get(12)

    assert item == Item(12, "Keyboard", 3000, 2)


def test_get_missing_item(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "item not found"})

    repository = make_repository(monkeypatch, handler)

    assert repository.get(999) is None


@pytest.mark.parametrize("status_code", [500, 503])
def test_storage_server_error(
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code)

    repository = make_repository(monkeypatch, handler)

    with pytest.raises(StorageUnavailableError):
        repository.get(1)


def test_storage_validation_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            422,
            json={"detail": "invalid item"},
        )

    repository = make_repository(monkeypatch, handler)

    with pytest.raises(StorageResponseError):
        repository.create("Mouse", -100, 5)


@pytest.mark.parametrize(
    "error",
    [
        httpx.ConnectError("connection refused"),
        httpx.ReadTimeout("read timed out"),
    ],
)
def test_network_errors(
    monkeypatch: pytest.MonkeyPatch,
    error: httpx.RequestError,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise error

    repository = make_repository(monkeypatch, handler)

    with pytest.raises(StorageUnavailableError):
        repository.get(1)


def test_invalid_storage_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not-json")

    repository = make_repository(monkeypatch, handler)

    with pytest.raises(StorageResponseError):
        repository.get(1)
