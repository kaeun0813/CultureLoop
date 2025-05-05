from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.challenge_generator import generate_challenges
from typing import List

router = APIRouter()

class ChallengeRequest(BaseModel):
    city: str
    style: List[str]
    date: str  # "25/05/01" 형식
    count: int = 5

@router.post("/generate")
async def create_challenges(request: ChallengeRequest):
    try:
        challenges = generate_challenges(
            city=request.city,
            style=request.style,
            date=request.date,  # 문자열 그대로 넘김
            count=request.count
        )
        return {"challenges": challenges}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
