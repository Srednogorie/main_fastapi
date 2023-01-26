from bson import ObjectId
from pydantic.utils import deep_update

from ..services.main import AppService, AppCRUD
from ..utils.app_exceptions import AppException
from ..utils.service_result import ServiceResult


class MongoService(AppService):
    async def create_item(self, item: any, collection: str) -> ServiceResult:
        item = await MongoCRUD(self.db).create_item(item, collection)
        if not item:
            return ServiceResult(AppException.CreateObject())
        return ServiceResult(item)

    async def update_item(self, item: any, item_id: str, collection: str) -> ServiceResult:
        item = await MongoCRUD(self.db).update_item(item, item_id, collection)
        if not item:
            return ServiceResult(AppException.CreateObject())
        return ServiceResult(item)

    async def get_item(self, item_id: str, collection: str) -> ServiceResult:
        item = await MongoCRUD(self.db).get_item(item_id, collection)
        if not item:
            return ServiceResult(AppException.GetObject({"item_id": item_id}))
        # if not item.public:
        #     return ServiceResult(AppException.ObjectRequiresAuth())
        return ServiceResult(item)

    async def get_all_items(self, collection: str) -> ServiceResult:
        foo_items = await MongoCRUD(self.db).get_all_items(collection)
        return ServiceResult(foo_items)

    async def delete_item(self, item_id: str, collection: str) -> ServiceResult:
        foo_items = await MongoCRUD(self.db).delete_item(item_id, collection)
        return ServiceResult(foo_items)


class MongoCRUD(AppCRUD):
    async def create_item(self, item: dict, collection: str) -> dict:
        collection = self.db.get_collection(collection)
        created_item = await collection.insert_one(item)
        new_created_item = await collection.find_one({"_id": created_item.inserted_id})
        return new_created_item

    async def update_item(self, item: dict, item_id: str, collection: str) -> dict | None:
        collection = self.db.get_collection(collection)
        existing = await collection.find_one({"_id": item_id})
        if existing:
            deep_updated = deep_update(existing, item)
            updated = await collection.update_one({"_id": item_id}, {"$set": deep_updated})
            if updated:
                return deep_updated
            return None
        return None

    async def get_item(self, item_id: str, collection: str) -> dict | None:
        collection = self.db.get_collection(collection)
        item = await collection.find_one({"_id": item_id})
        return item

    async def get_all_items(self, collection: str) -> list[dict] | None:
        collection = self.db.get_collection(collection)
        items = []
        async for item in collection.find():
            items.append(item)
        return items

    async def delete_item(self, item_id: str, collection: str) -> bool:
        collection = self.db.get_collection(collection)
        item = await collection.find_one({"_id": item_id})
        if item:
            await collection.delete_one({"_id": item_id})
            return True
