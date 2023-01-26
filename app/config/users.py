from __future__ import print_function

import os
import uuid
from typing import Optional

import sib_api_v3_sdk
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, CookieTransport
from fastapi_users.authentication.strategy import AccessTokenDatabase, DatabaseStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.password import PasswordHelper
from httpx_oauth.clients.google import GoogleOAuth2
from sib_api_v3_sdk.rest import ApiException
from starlette import status

from app.models.user import User, get_user_db, get_access_token_db

SECRET = "SECRET"


google_oauth_client = GoogleOAuth2(
    os.getenv("GOOGLE_OAUTH_CLIENT_ID", "583488678539-5e5jjs3jqcneom71e6qejhdrs08gl5pd.apps.googleusercontent.com"),
    os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "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"),
)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        configuration = sib_api_v3_sdk.Configuration()
        # Key is invalid
        configuration.api_key['api-key'] = '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'

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        subject = "Reset your password"
        sender = {"name": "Sando", "email": "akrachunov@gmail.com"}
        to = [{"email": user.email}]
        params = {"token": token}
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            sender=sender, to=to, subject=subject, template_id=2, params=params
        )

        try:
            api_response = api_instance.send_transac_email(send_smtp_email)
            print(api_response)
        except ApiException as e:
            print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        configuration = sib_api_v3_sdk.Configuration()
        # Key is invalid
        configuration.api_key['api-key'] = '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'

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        subject = "Verify your email"
        sender = {"name": "Sando", "email": "akrachunov@gmail.com"}
        to = [{"email": user.email}]
        params = {"token": token}
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            sender=sender, to=to, subject=subject, template_id=1, params=params
        )

        try:
            api_response = api_instance.send_transac_email(send_smtp_email)
            print(api_response)
        except ApiException as e:
            print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def oauth_callback(
        self,
        oauth_name: str,
        access_token: str,
        account_id: str,
        account_email: str,
        expires_at: Optional[int] = None,
        refresh_token: Optional[str] = None,
        request: Optional[Request] = None,
        *,
        associate_by_email: bool = False
    ) -> models.UOAP:
        user = await super().oauth_callback(
            oauth_name,
            access_token,
            account_id,
            account_email,
            expires_at,
            refresh_token,
            request,
            associate_by_email=associate_by_email
        )
        if not user.is_verified:
            password_helper = PasswordHelper()
            password = password_helper.generate()
            await self.user_db.update(
                user,
                update_dict={
                    "is_verified": True,
                    "hashed_password": password_helper.hash(password)
                }
            )
        return user


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


class AutoRedirectCookieAuthentication(CookieTransport):
    async def get_login_response(self, user, response):
        await super().get_login_response(user, response)
        response.status_code = status.HTTP_302_FOUND
        response.headers["Location"] = "http://localhost:3000"


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
cookie_transport = CookieTransport(cookie_max_age=60, cookie_secure=True, cookie_samesite="none")
google_cookie_transport = AutoRedirectCookieAuthentication(
    cookie_max_age=3600, cookie_secure=True, cookie_samesite="none"
)


# def get_jwt_strategy() -> JWTStrategy:
#     return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

def get_database_strategy(
        access_token_db: AccessTokenDatabase = Depends(get_access_token_db)
) -> DatabaseStrategy:
    return DatabaseStrategy(access_token_db, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)

cookie_auth_backend = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_database_strategy,
)
google_cookie_auth_backend = AuthenticationBackend(
    name="cookie",
    transport=google_cookie_transport,
    get_strategy=get_database_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager, [auth_backend, cookie_auth_backend]
)

current_active_user = fastapi_users.current_user(active=True)
