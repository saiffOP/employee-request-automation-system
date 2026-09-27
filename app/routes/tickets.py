from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from pydantic import ValidationError

from app.models.ticket import Ticket
from app.services.ticket_service import TicketService

from app.config.templates import templates
from app.schemas.ticket import (
    TicketCategory,
    TicketCreate,
    TicketPriority,
    TicketStatus,
)
from app.services.automation_service import (
    AutomationService,
)

from app.services.classification_service import (
    ClassificationService,
)


router = APIRouter(
    prefix="/requests",
    tags=["Requests"],
)


def generate_ticket_id() -> str:
    year = datetime.now(timezone.utc).year
    unique_part = uuid4().hex[:6].upper()

    return f"REQ-{year}-{unique_part}"


# def temporary_classification(request_text: str):
#     """
#     Temporary rule-based classification.
#
#     This will later be replaced by the AI classification service.
#     """
#
#     text = request_text.lower()
#
#     if any(
#             word in text
#             for word in [
#                 "laptop",
#                 "computer",
#                 "wifi",
#                 "password",
#                 "software",
#                 "email",
#                 "printer",
#             ]
#     ):
#         return (
#             TicketCategory.IT,
#             TicketPriority.MEDIUM,
#             "IT Support",
#             8,
#         )
#
#     if any(
#             word in text
#             for word in [
#                 "salary",
#                 "payroll",
#                 "payslip",
#                 "payment",
#                 "salary credit",
#             ]
#     ):
#         return (
#             TicketCategory.PAYROLL,
#             TicketPriority.HIGH,
#             "Payroll Team",
#             4,
#         )
#
#     if any(
#             word in text
#             for word in [
#                 "leave",
#                 "holiday",
#                 "manager",
#                 "benefits",
#                 "policy",
#             ]
#     ):
#         return (
#             TicketCategory.HR,
#             TicketPriority.MEDIUM,
#             "HR Team",
#             8,
#         )
#
#     if any(
#             word in text
#             for word in [
#                 "office",
#                 "facility",
#                 "access card",
#                 "workspace",
#                 "equipment",
#             ]
#     ):
#         return (
#             TicketCategory.OPERATIONS,
#             TicketPriority.MEDIUM,
#             "Operations Team",
#             8,
#         )
#
#     return (
#         TicketCategory.OTHER,
#         TicketPriority.LOW,
#         "General Support",
#         24,
#     )


@router.post("", response_class=HTMLResponse)
async def create_request(
        request: Request,
        employee_name: str = Form(...),
        employee_email: str = Form(...),
        request_text: str = Form(...),
):
    try:
        ticket_input = TicketCreate(
            employee_name=employee_name.strip(),
            employee_email=employee_email.strip(),
            request_text=request_text.strip(),
        )

    except ValidationError as exc:
        return templates.TemplateResponse(
            request=request,
            name="request_form.html",
            context={
                "error": "Please check the information entered and try again.",
                "employee_name": employee_name,
                "employee_email": employee_email,
                "request_text": request_text,
            },
            status_code=422,
        )

    try:
        classification = (
            await ClassificationService.classify(
                ticket_input.request_text
            )
        )

    except Exception as exc:

        print(
            f"AI classification failed: {exc}"
        )

        return templates.TemplateResponse(
            request=request,
            name="request_form.html",
            context={
                "error": (
                    "We couldn't process your request "
                    "right now. Please try again."
                ),
                "employee_name": employee_name,
                "employee_email": employee_email,
                "request_text": request_text,
            },
            status_code=503,
        )

    now = datetime.now(timezone.utc)

    ticket = Ticket(
        ticket_id=generate_ticket_id(),

        employee_name=ticket_input.employee_name,

        employee_email=str(
            ticket_input.employee_email
        ),

        request_text=ticket_input.request_text,

        category=classification.category,
        priority=classification.priority,

        assigned_team=classification.assigned_team,

        status=TicketStatus.OPEN,

        sla_hours=classification.sla_hours,

        sla_due_at=(
                now
                + timedelta(
            hours=classification.sla_hours
        )
        ),

        classification_confidence=(
            classification.confidence
        ),

        classification_reasoning=(
            classification.reasoning
        ),

        created_at=now,
        updated_at=now,

        resolved_at=None,
        is_escalated=False,
    )

    await TicketService.create_ticket(ticket)

    await AutomationService.notify_new_ticket(
        ticket
    )

    return templates.TemplateResponse(
        request=request,
        name="request_success.html",
        context={
            "ticket": ticket,
        },
    )