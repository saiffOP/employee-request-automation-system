from datetime import datetime

from pydantic import BaseModel

from app.schemas.ticket import (
    TicketCategory,
    TicketPriority,
    TicketStatus,
)


class Ticket(BaseModel):
    ticket_id: str

    employee_name: str
    employee_email: str
    request_text: str

    category: TicketCategory
    priority: TicketPriority

    assigned_team: str

    status: TicketStatus = TicketStatus.OPEN

    sla_hours: int
    sla_due_at: datetime

    created_at: datetime
    updated_at: datetime

    resolved_at: datetime | None = None

    is_escalated: bool = False

    classification_confidence: float | None = None
    classification_reasoning: str | None = None