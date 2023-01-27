import asyncio
import json
from datetime import datetime
import threading

from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, Body
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

# from env_settings import Settings
from .models import User
from .routers import foo, mongo
from fastapi.exceptions import HTTPException as StarletteHTTPException

from pydantic import BaseModel

from .config.database import get_db
from .schemas.user import UserRead, UserCreate, UserUpdate, UserReadRegister
from .utils.app_exceptions import AppExceptionCase, app_exception_handler
from .utils.request_exceptions import http_exception_handler, request_validation_exception_handler
from .config.users import (
    fastapi_users,
    auth_backend,
    cookie_auth_backend,
    google_oauth_client,
    google_cookie_auth_backend,
    current_active_user
)

app = FastAPI()
database = get_db()

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.on_event("startup")
# async def register():
#     asyncio.get_running_loop().create_task(foo())


# async def foo():
#     for i in range(1000):
#         await manager.broadcast(str(i))
#         await asyncio.sleep(3)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, e):
    return await http_exception_handler(request, e)


@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request, e):
    return await request_validation_exception_handler(request, e)


@app.exception_handler(AppExceptionCase)
async def custom_app_exception_handler(request, e):
    return await app_exception_handler(request, e)


app.include_router(foo.router)
app.include_router(mongo.router)

# User routers
app.include_router(
    fastapi_users.get_auth_router(auth_backend, requires_verification=True),
    prefix="/auth/bearer",
    tags=["bearer_auth"]
)
app.include_router(
    fastapi_users.get_auth_router(cookie_auth_backend, requires_verification=True),
    prefix="/auth/cookie",
    tags=["cookie_auth"]
)
# app.include_router(
#     fastapi_users.get_oauth_router(
#         google_oauth_client, auth_backend, "SECRET", associate_by_email=True,
#     ),
#     prefix="/auth/bearer/google",
#     tags=["bearer_auth"],
# )
app.include_router(
    fastapi_users.get_oauth_router(
        google_oauth_client, google_cookie_auth_backend, "SECRET", associate_by_email=True
    ),
    prefix="/auth/cookie/google",
    tags=["cookie_auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserReadRegister, UserCreate),
    prefix="/auth",
    tags=["register"],
)
# https://aryaniyaps.medium.com/better-email-verification-workflows-13500ce042c7
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


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        print(message)
        print(self.active_connections)
        for connection in self.active_connections:
            await connection.send_text(message)


ws_manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    print(f"CLIENT ID {client_id}")
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.send_personal_message(f"You wrote: {data}", websocket)
            await ws_manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        await ws_manager.broadcast(f"Client #{client_id} left the chat")


@app.post('/event')
async def on_worker_event(item=Body(...)):
    await ws_manager.broadcast(json.dumps(item))
