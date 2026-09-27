from datetime import datetime, timezone

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.config.templates import templates
from app.services.ticket_service import TicketService



router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.get("", response_class=HTMLResponse)
async def admin_dashboard(request: Request):

    tickets = await TicketService.get_all_tickets()

    now = datetime.now(timezone.utc)

    total_count = len(tickets)

    open_count = sum(
        ticket["status"] == "Open"
        for ticket in tickets
    )

    active_count = sum(
        ticket["status"] == "Active"
        for ticket in tickets
    )

    finalized_count = sum(
        ticket["status"] == "Finalized"
        for ticket in tickets
    )

    overdue_count = sum(
        ticket["status"] != "Finalized"
        and ticket.get("sla_due_at")
        and ticket["sla_due_at"] < now
        for ticket in tickets
    )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "tickets": tickets,
            "total_count": total_count,
            "open_count": open_count,
            "active_count": active_count,
            "finalized_count": finalized_count,
            "overdue_count": overdue_count,
            "now": now,
        },
    )


@router.get(
    "/tickets/{ticket_id}",
    response_class=HTMLResponse,
)
async def ticket_details(
        request: Request,
        ticket_id: str,
):

    ticket = await TicketService.get_ticket(
        ticket_id
    )

    if not ticket:
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            context={
                "message": "Ticket not found."
            },
            status_code=404,
        )

    now = datetime.now(timezone.utc)

    is_overdue = (
            ticket["status"] != "Finalized"
            and ticket.get("sla_due_at") is not None
            and ticket["sla_due_at"] < now
    )

    return templates.TemplateResponse(
        request=request,
        name="ticket_detail.html",
        context={
            "ticket": ticket,
            "is_overdue": is_overdue,
        },
    )


@router.post(
    "/tickets/{ticket_id}/status"
)
async def update_ticket_status(
        ticket_id: str,
        status: str = Form(...),
):

    await TicketService.update_ticket_status(
        ticket_id=ticket_id,
        new_status=status,
    )

    return RedirectResponse(
        url=f"/admin/tickets/{ticket_id}",
        status_code=303,
    )