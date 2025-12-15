from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from .. import models, schemas, database
from .auth import get_current_user
from ..services import wardrobe_logic
import shutil
import os
import uuid
import json

router = APIRouter(prefix="/wardrobe", tags=["Wardrobe"])

UPLOAD_DIR = "uploads/wardrobe"

@router.post("/", response_model=schemas.WardrobeItemResponse)
async def upload_wardrobe_item(
    category: str = Form(...),
    color_hex: str = Form(None),
    color_name: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Save file
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Determine match level
    match_level = "neutral"
    if current_user.style_analysis and color_hex:
        analysis = current_user.style_analysis
        match_level = wardrobe_logic.determine_match_level(
            color_hex,
            json.loads(analysis.best_colors),
            json.loads(analysis.neutral_colors),
            json.loads(analysis.worst_colors)
        )
    
    new_item = models.WardrobeItem(
        user_id=current_user.id,
        file_path=file_path,
        category=category,
        color_hex=color_hex,
        color_name=color_name,
        match_level=match_level
    )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.get("/", response_model=list[schemas.WardrobeItemResponse])
def get_wardrobe(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    return current_user.wardrobe_items
