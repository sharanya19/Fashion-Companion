from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database
from .auth import get_current_user
from ..services.stylist_service import stylist

router = APIRouter(prefix="/outfits", tags=["Outfit Generation"])

@router.post("/generate", response_model=schemas.OutfitGenResponse)
async def generate_outfit(
    request: schemas.OutfitGenRequest,
    current_user: models.User = Depends(get_current_user)
):
    """
    Generates a unique outfit recommendation based on the user's wardrobe and context via Gemini AI.
    """
    # Convert Pydantic model to dict
    req_dict = request.model_dump()
    
    result = await stylist.generate_outfit(current_user, req_dict)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    return result
