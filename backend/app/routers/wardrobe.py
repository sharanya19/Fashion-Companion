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
import re

router = APIRouter(prefix="/wardrobe", tags=["Wardrobe"])

UPLOAD_DIR = "uploads/wardrobe"

ALLOWED_CATEGORIES = {"Top", "Bottom", "OnePiece", "Outerwear", "Footwear", "Accessory"}

SRC_AI = "ai"
CONF_HIGH = "high"


# -------------------------
# Helpers
# -------------------------
def is_valid_hex(value: str) -> bool:
    return bool(value and re.fullmatch(r"#?[0-9a-fA-F]{6}", value))


def normalize_hex(value: str) -> str | None:
    if not is_valid_hex(value):
        return None
    return value if value.startswith("#") else f"#{value}"


# -------------------------
# Upload Item
# -------------------------
@router.post("/", response_model=schemas.WardrobeItemResponse)
async def upload_wardrobe_item(
    file: UploadFile = File(...),
    category: str = Form(None),
    color_hex: str = Form(None),
    color_name: str = Form(None),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Save file
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # -------------------------
    # 1️⃣ Gemini Vision
    # -------------------------
    try:
        ai_metadata = await vision_service.analyze_clothing_image(file_path)
    except Exception:
        ai_metadata = None

    ai_color_name = None
    ai_sub = None

    if ai_metadata:
        ai_color_name = ai_metadata.get("color_primary")
        ai_sub = ai_metadata.get("subcategory") or ai_metadata.get("item_type")

    # -------------------------
    # 2️⃣ CATEGORY (Gemini → Filename)
    # -------------------------
    final_category = "Uncategorized"
    decision_meta = {}

    semantic_inputs = []

    if ai_metadata:
        semantic_inputs.extend([
            ai_metadata.get("category"),
            ai_metadata.get("subcategory"),
            ai_metadata.get("type"),
            ai_metadata.get("item_type"),
            ai_metadata.get("garment"),
        ])

    normalized = normalize_category(*semantic_inputs)

    if normalized in ALLOWED_CATEGORIES:
        final_category = normalized
        decision_meta["category"] = {
            "value": final_category,
            "source": SRC_AI,
            "confidence": CONF_HIGH,
        }

    # Filename fallback
    if final_category == "Uncategorized":
        fname = (file.filename or "").lower()
        normalized = normalize_category(fname)
        if normalized in ALLOWED_CATEGORIES:
            final_category = normalized

    final_subcategory = normalize_text(ai_sub) if ai_sub else None

    # -------------------------
    # 3️⃣ COLOR
    # -------------------------
    final_hex = normalize_hex(color_hex) if color_hex else None
    final_name = color_name or ai_color_name or "Unknown"

    # -------------------------
    # 4️⃣ METADATA
    # -------------------------
    item_type = normalize_text(ai_metadata.get("type")) if ai_metadata else None
    pattern = normalize_text(ai_metadata.get("pattern")) if ai_metadata else None
    fabric = normalize_text(ai_metadata.get("fabric")) if ai_metadata else None
    fit = normalize_text(ai_metadata.get("fit")) if ai_metadata else None

    seasonality = json.dumps(ai_metadata.get("seasonality", [])) if ai_metadata else "[]"
    occasions = json.dumps(ai_metadata.get("occasion_tags", [])) if ai_metadata else "[]"
    styles = json.dumps(ai_metadata.get("style_tags", [])) if ai_metadata else "[]"

    # -------------------------
    # 5️⃣ MATCH LEVEL
    # -------------------------
    match_level = "neutral"
    if current_user.style_analysis and final_hex:
        sa = current_user.style_analysis
        match_level = wardrobe_logic.determine_match_level(
            final_hex,
            json.loads(sa.best_colors),
            json.loads(sa.neutral_colors),
            json.loads(sa.worst_colors),
        )

    # -------------------------
    # 6️⃣ SAVE
    # -------------------------
    ai_meta_to_store = None
    if isinstance(ai_metadata, dict):
        ai_meta_to_store = {**ai_metadata, "decision_meta": decision_meta}

    new_item = models.WardrobeItem(
        user_id=current_user.id,
        file_path=file_path,
        category=final_category,
        subcategory=final_subcategory,
        type=item_type,
        color_primary=final_hex,
        color_secondary=None,
        color_name=final_name,
        pattern=pattern,
        fabric=fabric,
        fit=fit,
        seasonality=seasonality,
        occasion_tags=occasions,
        style_tags=styles,
        match_level=match_level,
        ai_metadata=json.dumps(ai_meta_to_store) if ai_meta_to_store else None,
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return schemas.WardrobeItemResponse(
        id=new_item.id,
        file_path=new_item.file_path.replace("\\", "/"),
        category=new_item.category,
        subcategory=new_item.subcategory,
        type=new_item.type,
        color_primary=new_item.color_primary,
        color_secondary=None,
        color_name=new_item.color_name,
        pattern=new_item.pattern,
        fabric=new_item.fabric,
        fit=new_item.fit,
        seasonality=json.loads(new_item.seasonality),
        occasion_tags=json.loads(new_item.occasion_tags),
        style_tags=json.loads(new_item.style_tags),
        match_level=new_item.match_level,
        ai_metadata=json.loads(new_item.ai_metadata) if new_item.ai_metadata else None,
    )


# -------------------------
# Get Wardrobe
# -------------------------
@router.get("/", response_model=list[schemas.WardrobeItemResponse])
def get_wardrobe(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    return [
        schemas.WardrobeItemResponse(
            id=i.id,
            file_path=i.file_path.replace("\\", "/"),
            category=i.category,
            subcategory=i.subcategory,
            type=i.type,
            color_primary=i.color_primary,
            color_secondary=None,
            color_name=i.color_name,
            pattern=i.pattern,
            fabric=i.fabric,
            fit=i.fit,
            seasonality=json.loads(i.seasonality),
            occasion_tags=json.loads(i.occasion_tags),
            style_tags=json.loads(i.style_tags),
            match_level=i.match_level,
            ai_metadata=json.loads(i.ai_metadata) if i.ai_metadata else None,
        )
        for i in current_user.wardrobe_items
    ]


# -------------------------
# Delete Item
# -------------------------
@router.delete("/{item_id}")
def delete_wardrobe_item(
    item_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    item = (
        db.query(models.WardrobeItem)
        .filter(models.WardrobeItem.id == item_id)
        .first()
    )

    if not item or item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Item not found")

    if os.path.exists(item.file_path):
        os.remove(item.file_path)

    db.delete(item)
    db.commit()
    return {"message": "Deleted"}
