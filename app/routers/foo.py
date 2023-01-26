import uuid

from fastapi import APIRouter, Depends

from ..config.database import get_db
from ..models import Product, Order, OrderItem, User
from ..schemas.foo import (
    ProductReadCreate,
    ProductReadAll,
    ProductUpdate,
    OrderReadCreate,
    OrderItemReadCreate,
)
from ..schemas.user import UserOrders
from ..utils.service_result import handle_result

router = APIRouter(prefix="/foo", tags=["foo"],)

# PRODUCT TABLE


@router.get("/product/all_items", response_model=list[ProductReadAll])
async def get_all_products(db: get_db = Depends()):
    result = await Product.get_all(db)
    return handle_result(result)


@router.post("/product", response_model=ProductReadCreate)
async def create_product(item: ProductReadCreate, db: get_db = Depends()):
    result = await Product.create(item, db)
    return handle_result(result)


@router.get("/product/{item_id}", response_model=ProductReadCreate)
async def get_product(item_id: int, db: get_db = Depends()):
    result = await Product.get(item_id, db)
    return handle_result(result)


@router.delete("/product/{item_id}")
async def delete_product(item_id: int, db: get_db = Depends()):
    result = await Product.delete(item_id, db)
    return handle_result(result)


@router.patch("/product/{item_id}")
async def update_product(item: ProductUpdate, item_id: int, db: get_db = Depends()):
    result = await Product.update(item_id, db, item.dict(exclude_unset=True))
    return handle_result(result)


# ORDER TABLE


@router.post("/order", response_model=OrderReadCreate)
async def create_order(item: OrderReadCreate, db: get_db = Depends()):
    result = await Order.create(item, db)
    return handle_result(result)


# ORDER_ITEM TABLE


@router.post("/order_item", response_model=OrderItemReadCreate)
async def create_order_item(item: OrderItemReadCreate, db: get_db = Depends()):
    result = await OrderItem.create(item, db)
    return handle_result(result)


# ADDITIONAL TABLES
@router.get("/get_nested_data/{user_id}", response_model=UserOrders)
async def get_nested_data(user_id: uuid.UUID, db: get_db = Depends()):
    result = await User.get_complex_data(user_id, db)
    return handle_result(result)
