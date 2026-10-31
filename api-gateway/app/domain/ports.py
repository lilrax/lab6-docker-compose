from typing import Protocol

from app.domain.models import Item


class ItemRepository(Protocol):
    def create(self, name: str, price: float, quantity: int) -> Item: ...

    def get(self, item_id: int) -> Item | None: ...
