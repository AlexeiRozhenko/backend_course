from fastapi import APIRouter, Query
from http import HTTPStatus
from typing import Optional

from starlette.responses import JSONResponse

from models import Cart, Cart_Item
from functions import id_gen_cart
from database import carts, items

cart_server = APIRouter(prefix="/cart")


@cart_server.post("")
def create_cart() -> JSONResponse:
    cart_id_generator = id_gen_cart()
    cart_id = next(cart_id_generator)

    new_cart = Cart(id=cart_id, items=[], price=0)
    carts[cart_id] = new_cart

    location_url = f"/cart/{cart_id}"

    return JSONResponse(
        content={"id": cart_id, "cart": new_cart.dict()},
        status_code=HTTPStatus.CREATED,
        headers={"Location": location_url}
    )


@cart_server.get("/{cart_id}")
def get_cart(cart_id: int) -> JSONResponse:
    cart = carts.get(cart_id)
    if cart:
        return JSONResponse(content=cart.dict())

    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content={"error": "Cart not found", "cart_id": cart_id}
    )


@cart_server.get("")
def get_filtered_cart(
        offset: Optional[int] = Query(0, ge=0),
        limit: Optional[int] = Query(10, gt=0),
        min_price: Optional[float] = Query(None, ge=0),
        max_price: Optional[float] = Query(None, ge=0),
        min_quantity: Optional[int] = Query(None, ge=0),
        max_quantity: Optional[int] = Query(None, ge=0)
) -> JSONResponse:
    if not carts:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"error": "Carts list is empty"}
        )

    filtered_carts = list(carts.values())

    if min_price:
        filtered_carts = [cart for cart in filtered_carts if cart.price >= min_price]
    if max_price:
        filtered_carts = [cart for cart in filtered_carts if cart.price <= max_price]
    if min_quantity:
        filtered_carts = [cart for cart in filtered_carts if sum(item.quantity for item in cart.items) >= min_quantity]
    if max_quantity:
        filtered_carts = [cart for cart in filtered_carts if sum(item.quantity for item in cart.items) <= max_quantity]

    response = [cart.dict() for cart in filtered_carts[offset:offset + limit]]

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

    if not item or item.deleted:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"error": "Item not found or unavailable", "item_id": item_id}
        )

    existing_item = next((element for element in cart.items if element.id == item_id and element.available), None)

    if existing_item:
        existing_item.quantity += 1
        cart.price += item.price

    else:
        cart.items.append(Cart_Item(id=item.id, name=item.name, quantity=1, available=True))
        cart.price += item.price

    return JSONResponse(content=cart.dict())
