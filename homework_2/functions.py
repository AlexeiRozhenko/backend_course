from database import items
from models import Item

item_id_counter = 0
cart_id_counter = 0

def id_gen_item():
    global item_id_counter
    item_id_counter += 1
    yield item_id_counter

def id_gen_cart():
    global cart_id_counter
    cart_id_counter += 1
    yield cart_id_counter

def get_item_body(item_id: int) -> Item:
    item = items.get(item_id)
    if item and not item["deleted"]:
        return item
    return None
