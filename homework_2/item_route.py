from fastapi import APIRouter, Query
from http import HTTPStatus
from typing import Optional

from starlette.responses import JSONResponse

from models import Item, Update_Item, Create_Item
from functions import id_gen_item
from database import items

item_server = APIRouter(prefix="/item")


@item_server.post("")
def add_item(params: Create_Item):
    item_id_generator = id_gen_item()
    item_id = next(item_id_generator)

    new_item = Item(id=item_id, name=params.name, price=params.price, deleted=False)
    items[item_id] = new_item

    return JSONResponse(content=new_item.dict(),
                        status_code=HTTPStatus.CREATED)


@item_server.get("/{item_id}")
def get_item(item_id: int) -> JSONResponse:
    item = items.get(item_id)
    if item and not item.deleted:
        return JSONResponse(content=item.dict(), status_code=HTTPStatus.OK)

    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content={"error": "Item not found", "item_id": item_id}
    )


@item_server.get("")
def get_filtered_item(
        offset: Optional[int] = Query(0, ge=0),
        limit: Optional[int] = Query(10, gt=0),
        min_price: Optional[float] = Query(None, ge=0),
        max_price: Optional[float] = Query(None, ge=0),
        show_deleted: bool = False
):
    if not items:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"error": "Items list not found"}
        )
    else:
        filtered_items = list(items.values())

        if min_price:
            filtered_items = [item for item in filtered_items if item.price >= min_price]
        if max_price:
            filtered_items = [item for item in filtered_items if item.price <= max_price]
        if not show_deleted:
            filtered_items = [item for item in filtered_items if not item.deleted]

        response = [item.dict() for item in filtered_items[offset:offset + limit]]
        return JSONResponse(content=response)


@item_server.put("/{item_id}")
def change_item(item_id: int, params: Create_Item):
    item = items.get(item_id)
    if item and not item.deleted:
        item.name = params.name
        item.price = params.price
        return JSONResponse(content=item.dict())

    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content={"error": "Item not found", "item_id": item_id}
    )


@item_server.patch("/{item_id}")
def update_item(item_id: int, params: Update_Item):
    item = items.get(item_id)

    if item:
        if item.deleted:
            return JSONResponse(
                status_code=HTTPStatus.NOT_MODIFIED,
                content={"detail": "Item is deleted and cannot be modified."}
            )

        if params is not None and params.deleted:
            return JSONResponse(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                content={"detail": "Setting 'deleted' to True is not allowed."}
            )

        if params.name is not None:
            item.name = params.name
        if params.price is not None:
            item.price = params.price

        return JSONResponse(content=item.dict())

    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content={"error": "Item not found", "item_id": item_id}
    )


@item_server.delete("/{item_id}")
def delete_item(item_id: int):
    item = items.get(item_id)
    if item:
        item.deleted = True
        return JSONResponse(content={"operation": "successfully removed item with item_id={item_id}"})

    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content={"error": "Item not found", "item_id": item_id}
    )
