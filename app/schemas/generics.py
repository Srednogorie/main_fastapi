from bson import ObjectId
from pydantic.main import ModelMetaclass, BaseModel
from typing import Any, Dict, Optional, Tuple


class _AllOptionalMeta(ModelMetaclass):
    def __new__(mcs, name: str, bases: Tuple[type], namespaces: Dict[str, Any], **kwargs):
        annotations: dict = namespaces.get('__annotations__', {})

        for base in bases:
            for base_ in base.__mro__:
                if base_ is BaseModel:
                    break

                for k, v in base_.__annotations__.items():
                    if k not in annotations:
                        annotations[k] = v

        for field in annotations:
            if not field.startswith('__'):
                annotations[field] = Optional[annotations[field]]

        namespaces['__annotations__'] = annotations

        return super().__new__(mcs, name, bases, namespaces, **kwargs)


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")
