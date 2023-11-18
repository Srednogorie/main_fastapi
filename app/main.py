import os
import re
from typing import Annotated

from fastapi import FastAPI, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from starlette_csrf import CSRFMiddleware
from magnum import Magnum

from .models import User
from fastapi.exceptions import HTTPException as StarletteHTTPException

from .config.database import get_db
from .schemas.user import UserRead, UserCreate, UserUpdate, UserReadRegister
from .utils.app_exceptions import AppExceptionCase, app_exception_handler
from .utils.request_exceptions import http_exception_handler, request_validation_exception_handler
from .config.users import (
    fastapi_users,
    cookie_auth_backend,
    google_oauth_client,
    google_cookie_auth_backend,
    current_active_user
)

app = FastAPI()
handler = Magnum(app)
database = get_db()

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CSRFMiddleware,
    cookie_secure=True,
    cookie_samesite="none",
    secret="__CHANGE_ME__",
    # TODO available only in development
    exempt_urls=[re.compile("/*")]
)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, e):
    return await http_exception_handler(request, e)


@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request, e):
    return await request_validation_exception_handler(request, e)


@app.exception_handler(AppExceptionCase)
async def custom_app_exception_handler(request, e):
    return await app_exception_handler(request, e)

# User routers
app.include_router(
    fastapi_users.get_auth_router(cookie_auth_backend, requires_verification=True),
    prefix="/auth/cookie",
    tags=["cookie_auth"]
)
app.include_router(
    fastapi_users.get_oauth_router(
        google_oauth_client,
        google_cookie_auth_backend,
        os.getenv("AUTH_VERIFICATION_SECRET"),
        associate_by_email=True
    ),
    prefix="/auth/cookie/google",
    tags=["cookie_auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserReadRegister, UserCreate),
    prefix="/auth",
    tags=["register"],
)
# # https://aryaniyaps.medium.com/better-email-verification-workflows-13500ce042c7
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["verify"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["reset"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate, requires_verification=True),
    prefix="/users",
    tags=["users"],
)

CurrentActiveUser = Annotated[User, Depends(current_active_user)]

@app.get("/")
async def root(request: Request):
    return {"message": "Hello World"}


@app.get("/authenticated-route")
async def authenticated_route(user: CurrentActiveUser):
    return {"message": f"Hello {user.email}!"}
