from pymongo import AsyncMongoClient

from app.config.settings import (
    MONGODB_DATABASE,
    MONGODB_URI,
)


client = AsyncMongoClient(
    MONGODB_URI,
    tz_aware=True,
)

database = client[MONGODB_DATABASE]

tickets_collection = database["tickets"]


async def check_mongodb_connection() -> bool:
    try:
        await client.admin.command("ping")
        return True

    except Exception as exc:
        print(
            f"MongoDB connection failed: {exc}"
        )
        return False