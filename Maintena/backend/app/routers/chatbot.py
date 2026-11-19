
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from google import genai

from app.database import get_db
from app.models.machine import Machine
from app.models.maintenance import Maintenance


# Load backend .env file
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

router = APIRouter(
    prefix="/api/chat",
    tags=["AI Chatbot"]
)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(
        default_factory=list,
        max_length=10
    )


@router.post("/")
def chat(request: ChatRequest, db: Session = Depends(get_db)):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Gemini API key is not configured."
        )

    try:
        # Fetch actual machine records
        machines = db.query(Machine).limit(50).all()

        # Fetch actual maintenance records
        maintenance_records = (
            db.query(Maintenance)
            .order_by(Maintenance.created_at.desc())
            .limit(50)
            .all()
        )

        machine_data = []

        for machine in machines:
            machine_data.append({
                "id": machine.id,
                "name": machine.name,
                "code": machine.machine_code,
                "location": machine.location,
                "status": machine.status,
                "last_maintenance": (
                    machine.last_maintenance.isoformat()
                    if machine.last_maintenance else None
                )
            })

        maintenance_data = []

        for record in maintenance_records:
            maintenance_data.append({
                "machine_id": record.machine_id,
                "title": record.title,
                "description": record.description,
                "type": record.maintenance_type,
                "priority": record.priority,
                "status": record.status,
                "scheduled_date": (
                    record.scheduled_date.isoformat()
                    if record.scheduled_date else None
                ),
                "cost": (
                    float(record.cost)
                    if record.cost is not None else None
                )
            })

        # Build conversation history
        conversation = ""

        for item in request.history[-10:]:
            speaker = (
                "User" if item.role == "user"
                else "Assistant"
            )
            conversation += (
                f"\n{speaker}: {item.content}"
            )

        # Give Gemini real database context
        prompt = f"""
You are Maintena AI, an intelligent industrial
maintenance assistant.

Your responsibilities:
1. Analyze machine operational status.
2. Explain maintenance schedules.
3. Identify high-priority maintenance tasks.
4. Recommend preventive maintenance.
5. Help users understand their factory equipment.

IMPORTANT RULES:
- Use the supplied database information.
- Never invent machine records or maintenance history.
- Do not invent machine health scores or sensor readings.
- Clearly state when information is unavailable.
- Give practical, professional recommendations.
- Keep responses clear and easy to understand.
- Do not claim to have performed any database changes.

MACHINE DATABASE:
{machine_data}

MAINTENANCE DATABASE:
{maintenance_data}

PREVIOUS CONVERSATION:
{conversation}

CURRENT USER QUESTION:
{request.message}

Provide a helpful answer based on the available data.
"""

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )

        if not response.text:
            raise HTTPException(
                status_code=502,
                detail="AI returned an empty response."
            )

        return {
            "reply": response.text,
            "status": "success"
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="AI service is temporarily unavailable. Please try again."
        )
