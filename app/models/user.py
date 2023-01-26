from fastapi import Depends
from fastapi_users.db import (
    SQLAlchemyUserDatabase,
    SQLAlchemyBaseUserTableUUID,
    SQLAlchemyBaseOAuthAccountTableUUID
)
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTableUUID, SQLAlchemyAccessTokenDatabase
from sqlalchemy import Column, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, joinedload

from app.config.database import mapper_registry, get_db
from app.models.base import CreatedUpdateBase
from app.utils.app_exceptions import AppException
from app.utils.service_result import ServiceResult


@mapper_registry.mapped
class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID):
    pass


@mapper_registry.mapped
class User(SQLAlchemyBaseUserTableUUID, CreatedUpdateBase):
    username = Column(String)
    oauth_accounts: list[OAuthAccount] = relationship("OAuthAccount", lazy="joined")
    orders = relationship("Order", back_populates="user")

    @classmethod
    async def get_complex_data(cls, user_id, db):
        from app.models import Order
        user = await db.get(cls, user_id)
        if not user:
            return ServiceResult(AppException.GetObject({"item_id": user_id}))
        q = await db.execute(select(cls).where(cls.id == user_id).options(
            joinedload(User.orders).joinedload(Order.products)
        ))
        result = q.unique().scalar_one()
        return ServiceResult(result)


@mapper_registry.mapped
class AccessToken(SQLAlchemyBaseAccessTokenTableUUID):
    pass


async def get_user_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)


async def get_access_token_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)
