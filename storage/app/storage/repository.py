import sqlite3
from pathlib import Path

from app.domain.models import Item


class SQLiteItemRepository:
    def __init__(self, database_path: str) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL
                )
                """
            )

    def create(self, name: str, price: float, quantity: int) -> Item:
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO items (name, price, quantity)
                VALUES (?, ?, ?)
                """,
                (name, price, quantity),
            )
            item_id = cursor.lastrowid

        if item_id is None:
            raise RuntimeError("failed to create item")

        return Item(
            id=item_id,
            name=name,
            price=price,
            quantity=quantity,
        )

    def get(self, item_id: int) -> Item | None:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT id, name, price, quantity
                FROM items
                WHERE id = ?
                """,
                (item_id,),
            ).fetchone()

        if row is None:
            return None

        return Item(
            id=row[0],
            name=row[1],
            price=row[2],
            quantity=row[3],
        )
