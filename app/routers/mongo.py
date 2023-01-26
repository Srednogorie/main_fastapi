from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

from app.config.database import mongodb
from app.schemas.mongo import FooPerson, UpdateFooPerson
from app.services.mongo import MongoService
from app.utils.service_result import handle_result

router = APIRouter(prefix="/mongo", tags=["mongo"],)


# Retrieve all entries from collection
@router.get("/foo", response_model=list[FooPerson])
async def get_all_items():
    result = await MongoService(mongodb).get_all_items("foo")
    return handle_result(result)


# Add a new entry into to the database
@router.post("/foo", response_model=FooPerson)
async def create_item(person: FooPerson):
    person = jsonable_encoder(person)
    result = await MongoService(mongodb).create_item(person, "foo")
    return handle_result(result)


# Add a new entry into to the database
@router.patch("/foo/{foo_id}", response_model=FooPerson)
async def update_item(person: UpdateFooPerson, foo_id: str):
    person = jsonable_encoder(person.dict(exclude_unset=True))
    result = await MongoService(mongodb).update_item(person, foo_id, "foo")
    return handle_result(result)


# Retrieve entry with a matching ID
@router.get("/foo/{foo_id}", response_model=FooPerson)
async def get_item(foo_id: str):
    result = await MongoService(mongodb).get_item(foo_id, "foo")
    return handle_result(result)


# Delete a student from the database
@router.delete("/foo/{foo_id}")
async def delete_student(foo_id: str):
    result = await MongoService(mongodb).delete_item(foo_id, "foo")
    return handle_result(result)
