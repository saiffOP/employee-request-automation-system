from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class TicketCategory(str, Enum):
    HR = "HR"
    IT = "IT"
    PAYROLL = "Payroll"
    OPERATIONS = "Operations"
    OTHER = "Other"


class TicketPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class TicketStatus(str, Enum):
    OPEN = "Open"
    ACTIVE = "Active"
    FINALIZED = "Finalized"


class TicketCreate(BaseModel):
    employee_name: str = Field(min_length=2, max_length=100)
    employee_email: EmailStr
    request_text: str = Field(min_length=10, max_length=1000)

class AIClassification(BaseModel):
    category: TicketCategory
    priority: TicketPriority
    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )
    reasoning: str = Field(
        min_length=1,
        max_length=300,
    )