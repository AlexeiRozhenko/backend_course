from fastapi import FastAPI
from cart_route import cart_server
from item_route import item_server

app = FastAPI(title="Shop API")

app.include_router(cart_server)
app.include_router(item_server)
# uvicorn main:app --reload