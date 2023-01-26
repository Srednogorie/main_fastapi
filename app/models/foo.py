from sqlalchemy import (
    Column, Integer, String, ForeignKey, Table, UniqueConstraint, select, desc, update
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, joinedload

from app.config.database import mapper_registry
from .user import User
from ..schemas.foo import ProductReadCreate, OrderReadCreate, OrderItemReadCreate
from ..utils.app_exceptions import AppException
from ..utils.service_result import ServiceResult

product_order_association = Table(
    "product_order_association",
    mapper_registry.metadata,
    Column("product_id", ForeignKey("product.id"), primary_key=True),
    Column("order_id", ForeignKey("order.id"), primary_key=True),
)


@mapper_registry.mapped
class Product:
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    price = Column(Integer)
    orders = relationship(
        "Order", secondary=product_order_association, back_populates="products"
    )
    order_items = relationship("OrderItem", back_populates="product")

    @classmethod
    async def create(cls, item: ProductReadCreate, db) -> ServiceResult:
        product = cls(**item.dict())
        db.add(product)
        await db.commit()

        if not product:
            return ServiceResult(AppException.CreateObject())
        return ServiceResult(product)

    @classmethod
    async def get(cls, item_id: int, db) -> ServiceResult:
        product = await db.get(cls, item_id)
        if not product:
            return ServiceResult(AppException.GetObject({"item_id": item_id}))
        # if not product.public:
        #     return ServiceResult(AppException.ObjectRequiresAuth())
        return ServiceResult(product)

    @classmethod
    async def get_all(cls, db) -> ServiceResult:
        products = await db.execute(select(cls).order_by(desc(cls.id)))
        return ServiceResult(products.scalars().all())

    @classmethod
    async def delete(cls, item_id, db) -> ServiceResult:
        product = await db.get(cls, item_id)
        if not product:
            return ServiceResult(AppException.GetObject({"item_id": item_id}))
        await db.delete(product)
        await db.commit()
        return ServiceResult(True)

    @classmethod
    async def update(cls, item_id, db, data):
        product = await db.get(cls, item_id)
        if not product:
            return ServiceResult(AppException.GetObject({"item_id": item_id}))
        for key, value in data.items():
            setattr(product, key, value)
        db.add(product)
        await db.commit()
        await db.refresh(product)
        return ServiceResult(product)


@mapper_registry.mapped
class Order:
    __tablename__ = "order"

    id = Column(Integer, primary_key=True, index=True)
    total = Column(Integer)
    order_items = relationship("OrderItem", back_populates="order")
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    user = relationship(User, back_populates="orders")
    products = relationship(
        "Product", secondary=product_order_association, back_populates="orders"
    )

    @classmethod
    async def create(cls, item: OrderReadCreate, db) -> ServiceResult:
        order = cls(**item.dict())
        db.add(order)
        await db.commit()

        if not order:
            return ServiceResult(AppException.CreateObject())
        return ServiceResult(order)


@mapper_registry.mapped
class OrderItem:
    __tablename__ = "order_item"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id"))
    order = relationship("Order", back_populates="order_items")
    product_id = Column(Integer, ForeignKey("product.id"))
    product = relationship("Product", back_populates="order_items")
    quantity = Column(Integer)

    __table_args__ = (
        UniqueConstraint('order_id', 'product_id', name='_order_product_uc'),
    )

    @classmethod
    async def create(cls, item: OrderItemReadCreate, db) -> ServiceResult:
        order_item = cls(**item.dict())
        db.add(order_item)
        q_order = await db.execute(
            select(Order).where(Order.id == order_item.order_id).options(
                joinedload(Order.products)
            )
        )
        order = q_order.unique().scalar_one()
        product = await db.get(Product, order_item.product_id)
        order.products.append(product)
        db.add(order)
        await db.commit()

        if not order_item:
            return ServiceResult(AppException.CreateObject())
        return ServiceResult(order_item)
