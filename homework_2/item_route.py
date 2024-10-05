from fastapi import APIRouter, Query
from http import HTTPStatus
from fastapi.responses import JSONResponse
from typing import Optional
from models import Item, Update_Item, Create_Item
from functions import id_gen_item
from database import items

item_server = APIRouter(prefix="/item")

@item_server.post("")
def add_item(params: Item):
    item_id_generator = id_gen_item()
    item_id = next(item_id_generator)
    items[item_id] = Item
    location_url = f"/item/{item_id}"

    return JSONResponse(content={"id": item_id}, 
                        status_code=HTTPStatus.CREATED,
                        headers={"location": location_url})

@item_server.get("/{item_id}")
def get_item(item_id: int) -> Item:
    item = items.get(item_id)
    if item and not item["deleted"]:
        return JSONResponse(content=item)
    
    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND, 
        content={"error": "Item not found", "item_id": item_id}
        )


@item_server.get("/")
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
            filtered_items = [item for item in filtered_items if item["price"] >= min_price]
        if max_price:
            filtered_items = [item for item in filtered_items if item["price"] <= max_price]
        if not show_deleted:
            filtered_items = [item for item in filtered_items if item["deleted"] != True]
        
        response = filtered_items[offset:offset+limit]
        return JSONResponse(content=filtered_items)

@item_server.put("/{item_id}")
def change_item(item_id: int, params: Create_Item):
    item = items.get(item_id)
    if item and not item["deleted"]:
        item["name"] = params["name"]
        item["price"] = params["price"]
        return JSONResponse(content=item) 
    
    return JSONResponse(
    status_code=HTTPStatus.NOT_FOUND, 
    content={"error": "Item not found", "item_id": item_id}
    )

@item_server.patch("/{item_id}")
def update_item(item_id: int, params: Update_Item):
    item = items.get(item_id)
    if item and not item["deleted"]:
        if params["name"] != None:
            item["name"] = params["name"]
        if params["price"] != None:
            item["price"] = params["price"]
        return JSONResponse(content=item)
    
    return JSONResponse(
    status_code=HTTPStatus.NOT_FOUND, 
    content={"error": "Item not found", "item_id": item_id}
    )

@item_server.delete("/{item_id}")
def delete_item(item_id: int):
    item = items.get(item_id)
    if item:
        item["deleted"] = True
        return JSONResponse(content={"operation": "successfully removed item with item_id={item_id}"}) 
    
    return JSONResponse(
    status_code=HTTPStatus.NOT_FOUND, 
    content={"error": "Item not found", "item_id": item_id}
    )