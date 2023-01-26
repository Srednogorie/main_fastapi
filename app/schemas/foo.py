import uuid

import pydantic
from fastapi_users import models
from pydantic import BaseModel, Field, validator

# This is an example schema, realistically it will be spread around multiple files
# PRODUCT TABLE


class ProductReadCreate(BaseModel):
    description: str
    price: int

    class Config:
        orm_mode = True


class ProductReadAll(BaseModel):
    id: int
    description: str
    price: int

    class Config:
        orm_mode = True


class ProductUpdate(BaseModel):
    description: str | None
    price: int | None


# ORDER TABLE


class OrderReadCreate(BaseModel):
    total: int
    user_id: uuid.UUID

    class Config:
        orm_mode = True


# ORDER_ITEM TABLE


class OrderItemReadCreate(BaseModel):
    order_id: int
    product_id: int
    quantity: int

    class Config:
        orm_mode = True


# class Order(BaseModel):
#     total: int
#     order_items: list[BasketProduct] = []
#
#     totalDisplay: str = None
#
#     @validator("totalDisplay", always=True)
#     def total_currency(cls, v, values, **kwargs):
#         return f'{values["total"]} leva'
#
#     class Config:
#         orm_mode = True
#         allow_population_by_field_name = True
