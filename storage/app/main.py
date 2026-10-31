from fastapi import FastAPI

from app.api.routes import router
from app.config import Settings
from app.domain.services import ItemService
from app.storage.repository import SQLiteItemRepository


def create_app(service: ItemService | None = None) -> FastAPI:
    app = FastAPI(
        title="Storage Service",
        version="1.0.0",
    )

    if service is None:
        settings = Settings()
        repository = SQLiteItemRepository(settings.db_path)
        service = ItemService(repository)

    app.state.item_service = service
    app.include_router(router)

    return app


app = create_app()
