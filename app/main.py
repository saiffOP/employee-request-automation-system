from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes.web import router as web_router
from app.routes.tickets import router as tickets_router
from app.database.mongodb import check_mongodb_connection
from app.routes.admin import router as admin_router

from app.routes.internal import router as internal_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Employee Request Management System",
    description="Internal employee request management and automation system.",
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

app.include_router(web_router)
app.include_router(tickets_router)
app.include_router(admin_router)
app.include_router(internal_router)

@app.get("/health")
async def health_check():

    mongodb_connected = (
        await check_mongodb_connection()
    )

    return {
        "status": (
            "healthy"
            if mongodb_connected
            else "degraded"
        ),
        "service": "employee-request-system",
        "mongodb": (
            "connected"
            if mongodb_connected
            else "disconnected"
        ),
    }