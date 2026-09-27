from datetime import datetime, timezone

from app.database.mongodb import tickets_collection
from app.models.ticket import Ticket


class TicketService:

    @staticmethod
    async def create_ticket(
            ticket: Ticket,
    ) -> Ticket:

        document = ticket.model_dump(
            mode="python"
        )

        await tickets_collection.insert_one(
            document
        )

        return ticket


    @staticmethod
    async def get_ticket(
            ticket_id: str,
    ) -> dict | None:

        return await tickets_collection.find_one(
            {"ticket_id": ticket_id},
            {"_id": 0},
        )


    @staticmethod
    async def get_all_tickets() -> list[dict]:

        cursor = tickets_collection.find(
            {},
            {"_id": 0},
        ).sort(
            "created_at",
            -1,
        )

        return await cursor.to_list(
            length=500
        )


    @staticmethod
    async def update_ticket_status(
            ticket_id: str,
            new_status: str,
    ) -> bool:

        ticket = await tickets_collection.find_one(
            {"ticket_id": ticket_id}
        )

        if not ticket:
            return False

        current_status = ticket.get("status")

        allowed_transitions = {
            "Open": "Active",
            "Active": "Finalized",
        }

        expected_next_status = allowed_transitions.get(
            current_status
        )

        if expected_next_status != new_status:
            return False

        now = datetime.now(timezone.utc)

        update_fields = {
            "status": new_status,
            "updated_at": now,
        }

        if new_status == "Finalized":
            update_fields["resolved_at"] = now

        result = await tickets_collection.update_one(
            {
                "ticket_id": ticket_id,
                "status": current_status,
            },
            {
                "$set": update_fields
            },
        )

        return result.modified_count == 1