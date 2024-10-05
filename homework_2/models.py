from pydantic import BaseModel, Field
from typing import List, Optional


class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False


class Cart_Item(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool


class Cart(BaseModel):
    id: int
    items: List[Cart_Item]
    price: float


class Update_Item(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    deleted: Optional[bool] = False

    class Config:
        extra = "forbid"


class Create_Item(BaseModel):
    name: str
    price: float = Field(ge=0)
