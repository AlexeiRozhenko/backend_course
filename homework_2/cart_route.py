from fastapi import APIRouter, Query
from http import HTTPStatus
from fastapi.responses import JSONResponse
from typing import Optional, List
from models import Cart
from functions import id_gen_cart, get_item_body
from database import carts, items

cart_server = APIRouter(prefix="/cart")

@cart_server.post("")
def create_cart() -> Cart:
    cart_id_generator = id_gen_cart()
    cart_id = next(cart_id_generator)

    carts[cart_id] = Cart(id=cart_id, items=[], price=0)

    location_url = f"/cart/{cart_id}"

    return JSONResponse(
        content={"id": cart_id},
        status_code=HTTPStatus.CREATED,
        headers={"location": location_url}
    )

@cart_server.get("/{cart_id}")
def get_cart(cart_id: int) -> Cart:
    cart = carts.get(cart_id)
    if cart:
        return JSONResponse(content=cart)
    
    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND, 
        content={"error": "Cart not found", "cart_id": cart_id}
        )

@cart_server.get("/")
def get_filtered_cart(
    offset: Optional[int] = Query(0, ge=0),
    limit: Optional[int] = Query(10, gt=0), 
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0), 
    min_quantity: Optional[int] = Query(None, ge=0),
    max_quantity: Optional[int] = Query(None, ge=0)
    ) -> List:
    
    if not carts:
        return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND, 
        content={"error": "Carts list is empty"}
        )
    else:
        filtered_carts = list(carts.values())

        if min_price:
            filtered_carts = [cart for cart in filtered_carts if cart["price"] >= min_price]
        if max_price:
            filtered_carts = [cart for cart in filtered_carts if cart["price"] <= max_price]
        if min_quantity:
            filtered_carts = [cart for cart in filtered_carts if sum(item["quantity"] for item in cart["items"]) >= min_quantity]
        if max_quantity:
            filtered_carts = [cart for cart in filtered_carts if sum(item["quantity"] for item in cart["items"]) <= max_quantity]
        
        response = filtered_carts[offset:offset+limit]
        return JSONResponse(content=response)

@cart_server.post("/{cart_id}/add/{item_id}")
def add_item_to_cart(cart_id: int, item_id: int):
    cart = carts.get(cart_id)
    item = items.get(item_id)
    if not cart:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND, 
            content={"error": "Cart not found", "cart_id": cart_id}
        )
    
    if not item or item["deleted"]: 
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"error": "Item not found or unavailable", "item_id": item_id}
        )
    
    for element in cart["items"]:
        if element["id"] == item_id and element["available"]:
            element["quantity"] += 1
            cart["price"] += get_item_body(item_id)["price"]
            return JSONResponse(content=cart)
        else:
            cart["items"].append(item)
            return JSONResponse(content=cart)