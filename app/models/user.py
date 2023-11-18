from fastapi import Depends
from fastapi_users.db import (
    SQLAlchemyUserDatabase,
    SQLAlchemyBaseUserTableUUID,
    SQLAlchemyBaseOAuthAccountTableUUID
)
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyBaseAccessTokenTableUUID, SQLAlchemyAccessTokenDatabase
)
from sqlalchemy import Column, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from app.config.database import mapper_registry, get_db
from app.models.base import CreatedUpdateBase


@mapper_registry.mapped
class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID):
    pass


@mapper_registry.mapped
class User(SQLAlchemyBaseUserTableUUID, CreatedUpdateBase):
    username = Column(String)
    oauth_accounts: list[OAuthAccount] = relationship("OAuthAccount", lazy="joined")

    __allow_unmapped__ = True


@mapper_registry.mapped
class AccessToken(SQLAlchemyBaseAccessTokenTableUUID):
    pass


async def get_user_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)


async def get_access_token_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)
