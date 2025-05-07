from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.challenge_refiner import refine_challenge

router = APIRouter()

class RefineRequest(BaseModel):
    title: str
    description: str
    city: str

@router.post("/")
def refine_challenge_route(request: RefineRequest):
    try:
        result = refine_challenge(
            title=request.title,
            description=request.description,
            city=request.city
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
