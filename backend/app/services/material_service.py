from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId

from app.core.exceptions import AppException
from app.models.material import ListingStatus
from app.schemas.common import doc_timestamps, utc_now
from app.utils.object_id import oid_to_str, str_to_object_id


def _mongo_date(value: date) -> datetime:
    return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)


class MaterialService:
    def __init__(self, db):
        self.db = db

    async def _ensure_category(self, category_id: str) -> dict:
        cat = await self.db.categories.find_one(
            {"_id": str_to_object_id(category_id), "is_active": True}
        )
        if not cat:
            raise AppException("Category not found or inactive", status_code=404)
        return cat

    async def _ensure_project(self, company_id: str, project_id: Optional[str]) -> None:
        if not project_id:
            return
        project = await self.db.projects.find_one(
            {
                "_id": str_to_object_id(project_id),
                "company_id": company_id,
                "project_status": {"$ne": "ARCHIVED"},
            }
        )
        if not project:
            raise AppException("Project not found for company", status_code=404)

    def _geo_fields(self, lat: Optional[float], lon: Optional[float], location: str) -> dict:
        doc: Dict[str, Any] = {"location_text": location, "geo": None}
        if lat is not None and lon is not None:
            doc["latitude"] = lat
            doc["longitude"] = lon
            doc["geo"] = {"type": "Point", "coordinates": [lon, lat]}
        return doc

    async def create(self, company_id: str, data: dict) -> dict:
        await self._ensure_category(data["category_id"])
        await self._ensure_project(company_id, data.get("project_id"))
        geo = self._geo_fields(data.get("latitude"), data.get("longitude"), data["location"])
        doc = {
            "material_title": data["material_title"],
            "material_description": data.get("material_description"),
            "category_id": data["category_id"],
            "material_type": data["material_type"],
            "company_id": company_id,
            "project_id": data.get("project_id"),
            "available_quantity": data["available_quantity"],
            "reserved_quantity": 0.0,
            "unit": data["unit"].value if hasattr(data["unit"], "value") else data["unit"],
            "material_condition": data["material_condition"].value
            if hasattr(data["material_condition"], "value")
            else data["material_condition"],
            "expected_price": data.get("expected_price", 0),
            "is_free_material": data.get("is_free_material", False),
            "currency": data.get("currency", "INR"),
            "location_text": geo["location_text"],
            "geo": geo["geo"],
            "latitude": geo.get("latitude"),
            "longitude": geo.get("longitude"),
            "availability_date": _mongo_date(data["availability_date"])
            if isinstance(data.get("availability_date"), date)
            else data.get("availability_date"),
            "availability_type": data["availability_type"].value
            if hasattr(data["availability_type"], "value")
            else data["availability_type"],
            "material_images": data.get("material_images", []),
            "listing_status": data.get("listing_status", ListingStatus.DRAFT).value
            if hasattr(data.get("listing_status"), "value")
            else data.get("listing_status", ListingStatus.DRAFT.value),
            "status_history": [],
            **doc_timestamps(),
        }
        result = await self.db.materials.insert_one(doc)
        created = await self.db.materials.find_one({"_id": result.inserted_id})
        return self.serialize(created)

    def serialize(self, doc: dict) -> dict:
        if not doc:
            return doc
        out = oid_to_str(doc)
        out["location"] = doc.get("location_text", "")
        return out

    async def get_by_id(self, material_id: str) -> dict:
        doc = await self.db.materials.find_one({"_id": str_to_object_id(material_id)})
        if not doc:
            raise AppException("Material not found", status_code=404)
        return self.serialize(doc)

    async def update(self, material_id: str, company_id: str, data: dict, is_admin: bool = False) -> dict:
        doc = await self.db.materials.find_one({"_id": str_to_object_id(material_id)})
        if not doc:
            raise AppException("Material not found", status_code=404)
        if not is_admin and str(doc.get("company_id")) != str(company_id):
            raise AppException("Not authorized to modify this material", status_code=403)

        updates = {k: v for k, v in data.items() if v is not None}
        for enum_key in ("unit", "material_condition", "availability_type", "listing_status"):
            if enum_key in updates and hasattr(updates[enum_key], "value"):
                updates[enum_key] = updates[enum_key].value
        if "category_id" in updates:
            await self._ensure_category(updates["category_id"])
        if "project_id" in updates:
            await self._ensure_project(str(doc.get("company_id")), updates.get("project_id"))
        if "location" in updates or "latitude" in updates or "longitude" in updates:
            loc_text = updates.pop("location", doc.get("location_text", ""))
            geo = self._geo_fields(
                updates.get("latitude", doc.get("latitude")),
                updates.get("longitude", doc.get("longitude")),
                loc_text,
            )
            updates["location_text"] = geo["location_text"]
            updates["geo"] = geo["geo"]
            updates["latitude"] = geo.get("latitude")
            updates["longitude"] = geo.get("longitude")

        if "listing_status" in updates:
            history = doc.get("status_history", [])
            history.append({"status": updates["listing_status"], "at": utc_now()})
            updates["status_history"] = history

        updates["updated_at"] = utc_now()
        await self.db.materials.update_one({"_id": doc["_id"]}, {"$set": updates})
        return await self.get_by_id(material_id)

    async def delete_or_archive(self, material_id: str, company_id: str, is_admin: bool = False) -> None:
        doc = await self.db.materials.find_one({"_id": str_to_object_id(material_id)})
        if not doc:
            raise AppException("Material not found", status_code=404)
        if not is_admin and str(doc.get("company_id")) != str(company_id):
            raise AppException("Not authorized", status_code=403)
        await self.db.materials.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "listing_status": ListingStatus.INACTIVE.value,
                    "updated_at": utc_now(),
                }
            },
        )

    async def search(self, filters: dict, company_id: Optional[str] = None, own_only: bool = False) -> dict:
        query: Dict[str, Any] = {}
        if own_only and company_id:
            query["company_id"] = company_id
        else:
            query["listing_status"] = ListingStatus.ACTIVE.value

        if filters.get("category_id"):
            query["category_id"] = filters["category_id"]
        if filters.get("condition"):
            query["material_condition"] = filters["condition"]
        if filters.get("availability_type"):
            query["availability_type"] = filters["availability_type"]
        if filters.get("min_price") is not None or filters.get("max_price") is not None:
            price_q: Dict[str, Any] = {}
            if filters.get("min_price") is not None:
                price_q["$gte"] = filters["min_price"]
            if filters.get("max_price") is not None:
                price_q["$lte"] = filters["max_price"]
            query["expected_price"] = price_q
        if filters.get("min_quantity") is not None:
            query["available_quantity"] = {"$gte": filters["min_quantity"]}
        if filters.get("city"):
            query["location_text"] = {"$regex": filters["city"], "$options": "i"}
        if filters.get("q"):
            query["$or"] = [
                {"material_title": {"$regex": filters["q"], "$options": "i"}},
                {"material_type": {"$regex": filters["q"], "$options": "i"}},
            ]

        from app.utils.pagination import paginated_meta, pagination_params

        pg = pagination_params(filters.get("page", 1), filters.get("page_size", 20))
        total = await self.db.materials.count_documents(query)
        cursor = (
            self.db.materials.find(query)
            .sort(filters.get("sort_field", "created_at"), filters.get("sort_dir", -1))
            .skip(pg["skip"])
            .limit(pg["limit"])
        )
        items = [self.serialize(d) async for d in cursor]
        return {"items": items, **paginated_meta(total, pg["page"], pg["page_size"])}
