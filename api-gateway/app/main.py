from fastapi import FastAPI

from app.api.routes import router
from app.config import Settings
from app.domain.services import ItemService
from app.storage.client import HttpItemRepository


def create_app(service: ItemService | None = None) -> FastAPI:
    app = FastAPI(
        title="API Gateway",
        version="1.0.0",
    )

    if service is None:
        settings = Settings()

        repository = HttpItemRepository(
            base_url=settings.storage_url,
            timeout=settings.request_timeout,
        )

        service = ItemService(repository)

    app.state.item_service = service
    app.include_router(router)

    return app


app = create_app()
