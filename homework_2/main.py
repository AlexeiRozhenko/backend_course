from fastapi import FastAPI
from cart_route import cart_server
from item_route import item_server

app = FastAPI(title="Shop API")

app.include_router(cart_server)
app.include_router(item_server)
# uvicorn main:app --reload
# pytest test_homework_2.py
# poetry run pytest -vv --showlocals --strict ./hw_2/test_homework_2.py