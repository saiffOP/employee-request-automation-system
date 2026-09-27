from dataclasses import dataclass

from openai import AsyncOpenAI

from app.config.settings import (
    OPENAI_API_KEY,
    OPENAI_CLASSIFICATION_MODEL,
)
from app.schemas.ticket import (
    AIClassification,
    TicketCategory,
    TicketPriority,
)


client = AsyncOpenAI(
    api_key=OPENAI_API_KEY
)


TEAM_BY_CATEGORY = {
    TicketCategory.HR: "HR Team",
    TicketCategory.IT: "IT Support",
    TicketCategory.PAYROLL: "Payroll Team",
    TicketCategory.OPERATIONS: "Operations Team",
    TicketCategory.OTHER: "General Support",
}


SLA_BY_PRIORITY = {
    TicketPriority.CRITICAL: 1,
    TicketPriority.HIGH: 4,
    TicketPriority.MEDIUM: 8,
    TicketPriority.LOW: 24,
}


@dataclass
class ClassificationResult:
    category: TicketCategory
    priority: TicketPriority

    assigned_team: str
    sla_hours: int

    confidence: float
    reasoning: str


class ClassificationService:

    @staticmethod
    async def classify(
            request_text: str,
    ) -> ClassificationResult:

        response = await client.responses.parse(
            model=OPENAI_CLASSIFICATION_MODEL,

            input=[
                {
                    "role": "system",
                    "content": (
                        "You classify internal employee "
                        "support requests.\n\n"

                        "Choose exactly one category:\n"
                        "- HR: leave, benefits, workplace "
                        "policies, employee relations, "
                        "people-related requests.\n"
                        "- IT: laptops, computers, software, "
                        "accounts, passwords, email, network, "
                        "WiFi, printers and technical issues.\n"
                        "- Payroll: salary, payslips, "
                        "compensation payments, deductions "
                        "and payroll discrepancies.\n"
                        "- Operations: office facilities, "
                        "access cards, workspace, equipment "
                        "and operational support.\n"
                        "- Other: requests that do not "
                        "reasonably fit another category.\n\n"

                        "Choose exactly one priority:\n"
                        "- Critical: severe business impact, "
                        "security/access emergency, or an "
                        "issue preventing essential work "
                        "for multiple people.\n"
                        "- High: significant employee or "
                        "business impact requiring prompt "
                        "attention.\n"
                        "- Medium: normal support request "
                        "that should be addressed soon.\n"
                        "- Low: informational, minor, or "
                        "non-urgent request.\n\n"

                        "Use only information contained in "
                        "the employee request. Do not invent "
                        "missing facts.\n\n"

                        "Confidence must be between 0 and 1. "
                        "Use lower confidence when the "
                        "request is vague or could reasonably "
                        "belong to multiple categories.\n\n"

                        "Reasoning should be a short "
                        "operational explanation."
                    ),
                },
                {
                    "role": "user",
                    "content": request_text,
                },
            ],

            text_format=AIClassification,
        )

        ai_result = response.output_parsed

        if ai_result is None:
            raise RuntimeError(
                "AI classification returned no result."
            )

        assigned_team = TEAM_BY_CATEGORY[
            ai_result.category
        ]

        sla_hours = SLA_BY_PRIORITY[
            ai_result.priority
        ]

        return ClassificationResult(
            category=ai_result.category,
            priority=ai_result.priority,

            assigned_team=assigned_team,
            sla_hours=sla_hours,

            confidence=ai_result.confidence,
            reasoning=ai_result.reasoning,
        )