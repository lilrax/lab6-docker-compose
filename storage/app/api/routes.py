from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.schemas import ItemCreate, ItemRead
from app.domain.services import ItemNotFoundError, ItemService

router = APIRouter()


def get_service(request: Request) -> ItemService:
    return request.app.state.item_service


ServiceDep = Annotated[ItemService, Depends(get_service)]


@router.post(
    "/items",
    response_model=ItemRead,
    status_code=status.HTTP_201_CREATED,
)
def create_item(payload: ItemCreate, service: ServiceDep) -> ItemRead:
    try:
        item = service.create_item(
            name=payload.name,
            price=payload.price,
            quantity=payload.quantity,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return ItemRead.model_validate(asdict(item))


@router.get("/items/{item_id}", response_model=ItemRead)
def get_item(item_id: int, service: ServiceDep) -> ItemRead:
    try:
        item = service.get_item(item_id)
    except ItemNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="item not found",
        ) from exc

    return ItemRead.model_validate(asdict(item))
