import os

from dotenv import load_dotenv


load_dotenv()


MONGODB_URI = os.getenv("MONGODB_URI")

MONGODB_DATABASE = os.getenv(
    "MONGODB_DATABASE",
    "employee_request_system",
)


if not MONGODB_URI:
    raise RuntimeError(
        "MONGODB_URI is missing. "
        "Add it to the .env file."
    )

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENAI_CLASSIFICATION_MODEL = os.getenv(
    "OPENAI_CLASSIFICATION_MODEL",
    "gpt-5.6-luna",
)


if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY is missing. "
        "Add it to the .env file."
    )

N8N_NEW_REQUEST_WEBHOOK_URL = os.getenv(
    "N8N_NEW_REQUEST_WEBHOOK_URL"
)

INTERNAL_API_KEY = os.getenv(
    "INTERNAL_API_KEY"
)

if not INTERNAL_API_KEY:
    raise RuntimeError(
        "INTERNAL_API_KEY is missing. "
        "Add it to the .env file."
    )