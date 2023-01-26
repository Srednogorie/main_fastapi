from bson import ObjectId
from pydantic import BaseModel, Field

from app.schemas.generics import PyObjectId


class PhysicalStateCondition(BaseModel):
    sight: str
    hearing: str


class UpdatePhysicalStateCondition(PhysicalStateCondition):
    sight: str | None
    hearing: str | None


class PhysicalState(BaseModel):
    weight: int
    smoking: bool
    condition: PhysicalStateCondition


class UpdatePhysicalSate(PhysicalState):
    weight: int | None
    smoking: bool | None
    condition: UpdatePhysicalStateCondition | None


class FooPerson(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    first_name: str
    last_name: str
    age: int
    physical_state: PhysicalState

    class Config:
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "first_name": "Sash", "last_name": "She", "age": 40,
                "physical_state": {
                    "weight": 60,
                    "smoking": True,
                    "condition": {
                        "sight": "good",
                        "hearing": "bad"
                    }
                },
            }
        }


class UpdateFooPerson(FooPerson):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    first_name: str | None
    last_name: str | None
    age: int | None
    physical_state: UpdatePhysicalSate | None
