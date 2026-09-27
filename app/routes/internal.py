from datetime import datetime, timezone

import secrets

from fastapi import APIRouter, Header, HTTPException, Depends

from app.config.settings import INTERNAL_API_KEY

from app.database.mongodb import tickets_collection

from zoneinfo import ZoneInfo

UTC = timezone.utc
INDIA_TZ = ZoneInfo("Asia/Kolkata")

def verify_internal_api_key(
        x_internal_api_key: str = Header(...),
):
    if not secrets.compare_digest(
            x_internal_api_key,
            INTERNAL_API_KEY,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid internal API key.",
        )

router = APIRouter(
    prefix="/api/internal",
    tags=["Internal Automation"],
    dependencies=[
        Depends(verify_internal_api_key)
    ],
)


@router.get("/tickets/overdue")
async def get_overdue_tickets():

    now = datetime.now(UTC)

    now_india = now.astimezone(INDIA_TZ)

    start_of_today_india = now_india.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    start_of_today = start_of_today_india.astimezone(UTC)

    cursor = tickets_collection.find(
        {
            "status": {
                "$ne": "Finalized"
            },
            "sla_due_at": {
                "$lt": now
            },
            "$or": [
                {
                    "escalated_at": {
                        "$exists": False
                    }
                },
                {
                    "escalated_at": None
                },
                {
                    "escalated_at": {
                        "$lt": start_of_today
                    }
                },
            ],
        },
        {
            "_id": 0
        },
    )

    tickets = await cursor.to_list(
        length=500
    )

    return {
        "count": len(tickets),
        "tickets": tickets,
    }

@router.patch("/tickets/{ticket_id}/escalated")
async def mark_ticket_as_escalated(
        ticket_id: str,
):

    now = datetime.now(timezone.utc)

    result = await tickets_collection.update_one(
        {
            "ticket_id": ticket_id,
            "status": {
                "$ne": "Finalized"
            },
        },
        {
            "$set": {
                "is_escalated": True,
                "escalated_at": now,
                "updated_at": now,
            }
        },
    )

    if result.matched_count == 0:
        return {
            "success": False,
            "ticket_id": ticket_id,
            "message": (
                "Ticket not found or already finalized."
            ),
        }

    return {
        "success": True,
        "ticket_id": ticket_id,
        "is_escalated": True,
        "escalated_at": now,
    }

