from typing import Any, Dict, Optional

from app.core.config import get_settings
from app.core.exceptions import AppException
from app.models.material import ListingStatus
from app.models.notification import NotificationType
from app.models.request import RequestStatus
from app.models.transaction import TransactionStatus
from app.schemas.common import doc_timestamps, utc_now
from app.services.notification_service import NotificationService
from app.utils.object_id import oid_to_str, str_to_object_id


ACTIVE_REQUEST_STATUSES = [
    RequestStatus.PENDING.value,
    RequestStatus.ACCEPTED.value,
    RequestStatus.NEGOTIATION.value,
    RequestStatus.CONFIRMED.value,
]


class RequestService:
    def __init__(self, db):
        self.db = db
        self.notifications = NotificationService(db)

    def _append_status(self, doc: dict, status: str, note: Optional[str] = None) -> list:
        history = list(doc.get("status_history", []))
        history.append({"status": status, "at": utc_now(), "note": note})
        return history

    async def create_request(self, buyer_company_id: str, user_id: str, data: dict) -> dict:
        material = await self.db.materials.find_one({"_id": str_to_object_id(data["material_id"])})
        if not material:
            raise AppException("Material not found", status_code=404)
        supplier_company_id = str(material.get("company_id"))
        if supplier_company_id == buyer_company_id:
            raise AppException("Cannot request your own material", status_code=400)
        if material.get("listing_status") != ListingStatus.ACTIVE.value:
            raise AppException("Material is not available for requests", status_code=400)

        available = float(material.get("available_quantity", 0)) - float(
            material.get("reserved_quantity", 0)
        )
        qty = float(data["requested_quantity"])
        if qty > available:
            raise AppException("Requested quantity exceeds available quantity", status_code=400)

        dup = await self.db.requests.find_one(
            {
                "material_id": data["material_id"],
                "buyer_company_id": buyer_company_id,
                "request_status": {"$in": ACTIVE_REQUEST_STATUSES},
            }
        )
        if dup:
            raise AppException("An active request already exists for this material", status_code=409)

        doc = {
            "requirement_id": data.get("requirement_id"),
            "material_id": data["material_id"],
            "buyer_company_id": buyer_company_id,
            "supplier_company_id": supplier_company_id,
            "requested_quantity": qty,
            "offered_price": data.get("offered_price", 0),
            "supplier_quoted_price": None,
            "message": data.get("message"),
            "request_status": RequestStatus.PENDING.value,
            "status_history": [{"status": RequestStatus.PENDING.value, "at": utc_now()}],
            **doc_timestamps(),
        }
        result = await self.db.requests.insert_one(doc)
        doc["_id"] = result.inserted_id

        supplier_users = self.db.users.find({"company_id": supplier_company_id})
        async for su in supplier_users:
            await self.notifications.create(
                str(su["_id"]),
                NotificationType.NEW_REQUEST,
                "New material request",
                f"A buyer requested {qty} units of {material.get('material_title')}",
                {"request_id": str(result.inserted_id), "material_id": data["material_id"]},
            )

        return oid_to_str(doc)

    async def _get_request(self, request_id: str) -> dict:
        doc = await self.db.requests.find_one({"_id": str_to_object_id(request_id)})
        if not doc:
            raise AppException("Request not found", status_code=404)
        return doc

    def _ensure_party(self, doc: dict, company_id: str) -> None:
        if company_id not in (str(doc.get("buyer_company_id")), str(doc.get("supplier_company_id"))):
            raise AppException("Not authorized for this request", status_code=403)

    async def accept(self, request_id: str, supplier_company_id: str) -> dict:
        doc = await self._get_request(request_id)
        if str(doc.get("supplier_company_id")) != supplier_company_id:
            raise AppException("Only supplier can accept", status_code=403)
        if doc.get("request_status") != RequestStatus.PENDING.value:
            raise AppException("Request cannot be accepted in current status", status_code=400)
        history = self._append_status(doc, RequestStatus.ACCEPTED.value)
        await self.db.requests.update_one(
            {"_id": doc["_id"]},
            {"$set": {"request_status": RequestStatus.ACCEPTED.value, "status_history": history, "updated_at": utc_now()}},
        )
        await self._notify_company(
            doc["buyer_company_id"],
            NotificationType.REQUEST_ACCEPTED,
            "Request accepted",
            "Your material request was accepted",
            {"request_id": request_id},
        )
        return oid_to_str(await self._get_request(request_id))

    async def reject(self, request_id: str, supplier_company_id: str, message: Optional[str] = None) -> dict:
        doc = await self._get_request(request_id)
        if str(doc.get("supplier_company_id")) != supplier_company_id:
            raise AppException("Only supplier can reject", status_code=403)
        history = self._append_status(doc, RequestStatus.REJECTED.value, message)
        await self.db.requests.update_one(
            {"_id": doc["_id"]},
            {"$set": {"request_status": RequestStatus.REJECTED.value, "status_history": history, "updated_at": utc_now()}},
        )
        await self._notify_company(
            doc["buyer_company_id"],
            NotificationType.REQUEST_REJECTED,
            "Request rejected",
            message or "Your material request was rejected",
            {"request_id": request_id},
        )
        return oid_to_str(await self._get_request(request_id))

    async def negotiate(self, request_id: str, supplier_company_id: str, price: float, message: Optional[str] = None) -> dict:
        doc = await self._get_request(request_id)
        if str(doc.get("supplier_company_id")) != supplier_company_id:
            raise AppException("Only supplier can negotiate", status_code=403)
        history = self._append_status(doc, RequestStatus.NEGOTIATION.value, message)
        await self.db.requests.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "request_status": RequestStatus.NEGOTIATION.value,
                    "supplier_quoted_price": price,
                    "status_history": history,
                    "updated_at": utc_now(),
                }
            },
        )
        await self._notify_company(
            doc["buyer_company_id"],
            NotificationType.PRICE_UPDATED,
            "Counter offer received",
            f"Supplier quoted price: {price}",
            {"request_id": request_id},
        )
        return oid_to_str(await self._get_request(request_id))

    async def buyer_counter_response(self, request_id: str, buyer_company_id: str, accept: bool) -> dict:
        doc = await self._get_request(request_id)
        if str(doc.get("buyer_company_id")) != buyer_company_id:
            raise AppException("Only buyer can respond", status_code=403)
        if doc.get("request_status") != RequestStatus.NEGOTIATION.value:
            raise AppException("No negotiation in progress", status_code=400)
        new_status = RequestStatus.ACCEPTED.value if accept else RequestStatus.REJECTED.value
        history = self._append_status(doc, new_status)
        await self.db.requests.update_one(
            {"_id": doc["_id"]},
            {"$set": {"request_status": new_status, "status_history": history, "updated_at": utc_now()}},
        )
        return oid_to_str(await self._get_request(request_id))

    async def cancel(self, request_id: str, buyer_company_id: str) -> dict:
        doc = await self._get_request(request_id)
        if str(doc.get("buyer_company_id")) != buyer_company_id:
            raise AppException("Only buyer can cancel", status_code=403)
        if doc.get("request_status") in (RequestStatus.COMPLETED.value, RequestStatus.CONFIRMED.value):
            raise AppException("Cannot cancel request in current status", status_code=400)
        history = self._append_status(doc, RequestStatus.CANCELLED.value)
        await self.db.requests.update_one(
            {"_id": doc["_id"]},
            {"$set": {"request_status": RequestStatus.CANCELLED.value, "status_history": history, "updated_at": utc_now()}},
        )
        return oid_to_str(await self._get_request(request_id))

    async def confirm(self, request_id: str, actor_company_id: str) -> dict:
        doc = await self._get_request(request_id)
        if actor_company_id not in (
            str(doc.get("buyer_company_id")),
            str(doc.get("supplier_company_id")),
        ):
            raise AppException("Not authorized", status_code=403)
        if doc.get("request_status") not in (
            RequestStatus.ACCEPTED.value,
            RequestStatus.NEGOTIATION.value,
        ):
            raise AppException("Request must be accepted before confirmation", status_code=400)

        material = await self.db.materials.find_one({"_id": str_to_object_id(doc["material_id"])})
        if not material:
            raise AppException("Material not found", status_code=404)

        qty = float(doc["requested_quantity"])
        settings = get_settings()

        if settings.mongodb_supports_transactions:
            await self._confirm_with_transaction(doc, material, qty)
        else:
            await self._confirm_with_atomic_update(doc, material, qty)

        history = self._append_status(doc, RequestStatus.CONFIRMED.value)
        await self.db.requests.update_one(
            {"_id": doc["_id"]},
            {"$set": {"request_status": RequestStatus.CONFIRMED.value, "status_history": history, "updated_at": utc_now()}},
        )
        await self._notify_company(
            doc["buyer_company_id"],
            NotificationType.REQUEST_CONFIRMED,
            "Request confirmed",
            "Material exchange confirmed",
            {"request_id": request_id},
        )
        await self._notify_company(
            doc["supplier_company_id"],
            NotificationType.REQUEST_CONFIRMED,
            "Request confirmed",
            "Material exchange confirmed",
            {"request_id": request_id},
        )
        return oid_to_str(await self._get_request(request_id))

    async def _confirm_with_atomic_update(self, doc: dict, material: dict, qty: float) -> None:
        result = await self.db.materials.update_one(
            {
                "_id": material["_id"],
                "listing_status": ListingStatus.ACTIVE.value,
                "$expr": {
                    "$gte": [
                        {"$subtract": ["$available_quantity", "$reserved_quantity"]},
                        qty,
                    ]
                },
            },
            {"$inc": {"reserved_quantity": qty}, "$set": {"updated_at": utc_now()}},
        )
        if result.modified_count == 0:
            raise AppException(
                "Insufficient quantity available. Enable MONGODB_SUPPORTS_TRANSACTIONS with a replica set for stronger guarantees.",
                status_code=409,
            )

        agreed_price = doc.get("supplier_quoted_price") or doc.get("offered_price") or material.get(
            "expected_price", 0
        )
        await self._create_transaction(doc, qty, float(agreed_price))

    async def _confirm_with_transaction(self, doc: dict, material: dict, qty: float) -> None:
        client = self.db.client
        async with await client.start_session() as session:
            async with session.start_transaction():
                mat = await self.db.materials.find_one({"_id": material["_id"]}, session=session)
                available = float(mat["available_quantity"]) - float(mat.get("reserved_quantity", 0))
                if available < qty:
                    raise AppException("Insufficient quantity available", status_code=409)
                await self.db.materials.update_one(
                    {"_id": material["_id"]},
                    {"$inc": {"reserved_quantity": qty}, "$set": {"updated_at": utc_now()}},
                    session=session,
                )
                agreed_price = doc.get("supplier_quoted_price") or doc.get("offered_price") or mat.get(
                    "expected_price", 0
                )
                await self._create_transaction(doc, qty, float(agreed_price), session=session)

    async def _create_transaction(
        self, doc: dict, qty: float, agreed_price: float, session=None
    ) -> None:
        total = qty * agreed_price
        tx = {
            "request_id": str(doc["_id"]),
            "material_id": doc["material_id"],
            "buyer_company_id": doc["buyer_company_id"],
            "supplier_company_id": doc["supplier_company_id"],
            "quantity": qty,
            "agreed_price": agreed_price,
            "total_amount": total,
            "transaction_status": TransactionStatus.PENDING.value,
            "collection_details": None,
            **doc_timestamps(),
        }
        await self.db.transactions.insert_one(tx, session=session)

    async def complete_request(self, request_id: str) -> dict:
        doc = await self._get_request(request_id)
        if doc.get("request_status") != RequestStatus.CONFIRMED.value:
            raise AppException("Only confirmed requests can be completed", status_code=400)
        history = self._append_status(doc, RequestStatus.COMPLETED.value)
        await self.db.requests.update_one(
            {"_id": doc["_id"]},
            {"$set": {"request_status": RequestStatus.COMPLETED.value, "status_history": history, "updated_at": utc_now()}},
        )
        return oid_to_str(await self._get_request(request_id))

    async def list_requests(
        self, company_id: str, role: str = "all", page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:
        from app.utils.pagination import paginated_meta, pagination_params

        pg = pagination_params(page, page_size)
        if role == "buyer":
            query = {"buyer_company_id": company_id}
        elif role == "supplier":
            query = {"supplier_company_id": company_id}
        else:
            query = {
                "$or": [
                    {"buyer_company_id": company_id},
                    {"supplier_company_id": company_id},
                ]
            }
        total = await self.db.requests.count_documents(query)
        cursor = (
            self.db.requests.find(query)
            .sort("created_at", -1)
            .skip(pg["skip"])
            .limit(pg["limit"])
        )
        items = [oid_to_str(r) async for r in cursor]
        return {"items": items, **paginated_meta(total, pg["page"], pg["page_size"])}

    async def _notify_company(
        self, company_id: str, ntype: NotificationType, title: str, body: str, metadata: dict
    ) -> None:
        async for user in self.db.users.find({"company_id": company_id}):
            await self.notifications.create(str(user["_id"]), ntype, title, body, metadata)
