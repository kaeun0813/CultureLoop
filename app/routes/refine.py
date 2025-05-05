from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.challenge_refiner import refine_description

router = APIRouter()

class RefineRequest(BaseModel):
    raw_text: str

@router.post("/")
def refine_challenge(request: RefineRequest):
    try:
        refined = refine_description(request.raw_text)
        return {"refined_text": refined}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
