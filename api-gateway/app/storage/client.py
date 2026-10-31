import httpx
from pydantic import TypeAdapter, ValidationError

from app.domain.errors import (
    StorageResponseError,
    StorageUnavailableError,
)
from app.domain.models import Item


class HttpItemRepository:
    def __init__(self, base_url: str, timeout: float) -> None:
        self.base_url = base_url
        self.timeout = timeout
        self.item_adapter = TypeAdapter(Item)

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, str | float | int] | None = None,
    ) -> httpx.Response:
        try:
            with httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout,
            ) as client:
                response = client.request(
                    method,
                    path,
                    json=payload,
                )

                if method == "GET" and response.status_code == 404:
                    return response

                response.raise_for_status()
                return response

        except httpx.RequestError as exc:
            raise StorageUnavailableError("storage service unavailable") from exc

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code >= 500:
                raise StorageUnavailableError("storage service unavailable") from exc

            raise StorageResponseError(
                f"storage returned HTTP {exc.response.status_code}"
            ) from exc

    def _parse_item(self, response: httpx.Response) -> Item:
        try:
            return self.item_adapter.validate_json(response.content)
        except ValidationError as exc:
            raise StorageResponseError("invalid storage response") from exc

    def create(self, name: str, price: float, quantity: int) -> Item:
        response = self._request(
            "POST",
            "/items",
            {
                "name": name,
                "price": price,
                "quantity": quantity,
            },
        )
        return self._parse_item(response)

    def get(self, item_id: int) -> Item | None:
        response = self._request("GET", f"/items/{item_id}")

        if response.status_code == 404:
            return None

        return self._parse_item(response)
