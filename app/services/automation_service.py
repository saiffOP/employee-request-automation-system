import logging

import httpx

from app.config.settings import (
    N8N_NEW_REQUEST_WEBHOOK_URL,
)
from app.models.ticket import Ticket


logger = logging.getLogger(__name__)


class AutomationService:

    @staticmethod
    async def notify_new_ticket(
            ticket: Ticket,
    ) -> bool:

        if not N8N_NEW_REQUEST_WEBHOOK_URL:
            logger.warning(
                "n8n webhook URL is not configured."
            )
            return False

        payload = {
            "ticket_id": ticket.ticket_id,

            "employee_name": ticket.employee_name,
            "employee_email": ticket.employee_email,

            "request_text": ticket.request_text,

            "category": ticket.category.value,
            "priority": ticket.priority.value,

            "assigned_team": ticket.assigned_team,

            "status": ticket.status.value,

            "sla_hours": ticket.sla_hours,

            "sla_due_at": (
                ticket.sla_due_at.isoformat()
            ),

            "classification_confidence": (
                ticket.classification_confidence
            ),
        }

        try:

            async with httpx.AsyncClient(
                    timeout=10.0
            ) as client:

                response = await client.post(
                    N8N_NEW_REQUEST_WEBHOOK_URL,
                    json=payload,
                )

                response.raise_for_status()

            logger.info(
                "Ticket %s sent to n8n successfully.",
                ticket.ticket_id,
            )

            return True

        except Exception as exc:

            logger.exception(
                "Failed to send ticket %s to n8n: %s",
                ticket.ticket_id,
                exc,
            )

            return False