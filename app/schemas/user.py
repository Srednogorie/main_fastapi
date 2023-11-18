import uuid

from fastapi_users import schemas, models
from pydantic import model_validator, BaseModel


class UserRead(schemas.BaseUser[uuid.UUID]):
    username: str | None


class UserReadRegister(BaseModel):
    id: models.ID

    class Config:
        orm_mode = True


class UserCreate(schemas.BaseUserCreate):
    confirm_password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "sash@gmail.com",
                "password": "",
                "confirm_password": "",
            }
        }

    @model_validator(mode="after")
    def check_passwords_match(cls, values):
        pw1 = values.get('password') if values.get('password') else None
        pw2 = values.get('confirm_password') if values.get('confirm_password') else None
        if pw1 is None or pw2 is None or pw1 != pw2:
            raise ValueError('passwords do not match')
        values.pop('confirm_password')
        return values


class UserUpdate(schemas.BaseUserUpdate):
    username: str
