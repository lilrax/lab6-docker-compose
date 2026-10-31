import pytest

from app.domain.models import Item
from app.domain.services import ItemNotFoundError, ItemService


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
def service() -> ItemService:
    return ItemService(FakeItemRepository())


def test_create_item(service: ItemService) -> None:
    item = service.create_item("  Mouse  ", 1500, 5)

    assert item.id == 1
    assert item.name == "Mouse"
    assert item.price == 1500
    assert item.quantity == 5


def test_create_empty_name(service: ItemService) -> None:
    with pytest.raises(ValueError, match="item name must not be empty"):
        service.create_item("   ", 1500, 5)


@pytest.mark.parametrize("price", [0, -100])
def test_create_invalid_price(
    service: ItemService,
    price: float,
) -> None:
    with pytest.raises(ValueError, match="item price must be positive"):
        service.create_item("Mouse", price, 5)


def test_create_negative_quantity(service: ItemService) -> None:
    with pytest.raises(
        ValueError,
        match="item quantity must not be negative",
    ):
        service.create_item("Mouse", 1500, -5)


def test_get_existing_item(service: ItemService) -> None:
    created = service.create_item("Keyboard", 3000, 2)

    found = service.get_item(created.id)

    assert found == created


def test_get_missing_item(service: ItemService) -> None:
    with pytest.raises(ItemNotFoundError, match="item not found"):
        service.get_item(999)
