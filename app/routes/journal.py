from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.journal_creator import generate_travel_journal

router = APIRouter()

class JournalRequest(BaseModel):
    title: str
    description: str
    mission: str
    city: str

@router.post("/")
def generate_journal(request: JournalRequest):
    try:
        result = generate_travel_journal(
            title=request.title,
            description=request.description,
            mission=request.mission,
            city=request.city
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
