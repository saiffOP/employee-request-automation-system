from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config.templates import templates


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def request_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="request_form.html",
        context={},
    )