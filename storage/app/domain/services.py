from app.domain.models import Item
from app.domain.ports import ItemRepository


class ItemNotFoundError(Exception):
    pass


class ItemService:
    def __init__(self, repository: ItemRepository) -> None:
        self.repository = repository

    def create_item(
        self,
        name: str,
        price: float,
        quantity: int,
    ) -> Item:
        name = name.strip()

        if not name:
            raise ValueError("item name must not be empty")

        if price <= 0:
            raise ValueError("item price must be positive")

        if quantity < 0:
            raise ValueError("item quantity must not be negative")

        return self.repository.create(
            name=name,
            price=price,
            quantity=quantity,
        )

    def get_item(self, item_id: int) -> Item:
        item = self.repository.get(item_id)

        if item is None:
            raise ItemNotFoundError("item not found")

        return item
