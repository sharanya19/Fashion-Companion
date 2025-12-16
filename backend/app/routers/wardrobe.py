from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from .. import models, schemas, database
from .auth import get_current_user
from ..services import wardrobe_logic, vision_service
from ..services.clothing_normalizer import normalize_category, normalize_text
import shutil
import os
import uuid
import json

router = APIRouter(prefix="/wardrobe", tags=["Wardrobe"])

UPLOAD_DIR = "uploads/wardrobe"

@router.post("/", response_model=schemas.WardrobeItemResponse)
async def upload_wardrobe_item(
    category: str = Form(None), # Allow None initially, we normalized it later
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
        
    # --- 1. AI VISION ANALYSIS ---
    try:
        print(f"👁️ Analyzing {filename}...")
        ai_metadata = await vision_service.analyze_clothing_image(file_path)
    except Exception as e:
        print(f"❌ Vision Service Failed: {e}")
        ai_metadata = None

    # --- 2. DATA NORMALIZATION & REPAIR ---
    
    # Raw AI values
    ai_cat = ai_metadata.get("category") if ai_metadata else None
    ai_sub = ai_metadata.get("subcategory") if ai_metadata else None
    ai_color_name = ai_metadata.get("color_primary") if ai_metadata else None
    local_hex = ai_metadata.get("local_hex") if ai_metadata else None
    
    # NORMALIZE CATEGORY (Critical Fix)
    # Use user input if provided, otherwise AI, but ALWAYS normalize
    raw_cat_input = category if category else ai_cat
    final_category = normalize_category(raw_cat_input, ai_sub)
    
    final_subcategory = normalize_text(ai_sub) if ai_sub else None
    
    # COLOR LOGIC (Strict Separation)
    # DB: 'color_primary' stores HEX. 'color_name' stores NAME.
    
    # Hex Source: User Form > Local Vision Hex
    final_hex = color_hex
    if not final_hex and local_hex:
        final_hex = local_hex
        
    # Name Source: User Form > AI Vision Name
    final_name = color_name
    if not final_name and ai_color_name:
        final_name = ai_color_name

    # --- 3. METADATA EXTRACTION ---
    item_type = normalize_text(ai_metadata.get("type")) if ai_metadata else None
    pattern = normalize_text(ai_metadata.get("pattern")) if ai_metadata else None
    fabric = normalize_text(ai_metadata.get("fabric")) if ai_metadata else None
    fit = normalize_text(ai_metadata.get("fit")) if ai_metadata else None
    
    seasonality_str = json.dumps(ai_metadata.get("seasonality", [])) if ai_metadata else "[]"
    occasion_str = json.dumps(ai_metadata.get("occasion_tags", [])) if ai_metadata else "[]"
    style_str = json.dumps(ai_metadata.get("style_tags", [])) if ai_metadata else "[]"

    # --- 4. MATCH LEVEL CALCULATION ---
    match_level = "neutral"
    if current_user.style_analysis and final_hex:
        analysis = current_user.style_analysis
        match_level = wardrobe_logic.determine_match_level(
            final_hex,
            json.loads(analysis.best_colors),
            json.loads(analysis.neutral_colors),
            json.loads(analysis.worst_colors)
        )

    # --- 5. FINAL ASSERTION & LOGGING ---
    print("\n📦 --- FINAL ITEM DATA ---")
    print(f"   Category:    {final_category} (Normalized from '{raw_cat_input}')")
    print(f"   Subcategory: {final_subcategory}")
    print(f"   Color Hex:   {final_hex}")
    print(f"   Color Name:  {final_name}")
    print(f"   Match Level: {match_level}")
    print("-------------------------")

    new_item = models.WardrobeItem(
        user_id=current_user.id,
        file_path=file_path,
        category=final_category,
        subcategory=final_subcategory,
        type=item_type,
        color_primary=final_hex, # DB Field: color_primary stores HEX
        color_secondary=None,
        color_name=final_name,   # DB Field: color_name stores TEXT
        pattern=pattern,
        fabric=fabric,
        fit=fit,
        seasonality=seasonality_str,
        occasion_tags=occasion_str,
        style_tags=style_str,
        match_level=match_level,
        ai_metadata=json.dumps(ai_metadata) if ai_metadata else None
    )
    
    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    except Exception as e:
        print(f"🔥 DATABASE ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Database save failed: {str(e)}")
    
    # Format response for Pydantic
    new_item.seasonality = json.loads(new_item.seasonality) if new_item.seasonality else []
    new_item.occasion_tags = json.loads(new_item.occasion_tags) if new_item.occasion_tags else []
    new_item.style_tags = json.loads(new_item.style_tags) if new_item.style_tags else []
    new_item.ai_metadata = ai_metadata
    
    return new_item

@router.get("/", response_model=list[schemas.WardrobeItemResponse])
def get_wardrobe(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    return current_user.wardrobe_items

@router.delete("/{item_id}")
def delete_wardrobe_item(item_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    item = db.query(models.WardrobeItem).filter(models.WardrobeItem.id == item_id, models.WardrobeItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if os.path.exists(item.file_path):
        try:
            os.remove(item.file_path)
        except:
            pass
            
    db.delete(item)
    db.commit()
    return {"message": "Deleted"}
